# DAG JSON Schema — Analysis Synthesis

## Problem Statement

The DAG-first execution architecture needs a concrete JSON schema for two things: DAG pass instances (what was assembled and executed) and the node catalog (the library of available nodes). The context harness project (`human-in-loop-context-harness`) has a mature implementation with Pydantic entities, JSON Schema validation, NetworkX graph loading, subgraph views, structural validation, and edge endpoint constraints. This session scopes what to borrow and what to adapt for the plugin domain.

## Context & Constraints

- **Context harness implementation**: StrategyGraph entity with GraphNode[], Edge[], type-specific status enums, edge endpoint constraints, structural validator (9-step), subgraph views per edge type, DAG guard, topological sort, critical path, lineage (ancestors/descendants). All built on Pydantic + NetworkX.
- **Plugin domain differences**: Context harness has a single mutable graph over months. Plugin has immutable per-pass DAGs within a session. Plugin nodes have contracts (consumes/produces) and agent assignments — not present in context harness.
- **NetworkX confirmed**: Will be used for deterministic DAG components (see Supervisor design synthesis).
- **DAG-ops agents**: State Briefer and DAG Assembler consume these schemas (see Supervisor design synthesis).

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| DAG pass structure | Layered — graph definition (nodes + edges) separate from execution trace. Graph is the plan, trace is the record. | Confident | Can inspect the plan without execution noise, or audit execution without re-parsing the graph. Matches context harness clean separation. |
| Context harness borrowing | Directly reuse: entity structure, type-status validation, edge endpoint constraints, graph loader, subgraph views, structural validator, DAG guard, validation entities. Adapt: add contracts, agent assignment, pass metadata, execution trace. | Confident | Battle-tested patterns with comprehensive test suite. No reason to reinvent. |
| Node catalog format | Single file containing node definitions, edge constraints, and system invariants. One source of truth for all DAG-ops agents. | Confident | Keeps DAG-ops agents simple — one read for everything. Avoids sync issues between separate files. |
| Schema versioning | `schema_version` field on both DAG passes and node catalog, following context harness pattern | Confident | Essential for schema evolution as the architecture matures. |

## Patterns Borrowed from Context Harness

### Directly Reusable (minimal adaptation)

| Pattern | Source File | What It Does | Plugin Usage |
|---|---|---|---|
| Graph container entity | `strategy_graph.py` | `StrategyGraph(id, name, description, schema_version, nodes[], edges[])` | DAG pass container — add pass_number, outcome, assembly_rationale |
| Node entity | `graph_node.py` | `GraphNode(id, type, name, description, status, evidence[])` with type-status validation | Add contract (consumes/produces) and agent fields |
| Edge entity | `edge.py` | `Edge(id, source, target, type)` | Same structure, plugin's 5 edge types |
| Type-status map | `graph_node.py` | `_TYPE_STATUS_MAP` + Pydantic model_validator enforces valid statuses per node type | Map to plugin's 4 types: task, gate, decision, milestone |
| Edge endpoint constraints | `structural_validator.py` | `_EDGE_CONSTRAINTS` maps edge types to valid source/target node types | Map to plugin's edge types: validates→(gate,task), produces→(task,task/gate), etc. |
| Graph loader | `graph_loader.py` | `load_graph()` → NetworkX MultiDiGraph, nodes carry attributes, edges keyed by type | Directly reusable |
| Subgraph views | `graph_loader.py` | `depends_on_view()`, `assumes_view()`, etc. — filter by edge type | Plugin equivalents: `produces_view()`, `validates_view()`, `constrained_by_view()`, `informed_by_view()` |
| DAG guard | `dag_guard.py` | Acyclicity check on depends-on edges only (other types CAN cycle) | Same — `depends_on` must be acyclic; `informed_by` can reference previous passes |
| Structural validator | `structural_validator.py` | 9-step validation: self-loops, duplicates, dangling refs, endpoint types, cycles | DAG Assembler's invariant checking backbone |
| Validation entities | `validation.py` | `ValidationResult(valid, phase, violations[])` + `ValidationViolation` | Structured validation reporting from DAG Assembler to Supervisor |
| Evidence attachments | `evidence.py` | `EvidenceAttachment(id, type, description, reference)` on nodes | Artifact references (spec.md, advocate-report.md) |
| Topological sort | `topological_sort.py` | Lexicographic deterministic sort on depends-on edges, active-graph mode | Execution ordering for DAG traversal |
| JSON Schema | `graph_schema_v2.py` | Draft 2020-12 schema with if/then conditionals for type-status enforcement | Adapt for plugin node/edge types |

