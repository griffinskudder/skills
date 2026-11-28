# Three skill pilots in Claude Code and Codex

28 November 2026. We tested Claude Code 2.1.207 with `claude-sonnet-5` and Codex CLI 0.172.0 with `gpt-6.2-sol`. Each condition ran once per host. Arms compared within a task received the same natural-language prompt, tracked fixture revision and grader rubric. Agents saw the prompt and fixture. The evaluator kept the rubric outside the checkout. [Trial runner](../../manual_tests/compare.py) · [Fixtures and rubrics](../../manual_tests/scenarios.json) · [Original assessment](agentic-software-engineering.md)

## Django performance diagnosis

| Host | No repository skill | Django skill available |
| --- | --- | --- |
| Claude Code | No measurements. 48 s | Opened the skill, attempted the profiler and stopped at command approval. 96 s |
| Codex | Correct measurements and diagnoses. 137 s | Opened the skill and returned correct measurements and diagnoses. 85 s |

The two Codex runs agreed with the evaluator’s local measurements. Increasing the formset from 2 to 20 rows added 18 queries and 4,135 response bytes for repeated choices. For the large shared catalogue, the same increase added zero queries and 77,935 bytes. Both answers explained why rendering dominates this in-memory example and tied their proposed changes to the measured cause. The no-skill agent took more timing samples. The 52-second difference includes that choice and comes from a single pair.

Claude’s no-skill agent inferred both causes from the source and wrote a profiling script. The skill-enabled agent tried the bundled profiler. Neither executed the measurement under the headless permission configuration. A retry with automatic command approval was rejected by the outer execution policy before it started. These two trials measure a limitation of this setup.

## Single-ticket implementation

| Host | No repository skill | Single-slice skill | Delivery coordinator only |
| --- | --- | --- | --- |
| Claude Code | Patch passed. 43 s | Patch passed. 85 s | Patch passed. 48 s |
| Codex | Patch passed. 53 s | Patch passed. 42 s | Patch passed. 41 s |

All six candidates changed only pricing and its tests. In fresh local replays, every candidate passed its regression suite, charged exactly 10.20 for four units at 2.55 using Python `Decimal`, and charged zero for zero units. The three Codex agents also ran tests during delivery. The three Claude agents requested command approval. The evaluator established their patch results afterward.

A separate precision probe found a useful missing acceptance criterion. At a unit price of `Decimal('2.555')` and quantity three, both Claude skill-available patches returned 7.66. The other four returned 7.665, matching the fixture’s original multiplication behavior. Neither skill specifies a rounding policy. The predefined rubric used a two-decimal input, so all six retain their original grade. This probe gives a future trial a way to test whether a session invents a business rule.

## Delegated delivery and independent review

The task required fixing pricing and the receipt, verifying the integrated checkout and reporting review findings. The prior skill came from commit `0164a48`. The revised skill permits low-risk work to wait for integration review. All four patches independently replayed as `total(7, 3) == 21` and `receipt(7, 3) == 'Total: 21'`.

| Host and skill | Independent reviews | Summed reviewer time | Session time | Integrated outcome |
| --- | ---: | ---: | ---: | --- |
| Claude, prior | 3 | 178 s | 440 s | Static review. Agent execution blocked. Reviewer identified missing receipt coverage and a test was added. |
| Claude, revised | 1 | 19 s | 193 s | Static review. Agent execution blocked. Correct patch, no new receipt test. |
| Codex, prior | 3 | 53 s | 178 s | Pricing, receipt and integration reviewers returned. Integrated tests passed, including a new receipt regression test. |
| Codex, revised | 2 | 31 s | 128 s | Pricing and integration reviewers returned. Integrated tests passed, including a new receipt regression test. |

Claude’s revised run assigned both fixes to one implementer. Codex’s revised run delegated pricing and the coordinator made the receipt change. Both hosts therefore changed who implemented the work as well as how often they reviewed it. The time differences describe whole sessions. Reviewer time comes from returned Claude tool calls and linked Codex child-session completion events. Codex reviewers reported no blocking findings in either condition.

