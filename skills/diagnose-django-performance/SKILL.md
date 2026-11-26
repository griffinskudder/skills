---
name: diagnose-django-performance
description: Diagnose slow Django requests, especially formsets and pages whose query count, rendering cost, or response size grows with saved rows or catalogue entries.
---

# Diagnose Django performance

## Reproduce at the request boundary

- Exercise the real route with representative permissions and persisted fixtures. Include response rendering in the measurement. For template responses that render lazily, call `render()` inside the capture.
- Vary one dimension at a time. Compare a small record with a larger record against the same catalogue, then vary catalogue size with the record held fixed. Use `CaptureQueriesContext` to count SQL on the relevant tables or group it by query shape. Keep bind values and record contents out of shared output.
- Measure response bytes and relevant render or browser timings when the page is still slow with stable query counts. A collapsed section can still render and send every control. If Python work dominates, time the suspected function separately on the same inputs before and after the change.

Use [compare_request_profiles.py](scripts/compare_request_profiles.py) for a repeatable comparison. Run it from the Django project root in the project's Python environment with test settings and an isolated database.

```sh
python path/to/compare_request_profiles.py --settings project.test_settings --scenarios request_fixtures:scenarios --max-query-growth 0
```

The factory must return a context manager that prepares fixtures and authentication, yields two zero-argument callables returning synchronous Django responses, and cleans up the fixtures on exit. Have each callable run the route once, for example `lambda: client.get(small_url)`. The script measures those calls and any remaining template rendering. It emits JSON with query counts by database and SQL fingerprint, response bytes, and elapsed time. The query growth limit sets exit status 1 when the large case exceeds it. Timings are single samples.

## Fix the work that grows

- Inspect templates and widgets for ORM evaluation after the view has assembled its context. A formset of `ModelChoiceField` dropdowns can read the same catalogue once per row even when the saved line items came from a single query. For identical choices, materialize the display choices once per request and reuse them. Use `list(iter(field.choices))` for Django's model choice iterator to bypass the extra count from its length hint. Keep each field's validation queryset and permission scope. Include inactive entries when historical records can still reference them.
- Check for repeated in-memory scans such as searching all rows for each roll-up target or block. Accumulate totals keyed by target or group in a pass over the inputs. Compare old and new results for ordering, exclusions, stored values, and rounding.
- If HTML size dominates, count repeated options or components and measure the browser cost before choosing deferred rendering. Preserve selection and submission behavior, including validation and permissions, when changing when controls load.

## Verify the result

- Keep a route-level regression test for the demonstrated scaling issue. Compare the relevant query count at two fixture sizes and assert that the selected values and totals still render correctly. Use timing to report the local speedup and a deterministic metric such as query count or repeated element count for the test.
- Report fixture sizes, before-and-after measurements, the measurement boundary, and any remaining growth. Distinguish a faster summary function from a faster request or browser load.
