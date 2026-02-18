# State Analyst & DAG Assembler Redesign — Analysis Synthesis

> **Evolves**: [`dag-specialist-subagents-v2-synthesis.md`](../dag-specialist-subagents-v2-synthesis.md)
>
> **Depends on**: [`goal-oriented-supervisor-synthesis.md`](goal-oriented-supervisor-synthesis.md)
>
> **Related**: [`dag-first-execution-synthesis.md`](../dag-first-execution-synthesis.md), [`dag-strategy-skills-synthesis.md`](../dag-strategy-skills-synthesis.md)

## Problem Statement

The goal-oriented Supervisor redesign removes all domain knowledge from the Supervisor — no node IDs, no agent types, no strategy patterns. This shifts significant responsibility to the State Analyst and DAG Assembler. The State Analyst must become the domain-aware recommender that synthesizes catalog, strategy skills, artifacts, and history into actionable recommendations. The DAG Assembler must resolve abstract intent into concrete catalog nodes and handle all pass lifecycle mechanics. Strategy skills and the catalog need targeted extensions to support these expanded roles. This synthesis defines the new responsibility boundaries, action surfaces, and schema changes.

## Context & Constraints

- **Goal-oriented Supervisor**: The Supervisor speaks only DAG vocabulary (node types, pass lifecycle, gate verdicts). It passes intent through without knowing what specific nodes or agents fulfill it. See `goal-oriented-supervisor-synthesis.md`.
- **State Analyst on Opus**: Moving to Opus to handle expanded synthesis and recommendation responsibilities. Each call should do more work to justify the model cost and reduce round-trips.
- **DAG Assembler stays mechanical**: The Assembler resolves, builds, and validates — it doesn't judge. Its expanded role (intent resolution, invariant auto-resolution) is mapping and enforcement, not heuristic reasoning.
- **Existing infrastructure**: `hil-dag` CLI, catalog schema, strategy skills, invariant system all remain as infrastructure. This redesign changes what the agents do with them.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| State Analyst actions | Two actions: `briefing` (cold start per pass) and `parse-and-recommend` (merged parse-report + recommendation per agent node) | Confident | Eliminates separate mid-pass briefings. After parsing a report, the Analyst already has full context to recommend the next move. Reduces round-trips without losing quality. |
| State Analyst model | Opus | Confident | Expanded role requires deeper synthesis of catalog + strategy skills + artifacts + history into ranked recommendations with rationale. Opus handles this complexity per call. |
| DAG Assembler intent resolution | Capability-tag match (primary) with semantic description fallback | Confident | Primary path is deterministic — capability tags on catalog nodes matched against intent from State Analyst. Semantic fallback handles edge cases and new nodes without full tagging. Keeps common path mechanical. |
| DAG Assembler invariant auto-resolution | Auto-add prerequisite nodes when invariants require them, using `carry-forward` catalog property for gates verified in prior passes | Confident | Supervisor doesn't know pass setup is a concept. Assembler handles it during normal assembly. `carry-forward` generalizes beyond constitution-gate to any one-time verification gate. |
| DAG Assembler pass lifecycle | Assembler owns all pass mechanics — creation, structural setup, freezing. Supervisor has zero direct CLI usage. | Confident | Clean end state: Supervisor is a pure dispatcher with three verbs — ask Analyst, tell Assembler, dispatch agent. No procedural knowledge about pass mechanics. |
| Strategy skills nature | Heuristic guidance, not structured rules | Confident | If strategy skills become prescriptive rules, the State Analyst becomes a recipe-follower — same problem we're fixing in the Supervisor. Skills read like advice from an experienced practitioner; the Analyst synthesizes and applies judgment. |
| Catalog schema changes | Add `capabilities` tags (intent resolution) and `carry-forward` property (gate persistence). No sequencing hints. | Confident | Minimal additions. `consumes/produces` contracts already imply sequencing — adding explicit hints would duplicate and create maintenance burden. |
| Recommendation language | State Analyst recommends in intent/capability language, not node IDs | Confident | Keeps the Supervisor domain-agnostic. DAG Assembler resolves intent to catalog nodes. Clean separation: Analyst says what should happen, Assembler figures out which node does it. |

## Decision Trail

### Parse-report and recommendation: Separate vs. merged

