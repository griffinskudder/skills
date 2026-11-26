---
name: release-delivery-change
description: Prepare or execute a software release for a specified revision and environment, then verify rollout health. Use when asked to deploy, publish, monitor, or recover a software rollout.
---

# Release a Delivery Change

Requires access to the project's release workflow. Execution and health verification require authorized release and monitoring access.

1. Identify the candidate artifact or revision, release target, current deployed version, and applicable runbook. Confirm required checks and approvals apply to that artifact. Confirm authority for the release action, target, and any recovery actions before making those changes.
2. Identify how the rollout will be judged before starting it. Use the project's version check, smoke test, health signals and observation window. Find the supported recovery path. If data or schema changes affect recovery, check whether the previous application version can still operate on the resulting data and whether forward recovery is required.
3. For a new rollout, use the established deployment path and staged rollout when supported. If monitoring an existing rollout, locate its operation and confirm its target and artifact. If asked to recover a rollout, check its current impact and apply the authorized recovery procedure. Record the operation ID and verify which artifact reached the intended environment. If a mutation times out or its result is unclear, inspect the existing run and target state before retrying.
4. Verify the changed behavior and required health signals through the defined observation window. If the rollout breaches an agreed threshold, stop promotion and follow the authorized recovery path. Verify the resulting environment after recovery. Escalate with the operation ID and observed impact if the next remediation requires a decision or access.

For a preparation request, return the candidate, prerequisites, health checks, and recovery path. For execution, report the target environment, deployed artifact, rollout state, and observed health or remaining blocker. A pipeline success confirms the release operation ran. The runtime evidence establishes rollout health.
