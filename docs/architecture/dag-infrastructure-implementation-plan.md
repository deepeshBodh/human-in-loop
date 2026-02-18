# humaninloop_brain — Implementation Plan

## Overview

Build the `humaninloop_brain` Python package: a standalone, UV-managed package in the same repo that provides all deterministic DAG operations for the DAG-first execution architecture. The DAG Assembler agent invokes these operations via CLI entry points exposed as plugin skills.

**Guiding principle**: Maximize testable, deterministic surface. Every operation that CAN be deterministic lives here. LLM judgment stays in the agents.

## Package Structure

```
humaninloop_brain/
├── pyproject.toml                    # UV-managed, Pydantic + NetworkX deps
├── src/
│   └── humaninloop_brain/
│       ├── __init__.py
│       ├── entities/                 # Layer 1: Pydantic models
│       │   ├── __init__.py
│       │   ├── nodes.py              # GraphNode, NodeContract, ArtifactConsumption, EvidenceAttachment
│       │   ├── edges.py              # Edge with type validation
│       │   ├── dag_pass.py           # DAGPass, ExecutionTraceEntry, HistoryPass, HistoryContext
│       │   ├── catalog.py            # NodeCatalog, CatalogNodeDefinition, EdgeConstraint, SystemInvariant
│       │   └── validation.py         # ValidationResult, ValidationViolation
│       ├── graph/                    # Layer 2: NetworkX operations
│       │   ├── __init__.py
│       │   ├── loader.py             # DAG JSON → NetworkX MultiDiGraph
│       │   ├── views.py              # 5 subgraph views by edge type
│       │   ├── sort.py               # Deterministic topological sort
│       │   ├── guard.py              # Acyclicity guard on depends-on edges
│       │   └── inference.py          # Edge inference from consumes/produces contracts
│       ├── validators/               # Layer 3: Validation
│       │   ├── __init__.py
│       │   ├── structural.py         # 9-step structural validator
│       │   ├── invariants.py         # Catalog invariant checker
│       │   └── contracts.py          # Contract satisfiability checker
│       ├── passes/                   # Layer 4a: Pass lifecycle
│       │   ├── __init__.py
│       │   └── lifecycle.py          # Create, update node status, freeze
│       └── cli/                      # Layer 4b: CLI entry points
│           ├── __init__.py
│           └── main.py               # Click/argparse commands for DAG Assembler
├── tests/
│   ├── conftest.py                   # Shared fixtures
│   ├── fixtures/                     # Test data
│   │   ├── specify-catalog.json      # Full /specify node catalog
│   │   ├── pass-normal.json          # Standard: enrich → analyst → advocate
│   │   ├── pass-skip-enrichment.json # Scenario 1: skip enrichment
│   │   ├── pass-with-research.json   # Scenario 2: add research node
│   │   ├── pass-with-clarification.json  # Scenario 3: human clarification
│   │   ├── invalid-cycle.json        # Broken: cycle in depends-on
│   │   ├── invalid-endpoint.json     # Broken: wrong endpoint types
│   │   └── invalid-contract.json     # Broken: unsatisfied contract
│   ├── test_entities/
│   ├── test_graph/
│   ├── test_validators/
│   ├── test_passes/
│   └── test_cli/
```

## Dependencies

```toml
[project]
name = "humaninloop-brain"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.0",
    "networkx>=3.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]

[project.scripts]
hil-dag = "humaninloop_brain.cli.main:main"
```

## Phases

### Phase 1: Project Scaffold + Entities (Layer 1)

**Goal**: Establish the Python package and all Pydantic models. Every data structure the system uses is defined, validated, and serializable.

#### 1.1 Initialize package

- Create `humaninloop_brain/` directory at repo root
- Write `pyproject.toml` with UV configuration, Pydantic + NetworkX dependencies, pytest dev deps
- Create `src/humaninloop_brain/__init__.py` with version
- Create `tests/conftest.py`
- Verify `uv sync` installs dependencies and `pytest` runs (empty suite)

#### 1.2 Core graph entities