### New for Plugin Domain (not in context harness)

| Concept | Purpose | Location |
|---|---|---|
| Node contracts | `consumes[]` / `produces[]` on each node — artifact I/O declarations | Node entity + catalog |
| Agent assignment | Which domain agent executes this node | Node entity + catalog |
| Pass metadata | `pass_number`, `outcome`, `outcome_detail`, `assembly_rationale` | DAG pass container |
| Execution trace | Per-node: timing, agent_report_summary, verdict, artifacts_produced | Separate section in DAG pass |
| History context | Progressive summary of previous passes for Supervisor consumption | DAG pass container |
| System invariants | Rules that must hold regardless of DAG shape | Catalog file |

## DAG Pass Schema

```json
{
  "id": "specify-pass-002",
  "workflow_id": "specify-feature-auth",
  "schema_version": "1.0.0",
  "pass_number": 2,
  "outcome": "completed | halted",
  "outcome_detail": "advocate-verdict-ready | advocate-verdict-needs-revision | supervisor-halt-reason",
  "assembly_rationale": "Why the Supervisor chose these nodes and edges for this pass",
  "created_at": "ISO-8601",
  "completed_at": "ISO-8601",

  "nodes": [
    {
      "id": "string (kebab-case)",
      "type": "task | gate | decision | milestone",
      "name": "Human-readable name",
      "description": "What this node does",
      "status": "pending | in-progress | completed | passed | failed | needs-revision | decided | achieved | skipped | halted",
      "contract": {
        "consumes": [
          {"artifact": "artifact-name", "required": true}
        ],
        "produces": ["artifact-name"]
      },
      "agent": "agent-id or null",
      "evidence": [
        {"id": "ev-XX", "type": "file | url", "description": "...", "reference": "path/or/url"}
      ]
    }
  ],

  "edges": [
    {
      "id": "string",
      "source": "node-id",
      "target": "node-id",
      "type": "depends-on | produces | validates | constrained-by | informed-by"
    }
  ],

  "execution_trace": [
    {
      "node_id": "string",
      "started_at": "ISO-8601",
      "completed_at": "ISO-8601",
      "verdict": "ready | needs-revision | null (for non-gate nodes)",
      "agent_report_summary": "Structured summary parsed by DAG Assembler from agent prose",
      "artifacts_produced": ["file-paths"]
    }
  ],

  "history_context": {
    "previous_passes": [
      {
        "pass_number": 1,
        "outcome": "completed",
        "outcome_detail": "advocate-verdict-needs-revision",
        "summary": "Progressive summary for Supervisor context"
      }
    ]
  }
}
```

### Type-Status Map (Plugin Domain)

| Node Type | Valid Statuses |
|---|---|
| `task` | pending, in-progress, completed, skipped, halted |
| `gate` | pending, in-progress, passed, failed, needs-revision |
| `decision` | pending, decided |
| `milestone` | pending, achieved |

## Node Catalog Schema

Single file containing node definitions, edge constraints, and system invariants.

