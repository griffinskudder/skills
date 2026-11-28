---
name: implement-delivery-slice
description: Build and test one ticket or one slice of a delivery plan. Use when asked to fix a specific behavior, implement a bounded change, or leave a regression check for that ticket.
---

# Implement a Delivery Slice

Requires access to the target workspace. Running checks requires the project's development dependencies.

1. Identify the slice's acceptance check, current branch or patch, and the normal code path for the behavior. Inspect existing changes before editing. If other work shares the workspace, preserve it and isolate this slice's edits where needed.
2. Establish a baseline where it will help distinguish the change from existing failures. For a bug, reproduce the symptom when practical. For new behavior, find the smallest check that would detect an incomplete implementation through the real contract. Reuse existing test infrastructure and add a regression test when an important behavior would otherwise remain unguarded.
3. Make the smallest coherent change that exercises the intended path. Run the focused check early. When blocked by a reproducible failure, inspect the evidence and change one relevant hypothesis before retrying. Update the plan or surface the decision if a discovery materially changes the expected behavior, ownership, or release risk.
4. Run relevant broader checks and inspect the diff against the slice. If a test or fixture changed, confirm it still detects the failure it is meant to prevent. Separate baseline failures from failures introduced by the patch using comparable checks where feasible.

The slice is ready for verification when its intended behavior is implemented through the normal entry point, the local evidence applies to the current patch, and any outstanding check has an explicit reason and next action.
