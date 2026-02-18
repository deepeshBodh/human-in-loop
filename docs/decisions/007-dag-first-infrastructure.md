# ADR-007: DAG-First Infrastructure

**Status:** Proposed
**Date:** 2026-02-18

## Context

The humaninloop plugin's workflow commands (specify, techspec, plan, tasks, implement, audit) are implemented as hardcoded supervisor state machines in markdown. Each command reimplements the same patterns — clarification loops, agent invocation, state recovery, entry gates — as procedural prose. The dependency graph between phases and agents is implicit, buried in 500-600 line command files. This creates rigidity: workflows cannot be composed dynamically, phases cannot be reordered or skipped based on context.

The [human-in-loop-context-harness](https://github.com/deepeshBodh/human-in-loop-context-harness) project provides a proven model: typed nodes and edges, NetworkX for graph computation, Pydantic entities for type safety, and a structural validator for assembly-time guarantees.

## Decision

Introduce the `humaninloop_brain` Python package as the deterministic infrastructure layer for DAG-first workflow execution.

### Architecture

The package provides:

1. **Entity layer**: Pydantic models for nodes (4 types: task, gate, decision, milestone), edges (5 types: depends-on, produces, validates, constrained-by, informed-by), DAG passes, node catalogs, and validation results.

2. **Graph layer**: NetworkX-backed operations — graph loading, subgraph views per edge type, lexicographic topological sort, acyclicity guard, and edge inference from node contracts.

3. **Validator layer**: 9-step structural validation, assembly-time invariant checking (INV-001 through INV-005), and artifact contract verification.

4. **Lifecycle layer**: Pass creation, incremental node assembly with edge inference, status updates, execution trace recording, pass freezing, and JSON persistence.

5. **CLI layer**: `hil-dag` command with 7 subcommands (validate, sort, create, assemble, status, freeze, catalog-validate) producing constitution-compliant JSON output.

### Catalog Model

A single JSON file per workflow defines available nodes, edge endpoint constraints, and system invariants. The DAG Assembler agent selects nodes from the catalog and the infrastructure infers edges, validates constraints, and maintains structural guarantees.

### Key Design Choices

- **DAG-per-pass**: Each iteration produces a new immutable DAG. Previous passes preserved as history.
- **Frozen nodes, mutable container**: Individual `GraphNode` and `Edge` values are frozen Pydantic models. Status updates create new instances. The `DAGPass` container is mutable during assembly, frozen after completion.
- **System artifacts**: `raw-input` and `constitution.md` are always available without a producing node.
- **Deterministic Python for deterministic operations**: All graph operations, validation, and lifecycle management live in Python. LLM judgment stays in the agents.

## Rationale

- **Separation of concerns**: Deterministic operations (graph manipulation, validation, sort) belong in tested Python code, not in LLM prompts. This makes the architecture auditable and testable.
- **Proven patterns**: The entity structure, type-status validation, edge endpoint constraints, structural validator, and graph operations are adapted from the battle-tested context harness implementation.
- **Constitution compliance**: CLI output follows the `checks`/`summary` pattern mandated by Principle III (Error Handling Standards).
- **Flexibility proof**: The skip-enrichment scenario demonstrates genuine DAG assembly flexibility — the Supervisor can build different graphs from the same catalog based on context.

## Consequences

### Easier
- Adding new workflows: define a catalog JSON, reuse the infrastructure
- Validating DAG assembly: structural guarantees checked before execution
- Auditing workflow history: immutable JSON DAG passes on disk
- Composing workflows: catalog nodes are workflow-independent

### Harder
- Initial learning curve for DAG concepts
- Python dependency added to plugin ecosystem (UV-managed, self-contained)
- Two sources of truth for node definitions (catalog vs. actual DAG) until assembly

## Related

- **ADR-001**: Multi-Agent Architecture — extended, not replaced. Agents remain specialized.
- **ADR-005**: Decoupled Agents Architecture — strengthened. DAG model deepens decoupling through node contracts.
- Architecture synthesis documents in `docs/architecture/`:
  - `dag-first-execution-synthesis.md`
  - `dag-supervisor-design-synthesis.md`
  - `dag-json-schema-synthesis.md`
  - `dag-strategy-skills-synthesis.md`
  - `dag-specialist-subagents-synthesis.md`
