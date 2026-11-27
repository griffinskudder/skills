# Delivery checkpoint

Keep enough state for another session to take the next action without reconstructing the conversation. Use the project's existing work record when available.

- **Goal and endpoint** — Link to the source request and record the observable completion conditions, remaining decisions, and any agreed limits on remote actions.
- **Working state** — Record the branch, worktree or patch location, candidate revision, and current slice. If the candidate includes uncommitted changes, say so.
- **Evidence** — Record what passed, failed, or remains unverified, with commands or artifact links and the revision they apply to. Preserve a short failure symptom when it affects the next action.
- **Delegated slices** — For each dispatched slice, record its baseline, current candidate, implementation or review in progress, review verdicts, and open findings. Identify the agent handling any pending work so the coordinator can check its status before dispatching again.
- **External operations** — Record the pull request, CI run, or deployment ID, target revision and environment, and last observed state. Mark uncertain outcomes so the next session checks before retrying.
- **Next action** — Record the next runnable step, or the decision or access needed to unblock it. Remove superseded state as the work progresses.
