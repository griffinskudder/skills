---
name: setup-delivery-repository
description: Make a software repository ready for autonomous work with reproducible setup, navigable project guidance, and runnable feedback loops. Use when bootstrapping a repository or repairing setup and verification gaps.
---

# Set Up a Delivery Repository

Requires access to the target checkout. Clean-start verification also needs the project's supported runtime, dependency sources, and any local services.

1. Inspect existing runtime pins, manifests, lockfiles, developer commands, CI, and repository guidance. Attempt the documented workflow in a clean checkout or isolated environment where feasible. Identify the first meaningful gap between checkout and reliable behavior verification.
2. Establish a reproducible path from checkout to a running application or build. Use the existing package manager, version constraints, and task entry points where they work. Document prerequisites, safe sample configuration, and deterministic fixtures for real entry points. When the supported runtime range is unknown, report the version used for verification. A new version pin needs a project requirement. Prefer local or disposable dependencies and synthetic test data for agent checks.
3. Make important context discoverable from the checkout. Keep agent guidance short and point to the authoritative commands, architecture boundaries, and quirks. Where a recurring mistake can be recognized mechanically, encode the invariant in a test, linter, or build check at the appropriate boundary. Give failures enough context to reproduce and diagnose them.
4. Give agents a fast check for iterative work and a broader check for behavior across boundaries. For a contributor bootstrap request, the endpoint is a working local verification command. Add a hosted workflow only when requested. An existing workflow can identify the command contributors should run. For concurrent runs, isolate working directories and mutable resources such as ports, databases, and output directories. Keep test logs and traces accessible without exposing secrets or sensitive fixture data.
5. Run the documented check from a clean checkout and report its actual result. If setup succeeds and the check exposes an existing product defect, record the failing command and expected and observed behavior. Fix product behavior when the request includes that repair. Report which dependencies still require access or manual setup.

Use [tooling choices](references/tooling.md) when a demonstrated gap needs a tool. For a narrow setup request, implement the smallest useful improvement and run its check. For a new repo, establish one working path before layering on additional tools.
