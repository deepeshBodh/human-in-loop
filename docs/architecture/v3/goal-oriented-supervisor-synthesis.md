# Goal-Oriented Supervisor Redesign — Analysis Synthesis

> **Evolves**: [`dag-supervisor-design-synthesis.md`](../dag-supervisor-design-synthesis.md), [`dag-specialist-subagents-v2-synthesis.md`](../dag-specialist-subagents-v2-synthesis.md)
>
> **Related**: [`dag-first-execution-synthesis.md`](../dag-first-execution-synthesis.md)

## Problem Statement

After two dry runs of the DAG-based specify workflow, the Supervisor has become a 452-line procedural script that hard-codes node IDs, agent types, routing decisions, and sequencing logic. It names every domain agent, knows every catalog node, and follows a recipe rather than pursuing a goal. This contradicts the original design vision where commands become thin goal declarations and the Supervisor assembles DAGs dynamically based on context. The Supervisor has domain knowledge it shouldn't have, and the agents that should hold that knowledge (State Analyst, DAG Assembler) are underutilized as pass-through mechanics.

## Context & Constraints

- **Two dry runs completed**: The DAG protocol works mechanically — parse-reports fire, briefings produce, passes freeze, evidence populates. The plumbing is solid. The problem is architectural: responsibility is in the wrong place.
- **Supervisor context window**: Remains the scarcest resource. Every byte of domain knowledge in the Supervisor is a byte not available for goal-level judgment. This constraint drove the original three-tier design and drives this redesign.
- **State Analyst as fresh subagent**: Spawned fresh each call with full context from disk. No context pressure. Natural home for synthesis work that requires reading multiple sources (catalog + strategy skills + artifacts + history).
- **Existing infrastructure**: `hil-dag` CLI, catalog schema, strategy skills, invariant system — all remain. This redesign changes responsibility boundaries, not infrastructure.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Supervisor goal language | Gate-typed success criteria — "a gate node has produced verdict `ready`" — no agent or node names | Confident | Supervisor understands DAG node types (structural vocabulary) without knowing domain-specific agents or nodes |
| Strategy skill ownership | State Analyst reads strategy skills; Supervisor never sees them | Confident | Strategy skills are judgment heuristics — they belong with the agent that synthesizes recommendations, not the executor |
| Catalog ownership | State Analyst reads catalog for recommendations; DAG Assembler reads catalog for assembly mechanics; Supervisor sees neither | Confident | Catalog is structural truth. Two agents consume it for different purposes. Supervisor stays domain-agnostic |
| Catalog vs. strategy skills | Kept separate — catalog is structural truth (what exists, how it connects), strategy skills are judgment heuristics (when to use what pattern) | Confident | Different concerns. Catalog says analyst-review consumes enriched-input. Strategy skill says skip enrichment when input is already rich. Both inform recommendations but serve different functions |
| State Analyst recommendation depth | Ranked shortlist with rationale per recommendation, not single recommendation | Confident | Single recommendation makes Supervisor a rubber stamp. Ranked list preserves captain's call while keeping domain knowledge in the Analyst |
| Supervisor briefing verbosity | Richer structural information — node type/status counts, outcome trajectory across passes, alternatives — so Supervisor can exercise judgment | Confident | Supervisor needs enough signal to override a recommendation without needing domain knowledge. Convergence trends and DAG shape provide that signal |
| State Analyst judgment concentration | Accepted — State Analyst is the domain-aware thinker, Supervisor is the domain-agnostic executor | Confident | Risk mitigated by two safeguards: DAG Assembler enforces invariants structurally, and Supervisor sees parse-report summaries for outcome signals |
| Pass structural prerequisites | DAG Assembler handles all structural setup for new passes (including constitution-gate re-addition) | Confident | Constitution-gate re-addition is catalog-specific knowledge. Supervisor says "create a new pass," DAG Assembler knows what structural setup that requires |

## Decision Trail

### Success criteria: Agent-specific vs. Gate-typed vs. Artifact-based

- **Options considered**: (A) Gate-typed — "a gate node has produced verdict `ready`", (B) Artifact-based — "spec.md exists and has been validated"
- **Initial state**: Current spec says "advocate verdict `ready`" — names the agent directly
- **Chosen**: Option A — Gate-typed
- **Key reasoning**: The Supervisor already understands the 4 node types (task, gate, decision, milestone) as core DAG vocabulary. "A gate must pass with verdict ready" is structural, not domain-specific. Option B was too decoupled — the Supervisor couldn't distinguish "spec.md exists but unvalidated" from "spec.md exists and passed review" without reintroducing gate awareness through another mechanism.

### State Analyst judgment concentration: Concern vs. acceptance

