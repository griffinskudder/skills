# Skills

A personal collection of reusable [Agent Skills](https://agentskills.io/specification) organized by topic. Each group keeps its skills under `groups/<group>/skills/`. Each skill includes a `SKILL.md` and any supporting files.

Browse or clone the [griffinskudder/skills repository on GitHub](https://github.com/griffinskudder/skills).

## Skill groups

### Django

- [Diagnose Django performance](groups/django/skills/diagnose-django-performance/SKILL.md) covers query growth, template rendering costs, and response size in slow Django requests.

## Install from GitHub

Run these commands inside the Git repository where you want to use the skills. Use a recent version of [GitHub CLI with `gh skill`](https://cli.github.com/manual/gh_skill_install). The `universal` target installs into the shared project directory `.agents/skills`.

GitHub CLI discovers skills in nested directories such as `groups/django/skills/`. On GitHub, select a skill by name or install the entire repository with `--all`.

```sh
gh skill install griffinskudder/skills diagnose-django-performance --agent universal
gh skill install griffinskudder/skills --all --agent universal
```

For a user-wide install, use `--scope user` and set `--agent` to your agent's ID, such as `claude-code` or `codex`. Pass `--pin <tag-or-commit-sha>` to install a specific revision.

You can also install with [Vercel's `skills` CLI](https://github.com/vercel-labs/skills).

```sh
npx skills add griffinskudder/skills --skill diagnose-django-performance
```

## Install from a checkout

Run the script with Python 3.8 or later from the project where you want to use the skills. Replace `/path/to/skills` with the path to this checkout.

```sh
python /path/to/skills/install.py --list
python /path/to/skills/install.py --list-groups
python /path/to/skills/install.py --group django --list
python /path/to/skills/install.py --group django
python /path/to/skills/install.py diagnose-django-performance
python /path/to/skills/install.py --dir .claude/skills --group django
```

Repeat `--group` to select multiple groups. You can also include individual skill names. With no selection, the installer installs every skill. The default destination is `.agents/skills` under the current working directory. Use `--dir` for your agent's configured skills directory. The installer copies each complete skill directory directly into that destination and refuses to overwrite existing installations.

To install only one group with GitHub CLI, point `--from-local` at that group's directory and use `--all`.

```sh
gh skill install "/path/to/skills/groups/django" --from-local --all --agent universal
```

## Claude Code marketplace

The Claude Code marketplace offers one plugin per group. To use a local checkout, replace `griffinskudder/skills` with its path. [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugins/create-marketplace)

```sh
claude plugin marketplace add griffinskudder/skills
claude plugin install django@griffinskudder-skills
```

Plugins use the repository commit as their version. Claude's validator may suggest adding an explicit version.

## Add a group

For a new topic such as Software Delivery, put its first skill under `groups/software-delivery/skills/<skill-name>/`. The Python installer discovers the group automatically. To offer it through Claude Code, use the Django group's plugin manifest as a template and add a matching entry to `.claude-plugin/marketplace.json`. Keep skill names unique across groups because they share an installation directory.