**`entities/nodes.py`**:
- `ArtifactConsumption(artifact: str, required: bool, note: str | None)`
- `NodeContract(consumes: list[ArtifactConsumption], produces: list[str])`
- `EvidenceAttachment(id: str, type: Literal["file", "url"], description: str, reference: str)`
- `GraphNode(id: str, type: Literal["task", "gate", "decision", "milestone"], name: str, description: str, status: str, contract: NodeContract, agent: str | None, evidence: list[EvidenceAttachment])`
- Type-status validation via `model_validator`:
  - task: pending, in-progress, completed, skipped, halted
  - gate: pending, in-progress, passed, failed, needs-revision
  - decision: pending, decided
  - milestone: pending, achieved

**`entities/edges.py`**:
- `Edge(id: str, source: str, target: str, type: Literal["depends-on", "produces", "validates", "constrained-by", "informed-by"])`

**Tests**: Valid construction, type-status enforcement (all valid combos pass, invalid combos raise), serialization round-trip (model → JSON → model).

#### 1.3 DAG pass entity

**`entities/dag_pass.py`**:
- `ExecutionTraceEntry(node_id: str, started_at: str, completed_at: str, verdict: str | None, agent_report_summary: str | None, artifacts_produced: list[str])`
- `HistoryPass(pass_number: int, outcome: Literal["completed", "halted"], outcome_detail: str, summary: str)`
- `HistoryContext(previous_passes: list[HistoryPass])`
- `DAGPass(id: str, workflow_id: str, schema_version: str, pass_number: int, outcome: Literal["completed", "halted"], outcome_detail: str, assembly_rationale: str, created_at: str, completed_at: str | None, nodes: list[GraphNode], edges: list[Edge], execution_trace: list[ExecutionTraceEntry], history_context: HistoryContext)`

**Tests**: Full DAG pass construction from JSON fixture, serialization round-trip, validation of nested models.

#### 1.4 Catalog entities

**`entities/catalog.py`**:
- `CatalogNodeDefinition(id: str, type: ..., name: str, description: str, agent: str | None, skill: str | None, contract: NodeContract, valid_statuses: list[str], verdict_field: str | None, verdict_values: list[str] | None)`
- `EdgeConstraint(valid_sources: list[str], valid_targets: list[str], note: str)`
- `SystemInvariant(id: str, rule: str, enforcement: Literal["assembly-time", "runtime"], severity: Literal["error", "warning"])`
- `NodeCatalog(catalog_version: str, workflow: str, nodes: list[CatalogNodeDefinition], edge_constraints: dict[str, EdgeConstraint], invariants: list[SystemInvariant])`

**Tests**: Load `specify-catalog.json` fixture, validate all 7 nodes parse correctly, edge constraints and invariants load.

#### 1.5 Validation entities

**`entities/validation.py`**:
- `ValidationViolation(code: str, severity: Literal["error", "warning"], message: str, node_id: str | None, edge_id: str | None)`
- `ValidationResult(valid: bool, phase: str, violations: list[ValidationViolation])`

**Tests**: Construction, serialization, convenience methods (has_errors, error_count).

#### 1.6 Test fixtures

Hand-write the JSON fixtures:
- `specify-catalog.json` — all 7 nodes from the supervisor design synthesis (input-enrichment, analyst-review, advocate-review, human-clarification, targeted-research, constitution-gate, spec-complete) with full contracts, edge constraints, and 5 invariants
- `pass-normal.json` — standard specify flow: enrichment → analyst → advocate
- `pass-skip-enrichment.json` — Scenario 1: analyst → advocate (no enrichment)
- `pass-with-research.json` — Scenario 2: research node added after advocate rejection
- `pass-with-clarification.json` — Scenario 3: human clarification after advocate rejection
- `invalid-cycle.json` — depends-on cycle between two nodes
- `invalid-endpoint.json` — produces edge from gate (invalid source)
- `invalid-contract.json` — analyst consumes enriched-input but no node produces it

**Phase 1 exit criteria**: All entities construct from JSON, type-status validation works, all fixtures load cleanly, `pytest --cov` reports 90%+ on entities module.

---

### Phase 2: Graph Operations (Layer 2)

**Goal**: Load DAG pass JSON into NetworkX, provide subgraph views, topological sort, acyclicity guard, and edge inference.

#### 2.1 Graph loader

