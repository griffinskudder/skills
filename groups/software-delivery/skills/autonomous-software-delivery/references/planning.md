# Plan a Delivery Change

Requires access to the target project's source or delivery documentation for a repository-grounded plan.

1. Trace the current behavior through its normal entry point and identify the authoritative request and relevant repository constraints. Where sources disagree, cite the conflict and identify the decision it affects.
2. Express the outcome as observable behavior. Give each material criterion a scenario with inputs or preconditions and an expected result. Include compatibility for existing callers or stored data when affected. Name any assumption that would change the user-visible behavior or release strategy.
3. Split large changes into small increments with a meaningful acceptance check each. Prefer the shortest path that exercises the affected layers together. Where a shared contract or data migration requires sequencing, specify the compatibility window, what can ship independently, and when cleanup becomes safe.
4. Give each slice a target behavior, dependency if any, and verification entry point. Mark slices as parallelizable only when their write ownership and contracts allow independent work. Identify which uncertainty should be tested first.

For a narrow change, the acceptance check and a single slice can fit in a few lines. For a multi-session change, use the project's existing issue or plan format. The plan is ready when the first slice can start and the remaining sequencing and decisions are visible.
