"""Paired, naturally routed skill trials in disposable Claude Code or Codex projects."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from time import monotonic
from uuid import uuid4

from run import CASES, SCENARIOS, prepare, require, run


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def add_commands(commands):
    parser = commands.add_parser("compare", help="compare skill sets on identical fixtures")
    parser.add_argument("skill", choices=sorted(CASES))
    parser.add_argument("--scenario", default="default")
    parser.add_argument("--arms", nargs="+", choices=["all", "without", "only", "none",
                                                      "candidate", "coordinator"],
                        default=["all", "without"])
    parser.add_argument("--candidate-dir", type=Path, help="alternate complete skill directory")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--model", required=True)
    parser.add_argument("--host", choices=["claude", "codex"], default="claude")
    parser.add_argument("--retain-codex-session", action="store_true",
                        help="keep the local Codex session so delegated agents can load parent context")
    parser.add_argument("--executable", help="path to the selected host CLI")
    parser.add_argument("--timeout", type=int, default=900, metavar="SECONDS",
                        help="maximum wall time per session (default 900)")
    parser.add_argument("--prepare-only", action="store_true")
    parser.set_defaults(handler=compare)
    summary = commands.add_parser("summarize", help="summarize graded pairs")
    summary.add_argument("results", type=Path)
    summary.set_defaults(handler=summarize)


def execute(cli, case, work, prompt, model, installed, timeout):
    started = monotonic()
    with (case / "events.jsonl").open("wb") as events, (case / "stderr.txt").open("wb") as errors:
        command = [
            cli, "-p", "--model", model, "--setting-sources", "project", "--strict-mcp-config",
            "--no-session-persistence", "--permission-mode", "acceptEdits",
            "--tools", "Read,Write,Edit,Glob,Grep,Bash,Skill,Agent",
            "--output-format", "stream-json", "--verbose", prompt,
        ]
        try:
            result = subprocess.run(command, cwd=work, stdout=events, stderr=errors,
                                    stdin=subprocess.DEVNULL, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"valid": False, "error": "timeout", "elapsed_seconds": timeout}
    elapsed = round(monotonic() - started, 2)
    init, final = {}, {}
    for line in (case / "events.jsonl").read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if event.get("subtype") == "init":
            init = event
        if event.get("type") == "result":
            final = event
    discovered = set(init.get("skills", []))
    valid = ("skills" in init and discovered.intersection(CASES) == set(installed)
             and not init.get("plugins") and result.returncode == 0 and final
             and not final.get("is_error") and final.get("subtype") == "success")
    (case / "answer.txt").write_text(final.get("result", ""), encoding="utf-8")
    return {"valid": bool(valid), "exit": result.returncode, "model": init.get("model"),
            "elapsed_seconds": elapsed, "usage": final.get("usage"),
            "cost_usd": final.get("total_cost_usd"),
            "other_skills": sorted(discovered.difference(CASES))}


def execute_codex(cli, case, work, prompt, model, installed, timeout, retain_session=False):
    # Keep installed personal skills from filling in an intentionally absent condition.
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    personal = [p for root in (codex_home, Path.home() / ".agents")
                for p in (root / "skills").glob("*/SKILL.md")]
    exclusions = ",".join("{path=" + json.dumps(p.as_posix()) + ",enabled=false}" for p in personal)
    common = [cli, "--disable", "plugins", "--disable", "apps", "--disable", "skill_search",
              "-c", f"skills.config=[{exclusions}]", "-c", "model=" + json.dumps(model),
              "-a", "never", "-s", "workspace-write"]
    env = os.environ.copy()
    if os.name == "nt":
        index = int(env.get("GIT_CONFIG_COUNT", "0"))
        env.update({f"GIT_CONFIG_KEY_{index}": "safe.directory",
                    f"GIT_CONFIG_VALUE_{index}": work.as_posix(), "GIT_CONFIG_COUNT": str(index + 1)})
    with (case / "stderr.txt").open("wb") as errors:
        try:
            inventory = subprocess.run([*common, "debug", "prompt-input"], cwd=work, env=env,
                                       stdout=subprocess.PIPE, stderr=errors, timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"valid": False, "error": "Codex prompt inventory timed out"}
        if inventory.returncode:
            return {"valid": False, "error": "Codex prompt inventory unavailable"}
        sections = [item.get("text", "") for msg in json.loads(inventory.stdout)
                    for item in msg.get("content", []) if msg.get("role") == "developer"]
        discovered = {m for section in sections if "### Available skills" in section
                      for m in re.findall(r"^- (\S+?): .*?\(file: .+?\)$", section, re.M)}
        if not discovered or discovered.intersection(CASES) != set(installed):
            return {"valid": False, "error": "Codex skill inventory mismatch",
                    "discovered": sorted(discovered)}
        started = monotonic()
        with (case / "events.jsonl").open("wb") as events:
            try:
                session_flags = [] if retain_session else ["--ephemeral"]
                result = subprocess.run([*common, "exec", *session_flags, "--json", "-o",
                                         str(case / "answer.txt"), prompt], cwd=work, env=env,
                                        stdout=events, stderr=errors, stdin=subprocess.DEVNULL,
                                        timeout=timeout)
            except subprocess.TimeoutExpired:
                return {"valid": False, "error": "timeout", "elapsed_seconds": timeout}
    events = [json.loads(line) for line in (case / "events.jsonl").read_bytes().splitlines()]
    completed = [event for event in events if event.get("type") == "turn.completed"]
    spawn_errors = (case / "stderr.txt").read_bytes().count(b"collab spawn failed")
    return {"valid": bool(result.returncode == 0 and completed and (case / "answer.txt").is_file()),
            "exit": result.returncode, "model": model, "elapsed_seconds": round(monotonic() - started, 2),
            "usage": completed[-1].get("usage") if completed else None, "cost_usd": None,
            "other_skills": sorted(discovered.difference(CASES)), "spawn_errors": spawn_errors}


def compare(args):
    skill = args.skill
    require(args.scenario == "default" or args.scenario in SCENARIOS.get(skill, {}),
            f"Unknown scenario for {skill}: {args.scenario}")
    require(args.timeout > 0, "Use a positive timeout.")
    require(args.host == "codex" or not args.retain_codex_session,
            "--retain-codex-session requires --host codex.")
    require(args.repeat > 0 and len(set(args.arms)) == len(args.arms) >= 2,
            "Use at least two distinct arms and a positive repeat count.")
    if "candidate" in args.arms:
        require(args.candidate_dir and (args.candidate_dir / "SKILL.md").is_file(),
                "Supply --candidate-dir with the alternate skill and supporting files.")
        header = (args.candidate_dir / "SKILL.md").read_text(encoding="utf-8").split("---", 2)
        require(len(header) == 3 and f"name: {skill}" in header[1].splitlines(),
                "Candidate frontmatter must name the target skill.")
    cli = shutil.which(args.executable or args.host)
    require(args.prepare_only or cli, f"Missing executable: {args.executable or args.host}")
    results = Path(tempfile.mkdtemp(prefix="skill-comparison-"))
    print(f"Results: {results}", flush=True)
    manifest = {"skill": skill, "scenario": args.scenario, "model": args.model, "host": args.host,
                "repetitions": args.repeat,
                "harness": run(cli, "--version") if not args.prepare_only else None,
                "arms": args.arms, "trials": []}
    if args.host == "claude":
        manifest["permission_mode"] = "acceptEdits"
    else:
        manifest["retained_session"] = args.retain_codex_session
    sets = {"all": sorted(CASES), "without": sorted(CASES.keys() - {skill}), "only": [skill],
            "none": [], "candidate": [skill], "coordinator": ["autonomous-software-delivery"]}
    for repetition in range(args.repeat):
        # Rotate the starting condition to reduce order effects across repeats.
        start = repetition % len(args.arms)
        for arm in args.arms[start:] + args.arms[:start]:
            installed = sets[arm]
            destination = ".claude/skills" if args.host == "claude" else ".agents/skills"
            work, prompt, rubric = prepare(skill, "compare", args.scenario, installed,
                                           destination,
                                           args.candidate_dir if arm == "candidate" else None)
            revision = run("git", "rev-parse", "HEAD", cwd=work)
            case = results / uuid4().hex[:12]
            case.mkdir()
            save(case / "task.json", {"checkout": str(work), "prompt": prompt, "criteria": rubric})
            save(case / "grade.json", {"endpoint": "ungraded", "activation": "unknown",
                                       "findings": [], "review_seconds": None, "evidence": ""})
            bundle = work / destination
            digests = {p.relative_to(bundle).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in sorted(bundle.rglob("*")) if p.is_file()}
            trial = {"id": case.name, "repeat": repetition + 1, "arm": arm, "fixture": revision,
                     "skill_files": digests}
            manifest["trials"].append(trial)
            save(results / "manifest.json", manifest)
            if args.prepare_only:
                continue
            print(f"Running {case.name}", flush=True)
            params = (cli, case, work, prompt, args.model, installed, args.timeout)
            if args.host == "claude":
                trial.update(execute(*params))
            else:
                trial.update(execute_codex(*params, retain_session=args.retain_codex_session))
            save(results / "manifest.json", manifest)
            require(trial["valid"], f"Incomplete or contaminated trial. Inspect {case}.")


def summarize(args):
    manifest = json.loads((args.results / "manifest.json").read_text(encoding="utf-8"))
    baseline, *alternatives = manifest["arms"]
    pairs = {i: {} for i in range(1, manifest["repetitions"] + 1)}
    for trial in manifest["trials"]:
        grade = json.loads((args.results / trial["id"] / "grade.json").read_text(encoding="utf-8"))
        pairs[trial["repeat"]][trial["arm"]] = (trial, grade)
    for alternative in alternatives:
        counts = dict(wins=0, ties=0, losses=0, unverified=0)
        for pair in pairs.values():
            comparisons = [pair.get(name) for name in (baseline, alternative)]
            if not all(comparisons):
                counts["unverified"] += 1
                continue
            (left, a), (right, b) = comparisons
            if (not all(t.get("valid") and g["endpoint"] in ("pass", "fail") and g["evidence"]
                        for t, g in comparisons)
                    or any(left[k] != right[k] for k in ("fixture", "model", "other_skills"))):
                counts["unverified"] += 1
                continue
            if a["endpoint"] == b["endpoint"]:
                counts["ties"] += 1
            elif b["endpoint"] == "pass":
                counts["wins"] += 1
            else:
                counts["losses"] += 1
        print(f"{alternative} relative to {baseline}: {counts}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_commands(parser.add_subparsers(dest="command", required=True))
    args = parser.parse_args()
    args.handler(args)