- **Options considered**: (A) Keep `parse-report` mechanical and add recommendation logic to `briefing`, (B) Merge recommendation into `parse-report` so every parse call also produces the next recommendation
- **Chosen**: Option B — merged `parse-and-recommend`
- **Key reasoning**: After parsing an agent's report, the State Analyst has full context — it just read the report, knows the current DAG state, has the catalog and strategy skills. Producing a recommendation at that point is a natural extension, not a separate synthesis effort. A standalone `briefing` for recommendation would re-read everything the parse already processed. With Opus handling each call, heavier-per-call is better than more-calls.

### Intent resolution: Capability tags vs. semantic matching vs. both

- **Options considered**: (A) Capability tags only — deterministic lookup, (B) Semantic description matching only — flexible but LLM-dependent, (C) Both — capability tags as primary, semantic fallback
- **Chosen**: Option C — layered resolution
- **Key reasoning**: Capability tags keep the common path deterministic and fast. Semantic fallback handles edge cases (new nodes not fully tagged, fuzzy intent from Analyst). The DAG Assembler tries capability match first; if exactly one node matches, done. If multiple or none, falls back to semantic matching against descriptions.

### New-pass setup: Explicit `initialize-pass` action vs. invariant auto-resolution

- **Options considered**: (A) New `initialize-pass` action the Supervisor calls at pass start, (B) Invariant-driven auto-resolution — Assembler adds prerequisites automatically during first assembly in a new pass
- **Recommendation was**: Option B
- **Chosen**: Option B — invariant auto-resolution
- **Key reasoning**: An explicit `initialize-pass` is procedural knowledge in the Supervisor — "when creating a new pass, call initialize-pass." That's a recipe step. Invariant auto-resolution means the Supervisor says "assemble the next node" and the Assembler handles everything. If the pass is empty and invariants require constitution-gate, the Assembler adds it automatically. The Supervisor doesn't know pass initialization is a concept. `carry-forward` as a catalog property generalizes this beyond constitution-gate — any one-time verification gate auto-resolves in subsequent passes.

### Strategy skills: Heuristic guidance vs. structured rules

- **Options considered**: (A) Keep as heuristic guidance — "when input is sparse, consider enrichment", (B) Make more structured — "if input lacks Who/Problem/Value, recommend input-enrichment with priority high"
- **Chosen**: Option A — heuristic guidance
- **Key reasoning**: Structured rules would move the recipe from the Supervisor to the State Analyst. The Analyst's value is synthesis and judgment, not rule execution. Strategy skills read like advice from an experienced practitioner; the Analyst internalizes the advice and applies it to the specific situation using catalog contracts and artifact state.

### Catalog sequencing hints: Add vs. skip

- **Options considered**: (A) Add `typical_predecessors` field to encode common node sequencing, (B) Rely on existing `consumes/produces` contracts
- **Chosen**: Option B — skip sequencing hints
- **Key reasoning**: Over-engineering. If advocate-review consumes spec.md and analyst-review produces spec.md, the sequencing is obvious from the contracts. Explicit hints duplicate what's inferrable and create maintenance burden when contracts change.

## Architecture Overview

### Updated Three-Tier Agent Model

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: SUPERVISOR                                               │
│                                                                   │
│ Knows:    DAG vocabulary (4 node types, pass lifecycle,          │
│           gate verdicts). Goal criteria.                          │
│ Does:     Picks from ranked recommendations, dispatches,         │
│           watches convergence, makes captain's calls             │
│ CLI:      None — pure dispatcher                                 │
│                                                                   │
│ Three verbs:                                                      │
│   1. Ask the Analyst (briefing / parse-and-recommend)            │
│   2. Tell the Assembler (assemble / freeze / create pass)        │
│   3. Dispatch the agent (Task tool with NL prompt)               │
└─────────┬──────────────────────────────────┬─────────────────────┘
          │ structured protocol              │ structured protocol
          ▼                                  ▼