- **Concern raised**: The State Analyst becomes the single brain merging structural truth (catalog) with judgment heuristics (strategy skills) with situational awareness (artifacts, history). That's a lot of responsibility. A bad recommendation has no backstop if the Supervisor is domain-agnostic.
- **Resolution**: Two existing safeguards make this acceptable: (1) DAG Assembler enforces invariants at assembly time — structurally invalid recommendations get caught, (2) Supervisor sees parse-report summaries — it can detect non-convergence (gaps not shrinking) without domain knowledge. Adding rationale to recommendations gives the Supervisor enough signal for captain's calls.
- **Key reasoning**: The Supervisor's context window is the scarcest resource. Concentrating domain synthesis in the State Analyst (a fresh subagent each call with no context pressure) is architecturally superior to spreading domain knowledge into the context-constrained Supervisor.

### Catalog absorbing strategy skills: Considered and rejected

- **Options considered**: (A) Keep catalog and strategy skills separate, (B) Enrich catalog contracts to encode strategy skill knowledge (e.g., richer `consumes` contracts that imply when to skip nodes)
- **Chosen**: Option A — Keep separate
- **Key reasoning**: Different concerns. Catalog is structural truth — what exists and how it connects. Strategy skills are judgment heuristics — when to use what pattern given the situation. A catalog saying `analyst-review consumes enriched-input OR raw-input` is structural. A strategy skill saying "skip enrichment when input already has clear Who/Problem/Value" is judgment. Merging them would blur this boundary.

## Risks

- **State Analyst recommendation quality**: The Supervisor's decisions are only as good as the State Analyst's recommendations. A bad synthesis of catalog + strategy + state produces bad recommendations with no Supervisor backstop for domain-specific errors. Mitigation: rationale in recommendations gives the Supervisor a reasoning chain to evaluate; invariants catch structural errors; parse-report summaries catch outcome-level problems (non-convergence).
- **Supervisor becomes rubber stamp**: If the State Analyst's recommendations are always followed, the Supervisor adds latency without adding judgment. Mitigation: ranked shortlist (not single recommendation) preserves choice; richer briefing data (outcome trajectory, DAG shape) gives the Supervisor the signals it needs to exercise independent judgment on when things aren't working.
- **Responsibility split complexity**: Three agents reading the catalog for different purposes (State Analyst for recommendations, DAG Assembler for assembly, State Analyst again for parse-report context) increases the surface area for inconsistency. Mitigation: catalog is a single source of truth on disk; each agent reads it fresh per invocation.

## Open Questions

- **Supervisor instruction size**: How lean can `specify.md` actually get? The current 452 lines need to shrink dramatically, but the structural lifecycle rules (gate verdict handling, pass creation, milestone requirements) still need to live somewhere. What's the target line count?
- **State Analyst briefing schema**: The richer briefing (node type/status counts, outcome trajectory, ranked recommendations with rationale, alternatives) needs a concrete schema. What fields exactly?
- **DAG Assembler new-pass protocol**: If the DAG Assembler handles structural prerequisites for new passes, it needs a new action or an extension to an existing one. Does `freeze-pass` gain a "create next pass with prerequisites" capability, or is there a new `initialize-pass` action?
- **Cross-workflow generalization**: This redesign is scoped to `/specify`. If the Supervisor becomes truly goal-oriented and domain-agnostic, does the same Supervisor instruction set work for `/plan`, `/techspec`, `/tasks`? Or does each workflow need its own goal declaration with workflow-specific structural rules?
- **State Analyst model choice**: With expanded responsibility (catalog + strategy + artifacts + history synthesis into ranked recommendations with rationale), should the State Analyst move from `sonnet` to a more capable model?

## Recommended Next Steps

1. **Rewrite `specify.md` as a goal declaration**: Strip all node IDs, agent names, and procedural sequences. Replace with structural lifecycle rules in DAG vocabulary. Target: under 100 lines. The State Analyst briefing and DAG Assembler mechanics handle everything else.

2. **Design the enriched State Analyst briefing schema**: Define the concrete fields for the richer briefing: recommended next node with rationale, alternatives, outcome trajectory, current DAG shape summary. This is the contract between State Analyst and Supervisor — it must carry enough signal for captain's calls without leaking domain specifics.

3. **Design the DAG Assembler `initialize-pass` action**: Define how the DAG Assembler sets up structural prerequisites for new passes. Input: pass number, prior pass DAG path. Output: new DAG with invariant-required nodes already assembled and status-set. This removes the last piece of catalog-specific knowledge from the Supervisor.

4. **Update the State Analyst agent definition**: Expand the `briefing` action to produce ranked recommendations with rationale, and ensure it reads both catalog and strategy skills as inputs. The agent definition needs to reflect its expanded role as the domain-aware recommender.

5. **Dry run the redesigned workflow**: Execute `/specify` with the lean Supervisor instructions to validate that the State Analyst's recommendations are sufficient for the Supervisor to reach a `ready` verdict without domain-specific knowledge.