**`graph/loader.py`**:
- `load_graph(dag: DAGPass) -> nx.MultiDiGraph` — nodes carry all attributes (type, status, contract, agent), edges keyed by type
- Nodes indexed by ID, edges carry type as attribute

**Tests**: Load each fixture, verify node count, edge count, node attributes accessible, edge type filtering works.

#### 2.2 Subgraph views

**`graph/views.py`**:
- `depends_on_view(graph: nx.MultiDiGraph) -> nx.DiGraph`
- `produces_view(graph: nx.MultiDiGraph) -> nx.DiGraph`
- `validates_view(graph: nx.MultiDiGraph) -> nx.DiGraph`
- `constrained_by_view(graph: nx.MultiDiGraph) -> nx.DiGraph`
- `informed_by_view(graph: nx.MultiDiGraph) -> nx.DiGraph`

Each returns a simple DiGraph containing only edges of that type.

**Tests**: Load `pass-normal.json`, verify depends_on_view has 2 edges (enrichment→analyst, analyst→advocate), produces_view has correct artifact flow edges, validates_view has advocate→analyst edge.

#### 2.3 Topological sort

**`graph/sort.py`**:
- `execution_order(graph: nx.MultiDiGraph) -> list[str]` — deterministic lexicographic topological sort on depends-on edges only
- Uses `depends_on_view()` internally

**Tests**: Normal pass returns [enrichment, analyst, advocate]. Skip-enrichment pass returns [analyst, advocate]. Order is deterministic across runs.

#### 2.4 DAG guard

**`graph/guard.py`**:
- `check_acyclicity(graph: nx.MultiDiGraph) -> ValidationResult` — checks depends-on edges only for cycles
- Other edge types (informed-by, validates) are allowed to form cycles

**Tests**: Valid DAGs pass. `invalid-cycle.json` fails with specific cycle information in the violation.

#### 2.5 Edge inference

**`graph/inference.py`**:
- `infer_edges(node_id: str, dag: DAGPass, catalog: NodeCatalog) -> list[Edge]` — given a new node being added, infer edges by matching its consumes against produces of existing nodes
- If node X consumes "spec.md" and node Y produces "spec.md", infer a `produces` edge Y → X
- Also infer `depends-on` edges from the produces relationships
- Also infer `validates` edges when a gate node consumes a task node's output

**Tests**: Add analyst-review to a DAG containing enrichment → infer produces edge (enrichment produces enriched-input, analyst consumes it). Add advocate-review → infer validates edge to analyst, produces edge for spec.md.

**Phase 2 exit criteria**: All graph operations work against all fixtures. Topological sort is deterministic. Acyclicity guard catches cycles. Edge inference produces correct edges for all 3 flexibility scenarios.

---

### Phase 3: Validators (Layer 3)

**Goal**: Implement structural validation, invariant checking, and contract satisfiability verification.

#### 3.1 Structural validator

**`validators/structural.py`**:
- `validate_structure(dag: DAGPass, catalog: NodeCatalog) -> ValidationResult`
- 9 steps (adapted from context harness pattern):
  1. **Node existence**: All node IDs are unique
  2. **Edge references**: All edge source/target IDs reference existing nodes
  3. **Type-status validity**: All node statuses valid for their type (redundant with Pydantic, but catches manually-constructed JSON)
  4. **Self-loops**: No edge where source == target
  5. **Duplicate edges**: No two edges with same source + target + type
  6. **Edge endpoint constraints**: Source/target node types match catalog edge constraints
  7. **Acyclicity**: depends-on edges form a DAG (delegates to guard)
  8. **Contract satisfiability**: Every required consumed artifact is produced upstream (delegates to contracts)
  9. **Invariant compliance**: All assembly-time invariants satisfied (delegates to invariants)

