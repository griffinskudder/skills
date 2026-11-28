# Working in this repository

- When adding or moving a skill, keep its `SKILL.md` and supporting files together under `groups/<group>/skills/<skill-name>/`. Match the frontmatter `name` to the folder name and keep it unique across the repository. Installers use that name in a shared destination directory.
- When writing a skill, follow the [Agent Skills specification](https://agentskills.io/specification), describe when the skill should be used, and link to bundled files with paths relative to `SKILL.md`. Use agent-neutral instructions and state any runtime requirements.
- When adding a group or changing distribution, follow the [README instructions for the affected installer or marketplace](README.md).
- When changing the installer or group layout, list the affected group with `python install.py --group <group> --list`, then install it into a temporary `--dir` and check the copied files. When changing Claude marketplace manifests, run `claude plugin validate .` if the CLI is available.

## Evaluate skill value

- Use the [paired evaluation workflow](README.md#compare-skill-outcomes) to compare a natural task prompt with and without the target skill. Hold the model, settings, prompt, and fixture revision fixed within each pair. Use fresh, mountless [Docker Sandboxes](README.md#run-a-trial-in-docker-sandboxes) with synthetic fixtures for unattended execution.
- Grade each result against the case rubric using the answer, trace, and resulting checkout. Replay behavior checks with independent inputs when practical. Record skill activation from the trace and flag failed runs or mismatched pairs.
- Compare verified outcome first, then elapsed agent time and cost per attempt. Exclude sandbox setup and independent grading from agent time. Record reported cost when available. For estimates, record the rate source and price uncached input, cached input, and output separately.
- Rotate the order across repeats and use a held-out scenario to confirm a result before retaining, revising, or removing a skill on benchmark evidence. Report initial pairs as observations from their fixtures.
