# DAG Specialist Subagents v2 — Analysis Synthesis

> **Revises**: [`dag-specialist-subagents-synthesis.md`](dag-specialist-subagents-synthesis.md)
>
> **Related**: [`dag-supervisor-design-synthesis.md`](dag-supervisor-design-synthesis.md), [`dag-first-execution-synthesis.md`](dag-first-execution-synthesis.md)

## Problem Statement

After a successful dry run of the DAG-first specify workflow, the responsibility split between the two specialist subagents (State Briefer and DAG Assembler) was found to be conceptually impure. The DAG Assembler's `parse-report` action performs content analysis (reading prose reports, extracting structured data, classifying gaps) alongside graph mechanics (updating node status, writing execution traces) — two fundamentally different kinds of work in one agent. Meanwhile, the State Briefer already reads and analyzes artifacts for pass-start briefings, making it the natural home for all analysis work. This revision redesigns the responsibility boundary: the State Briefer expands into a **State Analyst** that owns all reading and analysis, while the DAG Assembler slims to pure graph mechanics.

## Context & Constraints

- **Dry run evidence**: The v1 design (from `dag-specialist-subagents-synthesis.md`) was executed in a full 3-pass, 7-domain-agent dry run. The protocol worked mechanically — all parse-reports fired, all briefings produced, all passes frozen correctly. But the DAG JSON had empty `evidence` and `execution_trace` fields, indicating the analysis-to-persistence pipeline was incomplete.
- **Original "split later" signal**: The v1 design explicitly noted: "Lets keep it as 1 for now, can breakup later." The coupling argument (build node AND construct prompt in one step) applies to `assemble-and-prepare` but not to `parse-report` — parsing a report has no coupling to graph building.
- **Same platform constraints apply**: No nested subagents, file system as communication channel, Supervisor context preservation as driving constraint, ADR-005 compatibility for domain agents.
- **Constitution Principle IX**: Deterministic infrastructure operations must live in `humaninloop_brain` and be consumed via CLI. This applies to any DAG JSON writes by the new State Analyst.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Analysis responsibility | State Analyst (renamed from State Briefer) absorbs all report parsing and content analysis | Confident | Single agent for all "read and understand" work. Clean separation from graph mechanics. |
| DAG Assembler scope | Slims to pure graph mechanics: `assemble-and-prepare` + `freeze-pass` only | Confident | Removes the analysis work that didn't belong. Builder builds, analyzer analyzes. |
| State Analyst actions | Two explicit actions: `parse-report` (per-node) and `briefing` (per-pass) | Confident | Mirrors DAG Assembler's proven explicit action model from the dry run. No adaptive behavior. |
| DAG JSON write boundary | Assembler writes structure (nodes, edges). Analyst writes observations (evidence, trace, status). | Confident | Two agents write to the same file but to different, non-overlapping fields. Natural scoping. |
| Status write ownership | State Analyst writes node status as part of `parse-report` | Confident | Status value is determined by analysis (interpreting verdict from report). Writing it alongside evidence is a natural atomic operation. Avoids extra round-trip. |
| CLI for Analyst writes | New `hil-dag record` command for State Analyst to write status + evidence + trace atomically | Confident | Follows Constitution Principle IX. Same pattern as DAG Assembler using `hil-dag` CLI. Prevents malformed JSON writes. |
| Agent naming | "State Briefer" renamed to "State Analyst" | Confident | Reflects expanded role — no longer just produces briefings, now also parses reports and records analysis results. |
| Per-node call count | Unchanged at 3 calls per node (assemble + execute + parse) | Confident | `parse-report` moves from DAG Assembler to State Analyst. Same protocol shape, different agent for step 3. No additional round-trips. |

## Decision Trail

### Parse-report ownership: DAG Assembler vs. State Analyst

- **v1 design**: DAG Assembler owned `parse-report` as one of three actions
- **Observation**: The State Briefer already reads reports when synthesizing DAG history for briefings — it's already parsing reports, just at a different point in the timeline
- **Key tension**: `parse-report` is fundamentally analysis work (read prose, extract meaning, classify gaps) with a thin graph-update layer. Keeping it in the DAG Assembler meant the "builder" agent had to "understand content"
- **Chosen**: Move to State Analyst
- **Key reasoning**: One agent for all "read and understand" work. The agent that extracts meaning should also be the one that records it. This also fixes the empty `evidence`/`execution_trace` problem from the dry run — the analyzing agent writes what it found.

### Extra round-trip concern

- **Initial concern**: Moving `parse-report` analysis to State Analyst and leaving status writes with DAG Assembler would add a round-trip per node (Analyst analyzes → Supervisor relays → Assembler writes status)
- **Resolution**: State Analyst writes status alongside evidence — same atomic operation, no extra round-trip
- **Counterargument considered**: Two agents writing to DAG JSON breaks single-writer rule
- **Resolution**: Scoped writes — Assembler owns structure (nodes, edges), Analyst owns observations (evidence, trace, status). Non-overlapping fields.

### State Analyst writing to DAG JSON: Direct manipulation vs. CLI

