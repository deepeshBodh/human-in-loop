# V3 Architecture Design — Unified Specification

> **Supersedes**: [`dag-first-execution-synthesis.md`](../dag-first-execution-synthesis.md), [`dag-supervisor-design-synthesis.md`](../dag-supervisor-design-synthesis.md), [`dag-specialist-subagents-v2-synthesis.md`](../dag-specialist-subagents-v2-synthesis.md)
>
> **Synthesized from**:
> - [`goal-oriented-supervisor-synthesis.md`](goal-oriented-supervisor-synthesis.md)
> - [`state-analyst-dag-assembler-redesign-synthesis.md`](state-analyst-dag-assembler-redesign-synthesis.md)
> - [`single-dag-iteration-model-synthesis.md`](single-dag-iteration-model-synthesis.md)

## Overview

V3 is a ground-up redesign of the DAG execution architecture driven by three problems observed across two dry runs:

1. **The Supervisor became a recipe-follower** — 452 lines of procedural script naming every node, agent, and routing decision instead of pursuing a goal
2. **The specialist agents were underutilized** — the State Analyst and DAG Assembler acted as pass-through mechanics instead of owning domain knowledge and graph mechanics
3. **The iteration model was redundant** — DAG-per-pass produced near-identical files with no structural link between revision cycles

V3 addresses all three with a unified architecture where the Supervisor is domain-agnostic, the specialist agents own their domains, and a single DAG captures the complete workflow story.

---

## Architecture

### Three-Tier Agent Model

```
┌──────────────────────────────────────────────────────────────────┐
│ TIER 1: SUPERVISOR                                                │
│                                                                    │
│ Knows:    DAG vocabulary (4 node types, 6 edge types,            │
│           pass lifecycle, gate verdicts). Goal criteria.           │
│ Does:     Picks from ranked recommendations, dispatches,          │
│           watches convergence, makes captain's calls              │
│ CLI:      None — pure dispatcher                                  │
│                                                                    │
│ Three outbound verbs:                                             │
│   1. Ask the Analyst   (briefing / parse-and-recommend)           │
│   2. Tell the Assembler (assemble / freeze / update-status)       │
│   3. Dispatch the agent (Task tool with NL prompt)                │
│                                                                    │
│ Also receives:                                                    │
│   - Synchronous returns from all three targets                    │
│   - Human input for decision nodes (via AskUserQuestion)          │
└─────────┬───────────────────────────────────┬────────────────────┘
          │ structured protocol               │ structured protocol
          ▼                                   ▼
┌───────────────────────────┐   ┌──────────────────────────────────┐
│ TIER 2a:                   │   │ TIER 2b:                          │
│ STATE ANALYST (Opus)       │   │ DAG ASSEMBLER                     │
│                            │   │                                    │
│ Actions:                   │   │ Actions:                           │
│ • briefing                 │   │ • assemble-and-prepare            │
│   (cold start per pass)    │   │   - intent → catalog resolution  │
│ • parse-and-recommend      │   │   - invariant auto-resolution    │
│   (per agent node)         │   │   - node add / re-open           │
│                            │   │   - edge inference (new nodes)   │
│ Reads:                     │   │   - NL prompt construction       │
│ • Node catalog             │   │ • freeze-pass                     │
│ • Strategy skills          │   │   - freeze current pass entries  │
│ • Artifacts on disk        │   │   - create next pass (optional)  │
│ • Single DAG file          │   │   - add triggered_by edges       │
│                            │   │ • update-status                   │
│                            │   │   - decision / milestone / gate  │
│                            │   │   - validates prerequisites      │
│                            │   │                                    │
│ Recommends in:             │   │ Reads:                             │
│ • Intent language          │   │ • Node catalog                    │
│ • Ranked with rationale    │   │ • Single DAG file                 │
│                            │   │                                    │
│ Writes (via CLI):          │   │ Resolves via:                      │
│ • Node history entries     │   │ • Capability tag match (primary)  │
│   (evidence, trace, status)│   │ • Semantic description (fallback) │
│                            │   │                                    │
│                            │   │ Writes (via CLI):                  │
│                            │   │ • nodes[], edges[]                │
│                            │   │ • pass metadata                   │
└───────────────────────────┘   └──────────────┬───────────────────┘
                                               │ natural language
                                               │ (ADR-005 preserved)
                                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ TIER 3: DOMAIN AGENTS (unchanged)                                 │
│ Requirements Analyst | Devil's Advocate | Plan Architect | ...    │
└──────────────────────────────────────────────────────────────────┘
```