┌──────────────────────────┐   ┌──────────────────────────────────┐
│ TIER 2a:                  │   │ TIER 2b:                          │
│ STATE ANALYST (Opus)      │   │ DAG ASSEMBLER                     │
│                           │   │                                    │
│ Actions:                  │   │ Actions:                           │
│ • briefing                │   │ • assemble-and-prepare            │
│   (cold start per pass)   │   │   - intent → catalog resolution  │
│ • parse-and-recommend     │   │   - invariant auto-resolution    │
│   (per agent node)        │   │   - edge inference               │
│                           │   │   - NL prompt construction       │
│ Reads:                    │   │ • freeze-pass                     │
│ • Node catalog            │   │   - includes pass creation       │
│ • Strategy skills         │   │                                    │
│ • Artifacts on disk       │   │ Reads:                             │
│ • DAG history             │   │ • Node catalog                    │
│                           │   │ • Current DAG                     │
│ Recommends in:            │   │ • Prior pass DAGs (carry-forward) │
│ • Intent language         │   │                                    │
│ • Ranked with rationale   │   │ Resolves via:                      │
│                           │   │ • Capability tag match (primary)  │
│ Writes (via CLI):         │   │ • Semantic description (fallback) │
│ • evidence[]              │   │                                    │
│ • execution_trace[]       │   │ Writes (via CLI):                  │
│ • node status             │   │ • nodes[], edges[]                │
│                           │   │ • pass metadata                   │
└──────────────────────────┘   └──────────────┬───────────────────┘
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
SUPERVISOR                STATE ANALYST           DAG ASSEMBLER          DOMAIN AGENT
    │                          │                      │                      │
    │                    [PASS START]                  │                      │
    │── briefing ────────────>│                       │                      │
    │                         │ reads: catalog,       │                      │
    │                         │ strategy skills,      │                      │
    │                         │ artifacts, history    │                      │
    │<── ranked recommendations with rationale ──│    │                      │
    │                          │                      │                      │
    │ PICKS: recommendation #1 │                      │                      │
    │                          │                      │                      │
    │── assemble (intent) ────────────────────────>  │                      │
    │                          │                      │ resolves intent      │
    │                          │                      │ via capabilities,    │
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
    │                          │ writes evidence +    │                      │
    │                          │ trace + status,      │                      │
    │                          │ synthesizes next     │                      │
    │                          │ recommendation       │                      │
    │<── summary + ranked recommendations ───────│   │                      │
    │                          │                      │                      │
    │ EVALUATES + PICKS next   │                      │                      │
    │ (or: gate ready → freeze)│                      │                      │
