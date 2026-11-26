# Repository tooling choices

Start from the supported runtime, host, and team workflow. Check current support and platform constraints before introducing a new dependency.

| Need | Practical starting point |
| --- | --- |
| Reproducible dependencies | Use the ecosystem's lockfile and locked install mode. For projects using uv or npm, see [uv locking and syncing](https://docs.astral.sh/uv/concepts/projects/sync/) and [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci/). |
| Shared commands | Keep existing package scripts, a Makefile, or repository scripts as the entry point. Add a command wrapper only when several consumers otherwise duplicate the same setup or checks. |
| Consistent system tooling | Use the existing runtime pin when it covers the need. A [Dev Container](https://code.visualstudio.com/docs/devcontainers/create-dev-container) helps when workspace provisioning needs consistent OS packages and the supported agents can use the container. |
| Disposable dependencies | [Docker Compose](https://docs.docker.com/reference/cli/docker/compose/) can start local backing services for integration checks. Keep service readiness, seed, and reset steps reproducible. |
| Browser behavior | Add a small [Playwright](https://playwright.dev/docs/trace-viewer-intro) suite when browser interaction is where correctness lives. Capture failure traces if reviewers can access them safely. |
| Repository navigation | Use the project's supported instruction file, such as [AGENTS.md](https://agents.md/), as a short map to authoritative project files. Use local architecture notes and machine-readable contracts where they help answer recurring questions. [OpenAI harness engineering case study](https://openai.com/index/harness-engineering/) |

Choose a tool when it removes a specific obstacle in the clean-start or verification path. Give each new tool a place in the documented setup and an observable way to verify it.