```json
{
  "catalog_version": "1.0.0",
  "workflow": "specify",

  "nodes": [
    {
      "id": "input-enrichment",
      "type": "task",
      "name": "Input Enrichment",
      "description": "Transform sparse feature input into structured Who/Problem/Value format",
      "agent": null,
      "skill": "analysis-iterative",
      "contract": {
        "consumes": [
          {"artifact": "raw-input", "required": true}
        ],
        "produces": ["enriched-input"]
      },
      "valid_statuses": ["pending", "in-progress", "completed", "skipped"]
    },
    {
      "id": "analyst-review",
      "type": "task",
      "name": "Requirements Analysis",
      "description": "Write specification with user stories, functional requirements, and edge cases",
      "agent": "requirements-analyst",
      "contract": {
        "consumes": [
          {"artifact": "enriched-input", "required": false, "note": "one of enriched or raw required"},
          {"artifact": "raw-input", "required": false},
          {"artifact": "constitution.md", "required": true},
          {"artifact": "clarification-answers", "required": false},
          {"artifact": "research-findings", "required": false}
        ],
        "produces": ["spec.md", "analyst-report.md"]
      },
      "valid_statuses": ["pending", "in-progress", "completed", "skipped"]
    },
    {
      "id": "advocate-review",
      "type": "gate",
      "name": "Specification Validation",
      "description": "Adversarial review of specification completeness and quality",
      "agent": "devils-advocate",
      "contract": {
        "consumes": [
          {"artifact": "spec.md", "required": true},
          {"artifact": "analyst-report.md", "required": true}
        ],
        "produces": ["advocate-report.md"]
      },
      "valid_statuses": ["pending", "in-progress", "passed", "needs-revision", "failed"],
      "verdict_field": "verdict",
      "verdict_values": ["ready", "needs-revision", "critical-gaps"]
    },
    {
      "id": "human-clarification",
      "type": "decision",
      "name": "User Clarification",
      "description": "Collect user input for gaps that cannot be resolved by research",
      "agent": null,
      "contract": {
        "consumes": [
          {"artifact": "advocate-report.md", "required": true}
        ],
        "produces": ["clarification-answers"]
      },
      "valid_statuses": ["pending", "decided"]
    },
    {
      "id": "targeted-research",
      "type": "task",
      "name": "Targeted Research",
      "description": "Investigate specific knowledge gaps identified by validation",
      "agent": "exploration",
      "contract": {
        "consumes": [
          {"artifact": "advocate-report.md", "required": true}
        ],
        "produces": ["research-findings"]
      },
      "valid_statuses": ["pending", "in-progress", "completed", "skipped"]
    },
    {
      "id": "constitution-gate",
      "type": "gate",
      "name": "Constitution Check",
      "description": "Verify project constitution exists and is current",
      "agent": null,
      "contract": {
        "consumes": [
          {"artifact": "constitution.md", "required": true}
        ],
        "produces": []
      },
      "valid_statuses": ["pending", "passed", "failed"],
      "verdict_field": "verdict",
      "verdict_values": ["pass", "fail"]
    },
    {
      "id": "spec-complete",
      "type": "milestone",
      "name": "Specification Complete",
      "description": "Marks the specification as validated and complete",
      "agent": null,
      "contract": {
        "consumes": [
          {"artifact": "spec.md", "required": true},
          {"artifact": "advocate-report.md", "required": true}
        ],
        "produces": []
      },
      "valid_statuses": ["pending", "achieved"]
    }
  ],

  "edge_constraints": {
    "depends-on": {
      "valid_sources": ["task", "gate", "decision", "milestone"],
      "valid_targets": ["task", "gate", "decision", "milestone"],
      "note": "General execution ordering — must form a DAG"
    },
    "produces": {
      "valid_sources": ["task"],
      "valid_targets": ["task", "gate"],
      "note": "Artifact flow — source produces what target consumes"
    },
    "validates": {
      "valid_sources": ["gate"],
      "valid_targets": ["task"],
      "note": "Review relationship — gate evaluates task output"
    },
    "constrained-by": {
      "valid_sources": ["task", "gate", "decision"],
      "valid_targets": ["gate"],
      "note": "Boundary enforcement — work must satisfy gate constraint"
    },
    "informed-by": {
      "valid_sources": ["task", "gate", "decision"],
      "valid_targets": ["task", "gate", "decision"],
      "note": "Context flow — not a hard dependency, may cross pass boundaries"
    }
  },

  "invariants": [
    {
      "id": "INV-001",
      "rule": "Every task node output must pass through a gate node before a milestone can be achieved",
      "enforcement": "assembly-time",
      "severity": "error"
    },
    {
      "id": "INV-002",
      "rule": "Constitution must exist before any specification task node executes",
      "enforcement": "assembly-time",
      "severity": "error"
    },
    {
      "id": "INV-003",
      "rule": "A validates edge must originate from a gate node",
      "enforcement": "assembly-time",
      "severity": "error"
    },
    {
      "id": "INV-004",
      "rule": "Maximum 5 DAG passes per workflow invocation before mandatory human checkpoint",
      "enforcement": "runtime",
      "severity": "warning"
    },
    {
      "id": "INV-005",
      "rule": "depends-on edges must form a DAG (no cycles)",
      "enforcement": "assembly-time",
      "severity": "error"
    }
  ]
}
```

