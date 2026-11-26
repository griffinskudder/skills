---
name: setup-continuous-delivery
description: Establish or improve CI, merge gates, and a repeatable release path for a software project. Use when setting up a delivery pipeline, selecting CI/CD tools, or making changes releasable in small batches.
---

# Set Up Continuous Delivery

Requires access to the project's source and pipeline configuration. Enabling hosted controls, publishing artifacts, or exercising deployments requires authorization and platform access.

## Establish the smallest working pipeline

1. Trace the current path from proposed change to release. Identify the source host, CI triggers, required checks, artifact store, release target, and any existing approvals and recovery procedure. Use the platform the project can operate. For a library or CLI, treat package or binary publication as the release endpoint.
2. Run fast, reliable checks for proposed changes with the same project commands used locally. Make required checks report explicit outcomes for all eligible changes, including when filtering paths or using a merge queue. Test the check on a disposable candidate before making it required. Keep slow jobs off the merge path unless their evidence is needed to merge safely.
3. Build a release artifact from a trusted revision. Record the source revision, build run, and immutable artifact identity. Where release promotion applies, promote the tested artifact rather than rebuilding it for each environment. Keep dependencies, automation references, and release configuration under version control.
4. Separate validation of untrusted contributions from jobs that can publish or deploy. Use narrowly scoped job permissions, isolated runners for different trust levels when needed, and short-lived workload identity where supported. Scope the trust policy to the approved source and target. Apply repository and environment controls through the host's supported mechanisms. Keep production promotion under the project's approved policy.
5. Exercise deployment or publication in an authorized test target. Check the artifact identity, runtime behavior or installability, and rollout signals. Decide how to stop promotion and recover if health degrades. For schema or data changes, verify compatibility across versions before depending on rollback, or establish a forward recovery path. Serialize releases per target where overlapping promotions could conflict.

For a first pipeline, prove one path from pull request checks to a releasable artifact and test release. Introduce advanced controls when the release target, risk, or operating load justifies them. For platform choices and common validation traps, see [pipeline tooling](references/pipeline-tooling.md).

## Verify the setup

Demonstrate that a passing candidate clears checks and a deliberately failing check prevents promotion in a disposable setting. Confirm that an untrusted change cannot access privileged deployment credentials through the configured workflow permissions. Demonstrate artifact traceability and a smoke check after test promotion. Exercise the recovery path when the environment permits. Report which checks were exercised, with run links or commands, and which controls require platform access to verify.
