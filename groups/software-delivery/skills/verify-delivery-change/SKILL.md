---
name: verify-delivery-change
description: Check whether a checkout, patch, or pull request is ready to ship or merge. Use when asked to verify the candidate, reproduce test results, or check that a reported build covers the revision under review.
---

# Verify a Delivery Change

Requires the candidate change and project access. CI or runtime verification requires access to the relevant checks or environment.

1. Identify the exact candidate revision or working-tree patch and intended base. Read the original request, acceptance criteria, and applicable project checks before relying on the implementation summary. Use the candidate diff to identify affected entry points and neighboring behavior.
2. For each material criterion, run the most direct observable check available. Exercise the affected route or workflow for changes that cross application boundaries. Use realistic fixtures for changed data shapes and check compatibility when existing clients or stored records are involved. Capture evidence that a reviewer can reproduce, such as commands, run links, or screenshots.
3. Inspect the checks themselves when the candidate changes them. Look for weakened assertions, skipped coverage, or fixtures that hide the original problem. For ambiguous or consequential behavior, derive a check from the acceptance criteria independently of the implementation and look for a plausible counterexample.
4. If reviewing a pull request, match the required check results to the current candidate revision. Track failed or pending checks as such. Recheck impacted evidence after any change to the candidate. Where practical, compare an unexpected failure on the same check and environment against the base before calling it pre-existing.

Return the revision and a concise result for each material criterion and required gate. Use passed, failed, pending, or unverified, and include the reason where evidence is missing. Report any blocking finding with expected behavior, observed behavior, and a reproducible location or check.