## Risks

- **Schema evolution complexity**: As more workflows move to DAG-first (techspec, plan, tasks), the catalog grows. Node definitions across workflows might conflict or duplicate. Mitigation: catalog files are per-workflow initially; consolidation deferred until patterns stabilize.
- **Contract expressiveness limits**: The simple `consumes[]/produces[]` model may not capture all artifact relationships (e.g., "consumes spec.md but only the user stories section"). Mitigation: start simple; extend contract model only when real limitations surface during PoC.
- **Validation performance**: The structural validator runs 9 checks. For small DAGs (5-7 nodes per pass), this is trivial. But if composition leads to large DAGs, validation could become expensive. Mitigation: plugin DAGs will be small by nature (one workflow pass); performance is unlikely to be an issue.

## Open Questions

- **Artifact resolution**: Node contracts reference artifacts by name (e.g., "spec.md"). How do these resolve to actual file paths? Via a convention (specs/{feature_id}/spec.md)? Via the execution trace? Via a separate artifact registry?
- **Catalog composition**: When command boundaries collapse and a single DAG spans specify + techspec, does the Supervisor read from two catalog files or a merged one?
- **Schema migration**: When the catalog schema evolves (new fields, changed constraints), how are existing DAG versions handled? Do they validate against the schema version they were created with?
- **Contract validation at assembly time**: Should the DAG Assembler verify that the produces/consumes chain is satisfied — i.e., every consumed artifact is produced by an upstream node? This would catch broken artifact chains before execution.

## Recommended Next Steps

1. **Write the Pydantic entities for the plugin domain**: Adapt GraphNode, Edge, StrategyGraph from context harness. Add Contract, PassMetadata, ExecutionTraceEntry. Reuse ValidationResult and ValidationViolation unchanged. This gives you type-safe Python objects immediately.

2. **Implement the plugin graph loader**: Adapt `load_graph()` to create NetworkX MultiDiGraph from plugin DAG JSON. Add the 5 subgraph views (depends_on, produces, validates, constrained_by, informed_by).

3. **Implement the plugin structural validator**: Adapt the 9-step validator. Replace context harness edge constraints with plugin edge constraints. Add invariant checking on top of structural validation.

4. **Create the specify catalog file**: Write the concrete `specify-catalog.json` with all 7 nodes, edge constraints, and invariants as defined above. This is the first artifact the DAG-ops agents will consume.

5. **Hand-write DAG passes for all 3 flexibility scenarios**: Scenario 1 (skip enrichment), Scenario 2 (add research), Scenario 3 (human clarification). Validate each against the catalog's edge constraints and invariants. This proves the schema supports the intended flexibility before any code runs.