- **Options considered**: (A) State Analyst reads/writes JSON directly, (B) Extend `hil-dag` CLI with new command
- **Chosen**: Option B — new `hil-dag record` command
- **Key reasoning**: The dry run showed empty `evidence`/`execution_trace` even when the DAG Assembler (a graph-specialist agent) was responsible. LLM agents doing raw JSON manipulation on nested structures is unreliable. A CLI command validates schema and writes atomically. Follows Constitution Principle IX.

## Architecture Overview

### Updated Three-Tier Agent Model

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: SUPERVISOR (main conversation thread)                    │
│                                                                  │
│ Role:     Assembly decisions, pass lifecycle, goal evaluation    │
│ Consumes: Structured briefings, structured parse summaries      │
│ Context:  Goal + strategy skills + DAG-ops structured reports   │
└─────────┬──────────────────────────────────┬────────────────────┘
          │ structured protocol              │ structured protocol
          ▼                                  ▼
┌─────────────────────────┐    ┌──────────────────────────────────┐
│ TIER 2a:                │    │ TIER 2b:                          │
│ STATE ANALYST           │    │ DAG ASSEMBLER                     │
│ (renamed from Briefer)  │    │ (slimmed)                         │
│                         │    │                                    │
│ Actions:                │    │ Actions:                           │
│ • parse-report          │    │ • assemble-and-prepare            │
│ • briefing              │    │ • freeze-pass                     │
│                         │    │                                    │
│ Reads:                  │    │ Reads:                             │
│ • Domain agent reports  │    │ • Node catalog                    │
│ • DAG history           │    │ • Current DAG                     │
│ • Node catalog          │    │                                    │
│ • Strategy skills       │    │ Does:                              │
│ • Current artifacts     │    │ • Add nodes + infer edges         │
│                         │    │ • Validate invariants             │
│ Writes (via CLI):       │    │ • Construct NL prompts            │
│ • evidence[]            │    │ • Freeze DAG snapshots            │
│ • execution_trace[]     │    │                                    │
│ • node status           │    │ Writes (via CLI):                  │
│                         │    │ • nodes[]                          │
│ Returns:                │    │ • edges[]                          │
│ • Structured summaries  │    │ • pass metadata                   │
│ • Briefings             │    │                                    │
└─────────────────────────┘    └──────────────┬───────────────────┘
                                              │ natural language
                                              │ (ADR-005 preserved)
                                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: DOMAIN AGENTS (unchanged)                                │
│ Requirements Analyst | Devil's Advocate | Plan Architect | ...   │
└─────────────────────────────────────────────────────────────────┘
```

### Updated Per-Node Protocol

```
SUPERVISOR                    STATE ANALYST          DAG ASSEMBLER         DOMAIN AGENT
    │                              │                     │                     │
    │──── briefing request ───────>│                     │                     │
    │     (per-pass or on-demand)  │  reads: history,    │                     │
    │                              │  catalog, strategy  │                     │
    │                              │  skills, artifacts  │                     │
    │<─── structured briefing ─────│                     │                     │
    │                              │                     │                     │
    │ DECIDES: next node + params  │                     │                     │
    │                              │                     │                     │
    │──── assemble-and-prepare ───────────────────────> │                     │
    │     {next_node, parameters}  │                     │  reads catalog,     │
    │                              │                     │  infers edges,      │
    │                              │                     │  validates,         │
    │                              │                     │  writes DAG JSON,   │
    │                              │                     │  builds NL prompt   │
    │<─── {valid, agent_prompt} ──────────────────────── │                     │
    │                              │                     │                     │
    │──── spawn with NL prompt ──────────────────────────────────────────────>│
    │                              │                     │   writes full       │
    │                              │                     │   report to disk    │
    │<─── brief status ─────────────────────────────────────────────────────│
    │                              │                     │                     │
    │──── parse-report ───────────>│                     │                     │
    │     {node_id, dag_path}      │  reads report       │                     │
    │                              │  FROM DISK,         │                     │
    │                              │  extracts summary,  │                     │
    │                              │  writes evidence +  │                     │
    │                              │  trace + status     │                     │
    │                              │  via hil-dag record │                     │
    │<─── structured summary ──────│                     │                     │
    │                              │                     │                     │
    │ EVALUATES: continue/halt/done│                     │                     │
