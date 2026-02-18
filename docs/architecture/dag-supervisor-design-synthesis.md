# DAG Supervisor Design — Analysis Synthesis

## Problem Statement

The DAG-first execution architecture (see `dag-first-execution-synthesis.md`) establishes that a Supervisor assembles and executes DAGs from a node catalog. This session scopes the Supervisor itself — how it assembles, executes, communicates, and what supporting agents it needs. The Supervisor is the most critical and novel component: an LLM that incrementally builds execution graphs while preserving its context window for judgment-rich decisions.

## Context & Constraints

- **Parent design**: DAG-first execution architecture with catalog-with-constraints model, DAG-per-pass versioning, 4 general node types, 5 expressive edge types (see `dag-first-execution-synthesis.md`)
- **Context window preservation**: The Supervisor's context is its most precious resource. Every byte spent on execution details is a byte not available for DAG reasoning. This is the driving constraint for the entire Supervisor design.
- **ADR-005 compatibility**: Domain agents (analyst, advocate, etc.) follow ADR-005's decoupled natural language protocol. They must remain portable and standalone-invocable. The DAG architecture wraps around them, not through them.
- **Proof-of-concept**: `/specify` workflow with functional parity plus demonstrated flexibility.
- **NetworkX**: Will be used for deterministic DAG components (graph algorithms, invariant validation, topological operations). Implementation details deferred — design-first.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Assembly mode | Incremental — Supervisor assembles node-by-node during execution, adapting based on results. DAG frozen into immutable snapshot when pass completes. | Confident | DAG needs to adapt based on results. Upfront assembly can't predict what the Supervisor will learn mid-pass. |
| Pass boundaries | Gates as primary boundary, Supervisor halt as escape hatch. Two distinct outcomes: "completed" (gate verdict) and "halted" (Supervisor judgment). | Confident | Gates provide predictable, auditable pass endings. Escape hatch preserves Supervisor autonomy for unexpected situations. |
| Agent tiers | Three tiers: Supervisor (decisions) → DAG-ops agents (graph mechanics) → Domain agents (actual work) | Confident | Maps to context harness three-tier model. Preserves Supervisor context by delegating operational weight. |
| DAG-ops agents | 2 agents: State Briefer (history + viable nodes) and DAG Assembler (build + validate + translate). Consolidated from 4 candidates. | Confident | Fewer, fatter subagent calls. 4 round-trips per node is too chatty. 2 combined agents cut round-trips in half while covering all responsibilities. |
| Supervisor decision loop | Per node: DAG Assembler (build + validate) → domain subagent → Supervisor evaluates. State Briefer runs at pass start and on-demand. 2 decisions per node. | Confident | Optimized for minimal context consumption. State Briefer only when needed, not every node. |
| DAG-ops communication | Structured protocol — minimal tokens, precise, parseable. | Confident | DAG-ops work is mechanical and data-heavy. Structured protocol avoids unnecessary natural language overhead. |
| Domain agent communication | Natural language preserved (ADR-005 unchanged). DAG Assembler acts as translation bridge — constructs NL prompts from structured contracts, parses prose reports into structured data. | Confident | Domain agents remain portable and standalone-invocable. Zero migration cost. The structure lives in the infrastructure, not in the agents. |
| Workflow strategy knowledge | Lives in skills — new "strategy skills" distilled from current command files. Commands reference relevant strategy skills in goal declarations. | Confident | Skills are already a first-class concept. Strategy skills separate workflow pattern knowledge from DAG mechanics. Supervisor reads strategy skill for guidance, makes its own assembly decisions. |
| Node catalog for /specify PoC | 7 nodes: 5 core (enrichment, analyst, advocate-gate, human-clarification, spec-complete) + 2 flexibility (targeted-research, constitution-gate) | Confident | Core nodes prove functional parity. Flexibility nodes enable 3 scenarios that demonstrate the architecture's value. |

## Decision Trail

### Assembly mode: Upfront vs. Incremental

- **Options considered**: (A) Full upfront assembly — Supervisor builds entire DAG, hands to deterministic executor. (B) Incremental assembly — Supervisor assembles node-by-node during execution.
- **Recommendation was**: Presented both as a spectrum
- **Chosen**: Incremental (option B)
- **Key reasoning**: "The DAG needs to be adapted based on the results." Upfront assembly forces the Supervisor to predict the entire workflow before seeing any results. Incremental lets it respond to what it learns — skip enrichment after seeing detailed input, add research after seeing knowledge gaps.

### Communication protocol: Structured everywhere vs. Structured + Natural Language

