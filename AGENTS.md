# Working in this repository

- When adding or moving a skill, keep its `SKILL.md` and supporting files together under `groups/<group>/skills/<skill-name>/`. Match the frontmatter `name` to the folder name and keep it unique across the repository. Installers use that name in a shared destination directory.
- When writing a skill, follow the [Agent Skills specification](https://agentskills.io/specification), describe when the skill should be used, and link to bundled files with paths relative to `SKILL.md`. Use agent-neutral instructions and state any runtime requirements.
- When adding a group or changing distribution, follow the [README instructions for the affected installer or marketplace](README.md).
- When changing the installer or group layout, list the affected group with `python install.py --group <group> --list`, then install it into a temporary `--dir` and check the copied files. When changing Claude marketplace manifests, run `claude plugin validate .` if the CLI is available.
