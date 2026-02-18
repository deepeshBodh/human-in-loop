# DAG Strategy Skills — Analysis Synthesis

## Problem Statement

The current workflow commands (specify.md at 644 lines, techspec.md at ~580 lines) contain ~150 lines of workflow strategy knowledge mixed into ~350 lines of procedural mechanics and ~100 lines of architecture documentation. In the DAG-first architecture, procedural mechanics move to the DAG executor and DAG-ops agents. The workflow strategy knowledge — when to skip enrichment, how to route different gap types, when to halt — needs a new home. Strategy skills are that home: concise, structured artifacts that the State Briefer consumes and distills into Supervisor briefings.

## Context & Constraints

- **Supervisor context preservation**: The Supervisor must not read raw strategy skills directly — they will grow over time and consume context budget. The State Briefer reads skills and produces targeted briefings.
- **Supervisor intelligence**: Strategy skills must inform, not dictate. The Supervisor needs room for genuine judgment — deviating from patterns when context warrants it. Prescriptive decision tables would recreate the rigidity of hardcoded commands.
- **Existing skill format**: Current skills (authoring, analysis, patterns, validation) use rich SKILL.md format with prose guidance, examples, and checklists. Strategy skills serve a different consumer (State Briefer → Supervisor) and need a different format.
- **Collapsing boundaries**: Command boundaries will collapse over time. Strategy skills must compose when workflows merge.
- **Static within this system**: DAGs persist as immutable artifacts. Pattern analysis and strategy skill evolution is a separate concern operating on that data externally.

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Format | Patterns + anti-patterns + guardrails with rationale. NOT prescriptive decision tables. | Confident | Decision tables make the Supervisor a lookup engine — same rigidity as hardcoded commands. Patterns with rationale let the Supervisor understand WHY things work and deviate when context warrants it. |
| Layered structure | `strategy-core` (universal patterns) + workflow-specific skills (e.g., `strategy-specification`). Supervisor reads core + relevant workflow skills. | Confident | Universal patterns (validate every output, gap classification) shared across all workflows. Workflow-specific patterns (enrichment, spec structure) scoped to their domain. When boundaries collapse, Supervisor picks up multiple workflow skills. |
| Consumer | State Briefer reads strategy skills, filters to relevant patterns, incorporates into structured briefing. Supervisor never reads raw skills. | Confident | Subagents spawn and die with fresh context. State Briefer can read growing skill files without impacting Supervisor context. Briefings are targeted — only patterns relevant to current state. |
| Constraint boundary | Hard constraints live in catalog invariants (enforced by DAG Assembler). Strategy skills are advisory (interpreted by State Briefer, applied by Supervisor judgment). | Confident | Clean separation: invariants are non-negotiable (constitution must exist, advocate gate required). Strategy patterns are informed defaults (enrichment typically helps for sparse input). |
| Evolution mechanism | Static within this system. DAGs persist for external analysis. Skill updates are a separate concern. | Confident | Clean boundary. This system produces data (persisted DAGs). Pattern discovery and skill improvement operate externally on that data. No learning loops to design in the executor. |

## Decision Trail

### Format: Decision tables vs. Patterns with rationale

- **Initial proposal**: Structured decision tables (`IF input lacks Who/Problem/Value → SELECT input-enrichment`, `After advocate-review | verdict: needs-revision, knowledge gaps → targeted-research`)
- **User challenged**: "Will this create a situation that is very prescriptive to supervisor and restrict its ability to critically think?"
- **Revised to**: Patterns + anti-patterns + guardrails with rationale
- **Key reasoning**: The whole point of DAG-first architecture is Supervisor flexibility. Decision tables recreate the rigidity of hardcoded commands in a different format. Patterns with rationale let the Supervisor understand WHY enrichment typically precedes analysis and WHEN it's appropriate to deviate. The Supervisor uses judgment informed by patterns, not rules.

### Consumption: Direct vs. State Briefer

- **Options considered**: (A) Supervisor reads skills directly at pass start — concise skills keep context cost manageable. (B) State Briefer incorporates into briefing — Supervisor gets pre-filtered guidance.
- **Chosen**: State Briefer (option B)
- **Key reasoning**: "Over time the skills will fill up main context. Because subagents spawn and die, this helps with a targeted operation." Each State Briefer invocation starts fresh with full context budget. As skills grow from 50 to 200+ lines, the Supervisor is insulated. The State Briefer filters to only patterns relevant to the current state.

