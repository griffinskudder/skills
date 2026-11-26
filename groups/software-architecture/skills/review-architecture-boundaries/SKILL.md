---
name: review-architecture-boundaries
description: Review existing software architecture for module coupling, data ownership violations, and ports-and-adapters leaks. Use for architecture conformance reviews or to find where a change crosses intended boundaries.
---

# Review architecture boundaries

Read the project's stated architecture and establish the scope of the review. Distinguish documented rules from preferences and inferred boundaries. When the rules are missing, describe what the code does and explain the impact of any proposed change.

Trace a representative workflow or changed path from entry point through business decisions to its writes and external effects. Compare import and build dependencies with runtime paths. Inspect the mechanisms that can bypass static checks, such as ORM relationships and raw queries, callbacks, job dispatch, event listeners, or dependency injection.

- Check whether modules use each other's public APIs, who writes each shared data set, and what happens to transactions or failure handling across boundaries. Follow dependency cycles to the behavior that requires the cycle before recommending a new seam.
- Check whether business rules can be exercised through the application boundary and whether framework or vendor details leak into contracts where they create concrete coupling. Verify that the real entry point follows the intended path.
- For each evidenced problem, show the path and relevant locations, the contract or invariant involved, the impact, and the smallest correction. Identify gaps in evidence and suggest a concrete trace or test when runtime behavior is uncertain.

Prioritize findings by consequences such as inconsistent data, failure propagation, or coordinated changes. Use a narrowly scoped dependency check to prevent recurrence where the rule is stable. For legacy violations, consider guarding new dependencies first and tracking existing exceptions. Use a runtime or integration check where dependencies are invisible to static analysis.