Returns `ValidationResult` with all violations collected (doesn't stop at first error).

**Tests**: Valid fixtures pass all 9 steps. Each invalid fixture triggers its specific violation. Test each step independently with targeted broken inputs.

#### 3.2 Invariant checker

**`validators/invariants.py`**:
- `check_invariants(dag: DAGPass, catalog: NodeCatalog) -> ValidationResult`
- Evaluates each `assembly-time` invariant from the catalog:
  - INV-001: Every task output passes through a gate before milestone
  - INV-002: Constitution must exist before spec task nodes
  - INV-003: validates edges originate from gate nodes
  - INV-005: depends-on edges are acyclic
- Runtime invariants (INV-004: max 5 passes) are checked separately, not here

**Tests**: Valid DAGs pass all invariants. Build specific DAGs that violate each invariant individually. Verify violation messages reference the invariant ID.

#### 3.3 Contract satisfiability

**`validators/contracts.py`**:
- `check_contracts(dag: DAGPass, catalog: NodeCatalog) -> ValidationResult`
- For each node: every `required: true` artifact in `consumes` must be produced by an upstream node (reachable via depends-on/produces edges)
- Optional artifacts (`required: false`) are noted but don't cause violations

**Tests**: Normal flow satisfies all contracts. `invalid-contract.json` fails (analyst consumes enriched-input with no enrichment node). Scenario 1 (skip enrichment) passes because analyst has `enriched-input` as `required: false`.

**Phase 3 exit criteria**: Structural validator catches all categories of errors. Invariant checker validates each invariant independently. Contract checker correctly handles required vs. optional artifacts. All invalid fixtures produce the expected violations.

---

### Phase 4: Pass Lifecycle + CLI (Layer 4)

**Goal**: Manage DAG pass files on disk and expose all operations as CLI commands.

#### 4.1 Pass lifecycle

**`passes/lifecycle.py`**:
- `create_pass(workflow_id: str, pass_number: int, feature_dir: str) -> DAGPass` — create new empty pass with metadata
- `add_node(dag: DAGPass, node_id: str, catalog: NodeCatalog) -> tuple[DAGPass, list[Edge]]` — add node from catalog, infer edges, return updated DAG + inferred edges
- `update_node_status(dag: DAGPass, node_id: str, status: str) -> DAGPass` — update node status with type-status validation
- `add_trace_entry(dag: DAGPass, entry: ExecutionTraceEntry) -> DAGPass` — record execution
- `freeze_pass(dag: DAGPass, outcome: str, outcome_detail: str, rationale: str) -> DAGPass` — finalize all statuses, set outcome, write completed_at
- `save_pass(dag: DAGPass, path: str) -> None` — write immutable JSON to disk
- `load_pass(path: str) -> DAGPass` — read from disk

**Tests**: Full lifecycle: create → add 3 nodes → update statuses → add traces → freeze → save → load → verify round-trip. Verify immutability (frozen pass rejects node additions).

#### 4.2 CLI entry points

**`cli/main.py`**:

All commands read JSON from stdin or file args, output JSON to stdout. Exit code 0 for success, 1 for validation failure, 2 for errors.

**Commands:**

```
hil-dag validate <dag-path> --catalog <catalog-path>
```
Run full structural validation. Output: ValidationResult JSON.

```
hil-dag assemble <dag-path> --catalog <catalog-path> --node <node-id> [--params <json>]
```
Add node to DAG, infer edges, validate. Output: `{status, node_added, edges_inferred, validation}` JSON.

```
hil-dag sort <dag-path>
```
Return execution order. Output: `{order: ["node-id", ...]}` JSON.

```
hil-dag freeze <dag-path> --outcome <completed|halted> --detail <string> --rationale <string>
```
Freeze pass. Output: `{pass_frozen, dag_path, outcome, nodes_executed, edges_total}` JSON.

```
hil-dag create <workflow-id> --pass <number> --dir <feature-dir>
```
Create new empty pass. Output: `{dag_path, pass_number}` JSON.

```
hil-dag status <dag-path> --node <node-id> --status <new-status>
```
Update node status. Output: `{node_id, old_status, new_status}` JSON.

```
hil-dag catalog validate <catalog-path>
```
Validate a catalog file. Output: ValidationResult JSON.

**Tests**: End-to-end CLI tests using subprocess. Each command tested with valid and invalid inputs. Verify JSON output is parseable and matches expected schema.

#### 4.3 Error output format

All CLI error output follows the plugin constitution's structured JSON pattern:

```json
{
  "status": "error | invalid | success",
  "checks": [...],
  "summary": "Human-readable summary",
  "issues": [...]
}
```

This aligns with the existing validator pattern in the plugin (`checks`, `summary`, `issues` fields).

**Phase 4 exit criteria**: Full lifecycle works end-to-end. CLI commands produce correct JSON output. Error output follows constitution pattern. All 3 flexibility scenarios can be assembled via CLI commands.

---

### Phase 5: Integration Proof

**Goal**: Verify the package works when called by a plugin skill (script) the way the DAG Assembler would use it.

#### 5.1 Create plugin skill (script)

Create a skill under `plugins/humaninloop/skills/` that wraps the `hil-dag` CLI:
- Script takes DAG Assembler parameters, calls `hil-dag assemble`, returns structured JSON
- Validates the integration model: plugin skill → CLI → Python package → JSON output

#### 5.2 End-to-end walkthrough

Hand-simulate Scenario 1 (skip enrichment) entirely through CLI commands:

```bash
# 1. Create pass
hil-dag create specify-feature-auth --pass 1 --dir specs/001/

# 2. Validate catalog
hil-dag catalog validate catalogs/specify-catalog.json

# 3. Add constitution-gate
hil-dag assemble specs/001/.workflow/dags/pass-001.json \
  --catalog catalogs/specify-catalog.json \
  --node constitution-gate

# 4. Add analyst-review (skip enrichment)
hil-dag assemble specs/001/.workflow/dags/pass-001.json \
  --catalog catalogs/specify-catalog.json \
  --node analyst-review

# 5. Update analyst status after agent execution
hil-dag status specs/001/.workflow/dags/pass-001.json \
  --node analyst-review --status completed

# 6. Add advocate-review
hil-dag assemble specs/001/.workflow/dags/pass-001.json \
  --catalog catalogs/specify-catalog.json \
  --node advocate-review

# 7. Get execution order
hil-dag sort specs/001/.workflow/dags/pass-001.json

# 8. Freeze pass
hil-dag freeze specs/001/.workflow/dags/pass-001.json \
  --outcome completed --detail advocate-verdict-ready \
  --rationale "Advocate approved specification"
```

#### 5.3 Write ADR-007

Document the DAG-first infrastructure as an Architecture Decision Record:
- References ADR-001 (multi-agent), ADR-005 (decoupled agents)
- Captures: catalog model, deterministic operations in Python, LLM judgment in agents
- Status: Proposed (until PoC proves the architecture)

**Phase 5 exit criteria**: Plugin skill successfully calls `hil-dag` CLI. Full Scenario 1 walkthrough produces valid, frozen DAG pass JSON. ADR-007 written.

---

## Quality Gates

| Gate | Requirement | Enforcement |
|------|-------------|-------------|
| Test coverage | >= 80% (target from constitution) | `pytest --cov --cov-fail-under=80` |
| All tests pass | Zero failures | `pytest` |
| Type checking | Clean mypy | `mypy src/` (optional, add if team uses it) |
| Fixtures valid | All JSON fixtures parse through Pydantic | Fixture-loading tests |
| CLI output valid | All CLI output is valid JSON | CLI integration tests |
| Constitution compliance | Structured JSON output with checks/summary/issues | Manual review |

## Sequencing Summary

| Phase | Depends On | Deliverables | Est. Files |
|-------|-----------|--------------|------------|
| 1. Entities | Nothing | 5 entity modules, 8 fixtures, entity tests | ~20 |
| 2. Graph Ops | Phase 1 | 5 graph modules, graph tests | ~12 |
| 3. Validators | Phase 1 + 2 | 3 validator modules, validator tests | ~8 |
| 4. CLI + Lifecycle | Phase 1 + 2 + 3 | 2 modules, CLI tests | ~6 |
| 5. Integration | Phase 1-4 | 1 plugin skill, ADR-007, walkthrough | ~4 |

## Open Decisions (Deferred to Implementation)

- **CLI framework**: argparse vs. click vs. typer. Decide when building Phase 4. Leaning toward argparse (no extra dependency) unless UX demands more.
- **Schema version migration**: How to handle evolving schemas. Defer until schema actually changes.
- **Catalog file location**: Where catalogs live in the repo (`catalogs/`, `humaninloop_brain/catalogs/`, plugin directory). Decide when building the specify catalog fixture.
- **Plugin skill format for scripts**: How script-based skills are declared in plugin.json. Investigate existing script patterns in Phase 5.