## Strategy Skill Structure

### `strategy-core` (Universal Patterns)

```markdown
# Strategy: Core

## Validation
Every agent output should pass through a gate before downstream consumption.
Even when confident in quality, validation catches blind spots. This is the
most consistently valuable pattern across all workflows.

## Gap Classification
Advocate rejections and gate verdicts carry different gap types that suggest
different responses:
- Gaps about unknowns (factual, investigable) are often resolvable through
  research without involving the user
- Gaps about preferences (subjective, business decisions) require user input —
  research cannot resolve what only humans can decide
- Gaps about scope (too broad, multiple concerns) may warrant halting or
  splitting rather than iterating within the current workflow

## Pass Evolution
Early passes establish structure. Later passes refine based on feedback.
By pass 3+, assess whether gaps are converging (good — the spec is
improving) or recurring (bad — something structural is wrong).
Diminishing returns are a signal to surface the situation to the user.

## Halt Escalation
Never force-exit without user consent. When halting, present the situation
with clear options (continue, accept current state, stop manually). The user
always has final say on workflow termination.

## Anti-Patterns
- Looping indefinitely without checking if the same gaps keep recurring
- Sending preference gaps to research (research can't answer "should we")
- Skipping validation even when output seems obviously correct
- Force-terminating without presenting options to the user
```

### `strategy-specification` (Workflow-Specific Patterns)

```markdown
# Strategy: Specification

## Goal
Produce a validated feature specification where advocate verdict is "ready".

## Success Criteria
- spec.md exists with user stories and functional requirements
- advocate-report.md verdict: ready

## Patterns

### Input Assessment
Sparse input (missing Who/Problem/Value) typically benefits from enrichment
before analysis. Detailed input with clear problem framing can go directly
to the analyst. Consider the domain context — a sparse input in a well-
understood domain may not need enrichment if the analyst can infer context
from existing artifacts (constitution, codebase analysis).

### Produce-then-Validate
The primary pattern is: an agent produces an artifact, then a different
agent (or gate) validates it. For specification, this means analyst produces
spec.md, advocate reviews it. Resist the urge to skip validation even when
the analyst report looks comprehensive.

### Gap-Informed Revision
When the advocate identifies gaps, the next analyst pass should be informed
by those specific gaps. The analyst should see what was flagged and focus
revision effort there, not re-write the entire spec. Use informed-by edges
to carry gap context forward.

### Research Before User
When gaps are knowledge-based (factual unknowns about the codebase, existing
protocols, technical constraints), targeted research often resolves them
faster than asking the user. Try research first; escalate to user only if
research is inconclusive or the question is genuinely about preference.

## Anti-Patterns
- Running enrichment after pass 1 (input is already established)
- Treating all gaps identically (knowledge, preference, and scope gaps need
  different responses)
- Asking the user about things that could be researched from the codebase
- Continuing to iterate when the advocate keeps flagging the same gaps

## Guardrails
- Constitution must exist before specification work begins
- After 5 passes, surface the situation to the user with options
- Never skip the advocate gate
```

## State Briefer Integration

The State Briefer reads strategy skills as part of its briefing preparation:

```
State Briefer briefing structure:
{
  "state_summary": "Pass 2. Advocate rejected with 3 gaps: 2 knowledge, 1 preference.",

  "viable_nodes": [
    {"id": "targeted-research", "reason": "2 knowledge gaps identified"},
    {"id": "human-clarification", "reason": "1 preference gap identified"},
    {"id": "analyst-review", "reason": "available after gaps resolved"}
  ],

  "relevant_patterns": [
    "Knowledge gaps are often resolvable through research without user involvement",
    "Preference gaps require user input — research cannot resolve subjective choices",
    "Pass 2: enrichment should be skipped, input already established"
  ],

  "relevant_anti_patterns": [
    "Don't send preference gaps to research",
    "Don't re-run enrichment after pass 1"
  ],

  "pass_context": "Pass 2 of 5 max before user checkpoint. Gaps are new (not recurring)."
}
```

The Supervisor receives this single structured briefing. It sees relevant patterns and anti-patterns for its current situation, not the full skill content. The State Briefer's fresh context handles the reading; the Supervisor's context handles the deciding.

## Specify.md Knowledge Migration

How the current specify.md's 644 lines map to the new architecture:

| Current specify.md Section | Lines | New Location |
|---|---|---|
| Argument parsing, empty input | 1-55 | Command goal declaration (thin) |
| Constitution check | 58-80 | Catalog invariant INV-002 |
| Architecture overview | 84-120 | Eliminated (DAG is self-documenting) |
| Resume detection | 123-151 | DAG versioning (inherent in pass model) |
| Input enrichment routing | 154-260 | `strategy-specification` (Input Assessment pattern) |
| Phase 1: Initialize | 264-337 | DAG Assembler (directory creation, template filling) |
| Phase 2: Analyst invocation | 340-385 | Node catalog (analyst-review node contract) + DAG Assembler (NL prompt construction) |
| Phase 3: Advocate invocation | 388-430 | Node catalog (advocate-review node contract) + DAG Assembler (NL prompt construction) |
| Phase 4: Verdict routing | 434-533 | `strategy-core` (Gap Classification) + `strategy-specification` (Research Before User, Gap-Informed Revision) |
| Phase 4: "Research this" handling | 462-498 | `strategy-core` (Gap Classification) + catalog (targeted-research node) |
| Phase 4: Clarification log | 500-533 | DAG execution trace (persisted in pass JSON) |
| Supervisor judgment: exit early | 537-561 | `strategy-core` (Pass Evolution, Halt Escalation) |
| Phase 5: Completion | 565-598 | Milestone node (spec-complete) + Supervisor completion handling |
| Error handling | 602-621 | DAG Assembler error handling |
| State recovery | 624-633 | Eliminated (DAG versioning makes this unnecessary) |

**Result**: 644 lines of monolithic command → distributed across catalog, strategy skills, DAG Assembler, and execution model. No single component exceeds ~80 lines. All workflow knowledge is inspectable and composable.

## Risks

- **State Briefer interpretation quality**: The State Briefer must correctly identify which patterns are relevant to the current state. If it includes irrelevant patterns or misses critical ones, Supervisor decisions degrade. Mitigation: strategy skills are structured with clear conditions ("when gaps are knowledge-based"), making pattern-matching straightforward.
- **Pattern gap**: The initial strategy skills are distilled from current command files. Novel situations not covered by existing patterns will require Supervisor judgment without guidance. Mitigation: the Supervisor is an LLM with general reasoning capability; patterns augment its judgment, they don't replace it.
- **Skill proliferation**: As more workflows adopt DAG-first, the number of strategy skills grows. The layered model (core + workflow-specific) helps, but shared patterns might diverge across workflows. Mitigation: `strategy-core` is the single source for universal patterns; workflow skills only add domain-specific content.

## Open Questions

- **Strategy skill file location**: Do strategy skills live alongside other skills in `plugins/humaninloop/skills/strategy-core/` and `plugins/humaninloop/skills/strategy-specification/`? Or in a separate `strategies/` directory?
- **State Briefer pattern matching**: How does the State Briefer decide which patterns are relevant? Keyword matching against current state? LLM judgment reading the skill? Since it's an LLM subagent, it can use judgment — but should there be structural hints in the skill to aid filtering?
- **Cross-workflow pattern sharing**: When command boundaries collapse and a single DAG spans specify + techspec, the State Briefer reads `strategy-core` + `strategy-specification` + `strategy-techspec`. How does it handle conflicting guidance between workflow skills?
- **Skill versioning**: Should strategy skills have version numbers? If a skill update changes patterns, existing DAG history was produced under old patterns. Does this matter?

## Recommended Next Steps

1. **Write `strategy-core`**: Author the universal patterns, anti-patterns, and guardrails. This is stable across all workflows and should be written first.

2. **Write `strategy-specification`**: Distill specification-specific patterns from specify.md. Map each current routing decision to a pattern with rationale. Validate that the patterns are advisory, not prescriptive.

3. **Design the State Briefer's pattern-matching approach**: Define how the State Briefer selects relevant patterns from skills. Prototype with a concrete scenario: "pass 2, advocate rejected with 2 knowledge gaps and 1 preference gap — which patterns does the briefing include?"

4. **Validate with a walkthrough**: Hand-simulate the full loop for flexibility Scenario 2 (research instead of asking user). State Briefer reads skills → produces briefing with gap classification patterns → Supervisor decides targeted-research → DAG Assembler builds → research agent executes → Supervisor evaluates. Confirm the strategy skill guidance leads to good assembly decisions without being prescriptive.

5. **Identify strategy patterns for other workflows**: Read techspec.md, plan.md, tasks.md and note which routing decisions would become patterns. This validates the layered model and identifies what goes in `strategy-core` vs. workflow-specific skills.
