"""Compare two synchronous Django requests prepared by a project fixture."""

import argparse
import json
import os
import sys
from collections import Counter
from collections.abc import Callable
from contextlib import ExitStack
from dataclasses import dataclass
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from time import perf_counter

import django
from django.db import connections
from django.http import HttpResponse
from django.template.response import SimpleTemplateResponse


@dataclass
class Profile:
    response_bytes: int
    elapsed_ms: float
    shapes: Counter[tuple[str, str]]

    def metrics(self) -> dict[str, int | float]:
        return {
            "queries": sum(self.shapes.values()),
            "response_bytes": self.response_bytes,
            "elapsed_ms": round(self.elapsed_ms, 3),
        }


def measure(request: Callable[[], HttpResponse]) -> Profile:
    statements: list[tuple[str, str]] = []

    def capture(execute, sql, params, many, context):
        statements.append((context["connection"].alias, sql))
        return execute(sql, params, many, context)

    with ExitStack() as stack:
        for alias in connections:
            stack.enter_context(connections[alias].execute_wrapper(capture))
        start = perf_counter()
        response = request()
        if isinstance(response, SimpleTemplateResponse):
            response.render()
        elapsed_ms = (perf_counter() - start) * 1000

    if not 200 <= response.status_code < 300 or response.streaming:
        raise ValueError(
            f"Expected a successful, non-streaming response (HTTP {response.status_code})."
        )

    # Report only fingerprints. Raw SQL can have values embedded in it.
    shapes = Counter(
        (alias, sha256(" ".join(sql.split()).encode()).hexdigest()[:16])
        for alias, sql in statements
    )
    return Profile(len(response.content), elapsed_ms, shapes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenarios",
        required=True,
        metavar="MODULE:FACTORY",
        help="Fixture context manager factory yielding (small_request, large_request).",
    )
    parser.add_argument("--settings", help="Override DJANGO_SETTINGS_MODULE.")
    parser.add_argument("--max-query-growth", type=int, metavar="N")
    args = parser.parse_args()
    module_name, _, factory_name = args.scenarios.partition(":")
    if not module_name or not factory_name:
        parser.error("--scenarios must be in MODULE:FACTORY form")
    if args.max_query_growth is not None and args.max_query_growth < 0:
        parser.error("--max-query-growth must be nonnegative")

    if args.settings:
        os.environ["DJANGO_SETTINGS_MODULE"] = args.settings
    sys.path.insert(0, str(Path.cwd()))
    django.setup()
    factory = getattr(import_module(module_name), factory_name)
    with factory() as (small_request, large_request):
        small = measure(small_request)
        large = measure(large_request)

    small_metrics, large_metrics = small.metrics(), large.metrics()
    delta = {
        key: round(large_metrics[key] - value, 3)
        for key, value in small_metrics.items()
    }
    shapes = [
        {
            "database": alias,
            "fingerprint": fingerprint,
            "small": small.shapes[alias, fingerprint],
            "large": large.shapes[alias, fingerprint],
        }
        for alias, fingerprint in sorted(small.shapes.keys() | large.shapes.keys())
    ]
    report = {
        "small": small_metrics,
        "large": large_metrics,
        "delta": delta,
        "query_shapes": shapes,
    }
    print(json.dumps(report, indent=2))
    if args.max_query_growth is not None and delta["queries"] > args.max_query_growth:
        print(
            f"Query growth exceeded the limit of {args.max_query_growth}.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
