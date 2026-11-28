"""Local regression checks for paired fixtures and grading. No provider calls."""

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import compare
from run import run


class ComparisonTests(unittest.TestCase):
    def test_codex_checks_inventory_before_starting_the_agent(self):
        target = "implement-delivery-slice"
        with tempfile.TemporaryDirectory() as temp:
            case = Path(temp)
            def emit(command, **streams):
                if "prompt-input" in command:
                    catalog = f"### Available skills\n- {target}: Trial skill (file: r0/{target}/SKILL.md)"
                    prompt = [{"role": "developer", "content": [{"text": catalog}]}]
                    return SimpleNamespace(returncode=0, stdout=json.dumps(prompt).encode())
                streams["stdout"].write(b'{"type":"turn.completed","usage":{"output_tokens":20}}\n')
                (case / "answer.txt").write_text("Done")
                return SimpleNamespace(returncode=0)

            with patch("compare.subprocess.run", side_effect=emit) as runner:
                trial = compare.execute_codex("unused", case, case, "prompt", "test", [], 1)
                self.assertFalse(trial["valid"])
                self.assertEqual(runner.call_count, 1)
                trial = compare.execute_codex("unused", case, case, "prompt", "test", [target], 1)
                self.assertTrue(trial["valid"])
                self.assertEqual(trial["usage"]["output_tokens"], 20)

    def test_discovery_and_provider_errors(self):
        def emit(command, **streams):
            for event in (init, final):
                streams["stdout"].write((json.dumps(event) + "\n").encode())
            return SimpleNamespace(returncode=0)

        target = "implement-delivery-slice"
        init = {"type": "system", "subtype": "init", "model": "test", "skills": [target]}
        final = {"type": "result", "subtype": "success", "result": "done", "is_error": False}
        with tempfile.TemporaryDirectory() as temp, patch("compare.subprocess.run", emit):
            case = Path(temp)
            def execute(installed):
                return compare.execute("unused", case, case, "prompt", "test", installed, 1)

            self.assertTrue(execute([target])["valid"])
            self.assertFalse(execute([])["valid"])
            final["is_error"] = True
            self.assertFalse(execute([target])["valid"])

    def test_paired_fixtures_and_scoring(self):
        with tempfile.TemporaryDirectory() as temp:
            original = tempfile.mkdtemp

            def make_temp(**kwargs):
                return original(dir=temp, **kwargs)

            args = SimpleNamespace(skill="implement-delivery-slice", scenario="held-out",
                                   arms=["none", "only", "without"], candidate_dir=None,
                                   repeat=2, timeout=1, executable="unused",
                                   prepare_only=True, model="test", host="claude", retain_codex_session=False)
            with patch.object(tempfile, "mkdtemp", make_temp), redirect_stdout(io.StringIO()):
                compare.compare(args)
            results, = Path(temp).glob("skill-comparison-*")
            manifest = json.loads((results / "manifest.json").read_text())
            prompts, revisions = set(), set()
            for trial in manifest["trials"]:
                case = results / trial["id"]
                task = json.loads((case / "task.json").read_text())
                checkout = Path(task["checkout"])
                prompts.add(task["prompt"])
                revisions.add(run("git", "rev-parse", "HEAD", cwd=checkout))
                installed = {p.parent.name for p in (checkout / ".claude/skills").glob("*/SKILL.md")}
                expected = {"none": set(), "only": {args.skill},
                            "without": compare.CASES.keys() - {args.skill}}
                self.assertEqual(installed, expected[trial["arm"]])
                self.assertEqual(run("git", "status", "--porcelain", cwd=checkout), "")
                # Synthetic grades exercise the aggregator, independently of model outcomes.
                trial.update(valid=True, model="test", other_skills=[])
                passed = trial["arm"] == "only"
                compare.save(case / "grade.json", {"endpoint": "pass" if passed else "fail",
                                                   "evidence": "synthetic test grade"})
            self.assertEqual(len(prompts), 1)
            self.assertEqual(len(revisions), 1)
            manifest["trials"][-1]["valid"] = False
            compare.save(results / "manifest.json", manifest)
            with redirect_stdout(io.StringIO()) as output:
                compare.summarize(SimpleNamespace(results=results))
            self.assertEqual(output.getvalue().splitlines(), [
                "only relative to none: {'wins': 1, 'ties': 0, 'losses': 0, 'unverified': 1}",
                "without relative to none: {'wins': 0, 'ties': 1, 'losses': 0, 'unverified': 1}",
            ])


if __name__ == "__main__":
    unittest.main()