- **Original direction**: Structured protocol for DAG-ops agents, natural language (ADR-005) for domain agents
- **User proposed**: Structured for domain agents too, noting ADR-005 is not a hard constraint going forward
- **Concern raised**: Would structured I/O make domain agents non-portable? Could the analyst still be used outside the workflow?
- **Final decision**: DAG Assembler as translation bridge. DAG-ops speak structured. Domain agents speak natural language. DAG Assembler translates between the two worlds.
- **Key reasoning**: Preserves agent portability (ADR-005) while giving the Supervisor structured data. Zero migration cost for existing agents. Best of both worlds.

### DAG-ops agent count: 4 specialized vs. 2 combined

- **Original proposal**: 4 agents — History Curator, Catalog Scout, DAG Builder, Invariant Checker
- **Recommendation was**: Consolidate to 2 combined agents
- **Chosen**: 2 agents — State Briefer (history + catalog) and DAG Assembler (build + validate + translate)
- **Key reasoning**: 4 subagent round-trips per node is too chatty. Combined agents do meaningful work per call. State Briefer runs on-demand (not every node), further reducing overhead. Also reduces the number of new agent definitions to maintain.

### Workflow strategy: Where knowledge lives

- **Options considered**: (A) Supervisor instructions, (B) State Briefer recommendations, (C) Command goal hints, (D) Emergent from contracts
- **User proposed**: Skills — a new category of strategy skills
- **Chosen**: Strategy skills referenced by commands
- **Key reasoning**: Skills are already first-class in the plugin. They separate knowledge from execution. The analyst references `authoring-requirements` for domain knowledge; the Supervisor references `strategy-specification` for workflow knowledge. Same pattern, different tier. Current 600-line command files get distilled into strategy skills — procedural logic disappears, domain wisdom is preserved.

## Architecture Overview

### Three-Tier Agent Model

```
┌─────────────────────────────────────────────────────────────────┐
│ TIER 1: SUPERVISOR (main conversation thread)                    │
│                                                                  │
│ Role:     Assembly decisions, pass lifecycle, goal evaluation    │
│ Consumes: Structured briefings, structured reports              │
│ Context:  Goal + strategy skills + DAG-ops structured reports   │
│                                                                  │
│ What it does NOT hold in context:                               │
│   - Raw node catalog (State Briefer filters)                    │
│   - Raw DAG history (State Briefer summarizes)                  │
│   - Full agent output (DAG Assembler translates)                │
│   - Invariant registry (DAG Assembler validates)                │
└─────────┬──────────────────────────────────┬────────────────────┘
          │ structured protocol              │ structured protocol
          ▼                                  ▼
┌─────────────────────┐    ┌──────────────────────────────────────┐
│ TIER 2a:            │    │ TIER 2b:                              │
│ STATE BRIEFER       │    │ DAG ASSEMBLER                         │
│                     │    │                                        │
│ Reads:              │    │ Reads:                                 │
│ - DAG history       │    │ - Node catalog                        │
│ - Node catalog      │    │ - Invariant registry                  │
│ - Current artifacts │    │ - Current DAG (in progress)           │
│ - Strategy skills   │    │                                        │
│                     │    │ Does:                                  │
│ Produces:           │    │ - Adds nodes/edges to DAG             │
│ - State summary     │    │ - Validates against invariants        │
│ - Viable nodes      │    │ - Constructs NL prompts for agents    │
│ - Strategy hints    │    │ - Parses prose reports to structured  │
│                     │    │ - Freezes DAG on pass completion      │
└─────────────────────┘    └──────────────┬───────────────────────┘
                                          │ natural language
                                          │ (ADR-005 preserved)
                                          ▼
┌─────────────────────────────────────────────────────────────────┐
│ TIER 3: DOMAIN AGENTS (unchanged from current architecture)      │
│                                                                  │
│ Requirements Analyst | Devil's Advocate | Plan Architect | ...   │
│                                                                  │
│ - Persona-defined, skill-augmented                              │
│ - Read artifacts, produce artifacts + prose reports             │
│ - Portable, standalone-invocable                                │
│ - Zero changes from current agent definitions                   │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Classification

| Category | Agents | Defined By | Protocol | Persistence |
|---|---|---|---|---|
| **Supervisor** | (main thread) | Core DAG mechanics + strategy skills | Structured I/O with DAG-ops | Session-scoped |
| **DAG Operations** | State Briefer, DAG Assembler | Role, inputs, outputs, operational rules | Structured with Supervisor, NL with domain agents | Persistent identity, role-defined |
| **Domain** | Analyst, Advocate, Plan Architect, Task Architect, Technical Analyst, UI Designer, Testing Agent, Principal Architect | Persona, expertise, skills, values | Natural language (ADR-005) | Persistent identity, persona-defined |

### Supervisor Decision Loop

```
┌─ PASS START ────────────────────────────────────────────────────┐
│                                                                  │
│  1. Supervisor → State Briefer:                                 │
│     "Summarize history + viable nodes + strategy guidance"       │
│     ← Structured briefing returned                              │
│                                                                  │
│  2. Supervisor DECIDES: "Start with node X"                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─ NODE CYCLE (repeats) ──────────────────────────────────────────┐
│                                                                  │
│  3. Supervisor → DAG Assembler:                                 │
│     "Add node X with edges [depends_on: Y, informed_by: Z]"    │
│     ← "Node added. DAG valid. Constructed NL prompt for agent." │
│                                                                  │
│  4. Supervisor spawns domain subagent with NL prompt from (3)   │
│                                                                  │
│  5. Domain agent → DAG Assembler (prose report)                 │
│     DAG Assembler → Supervisor (structured summary)             │
│                                                                  │
│  6. Supervisor EVALUATES:                                       │
│     → needs more nodes: DECIDE next node → loop to 3            │
│     → gate completed (ready): freeze DAG → pass complete        │
│     → gate completed (needs-revision): freeze DAG → new pass    │
│     → unexpected situation: HALT → freeze DAG with rationale    │
│     → needs fresh briefing: → go to 1                           │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**Per-node cost**: 1 DAG Assembler call (build + validate + translate) + 1 domain agent call + 1 DAG Assembler call (parse report). Supervisor makes 2 decisions (what to assemble, what to do with result).