```

### Updated Call Counts

| Phase | State Analyst | DAG Assembler | Domain Agent | Supervisor Decisions |
|---|---|---|---|---|
| Pass start | 1 (briefing) | 0 | 0 | 1 (pick from recommendations) |
| Per node | 1 (parse-and-recommend) | 1 (assemble-and-prepare) | 1 | 2 (pick + evaluate) |
| Pass end | 0 | 1 (freeze-pass) | 0 | 1 (done/new/halt) |

**Typical 3-node pass**: 1 briefing + 3 parse-and-recommend + 3 assemblies + 1 freeze + 3 domain agents = **11 subagent calls, 8 Supervisor decisions**. Same call count as v2 but each State Analyst call is richer (recommendation included).

### Catalog Schema Changes

```json
{
  "node_id": "analyst-review",
  "type": "task",
  "name": "Requirements Analysis",
  "description": "Produce specification with user stories and functional requirements",
  "capabilities": ["requirements-analysis", "specification-production"],
  "agent_type": "humaninloop:requirements-analyst",
  "consumes": [...],
  "produces": [...],
  "valid_statuses": [...]
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
  "consumes": [...],
  "valid_statuses": [...]
}
```

New fields:
- **`capabilities`**: Array of capability tags for intent resolution. DAG Assembler matches State Analyst intent against these tags.
- **`carry_forward`**: Boolean (gates only). When `true`, a gate that passed in any prior pass is auto-resolved as `passed` in subsequent passes during invariant auto-resolution.

### Strategy Skills

No structural changes. Strategy skills remain heuristic guidance consumed by the State Analyst:

- **`strategy-core`**: Universal workflow patterns — validation loops, gap classification, convergence detection, halt escalation
- **`strategy-specification`**: Specify-specific patterns — input assessment, produce-then-validate, gap-informed revision, enrichment heuristics

Content may need enrichment to support the State Analyst's expanded recommendation role, but the format and nature stay the same.

### Responsibility Boundaries

| Operation | Owner | Mechanism |
|-----------|-------|-----------|
| Pick from recommendations | Supervisor | Judgment based on briefing data |
| Dispatch domain agents | Supervisor | Task tool with NL prompt from Assembler |
| Watch convergence | Supervisor | Outcome trajectory from Analyst summaries |
| Captain's call overrides | Supervisor | Based on DAG shape + trend signals |
| Cold-start recommendation | State Analyst | `briefing` action — reads catalog, strategy, artifacts, history |
| Post-agent recommendation | State Analyst | `parse-and-recommend` — reads report, writes DAG, recommends next |
| Read domain agent reports | State Analyst | Inside `parse-and-recommend` (reads from disk) |
| Update domain node status | State Analyst | Inside `parse-and-recommend` via `hil-dag record` |
| Populate evidence + trace | State Analyst | Inside `parse-and-recommend` via `hil-dag record` |
| Resolve intent to catalog node | DAG Assembler | Capability tag match (primary) + semantic fallback |
| Auto-resolve invariant prerequisites | DAG Assembler | Invariant enforcement with `carry-forward` for verified gates |
| Create new pass | DAG Assembler | Inside `freeze-pass` or as standalone lifecycle action |
| Construct NL prompts | DAG Assembler | NL Prompt Construction Patterns |
| Freeze pass | DAG Assembler | `freeze-pass` action |
| Update Supervisor-owned node status | DAG Assembler | As part of invariant auto-resolution (e.g., carry-forward gates) |

## Risks

- **Intent resolution ambiguity**: If the State Analyst's intent language is too vague ("do some analysis"), the DAG Assembler may resolve to the wrong catalog node. Capability tags mitigate this for the common path, but semantic fallback introduces LLM judgment into the Assembler. Mitigation: well-defined capability vocabulary shared between State Analyst and catalog. If the Analyst recommends using terms that match capability tags, resolution is deterministic.
- **Opus cost per call**: The State Analyst on Opus with expanded responsibilities (catalog + strategy + artifacts + history synthesis) is expensive per invocation. For a 5-pass, 3-nodes-per-pass workflow, that's 16 Opus calls just for the Analyst. Mitigation: the merged `parse-and-recommend` eliminates separate mid-pass briefings, keeping total call count the same as v2 despite richer per-call output.
- **Strategy skill quality becomes critical**: The State Analyst's recommendation quality depends directly on strategy skill content. Poor heuristics produce poor recommendations, and the Supervisor has no domain knowledge to catch them. Mitigation: strategy skills are versioned files reviewable in PRs. Treat them as first-class artifacts with the same rigor as agent definitions.

## Open Questions

- **Capability vocabulary**: What are the canonical capability tags across all catalog nodes? This vocabulary needs to be consistent enough for deterministic matching but flexible enough for new nodes. Should it be formalized in a schema or emergent from catalog authoring?
- **State Analyst briefing schema**: The enriched briefing (ranked recommendations with rationale, outcome trajectory, DAG shape summary) needs a concrete field-level schema. What exactly does the Supervisor see?
- **`parse-and-recommend` output schema**: The merged action returns both a parse summary (status, evidence, gaps) and recommendations (ranked, with rationale). What's the concrete structure?
- **`freeze-pass` with pass creation**: Should freeze and create-next-pass be a single atomic action, or should the Supervisor explicitly request a new pass after freezing? The former is cleaner but couples two operations.
- **Supervisor-owned node status**: With the Supervisor having zero CLI usage, who updates status for skill nodes, decision nodes, and milestones? Does this move to the DAG Assembler as well, or does the State Analyst handle it inside `parse-and-recommend`?

## Recommended Next Steps

1. **Define the capability vocabulary for the specify catalog**: Tag all 7 nodes in `specify-catalog.json` with capability arrays. Validate that the State Analyst's likely intent language resolves unambiguously to the right nodes via capability match.

2. **Design the `parse-and-recommend` output schema**: Define the concrete fields that the State Analyst returns — parse summary (status, evidence, gaps) plus ranked recommendations (intent, rationale, priority). This is the primary contract between Analyst and Supervisor.

3. **Design the enriched `briefing` output schema**: Define the cold-start briefing fields — outcome trajectory, DAG shape summary, ranked initial recommendations with rationale.

4. **Extend `freeze-pass` to include pass creation**: Design how the DAG Assembler creates a new pass as part of (or immediately after) freezing the current one. Define the invariant auto-resolution flow including `carry-forward` gate handling.

5. **Rewrite `specify.md` as a goal declaration**: With both agent roles now defined, rewrite the Supervisor instructions as structural lifecycle rules in DAG vocabulary — under 100 lines, no node IDs, no agent names.
