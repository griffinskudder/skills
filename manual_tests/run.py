"""Prepare and check local skill evaluations. Run with --help for commands."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = json.loads((HERE / "cases.json").read_text())
SCENARIOS = json.loads((HERE / "scenarios.json").read_text())
SKILLS = sorted((ROOT / "groups").glob("*/skills/*/SKILL.md"))


def run(*args, cwd=ROOT):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def install(*args):
    return run(sys.executable, str(ROOT / "install.py"), *args)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def files(directory):
    return {p.relative_to(directory): p.read_bytes() for p in directory.rglob("*") if p.is_file()}


def check():
    names = [p.parent.name for p in SKILLS]
    require(len(names) == len(set(names)), "Duplicate skill names")
    require(set(names) == set(CASES), f"Case coverage mismatch: {set(names) ^ set(CASES)}")
    require(SCENARIOS.keys() <= CASES.keys(), "Unknown skill in scenarios")
    for variants in SCENARIOS.values():
        for label, scenario in variants.items():
            require(label != "default" and scenario.get("prompt") and scenario.get("criteria"),
                    f"Incomplete scenario: {label}")
            require(all(Path(name).name == name for name in scenario.get("files", {})),
                    f"Fixture files must be local filenames: {label}")
    for path in SKILLS:
        content = path.read_text(encoding="utf-8")
        header = re.match(r"^---\n(.*?)\n---\n", content, re.S)
        require(header, f"Missing frontmatter: {path}")
        fields = dict(re.findall(r"^(name|description):[ \t]*(.+)$", header[1], re.M))
        require(fields.get("name") == path.parent.name and fields.get("description", "").strip(),
                f"Invalid name or description: {path}")
        for link in re.findall(r"\]\(([^)]+)\)", content):
            target = link.split("#")[0]
            if target and not re.match(r"[a-z]+:", target):
                require((path.parent / target).exists(), f"Broken link in {path}: {link}")
    for group in sorted({p.parents[2].name for p in SKILLS}):
        expected = {p.parent.name: p.parent for p in SKILLS if p.parents[2].name == group}
        require(set(install("--group", group, "--list").splitlines()) == set(expected), group)
        with tempfile.TemporaryDirectory() as temp:
            install("--group", group, "--dir", temp)
            require({p.name for p in Path(temp).iterdir()} == set(expected), group)
            for name, source in expected.items():
                require(files(source) == files(Path(temp) / name), f"Incomplete install: {name}")
        print(f"{group}: {len(expected)} skills passed")


def prepare(skill, mode, scenario="default", installed=None, destination=".agents/skills",
            replacement=None):
    group = next(p.parents[2].name for p in SKILLS if p.parent.name == skill)
    fixture = HERE / "fixtures" / group.removeprefix("software-")
    work = Path(tempfile.mkdtemp(prefix="skill-trial-")).resolve()
    shutil.copytree(fixture, work, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))

    def git(*args):
        env = dict(os.environ, GIT_AUTHOR_DATE="2020-01-01T00:00:00Z",
                   GIT_COMMITTER_DATE="2020-01-01T00:00:00Z")
        return subprocess.check_output([
            "git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "-c", "commit.gpgsign=false", *args], cwd=work, env=env, text=True).strip()

    git("init", "-q")
    git("config", "core.autocrlf", "false")
    git("add", ".")
    git("commit", "-qm", "Baseline")
    if group == "software-delivery":
        run(sys.executable, "-B", "-m", "unittest", cwd=work)
        (work / "build.txt").write_text(f"Passing unit tests for {git('rev-parse', 'HEAD')}\n")
        (work / "pricing.py").write_text("def total(price, quantity):\n    return price\n")
        git("add", "pricing.py", "build.txt")
        git("commit", "-qm", "Candidate")
    prompt, rubric = CASES[skill]
    if scenario != "default":
        variant = SCENARIOS[skill][scenario]
        prompt, rubric = variant["prompt"], variant["criteria"]
        for name, content in variant.get("files", {}).items():
            (work / name).write_bytes(content.encode("utf-8"))
        if variant.get("files"):
            git("add", ".")
            git("commit", "-qm", "Scenario")
    sources = {p.parent.name: p.parent for p in SKILLS}
    if replacement:
        sources[skill] = replacement
    for name in sources if installed is None else installed:
        shutil.copytree(sources[name], work / destination / name)
    with (work / ".git" / "info" / "exclude").open("a") as exclude:
        exclude.write("\n.agents/\n.claude/\n__pycache__/\n")
    if mode == "outcome":
        prompt = f"Use the {skill} skill. " + prompt
    elif mode == "routing":
        rubric = f"Look for activation of {skill} in the session trace."
    return work, prompt, rubric


def codex_trials(selection, modes, executable):
    cli = shutil.which(executable)
    require(cli, f"Cannot find {executable}. Supply the CLI path with --executable.")
    results = Path(tempfile.mkdtemp(prefix="codex-skill-results-")).resolve()
    print(f"Results: {results}", flush=True)
    for skill in selection:
        for mode in modes:
            work, prompt, rubric = prepare(skill, mode)
            case = results / f"{skill}.{mode}"
            case.mkdir()
            (case / "trial.json").write_text(json.dumps({
                "checkout": str(work), "prompt": prompt, "criteria": rubric,
            }, indent=2), encoding="utf-8")
            print(f"Running {skill} {mode}", flush=True)
            env = os.environ.copy()
            if os.name == "nt":
                # The Windows sandbox runs Git as a different user from the fixture creator.
                index = int(env.get("GIT_CONFIG_COUNT", "0"))
                env[f"GIT_CONFIG_KEY_{index}"] = "safe.directory"
                env[f"GIT_CONFIG_VALUE_{index}"] = work.as_posix()
                env["GIT_CONFIG_COUNT"] = str(index + 1)
            with (case / "events.jsonl").open("wb") as events, (case / "stderr.txt").open("wb") as errors:
                result = subprocess.run([
                    cli, "exec", "--ephemeral", "--sandbox", "workspace-write", "--json",
                    "-o", str(case / "answer.txt"), prompt,
                ], cwd=work, env=env, stdin=subprocess.DEVNULL, stdout=events, stderr=errors)
            require(result.returncode == 0, f"Codex exited {result.returncode}. Inspect {case}")
    print(f"Grade each trace and checkout against the criteria in {results}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("check")
    commands.add_parser("list")
    trial = commands.add_parser("prepare")
    trial.add_argument("skill", choices=sorted(CASES))
    trial.add_argument("mode", choices=["routing", "outcome"])
    trial.add_argument("--scenario", default="default")
    codex = commands.add_parser("codex", help="run fresh Codex CLI trials and retain evidence")
    codex.add_argument("skill", choices=[*sorted(CASES), "all"])
    codex.add_argument("mode", choices=["routing", "outcome", "both"])
    codex.add_argument("--executable", default="codex")
    args = parser.parse_args()
    if args.command == "check":
        check()
    elif args.command == "list":
        print(*sorted(CASES), sep="\n")
    elif args.command == "codex":
        skills = sorted(CASES) if args.skill == "all" else [args.skill]
        modes = ["routing", "outcome"] if args.mode == "both" else [args.mode]
        codex_trials(skills, modes, args.executable)
    else:
        require(args.scenario == "default" or args.scenario in SCENARIOS.get(args.skill, {}),
                f"Unknown scenario for {args.skill}: {args.scenario}")
        work, prompt, rubric = prepare(args.skill, args.mode, args.scenario)
        print(f"Open a fresh agent session in {work}\n\nPrompt:\n{prompt}")
        print(f"\nEvaluator only:\n{rubric}")


if __name__ == "__main__":
    main()
