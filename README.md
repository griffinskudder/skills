# Skills

A personal collection of reusable [Agent Skills](https://agentskills.io/specification) organized by topic. Each group keeps its skills under `groups/<group>/skills/`. Each skill includes a `SKILL.md` and any supporting files.

Browse or clone the [griffinskudder/skills repository on GitHub](https://github.com/griffinskudder/skills).

## Skill groups

### Software Architecture

Start with [Design a Modular Monolith](groups/software-architecture/skills/design-modular-monolith/SKILL.md) to choose a deployment model and define business module boundaries. The default is one deployable with clear module APIs and data ownership, using ports and adapters where they help isolate business behavior.

- [Apply Hexagonal Architecture](groups/software-architecture/skills/apply-hexagonal-architecture/SKILL.md) introduces ports and adapters around a use case and verifies the real entry point.
- [Review Architecture Boundaries](groups/software-architecture/skills/review-architecture-boundaries/SKILL.md) traces code and runtime coupling, data ownership, and dependency direction.
- [Evaluate Service Extraction](groups/software-architecture/skills/evaluate-service-extraction/SKILL.md) tests the case for independent deployment and plans an incremental migration when warranted.

The [research findings](groups/software-architecture/skills/design-modular-monolith/references/research.md) explain the rationale, trade-offs, and limits of the evidence.

### Software Delivery

Start with [Autonomous Software Delivery](groups/software-delivery/skills/autonomous-software-delivery/SKILL.md) to carry a change to a specified endpoint, such as a verified patch, a pull request with passing CI, or a verified rollout. Use any of the phase skills directly when you need a narrower workflow.

For a multi-slice plan, ask to use subagent-driven delivery. When the host supports delegation, the workflow assigns each slice to a fresh implementer, reviews it independently, and checks the integrated change before proceeding to the requested endpoint.

- [Triage a Delivery Request](groups/software-delivery/skills/triage-delivery-request/SKILL.md) decides whether a request is ready for autonomous execution and returns underspecified work with the question that would unblock it.
- [Plan a Delivery Change](groups/software-delivery/skills/plan-delivery-change/SKILL.md) turns a request into observable acceptance criteria and independently verifiable slices.
- [Implement a Delivery Slice](groups/software-delivery/skills/implement-delivery-slice/SKILL.md) builds one slice with fast feedback and leaves evidence the next session can use.
- [Verify a Delivery Change](groups/software-delivery/skills/verify-delivery-change/SKILL.md) checks the actual behavior, relevant regressions, and CI for the candidate revision.
- [Release a Delivery Change](groups/software-delivery/skills/release-delivery-change/SKILL.md) drives an authorized rollout through health checks and recovery when needed.

Use [Set Up a Delivery Repository](groups/software-delivery/skills/setup-delivery-repository/SKILL.md) to make the project easy to bootstrap, navigate, and verify. Use [Set Up Continuous Delivery](groups/software-delivery/skills/setup-continuous-delivery/SKILL.md) to establish merge checks, artifact promotion, and release verification. Both include tooling options and selection criteria.

The workflow uses repository-local context, short feedback loops, and checkpoints for work that spans sessions. It treats independent evaluation as an option for difficult changes and measures progress at the requested delivery endpoint. The design draws on [OpenAI's harness engineering case study](https://openai.com/index/harness-engineering/), [Anthropic's long-running harness experiments](https://www.anthropic.com/research/harness-design-long-running-apps), [DORA's research on small batches](https://dora.dev/capabilities/working-in-small-batches/), and the working paper [Writing Code vs. Shipping Code](https://doi.org/10.3386/w35275).

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
python /path/to/skills/install.py --group software-architecture
python /path/to/skills/install.py --group software-delivery
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
claude plugin install software-architecture@griffinskudder-skills
claude plugin install software-delivery@griffinskudder-skills
claude plugin install django@griffinskudder-skills
```

Plugins use the repository commit as their version. Claude's validator may suggest adding an explicit version.

## Run the manual skill tests

From the checkout, use Python 3.9+ to check all skill packages or prepare an agent trial. Trials also require Git. The Django outcome case needs a Python environment with Django installed.

```sh
python manual_tests/run.py check
python manual_tests/run.py list
python manual_tests/run.py prepare verify-delivery-change outcome
python manual_tests/run.py prepare verify-delivery-change routing
python manual_tests/run.py codex verify-delivery-change both
python manual_tests/run.py codex all both
```

The `codex` command requires a signed-in Codex CLI supporting `exec --ephemeral --json`. Use `--executable "<path to codex>"` if it is outside PATH. Each trial sends its prompt and the fixture content Codex reads to your configured model provider. The full run starts 26 independent sessions. The printed results directory contains each trial’s prompt, checkout path, grading criteria, JSONL trace, error log and final answer. A successful CLI exit means the session completed. Grade routing from evidence that Codex opened the checkout’s copy of the skill or explicitly activated it, and grade outcomes from the answer and checkout. If activation is hidden, record routing as unverified.

`check` verifies case coverage, skill metadata, local links, group listings and byte-for-byte installs. For a trial, open the printed temporary repository in a fresh agent session that discovers project skills from `.agents/skills`. Paste only the printed prompt. Each run creates an independent checkout with all skills installed and leaves it available for inspection.

Use `routing` to see which skill the agent opens for a natural request. Record the actual activation from the session trace. Mark it unverified if the host doesn’t expose activation. Prompts for neighboring skills serve as negative examples: for instance, the plan-only request should end with a plan. Use `outcome` to name the skill explicitly and compare the final checkout, commands and answer with the printed evaluator criteria. Record the skill, mode, model, pass/fail and supporting evidence. Repeat both modes for each name from `list` for a full manual run. Delete a trial directory after reviewing it.

## Add a group

For a new topic such as Software Delivery, put its first skill under `groups/software-delivery/skills/<skill-name>/`. The Python installer discovers the group automatically. To offer it through Claude Code, use the Django group's plugin manifest as a template and add a matching entry to `.claude-plugin/marketplace.json`. Keep skill names unique across groups because they share an installation directory.