```

### Updated Call Counts

| Phase | State Analyst | DAG Assembler | Domain Agent | Supervisor Decisions |
|---|---|---|---|---|
| Pass start | 1 (briefing) | 0 | 0 | 0 |
| Per node | 1 (parse-report) | 1 (assemble-and-prepare) | 1 | 2 (select + evaluate) |
| Pass end | 0 | 1 (freeze-pass) | 0 | 1 (done/new/halt) |

**Typical 3-node pass**: 1 State Analyst briefing + 3 State Analyst parse-reports + 3 DAG Assembler assemblies + 1 DAG Assembler freeze + 3 domain agents = **11 subagent calls, 7 Supervisor decisions** (unchanged from v1).

### Updated Agent Classification

| Category | Agents | Actions | Protocol | DAG JSON Writes |
|---|---|---|---|---|
| **Supervisor** | (main thread) | Decisions, pass lifecycle | Structured I/O with DAG-ops | `hil-dag create` only |
| **DAG Operations — Analyst** | State Analyst | `parse-report`, `briefing` | Structured with Supervisor | Observations: evidence, trace, status (via `hil-dag record`) |
| **DAG Operations — Builder** | DAG Assembler | `assemble-and-prepare`, `freeze-pass` | Structured with Supervisor, NL with domain agents | Structure: nodes, edges, metadata (via `hil-dag assemble`, `hil-dag freeze`) |
| **Domain** | Analyst, Advocate, etc. | (agent-specific) | Natural language (ADR-005) | None |

### What Enters Supervisor Context

| Data | In Supervisor Context? | Source |
|---|---|---|
| State Analyst structured briefing | Yes | State Analyst `briefing` return |
| State Analyst parse summary | Yes | State Analyst `parse-report` return |
| Node selection + parameters | Yes (Supervisor generates) | Supervisor decision |
| DAG Assembler validation result | Yes | DAG Assembler return |
| NL prompt for domain agent | Yes (brief, passed through) | DAG Assembler return |
| Domain agent full report | **No** | Written to disk, read by State Analyst |
| Domain agent brief status | Yes (1-2 sentences) | Domain agent return |
| Raw catalog, history, strategy skills | **No** | Read by State Analyst / DAG Assembler |
| Raw DAG JSON | **No** | Read/written by DAG-ops agents |

## New CLI Command

### `hil-dag record`

Atomic write of analysis results to a node in the DAG JSON.

```bash
hil-dag record --node <node_id> \
  --status <status> \
  --evidence '<json_array>' \
  --trace '<json_object>' \
  <dag_path>
```

| Flag | Description |
|------|-------------|
| `--node` | Node ID to update |
| `--status` | New status value (e.g., `completed`, `passed`, `needs-revision`) |
| `--evidence` | JSON array of evidence entries for the node's `evidence` field |
| `--trace` | JSON object to append to the pass-level `execution_trace` array |
| positional | Path to the DAG JSON file |

**Validation**: The command validates that the node exists, the status is valid for the node type (per `valid_statuses` in catalog), and the evidence/trace conform to expected schema.

## Risks

- **State Analyst complexity**: The State Analyst now has two distinct actions with different invocation frequencies (per-node vs. per-pass). If the agent definition becomes too complex, action quality may degrade. Mitigation: explicit action separation with clear input/output contracts, same pattern that proved reliable for DAG Assembler in the dry run.
- **Two writers to DAG JSON**: Both agents write to the same file, albeit to non-overlapping fields. Concurrent writes could corrupt the file if two agents ran simultaneously. Mitigation: the Supervisor orchestrates sequentially — no parallel writes are possible in the current architecture.
- **`hil-dag record` development cost**: A new CLI command needs implementation, testing, and integration. Mitigation: the command is structurally simple (read JSON, update fields, write JSON) and follows established patterns in `humaninloop_brain`.

## Open Questions

- **State Analyst model choice**: The State Briefer used `sonnet`. With the expanded `parse-report` responsibility (called more frequently), should the State Analyst stay on `sonnet` or move to a different model for cost/latency optimization?
- **Evidence schema**: What structure should evidence entries follow? Freeform text? Structured fields (finding, source, confidence)? Should the schema be defined in the catalog or in the State Analyst's agent definition?
- **Execution trace schema**: What fields should each trace entry contain? Timestamp, node_id, action, result, duration? Should it mirror the structured summary fields?
- **State Analyst and NL prompt awareness**: The State Analyst now reads reports that were prompted by NL prompts the DAG Assembler constructed. Does the Analyst need access to the prompt that was sent, to better parse the expected response structure? Or are report conventions (ADR-005 headings) sufficient?

## Recommended Next Steps

1. **Design the `hil-dag record` command**: Define the evidence and execution_trace schemas, implement in `humaninloop_brain`, add tests. This unblocks the State Analyst's write capability.

2. **Update the State Analyst agent definition**: Expand `plugins/humaninloop/agents/state-briefer.md` (rename to `state-analyst.md`) with the new `parse-report` action, including input/output schemas and report parsing patterns moved from the DAG Assembler definition.

3. **Slim the DAG Assembler agent definition**: Remove `parse-report` action and report parsing patterns from `plugins/humaninloop/agents/dag-assembler.md`. Verify `assemble-and-prepare` and `freeze-pass` remain self-contained.

4. **Update `specify.md` command file**: Change all `parse-report` calls from `humaninloop:dag-assembler` to `humaninloop:state-analyst`. Update the Responsibility Boundaries table.

5. **Update the plugin agent registry**: Rename agent file, update `plugin.json` manifest to reference `state-analyst` instead of `state-briefer`.

6. **Dry run the updated protocol**: Execute the specify workflow with the v2 agent split to validate that evidence and execution_trace fields are now populated, and the per-node call count remains at 3.
