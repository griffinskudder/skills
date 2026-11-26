---
name: autonomous-software-delivery
description: Drive a software change autonomously from a request or backlog item through the requested delivery endpoint. Use for end-to-end implementation, pull request and CI follow-through, or resuming a delivery run.
---

# Autonomous Software Delivery

Requires access to the target project. Remote endpoints require the project's authorized repository, CI, or deployment tools.

## Establish the endpoint

Read the request, repository guidance, current work, and the checks that govern the intended endpoint. Identify the furthest requested outcome and its observable completion condition. If asked only to build or fix something, use a verified local patch as the default. For an endpoint that involves remote changes, establish the authorized repository, branch or environment, and actions. Check whether those actions trigger downstream effects, such as a merge that automatically deploys.

Turn the outcome into acceptance checks and choose the smallest slice that can be verified through a real entry point. Resolve routine decisions from existing behavior and conventions. If a product decision, external permission, or increase in risk changes what can safely proceed, resolve what you can from available evidence, continue independent work, and ask for the specific decision at the blocked step.

## Run the delivery loop

1. Establish the relevant baseline and implement the active slice. Run the cheapest meaningful behavior check early and inspect failures before retrying.
2. Verify the slice against the original acceptance checks. Use the actual application, API, or CLI when that is where the behavior lives. For a material risk that ordinary checks do not cover, use a fresh verification pass against the task and candidate, or an independent evaluator when available and authorized.
3. For a requested pull request, inspect the current remote state, update the intended pull request or open it, and attach reproducible evidence. When the endpoint includes CI or review follow-through, watch required checks on the latest revision, diagnose failures, and resolve in-scope findings. After a push, verify the new revision.
4. For an authorized merge, confirm the current candidate meets the project's required checks and approvals, then use the normal merge or queue mechanism. Observe the merge result and identify the resulting revision. If the merge triggers an authorized deployment, observe that run before deciding whether another deployment action is needed.
5. For an authorized release, use the existing pipeline for the verified artifact or revision. Observe the target version, rollout health, and affected behavior. Follow the established recovery process if health checks fail.

Repeat for the remaining slices until the endpoint's conditions are observed. Phase skills in this collection can provide additional detail when installed. For a small change, keep the loop in one session. Parallel work can help when slices have separate write ownership and stable contracts. Verify the integrated result once the changes come together.

## Resume or stop

For work likely to outlast a session, keep a brief checkpoint in the existing issue, plan, or other authorized location using [the checkpoint fields](references/checkpoint.md). Record it before a handoff and after any external action with a pending result. On resume, reconcile it with the working tree and remote state before acting. A timeout can leave an operation running or completed.

Change the hypothesis after a repeatable failure. When further progress depends on missing access, judgment, or an external state the agent cannot change, report the exact dependency and the last verified state. Report the endpoint reached, the revision or artifact where applicable, and any acceptance checks still unverified.