**State Briefer**: Runs once at pass start. Re-invoked on-demand when the Supervisor needs a fresh perspective (e.g., after an unexpected result).

### Pass Lifecycle

| Outcome | Trigger | DAG State | Next Action |
|---|---|---|---|
| **Completed: ready** | Gate verdict "ready" | Frozen, all nodes executed | Milestone node → workflow complete |
| **Completed: needs-revision** | Gate verdict "needs-revision" | Frozen, verdict recorded | Supervisor assembles new pass with history |
| **Halted** | Supervisor judgment | Frozen with halt rationale | Supervisor re-evaluates approach, may assemble different pass or escalate to user |

### Strategy Skills (New Concept)

Strategy skills distill workflow pattern knowledge from the current command files. They are referenced by commands in goal declarations and read by the State Briefer to inform Supervisor decisions.

**Example: `strategy-specification`**

```markdown
# Strategy: Specification Workflow

## Typical Flow Pattern
enrich → analyze → validate

## When to Skip Enrichment
- Input already has clear Who/Problem/Value structure
- Input references existing requirements or user research

## When Advocate Rejects
- Knowledge gaps → add targeted-research node before re-analysis
- Scope gaps → add human-checkpoint to narrow scope
- Quality gaps → re-invoke analyst with specific feedback

## When to Halt
- Advocate identifies fundamental feasibility concerns
- Feature scope exceeds single-specification boundary
```

**Command goal declaration references strategy skills:**

```markdown
## Goal
Produce a validated feature specification.

## Success Criteria
- spec.md exists with user stories and functional requirements
- Advocate verdict is "ready"

## Strategy Skills
- strategy-specification

## Initial Context
- Feature description (from user input or arguments)
- Constitution (from .humaninloop/memory/constitution.md)
```

### Node Catalog for /specify PoC

**Core Nodes (functional parity):**

| Node ID | Type | Agent | Consumes | Produces |
|---|---|---|---|---|
| `input-enrichment` | task | (skill-based) | raw user input | enriched input with Who/Problem/Value |
| `analyst-review` | task | requirements-analyst | enriched input or raw input, constitution | spec.md, analyst-report.md |
| `advocate-review` | gate | devils-advocate | spec.md, analyst-report.md | advocate-report.md with verdict |
| `human-clarification` | decision | (user interaction) | advocate gaps (preference-type) | clarification answers |
| `spec-complete` | milestone | (none) | advocate verdict: ready | spec marked complete |

**Flexibility Nodes (demonstrate architecture value):**

| Node ID | Type | Agent | Consumes | Produces |
|---|---|---|---|---|
| `targeted-research` | task | (exploration agent) | specific knowledge gaps from advocate | research findings addressing gaps |
| `constitution-gate` | gate | (deterministic) | constitution.md | pass/fail on constitution existence and currency |

### Flexibility Demonstration Scenarios

**Scenario 1 — Skip enrichment (input-aware assembly):**
User provides detailed input with clear Who/Problem/Value. Supervisor determines enrichment is unnecessary.
```
Current flow:  enrichment → analyst → advocate
DAG-assembled: constitution-gate → analyst → advocate
```

