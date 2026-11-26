---
name: evaluate-service-extraction
description: Decide whether to extract a monolith module into a separately deployed service, or plan an incremental extraction after the decision. Use for monolith decomposition, independent deployment, scaling, and isolation trade-offs.
---

# Evaluate service extraction

Start with the outcome a separate deployable is meant to achieve. Look for a binding constraint such as sustained scaling differences, release coordination, fault isolation, or required data isolation. Establish a baseline or cite the hard requirement. Compare the smallest in-process or operational change that could meet it with the cost and benefits of a service. If the evidence is weak, name what to measure and what result would change the decision.

Trace the candidate's callers, data owners, transactions, shared jobs, and failure paths. Check whether the candidate can own its state, change independently of its callers, and meet its latency and consistency requirements across a network. Confirm who can deploy, observe, and support it and how they will recover it. If the boundary is unstable or a shared transaction is essential, strengthen or rethink the in-process boundary first.

When extraction meets the constraint, plan one capability at a time.

1. Establish the contract and data ownership inside the existing application where feasible. Identify how callers will migrate and which implementation is authoritative at each stage.
2. Plan data backfill, reconciliation, cutover, and failed cutover recovery before moving writes. Keep one authoritative write path at each stage and account for writes that occur during migration. Explain how to restore routing and reconcile new writes if rollback follows the cutover.
3. Allow for network latency and partial failure. Specify applicable deadlines, safe retry behavior, idempotency, and what happens when a workflow can no longer use a shared transaction. If introducing messaging, specify delivery assumptions and how producers and consumers handle gaps or duplicate delivery.
4. Migrate a limited slice of traffic where feasible. Verify the business outcome, data consistency, health signals, and the original success measure before retiring the old path.

Deliver a recommendation with evidence, trade-offs, and revisit criteria, or an incremental migration plan with ownership, verification, and rollback when extraction is justified or explicitly requested.
