"""Run one natural-prompt trial in a mountless local Docker Sandbox."""

import argparse
import json
import re
import subprocess
import tarfile
from pathlib import Path
from time import monotonic
from uuid import uuid4

from run import CASES, SCENARIOS, prepare, require


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host", choices=["claude", "codex"])
    parser.add_argument("skill", choices=sorted(CASES))
    parser.add_argument("arm", choices=["none", "only", "coordinator", "prior"])
    parser.add_argument("--scenario", default="default")
    parser.add_argument("--prior-dir", type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--sbx", default="sbx")
    parser.add_argument("--results", type=Path, required=True,
                        help="new output directory, or an unfinished run to resume after sign-in")
    args = parser.parse_args()
    out = args.results.resolve()
    params = [args.host, args.skill, args.arm, args.scenario, args.model]
    require(args.scenario == "default" or args.scenario in SCENARIOS.get(args.skill, {}),
            "Unknown scenario for this skill")
    meta_path = out / "trial.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        require(meta["parameters"] == params and "elapsed_seconds" not in meta, "Trial mismatch or finished")
    else:
        require(args.arm != "prior" or (args.prior_dir and (args.prior_dir / "SKILL.md").is_file()),
                "Supply the complete prior skill directory")
        out.mkdir(parents=True)
        installed = {"none": [], "coordinator": ["autonomous-software-delivery"]}.get(args.arm, [args.skill])
        work, prompt, rubric = prepare(args.skill, "compare", args.scenario, installed,
                                       ".claude/skills" if args.host == "claude" else ".agents/skills",
                                       args.prior_dir if args.arm == "prior" else None)
        meta = {"parameters": params, "sandbox": "skill-" + uuid4().hex[:12], "installed": installed,
                "fixture": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=work, text=True).strip(),
                "prompt": prompt, "rubric": rubric}
        with tarfile.open(out / "inputs.tar.gz", "w:gz") as archive:
            archive.add(work, arcname="fixture")
            if args.skill in {"diagnose-django-performance", "verify-django-migrations"}:
                import asgiref
                import django
                import sqlparse
                def sources(member):
                    return None if "__pycache__" in Path(member.name).parts else member
                for module in (asgiref, django, sqlparse):
                    archive.add(Path(module.__file__).parent, arcname="deps/" + module.__name__, filter=sources)
        save(meta_path, meta)
    name = meta["sandbox"]
    sbx = [args.sbx, "--no-input"]
    inside = [*sbx, "exec", "-w", "/tmp/fixture", "-e", "PYTHONPATH=/tmp/deps",
              "-e", "PYTHONDONTWRITEBYTECODE=1", name, "--"]
    if not meta.get("created"):
        subprocess.run([*sbx, "create", "--name", name, "--skills", "off", "--cpus", "2",
                        "--memory", "4g", args.host], check=True)
        meta["created"] = True
        save(meta_path, meta)
    if not meta.get("prepared"):
        domains = ("api.anthropic.com:443,claude.ai:443,platform.claude.com:443" if args.host == "claude"
                   else "chatgpt.com:443,api.openai.com:443,auth.openai.com:443")
        subprocess.run([*sbx, "policy", "allow", "network", domains, "--sandbox", name], check=True)
        subprocess.run([*sbx, "cp", str(out / "inputs.tar.gz"), name + ":/tmp/inputs.tar.gz"], check=True)
        subprocess.run([*sbx, "exec", name, "--", "tar", "-xzf", "/tmp/inputs.tar.gz", "-C", "/tmp"], check=True)
        meta["prepared"] = True
        save(meta_path, meta)
    print(f"Sandbox {name}. Evidence {out}", flush=True)
    uid = subprocess.check_output([*inside, "id", "-u"], text=True).strip()
    require(uid.isdecimal() and int(uid) > 0, "Expected an unprivileged trial user")
    if subprocess.run([*inside, "test", "-S", "/var/run/docker.sock"]).returncode == 0:
        # Some sbx kits supply a Docker engine inside their own VM.
        engine_id = ["docker", "info", "--format", "{{.ID}}"]
        guest = subprocess.check_output([*inside, *engine_id], text=True).strip()
        host = subprocess.check_output(engine_id, text=True).strip()
        require(guest and host and guest != host, "Expected separate guest and host Docker engines")
    revision = subprocess.check_output([*inside, "git", "rev-parse", "HEAD"], text=True).strip()
    require(revision == meta["fixture"], "Copied fixture revision differs from the trial manifest")
    if args.host == "claude":
        auth = subprocess.run([*inside, "claude", "auth", "status"], capture_output=True)
        require(auth.returncode == 0, f"Sign in using sbx exec -it {name} -- claude auth login and repeat the command")
        command = ["claude", "-p", "--model", args.model, "--setting-sources", "project",
                   "--strict-mcp-config", "--no-session-persistence", "--dangerously-skip-permissions",
                   "--tools", "Read,Write,Edit,Glob,Grep,Bash,Skill,Agent",
                   "--output-format", "stream-json", "--verbose", meta["prompt"]]
    else:
        common = ["codex", "-m", args.model, "-s", "danger-full-access", "-a", "never",
                  "--disable", "plugins", "--disable", "apps", "--disable", "skill_search"]
        inventory = json.loads(subprocess.check_output([*inside, *common, "debug", "prompt-input"]))
        names = {m for msg in inventory if msg.get("role") == "developer" for item in msg.get("content", [])
                 for m in re.findall(r"^- (\S+?): .*?\(file: .+?\)$", item.get("text", ""), re.M)}
        require(names and names.intersection(CASES) == set(meta["installed"]), "Codex skill catalog mismatch")
        meta["skills"] = sorted(names)
        command = [*common, "exec", "--json", "-o", "/tmp/final.txt", meta["prompt"]]
    meta["cli_version"] = subprocess.check_output([*inside, args.host, "--version"], text=True).strip()
    save(meta_path, meta)
    start = monotonic()
    try:
        with (out / "events.jsonl").open("wb") as stdout, (out / "stderr.txt").open("wb") as stderr:
            result = subprocess.run([*inside, *command], stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                    timeout=900)
    except subprocess.TimeoutExpired:
        meta["error"] = "Timed out after 900 seconds"
        save(meta_path, meta)
        subprocess.run([*sbx, "stop", name], check=True)
        raise
    meta["elapsed_seconds"] = round(monotonic() - start, 2)
    meta["exit"] = result.returncode
    save(meta_path, meta)
    events = [json.loads(line) for line in (out / "events.jsonl").read_bytes().splitlines() if line.startswith(b"{")]
    if args.host == "claude":
        init = next((e for e in events if e.get("subtype") == "init"), {})
        final = next((e for e in reversed(events) if e["type"] == "result"), {})
        (out / "answer.txt").write_text(final.get("result", ""), encoding="utf-8")
        meta["plugins"] = init.get("plugins", [])
        meta["skills"] = init.get("skills", [])
        save(meta_path, meta)
        require(not final.get("is_error", True) and all(p.get("path") == "builtin" for p in meta["plugins"])
                and "skills" in init and set(init["skills"]).intersection(CASES) == set(meta["installed"]),
                "Claude error or skill inventory mismatch")
    else:
        require(any(e["type"] == "turn.completed" for e in events), "Missing Codex completion")
        subprocess.run([*sbx, "cp", name + ":/tmp/final.txt", str(out / "answer.txt")], check=True)
    require(result.returncode == 0, "Agent process failed")
    with (out / "patch.diff").open("wb") as patch:
        subprocess.run([*inside, "git", "diff", meta["fixture"]], stdout=patch, check=True)
    subprocess.run([*sbx, "stop", name], check=True)


if __name__ == "__main__":
    main()
