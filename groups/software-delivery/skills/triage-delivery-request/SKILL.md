---
name: triage-delivery-request
description: Decide whether a software request is ready for unattended execution. Use when screening a backlog, dispatching autonomous jobs, or deciding whether an ambiguous delivery request should be returned for clarification.
---

# Triage a Delivery Request

Use the supplied request and accessible project context. An unattended run needs enough agreement on the outcome to select a change and tell whether it succeeded.

## Make the readiness decision

Read the request and its authoritative linked context. Do a bounded, read-only check of the relevant repository area, examples, or prior decisions when that could resolve a material uncertainty. Stop investigating once the evidence settles the choice or shows that the remaining choice belongs to the requester.

Check whether you can name the affected behavior or investigation target, an observable completion condition, and the intended delivery endpoint. Infer a verified local patch when implementation is requested and no remote endpoint is specified. Leave ordinary implementation choices to the agent. Ask about ambiguity only if plausible interpretations would lead to materially different behavior, deliverables, or risk.

Return one of these decisions for each independently actionable part.

- **Ready** when the outcome is sufficiently grounded. State the target, check, and endpoint, plus any inference a later session needs. If the requested deliverable is investigation, a defined question and useful evidence can be its completion condition.
- **Needs clarification** when the intended outcome, affected scope, or success condition remains materially ambiguous. Decline autonomous execution of that part. State what the evidence established, the missing decision, and the smallest question or example that would unblock it. Distinguish competing interpretations only when doing so helps the requester choose.
- **Blocked** when the request is clear and execution depends on missing access, authorization, or an external prerequisite. State the missing dependency and the safe work that can proceed.

In an unattended queue, return the disposition through its existing reporting mechanism. Park the unresolved part until the request or relevant evidence changes. Retain any decision and evidence already recorded so repeat runs can resume from the same point. Update a shared tracker only within existing authorization.

## Calibrate the threshold

- “Make billing better” leaves open whether the target is checkout conversion, invoice accuracy, or another outcome. Ask which behavior should improve and what observation would count as success.
- “Expired invite links should offer a resend,” with an established invite flow, is ready when the expired state and expected action can be traced. The UI implementation is routine.
- “Investigate why invoice export times doubled last week and report the likely causes with evidence” is a discovery request with an observable deliverable.
- “Deploy build 42 to production” is clear but blocked if authority for the target is missing.
- “Fix the export crash for empty reports and modernize reporting” can proceed on the reproducible crash when the work is independent. Return the modernization request for a target outcome.
