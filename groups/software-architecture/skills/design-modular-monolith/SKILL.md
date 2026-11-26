---
name: design-modular-monolith
description: Choose the architecture for a new application or design business module boundaries in an existing monolith. Use for modular monolith design, module APIs, and decisions about data ownership and transactions.
---

# Design a modular monolith

Start with one deployable application for a new system while business boundaries are still evolving. A small application can start with only the modules its current workflows justify. Use ports and adapters where business rules need isolation from external technology. Treat deployment topology and dependency direction as separate decisions. Read the [research findings](references/research.md) when explaining the default or comparing it with a distributed design.

1. Establish the constraints that could change the design. Identify representative workflows, invariants, consistency needs, expected load, and the people who will own deployment and operations. In an existing system, trace the current call and write paths before suggesting moves. For a new system, label proposed boundaries as hypotheses and validate them with the first working slice.
2. Group behavior and data around business capabilities. Give each module a purpose, a public API, and responsibility for its writes and migrations. Keep dependencies acyclic and use the owning module's public API to change its state. A shared database can support a single deployment while ownership remains explicit. For cross-module reads, choose an owning API or an explicit read model or query contract, and keep dependencies on storage schema visible.
3. Walk one normal workflow and one meaningful failure through the proposed boundaries. Prefer a direct in-process call when a result is needed immediately. Use events when the consumer can react independently, and state any delivery or consistency guarantees the workflow needs. If an invariant needs atomic changes across modules, consider redrawing the boundary or use an explicit shared transaction with clear ownership. Identify what must change before that workflow could cross a process boundary.
4. Propose the smallest useful slice that exercises the design. Verify public behavior and use the language's visibility rules or a focused dependency check where unintended imports are likely. In an existing codebase, introduce or strengthen boundaries around a working flow and preserve observed behavior as it moves.

Deliver a module map with responsibilities, callers and public operations, owned data, and transaction boundaries. Include the chosen deployment model, the constraints behind it, and any concrete signal that would warrant revisiting it. Follow the project's existing format for architecture decisions when a decision needs to be saved.
