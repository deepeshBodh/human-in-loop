# Single-DAG Iteration Model — Analysis Synthesis

> **Replaces**: DAG-per-pass versioning model from [`dag-first-execution-synthesis.md`](../dag-first-execution-synthesis.md)
>
> **Depends on**: [`goal-oriented-supervisor-synthesis.md`](goal-oriented-supervisor-synthesis.md), [`state-analyst-dag-assembler-redesign-synthesis.md`](state-analyst-dag-assembler-redesign-synthesis.md)
>
> **Reference**: [human-in-loop-context-harness](https://github.com/deepeshBodh/human-in-loop-context-harness) — single-graph model with frozen Pydantic entities and append-only evidence

## Problem Statement

The DAG-per-pass iteration model produces nearly identical files across passes. A 5-pass specify workflow generated 5 separate JSON files where 4 of 5 had the same node structure (constitution-gate, analyst-review, advocate-review). The meaningful differences — what the analyst produced, what the advocate found, what the user clarified — were buried across files with no structural link between them. Understanding the workflow's story required reading 5 files and mentally stitching them together. The relationship between "advocate rejected in pass 1" and "analyst revised in pass 2" was implicit, reconstructed by the State Analyst from file history rather than expressed in the graph itself.

## Context & Constraints

- **Dry run evidence**: 5 pass files with 80% structural redundancy. The graph shape barely changed across passes — only node content and verdicts changed.
- **Supervisor is context-constrained**: The Supervisor cannot efficiently read multiple files or git history mid-workflow. The revision story must be readable from a single JSON document.
- **Context harness reference**: The context harness uses a single-graph model with frozen Pydantic entities and append-only evidence accumulation. It defers history to git (planned, not yet implemented). Our system needs history in the JSON itself because the State Analyst consumes it per-call.
- **Immutability requirement**: The DAG-per-pass model guaranteed immutability by freezing entire files. The single-DAG model needs an equivalent guarantee without file-level freezing.
- **Existing infrastructure**: `hil-dag` CLI handles all DAG writes. Immutability enforcement can be added to the CLI without changing the agent protocol.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Iteration model | Single DAG with node-level revision history. One file per workflow invocation, not per pass. | Confident | Eliminates redundancy, preserves continuity, tells the complete story in one place. |
| Pass concept | Pass markers as metadata on the DAG. Passes are boundaries within one file, not separate files. | Confident | Passes remain a meaningful lifecycle concept (created → frozen) but don't require separate files. |
| Node history | Array of self-contained pass entries per node. Each entry includes status, evidence, execution trace, and metrics for that pass. | Confident | Co-locates all information about what happened to a node in a given pass. No cross-referencing needed. |
| Evidence location | Nested inside node history entries, not flat on the node | Confident | Consistent with self-contained history entries. Each frozen pass entry is a complete record. |
| Execution trace location | Nested inside node history entries, not at pass level | Confident | Same logic as evidence — the trace describes what happened to a specific node in a specific pass. One entry, one complete story. |
| Immutability mechanism | Pass-entry level freezing enforced by `hil-dag` CLI. Frozen entries cannot be modified. Only current pass entries are mutable. | Confident | Equivalent guarantee to file-level freezing but within a single growing document. CLI enforcement prevents accidental or malicious modification. |
| Revision causality | `triggered_by` as a 6th edge type. Captures causal link between a verdict in pass N and a re-execution in pass N+1. | Confident | Makes the revision story explicit in the graph. Traceable causal chains without reading history entries. |
| Edge type taxonomy | Flat — `triggered_by` is a 6th edge type alongside the existing 5. No structural/revision subcategories. | Confident | All edges stored and queried the same way. The type field distinguishes them. No taxonomy overhead. |
| Structural edges | Created once during assembly, persist across passes. Not recreated per pass. | Confident | Edges represent relationships between nodes, not between pass-specific executions. They're stable across the workflow. |

## Decision Trail

### DAG-per-pass vs. single DAG

- **Original design**: DAG-per-pass from `dag-first-execution-synthesis.md`. Each iteration produces a new immutable DAG. Previous DAGs preserved as history.
- **Problems observed**: 5 files with 80% redundancy. Lost continuity between passes. No structural link between "advocate rejected" and "analyst revised." Story requires reading all files.
- **Chosen**: Single DAG with revision history on nodes
- **Key reasoning**: Three pain points drove the change — redundancy (identical structures repeated), lost continuity (no causal links between passes), and poor observability (story split across files). All three resolve with a single DAG where nodes accumulate history and `triggered_by` edges capture causality.

### Immutability: File-level vs. entry-level

- **Original model**: Freeze entire file → never touch again. Simple and absolute.
- **Problem**: Single DAG must keep growing — can't freeze the file.
- **Chosen**: Pass-entry level freezing. When a pass completes, all its entries across all nodes get `frozen: true`. `hil-dag` CLI refuses writes to frozen entries.
- **Key reasoning**: Same immutability guarantee, different granularity. The ledger analogy: you can add entries but never modify past ones. CLI enforcement is the single write gate — agents never write JSON directly.

### Evidence and trace location: Flat vs. nested

- **Options considered**: (A) Flat append-only evidence list on node (context harness pattern), (B) Evidence nested inside pass history entries
- **Chosen**: Option B — nested inside history entries
- **Key reasoning**: The primary consumer is the State Analyst reading pass-by-pass. Co-locating evidence and trace with their pass context makes each frozen entry a self-contained record. "What happened to analyst-review in pass 3?" → read one history entry, get status, evidence, trace, and metrics.

### Revision edges: Implicit vs. explicit

- **Options considered**: (A) Implicit — infer causal links from pass numbers in history entries, (B) Explicit `triggered_by` edge type with source_pass, target_pass, and reason
- **Chosen**: Option B — explicit edges
- **Key reasoning**: The single DAG should tell the complete story by itself. Explicit causal edges mean you can trace "advocate rejected → clarification collected → analyst revised → advocate approved" as a graph traversal, not a history inference.

### Edge taxonomy: Categorized vs. flat

- **Options considered**: (A) Two categories — structural edges and revision edges, (B) Flat — `triggered_by` as a 6th edge type
- **Chosen**: Option B — flat
- **Key reasoning**: A category distinction adds taxonomy the DAG Assembler and CLI must enforce. `triggered_by` is just an edge with extra metadata (`source_pass`, `target_pass`, `reason`). Stored and queried the same way as all other edges. Distinguishable by type field alone.

## Architecture Overview

### Single-DAG Structure

```json
{
  "id": "specify-002-storing-memories-created",
  "workflow_id": "specify",
  "schema_version": "2.0.0",
  "current_pass": 5,
  "status": "completed",
  "created_at": "2026-02-18T18:54:51Z",
  "completed_at": "2026-02-18T20:01:32Z",

  "passes": [
    {"pass": 1, "outcome": "completed", "detail": "needs-revision",
     "created_at": "...", "completed_at": "...", "frozen": true},
    {"pass": 2, "outcome": "completed", "detail": "needs-revision",
     "created_at": "...", "completed_at": "...", "frozen": true},
    {"pass": 3, "outcome": "completed", "detail": "needs-revision",
     "created_at": "...", "completed_at": "...", "frozen": true},
    {"pass": 4, "outcome": "completed", "detail": "needs-revision",
     "created_at": "...", "completed_at": "...", "frozen": true},
    {"pass": 5, "outcome": "completed", "detail": "ready",
     "created_at": "...", "completed_at": "...", "frozen": true}
  ],

  "nodes": [
    {
      "id": "constitution-gate",
      "type": "gate",
      "status": "passed",
      "current_pass": 1,
      "history": [
        {"pass": 1, "status": "passed", "frozen": true,
         "evidence": [],
         "trace": {"started_at": "...", "completed_at": "...", "duration_ms": 500}}
      ]
    },
    {
      "id": "analyst-review",
      "type": "task",
      "status": "completed",
      "current_pass": 5,
      "history": [
        {"pass": 1, "status": "completed", "frozen": true,
         "evidence": [{"id": "EV-001", "type": "analyst-report",
                        "description": "Created spec: 5 user stories, 18 FRs",
                        "reference": "specs/.../analyst-report.md"}],
         "trace": {"started_at": "...", "completed_at": "...", "duration_ms": 186000,
                   "agent_summary": "Produced spec with 5 user stories, 18 FRs, 5 edge cases"},
         "gaps_found": 7},
        {"pass": 2, "status": "completed", "frozen": true,
         "evidence": [{"id": "EV-002", "...": "..."}],
         "trace": {"...": "..."},
         "gaps_found": 5},
        {"pass": 5, "status": "completed", "frozen": true,
         "evidence": [{"id": "EV-005", "...": "..."}],
         "trace": {"...": "..."},
         "gaps_found": 0}
      ]
    },
    {
      "id": "advocate-review",
      "type": "gate",
      "status": "passed",
      "current_pass": 5,
      "history": [
        {"pass": 1, "status": "needs-revision", "frozen": true,
         "verdict": "needs-revision",
         "evidence": [{"id": "EV-AR-001", "type": "advocate-report",
                        "description": "7 important gaps, 5 minor gaps"}],
         "trace": {"...": "..."}},
        {"pass": 5, "status": "passed", "frozen": true,
         "verdict": "ready",
         "evidence": [{"id": "EV-AR-005", "...": "..."}],
         "trace": {"...": "..."}}
      ]
    },
    {
      "id": "human-clarification",
      "type": "decision",
      "status": "decided",
      "current_pass": 4,
      "history": [
        {"pass": 1, "status": "decided", "frozen": true,
         "clarifications": 7,
         "trace": {"...": "..."}},
        {"pass": 4, "status": "decided", "frozen": true,
         "clarifications": 3,
         "trace": {"...": "..."}}
      ]
    },
    {
      "id": "spec-complete",
      "type": "milestone",
      "status": "achieved",
      "current_pass": 5,
      "history": [
        {"pass": 5, "status": "achieved", "frozen": true,
         "trace": {"...": "..."}}
      ]
    }
  ],

  "edges": [
    {"id": "E-001", "source": "constitution-gate", "target": "analyst-review",
     "type": "depends_on"},
    {"id": "E-002", "source": "analyst-review", "target": "advocate-review",
     "type": "validates"},
    {"id": "E-003", "source": "advocate-review", "target": "spec-complete",
     "type": "depends_on"},

    {"id": "E-T01", "source": "advocate-review", "target": "analyst-review",
     "type": "triggered_by", "source_pass": 1, "target_pass": 2,
     "reason": "needs-revision, 7 important gaps"},
    {"id": "E-T02", "source": "advocate-review", "target": "analyst-review",
     "type": "triggered_by", "source_pass": 2, "target_pass": 3,
     "reason": "needs-revision, 5 important gaps"},
    {"id": "E-T03", "source": "advocate-review", "target": "analyst-review",
     "type": "triggered_by", "source_pass": 3, "target_pass": 4,
     "reason": "needs-revision, 3 important gaps"},
    {"id": "E-T04", "source": "advocate-review", "target": "analyst-review",
     "type": "triggered_by", "source_pass": 4, "target_pass": 5,
     "reason": "needs-revision, 3 important gaps"}
  ]
}
```

### The Story in One Place

Reading this single DAG tells the complete workflow story:

1. **Nodes**: constitution-gate passed once, analyst revised 5 times, advocate rejected 4 times then approved, 4 rounds of clarification, milestone achieved
2. **Convergence**: gaps_found on analyst: 7 → 5 → 3 → 3 → 0
3. **Causality**: `triggered_by` edges trace why each revision happened
4. **Evidence**: each history entry shows what was produced
5. **Timing**: each trace shows when and how long

No file stitching. No mental reconstruction. One document.

### Edge Types (6 total)

| Edge Type | Created | Purpose | Participates in Topological Sort |
|---|---|---|---|
| `depends_on` | Assembly | Execution ordering | Yes |
| `produces` | Assembly | Artifact flow | No |
| `validates` | Assembly | Review relationship | No |
| `constrained_by` | Assembly | Boundary enforcement | No |
| `informed_by` | Assembly | Context without hard dependency | No |
| `triggered_by` | Pass transition | Causal link between verdict and re-execution | No |

`triggered_by` edges carry additional metadata: `source_pass`, `target_pass`, `reason`.

### Immutability Model

```
Pass 1: FROZEN                    Pass 2: FROZEN               ...  Pass 5: FROZEN
┌─────────────────────┐          ┌─────────────────────┐           ┌─────────────────────┐
│ analyst-review       │          │ analyst-review       │           │ analyst-review       │
│   pass: 1           │          │   pass: 2           │           │   pass: 5           │
│   status: completed │          │   status: completed │           │   status: completed │
│   evidence: [...]   │          │   evidence: [...]   │           │   evidence: [...]   │
│   trace: {...}      │          │   trace: {...}      │           │   trace: {...}      │
│   frozen: true      │◄──IMMUTABLE──►frozen: true      │           │   frozen: true      │
└─────────────────────┘          └─────────────────────┘           └─────────────────────┘
```

Rules:
- History entries for completed passes have `frozen: true`
- `hil-dag` CLI refuses to modify any field in a frozen entry
- Only the current pass's entries are mutable (being built)
- When a pass completes, all its entries across all nodes are frozen atomically
- New passes add new history entries — they never touch prior entries
- The `passes` array entries are also frozen when their pass completes

### Comparison: DAG-per-pass vs. Single DAG

| Aspect | DAG-per-pass (v1) | Single DAG (v3) |
|---|---|---|
| Files per workflow | N (one per pass) | 1 |
| Redundancy | High — same nodes recreated | None — nodes accumulate history |
| Continuity | Implicit — State Analyst reads all files | Explicit — `triggered_by` edges + history |
| Observability | Read N files, stitch mentally | Read 1 file, story is complete |
| Immutability | File-level freeze | Entry-level freeze |
| Structural edges | Recreated each pass | Created once, persist |
| Node identity | Separate instances per pass | Single node with revision history |
| Pass lifecycle | Separate file lifecycle | Metadata entries in `passes` array |
| State Analyst reads | Multiple files + history context | One file — all history co-located |

## Risks

- **Single file corruption**: With DAG-per-pass, corruption of one file loses one pass. With a single DAG, corruption loses everything. Mitigation: `hil-dag` CLI uses atomic write-validate-swap (write to temp, validate, `os.replace`). Backup copies before writes.
- **File size growth**: A long-running workflow with many passes accumulates history in one file. For a 5-pass specify workflow this is modest, but cross-workflow generalization (if `/specify` + `/plan` + `/tasks` share one DAG) could produce large files. Mitigation: the current scope is one DAG per workflow invocation. Cross-workflow sharing is a separate design decision.
- **Schema migration**: Existing DAG-per-pass files from dry runs are incompatible with the single-DAG schema. Mitigation: this is a pre-production architecture change. No migration needed — new schema replaces old.
- **`triggered_by` edge proliferation**: A 5-pass workflow with analyst + advocate + clarification produces 12+ triggered_by edges. For workflows with many revision cycles, the edge count grows linearly. Mitigation: `triggered_by` edges are lightweight (5 fields each). Even 50 edges add minimal file size. The observability value justifies the storage.

## Open Questions

- **`hil-dag` CLI changes**: The CLI currently operates on DAG-per-pass files. It needs changes for: single-file pass management, entry-level freeze enforcement, `triggered_by` edge creation, history entry appending. What's the migration scope?
- **Node re-assembly in new passes**: When the analyst re-executes in pass 2, the node already exists in the DAG. Does the DAG Assembler "re-open" the node (add a new history entry) rather than "add" it? What does the `assemble-and-prepare` action look like for existing nodes?
- **Pydantic model changes**: The current `humaninloop_brain` models follow DAG-per-pass structure. The frozen Pydantic model pattern from the context harness applies — but the models need history arrays and entry-level freeze flags. What's the model redesign scope?
- **Cross-workflow DAGs**: Could `/specify` and `/plan` eventually share one DAG? The single-DAG model makes this architecturally possible but introduces node namespace and pass boundary questions.

## Recommended Next Steps

1. **Design the single-DAG Pydantic models**: Redesign `StrategyGraph`, `GraphNode`, and `Edge` models in `humaninloop_brain` to support node-level history arrays, entry-level freezing, pass metadata, and the `triggered_by` edge type. Follow the context harness pattern of frozen Pydantic models with model validators.

2. **Redesign the `hil-dag` CLI commands**: Map each existing command (`create`, `assemble`, `status`, `record`, `freeze`) to single-DAG equivalents. Key changes: `create` initializes a new pass entry (not a new file), `assemble` either adds a new node or re-opens an existing one, `freeze` freezes all current-pass entries atomically.

3. **Update the specify catalog**: Add `capabilities` tags and `carry_forward` property (from the agent redesign synthesis). Verify that the catalog schema supports the single-DAG model.

4. **Prototype one full workflow**: Hand-write the single-DAG JSON for the "storing memories" dry run (5 passes, 15 stakeholder clarifications, ready verdict). Validate that the structure tells the complete story and the State Analyst can produce recommendations from it.

5. **Implement and test**: Build the new Pydantic models and CLI commands with the 90%+ test coverage gate from the constitution. Use the hand-written prototype as a golden file test.