### Knowledge Distribution

| Layer | Knows | Does NOT Know |
|---|---|---|
| **Supervisor** | 4 node types, 6 edge types, pass lifecycle, gate verdicts, goal criteria | Node IDs, agent types, strategy patterns, catalog contents, procedural sequences |
| **State Analyst** | Catalog, strategy skills, artifact state, DAG history, gap classification | Assembly mechanics, prompt construction, graph structure operations |
| **DAG Assembler** | Catalog structure, invariants, edge inference, prompt templates, intent resolution | Strategy patterns, artifact content, what happened in prior passes |
| **Domain Agents** | Their domain expertise, skills, artifact conventions | Workflow structure, DAG mechanics, other agents' existence |

---

## Supervisor

### Goal Language

The Supervisor receives a goal expressed in DAG vocabulary — no node IDs, no agent names:

```markdown
## Goal
Produce a validated specification.

## Success Criteria
- A gate node has produced verdict `ready`
- A milestone node has been achieved

## DAG Vocabulary
- 4 node types: task, gate, decision, milestone
- 6 edge types: depends_on, produces, validates, constrained_by, informed_by, triggered_by
- Pass lifecycle: passes are created, executed, and frozen within a single DAG
```

### Structural Lifecycle Rules

These replace the procedural recipes in the old `specify.md`. Written in DAG vocabulary, no domain knowledge:

1. **When a gate verdict is `needs-revision`**: Tell the Assembler to freeze the current pass and create a new one. Return to asking the Analyst for recommendations.
2. **When a gate verdict is `ready`**: Tell the Assembler to assemble the appropriate milestone node. Tell the Assembler to update-status the milestone to `achieved`. Tell the Assembler to freeze the pass. Go to completion.
3. **When a gate verdict is `critical-gaps`**: Present the situation to the user with options (continue, accept, stop).
4. **When a parse-and-recommend summary contains `unresolved` items requiring user input**: Tell the Assembler to assemble the appropriate decision node. Collect user input via AskUserQuestion. Tell the Assembler to update-status the decision node to `decided`. Continue with the Analyst's recommendation.
5. **When convergence stalls (same gap count across 2+ passes)**: Surface to the user — do not silently continue.
6. **When 5 passes are reached without a `ready` verdict**: Surface to the user with options.
7. **When an unexpected situation occurs**: Tell the Assembler to freeze the pass as `halted`. Present to the user.

### Captain's Call Signals

The Supervisor exercises judgment based on structural signals, not domain knowledge:

- **Outcome trajectory**: gaps shrinking across passes → convergence. Flat or growing → stall.
- **DAG shape**: node type/status counts — "2 tasks completed, 1 gate needs-revision, 1 decision pending"
- **Recommendation rationale**: the State Analyst explains *why* it recommends each next step. The Supervisor evaluates the reasoning without needing domain knowledge.
- **Alternative nodes**: the State Analyst provides ranked alternatives so the Supervisor can pick differently.

---

## State Analyst

**Model**: Opus — expanded synthesis and recommendation responsibilities justify the capability.

### Actions

#### `briefing` (cold start — once per pass)

Called at the start of each pass. Reads catalog, strategy skills, artifacts, and the single DAG file. Produces:

| Field | Description |
|---|---|
| `state_summary` | Current DAG shape — node type/status counts, artifact inventory |
| `outcome_trajectory` | Convergence signal across passes (e.g., "gaps: 7 → 5 → 3") |
| `recommendations` | Ranked list of recommended next nodes, each with: intent, capability tags, rationale, priority |
| `alternatives` | Other viable nodes not in the primary recommendation |
| `relevant_patterns` | Heuristics from strategy skills that apply to current state |
| `pass_context` | Any convergence concerns, recurring gap detection |

Both `briefing` and `parse-and-recommend` share the same recommendation structure — the Supervisor sees a consistent format regardless of which action produced it.

#### `parse-and-recommend` (per agent node — after each domain agent execution)

Replaces the v2 `parse-report` action. Reads the domain agent's report from disk, extracts structured data, writes to the DAG via `hil-dag record`, and produces the next recommendation. Combines what were two separate round-trips (parse + brief) into one.