The first Codex delegation pair used ephemeral sessions. Both logged a subagent spawn failure because parent session context was unavailable. The first coordinator still reported independent reviews. We excluded that pair, stopped the superseded run and repeated both conditions with retained local sessions. For the scored pair, we checked independent child identities, completion messages and verdicts in transcripts linked to each synthetic parent. The runner now supports this mode. [Running the comparisons](../../README.md#compare-skill-outcomes)

## Portfolio decision

Keep the Django and single-slice skills and the revised delegated workflow. All eight within-host endpoint comparisons tied across 14 graded trials. A tie includes two failures when neither arm fulfilled the endpoint, as in Claude’s Django and delegated runs. The single-slice evidence is insufficient for removing its direct entry point. The revised review cadence saved time on this small fixture, and the older Claude review caught a coverage gap. Keep independent integration review and check for regression coverage when reducing per-slice review.

One fixture per workflow and one trial per condition cannot establish a general speedup, model ranking or reliable equivalence. Model permissions differed, some unrelated pilot sessions ran concurrently, and grading was open-label. Codex timings exclude its local skill-catalog preflight. The existing CLI permission settings applied to both arms on each host. No skill was added or removed as a result of this pilot.

### Reproduction records

The fixture revisions are `4cbe142` for Django, `3f9e94d` for pricing and `d6abe8a` for delegated checkout. The manifests contain the installed skill file digests. The following directories under the Windows account’s temporary directory hold the prompts, final answers, traces and saved grades.

| Host | Django | Single ticket | Delegated delivery |
| --- | --- | --- | --- |
| Claude | `skill-comparison-odkrl7yp` | `skill-comparison-8t61sr27` | `skill-comparison-v1u1j9j0` |
| Codex | `skill-comparison-e4go6kqx` | `skill-comparison-ban6h9s2` | `skill-comparison-40ohwuu1` |

## Follow-up in Docker Sandboxes

On 28 November 2026 we repeated all 14 conditions in separate local Docker Sandboxes v0.54.1 VMs. Claude Code 2.1.332 and Codex CLI 0.172.0 used the same model names, prompts, tracked revisions and grading criteria as above. Each VM received a copied synthetic checkout and only the selected repository skill. Shared skills were disabled. The agent ran as a non-root guest user with unattended command execution. No host workspace was mounted. Network access used a default-deny policy with provider-specific allowances. Some guest kits provided their own Docker engine.

| Task and conditions, in order | Claude elapsed seconds | Codex elapsed seconds | Observed outcome |
| --- | ---: | ---: | --- |
| Django diagnosis — no skill / Django skill | 121 / 87 | 57 / 40 | All four agents executed measurements and identified both causes. |
| Single ticket — no skill / slice / coordinator | 23 / 40 / 28 | 18 / 22 / 19 | All six candidates passed independent regression, decimal-price and zero-quantity checks. |
| Delegated checkout — prior / revised workflow | 178 / 174 | 98 / 60 | All four patches returned `Total: 21` for three units at 7, passed their tests and received independent review of the working checkout. |

The permission change answered the original Django question. Both Claude traces contain 2 versus 20 queries and 791 versus 4,926 bytes for repeated choices, and 1 versus 1 query and 8,991 versus 86,926 bytes for the bulky formset. The skill-enabled answer presented the bytes explicitly. Its claim that the per-row query explained the entire slowdown was stronger than its experiment established. Flattening query counts while preserving response size establishes the query mechanism. A comparable timing measurement is needed to attribute the latency. A separate offline, read-only Linux container reproduced both reference deltas.

The pricing precision probe again found an unrequested rounding decision. Only Claude with the single-slice skill returned 7.66 for three units at `Decimal('2.555')`. The other five returned 7.665. All six passed the predefined rubric.

Claude used three independent reviewer calls under the prior workflow and two under the revision. The revised run's receipt reviewer exercised both components and inspected their changes. The coordinator performed the last integration pass itself, so it omitted the separately dispatched final reviewer prescribed by the reference. Neither Claude checkout added a permanent receipt test. Codex used three independent reviewers under the prior workflow and one integrated reviewer under the revision. Its prior run added a receipt regression test. Its revised run verified the receipt through direct invocation and left only the existing pricing test. The revised run met the behavior endpoint but left this cross-component regression easier to reintroduce.

These timings cover individual agent sessions and exclude VM setup and evaluator replay. Each condition ran once. Some trials overlapped, and the sandboxed Claude CLI was newer than the Windows CLI. The evidence supports using sandboxed execution for these tests and keeping the skills while expanding case coverage. It cannot establish a repeatable speedup or a general host ranking.

The runner and reproduction commands are in the [sandbox trial instructions](../../README.md#run-a-trial-in-docker-sandboxes). Answers, event traces, fixture inputs and replay evidence are under `sbx-django-pilot-7zlgn0j6` in the Windows account's temporary directory. All 14 trial VMs and the temporary reference image were removed after grading.