**Scenario 2 — Research instead of asking user (gap-type-aware assembly):**
Advocate rejects with knowledge gaps (e.g., "unclear what auth protocols the existing system uses"). Supervisor adds research node.
```
Current flow:  → ask user for clarification → analyst → advocate
DAG-assembled: → targeted-research → analyst → advocate
```

**Scenario 3 — Direct to user for preference gaps (gap-type discrimination):**
Advocate rejects with preference gaps (e.g., "should notifications be opt-in or opt-out?"). Supervisor recognizes this isn't researchable.
```
Current flow:  → ask user for clarification → analyst → advocate
DAG-assembled: → human-clarification → analyst → advocate
```

These scenarios prove the Supervisor makes genuinely different assembly decisions based on context — the core value proposition.

## Risks

- **Translation fidelity**: The DAG Assembler translates between structured and natural language. If it constructs a poor NL prompt from the structured contract, the domain agent gets bad instructions. If it parses the prose report incorrectly, the Supervisor gets bad data. The translation layer is a single point of fidelity risk. Mitigation: well-defined translation patterns tested against known agent I/O examples.
- **State Briefer quality**: The Supervisor's decisions are only as good as the briefings it receives. A State Briefer that misses relevant history or filters out a viable node degrades assembly quality. Mitigation: the Supervisor can always request a fresh briefing or ask for specific information.
- **Strategy skill staleness**: If strategy skills don't evolve as the team learns new workflow patterns, the Supervisor keeps following outdated guidance. Mitigation: strategy skills are versioned and reviewable — treat them like any other skill in the plugin.
- **Subagent round-trip latency**: Even with 2 DAG-ops agents instead of 4, each node involves multiple subagent calls. For a 5-node DAG pass, that's 10+ subagent invocations. Latency may be noticeable. Mitigation: the flexibility and context preservation benefits justify the overhead; optimize hot paths later.
- **Supervisor prompt complexity**: The Supervisor needs to understand DAG mechanics, strategy skills, structured protocol, and pass lifecycle. If its instructions are too complex, decision quality degrades. Mitigation: keep Supervisor instructions focused on decision-making; all mechanical details live in DAG-ops agents.

## Open Questions

- **DAG Assembler report parsing**: How does the DAG Assembler reliably parse domain agent prose into structured data? Pattern matching on headings? LLM-based extraction? Hybrid?
- **Parallel node execution**: Can the Supervisor identify independent nodes and execute them concurrently? The incremental assembly model naturally serializes, but some nodes may be parallelizable.
- **State Briefer caching**: If the State Briefer is expensive, can its briefing be cached and incrementally updated rather than regenerated from scratch?
- **Strategy skill authoring**: Who writes strategy skills? Distilled automatically from current command files? Hand-authored by the team? A combination?
- **Error recovery**: What happens when a domain agent fails mid-node? Does the DAG Assembler handle retries, or does the Supervisor decide?
- **Supervisor bootstrapping**: How does the Supervisor receive its initial instructions? As part of the command file? As a dedicated agent definition? Injected by the plugin framework?
- **DAG JSON schema**: What is the concrete JSON structure for a DAG version? This shapes what the DAG Assembler builds and what the State Briefer reads.

## Recommended Next Steps

1. **Define the DAG JSON schema**: Design the concrete structure for a DAG version — nodes, edges, metadata, execution trace, pass outcome. This is the canonical data format that every component reads and writes. Start with a hand-written example for one pass of the `/specify` workflow.

2. **Design the State Briefer's output format**: Define exactly what the Supervisor sees in a briefing — state summary, viable nodes with contracts, strategy guidance, history digest. Prototype with a concrete example: "pass 1 completed, advocate said needs-revision with 3 gaps, here are the viable nodes for pass 2."

3. **Design the DAG Assembler's translation patterns**: Define how structured node contracts map to natural language prompts, and how prose reports map back to structured summaries. Test against existing analyst and advocate I/O examples from the current workflow.

4. **Write the `strategy-specification` skill**: Distill the workflow patterns from the current `specify.md` command file into a strategy skill. This is the first concrete artifact that bridges the old and new architectures.

5. **Prototype one full Supervisor loop**: Hand-simulate the Supervisor decision loop for the "skip enrichment" scenario (Scenario 1). Walk through each step: State Briefer produces briefing → Supervisor decides → DAG Assembler builds → domain agent executes → Supervisor evaluates. Validate the protocol end-to-end before building any tooling.

6. **Define the Supervisor's core instructions**: Write the agent definition for the Supervisor — what it knows about DAG mechanics, how it reads structured reports, how it makes assembly decisions. Keep it lean — strategy knowledge lives in skills, mechanical details live in DAG-ops agents.