| Field | Description |
|---|---|
| `node_id` | Which node was executed |
| `status` | Extracted status for the node |
| `summary` | Brief summary of what the agent produced |
| `verdict` | For gate nodes: the gate's judgment (ready/needs-revision/critical-gaps) |
| `evidence` | Evidence entries to record |
| `trace` | Execution trace data (timestamps, duration, agent summary) |
| `gaps_addressed` | Gaps resolved by this execution |
| `gaps_found` | New gaps discovered |
| `unresolved` | Items requiring user input (triggers decision node assembly) |
| `recommendations` | Ranked list of recommended next nodes (same structure as briefing) |

The State Analyst writes to the DAG via `hil-dag record --node <id> --pass <n> --status <status> --evidence '<json>' --trace '<json>' <dag_path>`. The CLI targets the current pass's history entry within the node.

### What the State Analyst Does NOT Do

- Does not assemble nodes or edges (DAG Assembler's job)
- Does not construct NL prompts for domain agents (DAG Assembler's job)
- Does not make assembly decisions (Supervisor's job)
- Does not interact with users (Supervisor's job)

### On-Demand Re-briefing

The Supervisor may request a full `briefing` mid-pass if a `parse-and-recommend` result is insufficient or confusing. This is the escape valve — the Supervisor always has the option to ask for a fresh situational assessment.

---

## DAG Assembler

**Model**: Sonnet — mechanical work, no deep synthesis required.

### Actions

#### `assemble-and-prepare`

Receives intent from the Supervisor (passed through from the State Analyst's recommendation). Resolves intent to a catalog node, adds or re-opens the node in the DAG, and constructs the NL prompt for the domain agent.

**Input**: The State Analyst's recommendation object containing intent, capability tags, and rationale. The Supervisor passes this through without modification.

**Intent Resolution** (two-tier):
1. **Capability tag match** (primary): Match the recommendation's capability tags against catalog nodes' `capabilities` arrays. If exactly one node matches, resolve to it.
2. **Semantic description match** (fallback): If multiple or no capability matches, use the catalog nodes' `description` fields and the recommendation's intent to pick the best match.

**Node Add vs. Re-open**:
- If the resolved catalog node does **not** exist in the DAG: add the node, infer structural edges from `consumes/produces` contracts, create the first history entry for the current pass.
- If the resolved catalog node **already** exists in the DAG: re-open it by adding a new history entry for the current pass. Do NOT re-infer structural edges (they persist from prior assembly). Do NOT duplicate the node.

**Invariant Auto-Resolution**:
When assembling a node, the Assembler checks invariants. If a prerequisite is missing (e.g., INV-002 requires constitution-gate before task nodes), the Assembler auto-adds the prerequisite. For gates marked `carry_forward: true` in the catalog, the Assembler checks prior pass history — if the gate passed in any prior pass, it auto-adds the node with a `passed` status in the current pass. On pass 1, where no prior pass history exists, the mechanism auto-resolves the gate with `passed` status — trusting that the Supervisor's workflow has already verified the external prerequisite (e.g., constitution file exists on disk). The Supervisor never knows this happened.

**Output**: `{valid, agent_type, agent_prompt, node_id}` or `{invalid, reason}`.

#### `freeze-pass`

Freezes the current pass and optionally creates the next one.

**Freeze operations** (atomic):
1. Set `frozen: true` on all current-pass history entries across all nodes
2. Update the current pass entry in the `passes` array: set `outcome`, `detail`, `completed_at`, `frozen: true`
3. Add `triggered_by` edges: for each node that will re-execute in the next pass, create a `triggered_by` edge from the gate node whose verdict triggered the new pass to the re-executing node. The `reason` field comes from the Supervisor's freeze request (which carries the verdict summary from the State Analyst).
4. If the Supervisor indicates continuation: create the next pass entry in the `passes` array with `pass` number and `created_at`

**DAG Bootstrap**: On the very first `assemble-and-prepare` call for a workflow, if no DAG file exists, the Assembler creates it. No separate "create DAG" action needed. The Supervisor never calls `hil-dag create` directly.

#### `update-status`

Updates the status of supervisor-owned nodes (decision, milestone, deterministic gate) that have no domain agent to drive their lifecycle. Added post-synthesis to address Dry Run 2 divergence D3: the original two-action design assumed all nodes had backing agents, but decision nodes, milestones, and deterministic gates require the Supervisor to relay status changes through the Assembler.

**Input**: `{node_id, status, verdict (optional, gates only), pass_number}`

**Node type routing**:
- **Decision nodes**: Supervisor collects user input via AskUserQuestion, then tells the Assembler to set status to `decided`.
- **Milestone nodes**: Assembler verifies all prerequisite nodes are complete before setting status to `achieved`. Prerequisite edges are `depends_on` and `validates` — these are the only edge types that imply execution ordering. Other edge types (`produces`, `constrained_by`, `informed_by`, `triggered_by`) represent data flow or metadata and are not treated as prerequisites. Returns `{invalid, reason}` if prerequisites are not met.
- **Deterministic gates**: Assembler evaluates the gate condition (e.g., file existence check) and sets both `status` and `verdict`.

**Output**: `{valid, node_id, new_status}` or `{invalid, reason}`.

**Mechanism**: Calls `hil-dag status` to update the current pass's history entry. Auto-computes derived fields.

### What the DAG Assembler Does NOT Do

- Does not read strategy skills (State Analyst's job)
- Does not read domain agent reports (State Analyst's job)
- Does not evaluate artifact quality (State Analyst's job)
- Does not make recommendations about what to do next (State Analyst's job)
- Does not interact with users (Supervisor's job)

---

## Single-DAG Iteration Model

### Core Principles

1. **One file per workflow invocation** — the entire story in one place
2. **Nodes accumulate history** — each pass adds a new history entry, never modifies prior entries
3. **Structural edges persist** — created once at first assembly, not recreated per pass
4. **Revision edges are explicit** — `triggered_by` captures why a node re-executed
5. **Pass-entry immutability** — frozen entries cannot be modified; enforced by `hil-dag` CLI

### DAG Schema

```json
{
  "id": "specify-{feature-id}",
  "workflow_id": "specify",
  "schema_version": "3.0.0",
  "current_pass": 5,
  "status": "completed",
  "created_at": "2026-02-18T18:54:51Z",
  "completed_at": "2026-02-18T20:01:32Z",

  "passes": [
    {"pass": 1, "outcome": "completed", "detail": "needs-revision",
     "created_at": "...", "completed_at": "...", "frozen": true},
    {"pass": 5, "outcome": "completed", "detail": "ready",
     "created_at": "...", "completed_at": "...", "frozen": true}
  ],

  "nodes": [
    {
      "id": "analyst-review",
      "type": "task",
      "status": "completed",
      "last_active_pass": 5,
      "history": [
        {
          "pass": 1, "status": "completed", "frozen": true,
          "evidence": [{"id": "EV-analyst-review-001-1", "type": "analyst-report",
                         "description": "...", "reference": "..."}],
          "trace": {"started_at": "...", "completed_at": "...",
                    "duration_ms": 186000, "agent_summary": "..."}
        },
        {
          "pass": 5, "status": "completed", "frozen": true,
          "evidence": [{"id": "EV-analyst-review-005-1", "...": "..."}],
          "trace": {"...": "..."}
        }
      ]
    },
    {
      "id": "advocate-review",
      "type": "gate",
      "status": "completed",
      "verdict": "ready",
      "last_active_pass": 5,
      "history": [
        {
          "pass": 1, "status": "completed", "verdict": "needs-revision",
          "frozen": true,
          "evidence": [{"id": "EV-advocate-review-001-1", "...": "..."}],
          "trace": {"...": "..."}
        },
        {
          "pass": 5, "status": "completed", "verdict": "ready",
          "frozen": true,
          "evidence": [{"id": "EV-advocate-review-005-1", "...": "..."}],
          "trace": {"...": "..."}
        }
      ]
    }
  ],

  "edges": [
    {"id": "E-001", "source": "constitution-gate", "target": "analyst-review",
     "type": "depends_on"},
    {"id": "E-002", "source": "analyst-review", "target": "advocate-review",
     "type": "validates"},

    {"id": "E-T01", "source": "advocate-review", "target": "analyst-review",
     "type": "triggered_by", "source_pass": 1, "target_pass": 2,
     "reason": "needs-revision, 7 important gaps"}
  ]
}
```

### Derived Fields

These fields are computed by the `hil-dag` CLI, not set independently:

| Field | Derivation Rule |
|---|---|
| Node `status` | Always equals the status from the most recent history entry |
| Node `verdict` | (Gates only) Always equals the verdict from the most recent history entry |
| Node `last_active_pass` | Always equals the pass number of the most recent history entry |

The `hil-dag record` command updates the history entry and automatically recomputes these top-level fields.

### Gate Status vs. Verdict

Gates have both `status` and `verdict` to separate lifecycle from judgment:

| Field | Meaning | Example |
|---|---|---|
| `status` | Lifecycle — did the gate complete its evaluation? | `completed` |
| `verdict` | Judgment — what did the gate decide? | `ready`, `needs-revision`, `critical-gaps` |

A gate with `status: "completed"` and `verdict: "needs-revision"` means "the gate ran successfully and its judgment is that revisions are needed." The Supervisor cares about `verdict` for decision-making.

### 6 Edge Types

| Edge Type | Created By | When | Topological Sort | Extra Fields |
|---|---|---|---|---|
| `depends_on` | DAG Assembler | First node assembly | Yes | — |
| `produces` | DAG Assembler | First node assembly | No | — |
| `validates` | DAG Assembler | First node assembly | No | — |
| `constrained_by` | DAG Assembler | First node assembly | No | — |
| `informed_by` | DAG Assembler | First node assembly | No | — |
| `triggered_by` | DAG Assembler | Pass transition (inside `freeze-pass`) | No | `source_pass`, `target_pass`, `reason` |

### Immutability Rules

1. History entries with `frozen: true` cannot be modified by any `hil-dag` command
2. Pass entries in the `passes` array with `frozen: true` cannot be modified
3. Only the current pass's history entries are mutable
4. When a pass freezes, all its entries across all nodes are frozen atomically
5. The `hil-dag` CLI is the single write gate — agents never write JSON directly

---

## Node Catalog

### Schema Extensions

Two new fields added to the catalog schema:

```json
{
  "node_id": "analyst-review",
  "type": "task",
  "name": "Requirements Analysis",
  "description": "Produce specification with user stories and functional requirements",
  "capabilities": ["requirements-analysis", "specification-production"],
  "agent_type": "humaninloop:requirements-analyst",
  "consumes": ["enriched-input OR raw-input", "constitution.md"],
  "produces": ["spec.md", "analyst-report.md"],
  "valid_statuses": ["pending", "in-progress", "completed"]
}
```

```json
{
  "node_id": "constitution-gate",
  "type": "gate",
  "name": "Constitution Check",
  "description": "Verify project constitution exists and is accessible",
  "capabilities": ["constitution-verification"],
  "carry_forward": true,
  "gate_type": "deterministic",
  "consumes": ["constitution.md"],
  "valid_statuses": ["pending", "passed", "failed"]
}
```

| New Field | Type | Scope | Purpose |
|---|---|---|---|
| `capabilities` | `string[]` | All nodes | Intent resolution — DAG Assembler matches State Analyst recommendations against these tags |
| `carry_forward` | `boolean` | Gates only | When `true`, a gate that passed in any prior pass is auto-resolved as `passed` in subsequent passes during invariant auto-resolution |

`carry_forward` lives in the catalog only (single source of truth). It does not appear on DAG node instances.

---

## Strategy Skills

No structural changes. Strategy skills remain heuristic guidance consumed exclusively by the State Analyst:

- **`strategy-core`**: Universal workflow patterns — validation loops, gap classification, convergence detection, halt escalation
- **`strategy-specification`**: Specify-specific patterns — input assessment, produce-then-validate, gap-informed revision, enrichment heuristics

The State Analyst **recommends** based on strategy skill heuristics. This is an intentional change from the v2 State Briefer, which presented options without recommending. The shift reflects the State Analyst's expanded role as the domain-aware recommender.

---

## Invariants

The system invariants from the original design carry forward with updated semantics for the single-DAG model:

| Invariant | Rule | Single-DAG Semantics |
|---|---|---|
| **INV-001** | Every task node output must pass through a gate node before being treated as complete | Per-pass: every task node execution in the current pass must have a corresponding gate evaluation in the same pass. The structural `validates` edge exists once; the gate re-executes each pass the task re-executes. |
| **INV-002** | Constitution must exist and be accessible before any specification work | Enforced via invariant auto-resolution. The `carry_forward` mechanism ensures constitution-gate is present and passed in every pass without manual re-addition. |
| **INV-003** | A `validates` edge must connect to a gate node, not a task node | Unchanged — enforced at assembly time by the DAG Assembler. |
| **INV-004** | Maximum 5 passes per workflow invocation before mandatory human checkpoint | **Structural invariant**, not advisory. The DAG Assembler refuses to create pass 6 in `freeze-pass`. The Supervisor surfaces the situation to the user, who may authorize continuation. |

---

## Per-Node Protocol

```
SUPERVISOR                STATE ANALYST           DAG ASSEMBLER          DOMAIN AGENT
    │                          │                      │                      │
    │                    [PASS START]                  │                      │
    │── briefing ────────────>│                       │                      │
    │                         │ reads: catalog,       │                      │
    │                         │ strategy, artifacts,  │                      │
    │                         │ single DAG file       │                      │
    │<── ranked recommendations + rationale ─────│    │                      │
    │                          │                      │                      │
    │ PICKS recommendation     │                      │                      │
    │                          │                      │                      │
    │── assemble (recommendation obj) ────────────>  │                      │
    │                          │                      │ resolves intent,     │
    │                          │                      │ adds/re-opens node,  │
    │                          │                      │ auto-resolves        │
    │                          │                      │ invariants,          │
    │                          │                      │ builds NL prompt     │
    │<── {valid, agent_prompt} ───────────────────── │                      │
    │                          │                      │                      │
    │── dispatch with NL prompt ──────────────────────────────────────────>│
    │                          │                      │    writes report     │
    │<── brief status ────────────────────────────────────────────────────│
    │                          │                      │                      │
    │── parse-and-recommend ──>│                      │                      │
    │                          │ reads report,        │                      │
    │                          │ writes history entry  │                      │
    │                          │ via hil-dag record,  │                      │
    │                          │ synthesizes next     │                      │
    │                          │ recommendation       │                      │
    │<── summary + ranked recommendations ───────│   │                      │
    │                          │                      │                      │
    │ EVALUATES + PICKS next   │                      │                      │
    │                          │                      │                      │
    │              [SUPERVISOR-OWNED NODES: decision, milestone, det. gate]  │
    │                          │                      │                      │
    │── update-status (node_id, status) ─────────────>│                      │
    │                          │                      │ validates + updates   │
    │                          │                      │ via hil-dag status   │
    │<── {valid, new_status} ──────────────────────── │                      │
```

### Call Counts (typical 3-node pass)

| Phase | State Analyst | DAG Assembler | Domain Agent | Supervisor Decisions |
|---|---|---|---|---|
| Pass start | 1 (briefing) | 0 | 0 | 1 (pick from recommendations) |
| Per node | 1 (parse-and-recommend) | 1 (assemble-and-prepare) | 1 | 2 (pick + evaluate) |
| Pass end | 0 | 1 (freeze-pass) | 0 | 1 (done/new/halt) |

**Total**: 1 briefing + 3 parse-and-recommend + 3 assemblies + 1 freeze + 3 domain agents = **11 subagent calls, 8 Supervisor decisions**.

---

## Responsibility Boundaries

| Operation | Owner | Mechanism |
|-----------|-------|-----------|
| Pick from recommendations | Supervisor | Judgment based on briefing + trajectory signals |
| Dispatch domain agents | Supervisor | Task tool with NL prompt from Assembler |
| Collect human input (decision nodes) | Supervisor | AskUserQuestion, then passes input for status update |
| Watch convergence / captain's calls | Supervisor | Outcome trajectory from Analyst summaries |
| Cold-start recommendation | State Analyst | `briefing` action |
| Post-agent recommendation | State Analyst | `parse-and-recommend` action |
| Read domain agent reports | State Analyst | Inside `parse-and-recommend` (reads from disk) |
| Write node history entries | State Analyst | `hil-dag record --pass <n>` (targets current pass entry) |
| On-demand re-briefing | State Analyst | `briefing` action (Supervisor may request mid-pass) |
| Resolve intent to catalog node | DAG Assembler | Capability tag match + semantic fallback |
| Add or re-open nodes | DAG Assembler | `assemble-and-prepare` (checks node existence) |
| Infer edges (new nodes only) | DAG Assembler | `assemble-and-prepare` (skips for re-opened nodes) |
| Auto-resolve invariant prerequisites | DAG Assembler | Invariant enforcement with `carry_forward` |
| Construct NL prompts | DAG Assembler | NL Prompt Construction Patterns |
| Freeze pass + create next pass | DAG Assembler | `freeze-pass` action (atomic) |
| Create `triggered_by` edges | DAG Assembler | Inside `freeze-pass` (reason from Supervisor request) |
| Bootstrap DAG file | DAG Assembler | Auto-create on first `assemble-and-prepare` if no file exists |
| Update decision node status | DAG Assembler | `update-status` action — Supervisor relays user input, Assembler sets `decided` via `hil-dag status` |
| Update milestone node status | DAG Assembler | `update-status` action — Assembler verifies prerequisites met, sets `achieved` via `hil-dag status` |
| Update deterministic gate status | DAG Assembler | `update-status` action — Assembler evaluates gate condition, sets status + verdict via `hil-dag status` |
| Enforce entry-level immutability | `hil-dag` CLI | Refuses writes to frozen history entries |
| Generate evidence IDs | `hil-dag` CLI | Auto-generated: `EV-{node_id}-{pass}-{sequence}` |
| Compute derived fields | `hil-dag` CLI | Node `status`, `verdict`, `last_active_pass` derived from latest history entry |

---

## `hil-dag` CLI Changes

### Updated Commands

| Command | V2 Behavior | V3 Behavior |
|---|---|---|
| `hil-dag create` | Creates new DAG file per pass | **Removed** — DAG Assembler auto-creates on first assembly |
| `hil-dag assemble` | Adds node to DAG | Adds new node OR re-opens existing node with new history entry. Auto-resolves invariant prerequisites with `carry_forward`. |
| `hil-dag record` | Writes flat evidence/trace/status to node | Writes to current pass's history entry within node. Accepts `--pass <n>` parameter. Auto-computes derived top-level fields. |
| `hil-dag freeze` | Freezes entire DAG file | Freezes all current-pass entries atomically. Updates pass metadata. Optionally creates next pass entry. |
| `hil-dag status` | Sets node status directly | Sets status in current pass's history entry. Auto-computes derived fields. |

### New Capabilities

- **Entry-level immutability enforcement**: All write commands check `frozen` flag on target entries
- **Derived field computation**: `record` and `status` commands auto-update top-level `status`, `verdict`, `last_active_pass`
- **Evidence ID generation**: `record` command auto-generates IDs using `EV-{node_id}-{pass}-{sequence}`
- **`triggered_by` edge creation**: `freeze` command accepts `--triggered-nodes` and `--reason` to create revision edges
- **DAG bootstrap**: `assemble` command auto-creates DAG file if it doesn't exist

---

## Clashes Identified and Resolved

During synthesis of the three v3 documents, 20 clashes were identified. All breaking issues are resolved in this document:

| # | Clash | Resolution |
|---|---|---|
| **3** | DAG bootstrap — who creates the initial file? | DAG Assembler auto-creates on first `assemble-and-prepare`. No `hil-dag create` needed. |
| **4** | `triggered_by` edges have no assigned owner | DAG Assembler creates them inside `freeze-pass`. Reason comes from State Analyst via Supervisor. |
| **5** | `hil-dag record` incompatible with single-DAG history | `hil-dag record` accepts `--pass <n>` and targets the current pass's history entry. |
| **9** | Decision/milestone nodes have no status-update path | Resolved by adding `update-status` as a third DAG Assembler action. Decision: Supervisor collects input, tells Assembler to update-status. Milestone: Assembler verifies prerequisites, sets `achieved`. Deterministic gates: Assembler evaluates condition, sets status + verdict. (Dry Run 2 divergence D3 fix.) |
| **10** | `assemble-and-prepare` doesn't handle re-opening existing nodes | Assembler checks node existence — adds if new, re-opens (new history entry) if existing. |
| 1 | Briefing recommendation depth ambiguity | Both `briefing` and `parse-and-recommend` share the same recommendation structure. |
| 2 | `freeze-pass` scope undecided | `freeze-pass` atomically freezes current pass and optionally creates next pass. |
| 6 | Node status derivation ambiguous | Top-level `status` is derived — always equals latest history entry. CLI computes automatically. |
| 7 | Node `current_pass` naming ambiguous | Renamed to `last_active_pass`. Equals pass number of most recent history entry. |
| 8 | "Same call count as v2" claim is wrong | Corrected: same subagent call count (11), one additional Supervisor decision (8 vs 7). |
| 11 | Edge inference for re-opened nodes would duplicate | Edge inference skipped for re-opened nodes. Only new nodes get edges inferred. |
| 12 | `carry_forward` location ambiguous | Catalog-only. Not duplicated on DAG node instances. |
| 13 | `verdict` vs `status` redundancy for gates | `status` = lifecycle (completed), `verdict` = judgment (ready/needs-revision). Both tracked. |
| 15 | Doc 1 recommends `initialize-pass`; Doc 2 rejects it | Resolved: invariant auto-resolution, no `initialize-pass` action. |

### Original Design Decisions Carried Forward

| Original Decision | V3 Status |
|---|---|
| 4 node types (task, gate, decision, milestone) | Carried forward unchanged |
| Catalog-with-constraints model | Carried forward — "assembly" now means add-or-re-open in single DAG |
| Incremental assembly | Carried forward — now intent-based (State Analyst recommends, Assembler resolves) instead of node-ID-based |
| ADR-005 compatibility | Preserved — domain agents still speak natural language |
| Strategy skills concept | Carried forward — consumed by State Analyst exclusively |
| Progressive summarization | **Superseded** — single DAG file replaces multi-file history. For current scope (5-pass workflows), file size is manageable. |

### Original Design Decisions Explicitly Changed

| Original Decision | V3 Change | Rationale |
|---|---|---|
| DAG-per-pass versioning | Single DAG with node history | Eliminates redundancy, preserves continuity, tells complete story in one place |
| 5 edge types | 6 edge types (`triggered_by` added) | Explicit causal chains for revision tracking |
| Supervisor uses `hil-dag create` | Supervisor has zero CLI usage | Pure dispatcher — all mechanics delegated |
| State Briefer "never recommends" | State Analyst recommends with ranked shortlist | Supervisor is domain-agnostic; needs recommendations to function |
| Separate `parse-report` and `briefing` | Merged `parse-and-recommend` | Reduces round-trips; Analyst already has full context after parsing |

---

## Risks

- **State Analyst as single point of recommendation quality**: Bad synthesis of catalog + strategy + state produces bad recommendations with limited Supervisor backstop. Mitigated by: invariant enforcement (structural errors caught), parse-report summaries (outcome signals), recommendation rationale (reasoning chain for captain's calls).
- **Single DAG file corruption**: Loses entire workflow history vs. one pass in DAG-per-pass. Mitigated by: atomic write-validate-swap in `hil-dag` CLI, backup before writes.
- **Intent resolution ambiguity**: Vague intent from State Analyst may resolve to wrong catalog node. Mitigated by: capability tags for deterministic common path, semantic fallback for edge cases, shared capability vocabulary.
- **Opus cost**: State Analyst on Opus with expanded responsibilities is expensive per call. Mitigated by: merged `parse-and-recommend` keeps total call count same as v2 despite richer output.
- **Schema migration**: Existing `humaninloop_brain` Pydantic models and 190+ tests assume DAG-per-pass. Schema 3.0.0 requires model redesign and test rewrite. Mitigated by: pre-production architecture change, 90% coverage gate still applies to new models.

---

## Recommended Next Steps

1. **Design the V3 Pydantic models**: Redesign `StrategyGraph`, `GraphNode`, `Edge` models for single-DAG with node history, entry-level freezing, `triggered_by` edges, derived fields. Follow context harness pattern of frozen Pydantic models with model validators.

2. **Redesign the `hil-dag` CLI**: Update all commands for single-DAG semantics. Key changes: `assemble` handles add/re-open + invariant auto-resolution + DAG bootstrap, `record` targets pass-specific history entries, `freeze` handles atomic pass freezing + next-pass creation + `triggered_by` edge creation.

3. **Define the capability vocabulary**: Tag all catalog nodes with capability arrays. Validate that State Analyst intent language resolves unambiguously via capability match.

4. **Design the State Analyst output schemas**: Concrete field-level schemas for `briefing` and `parse-and-recommend` responses, sharing a common recommendation structure.

5. **Rewrite `specify.md` as a goal declaration**: Strip all node IDs, agent names, procedural sequences. Replace with structural lifecycle rules in DAG vocabulary. Target: under 100 lines.

6. **Update agent definitions**: Expand State Analyst definition for `parse-and-recommend` and ranked recommendations. Update DAG Assembler for intent resolution, node re-open, `triggered_by` edges, and DAG bootstrap.

7. **Prototype and dry run**: Hand-write the single-DAG JSON for the "storing memories" workflow. Execute `/specify` with the redesigned architecture to validate.
