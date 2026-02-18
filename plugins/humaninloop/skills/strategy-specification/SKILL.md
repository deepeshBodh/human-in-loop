# Strategy: Specification

Workflow-specific patterns for the specification workflow. Consumed by the State Briefer alongside `strategy-core` to produce targeted Supervisor briefings.

## Goal

Produce a validated feature specification where the advocate verdict is `ready`.

## Success Criteria

- `spec.md` exists with user stories and functional requirements
- `advocate-report.md` verdict: `ready`

## Patterns

### Input Assessment

Sparse input (missing Who/Problem/Value) typically benefits from enrichment before analysis. Detailed input with clear problem framing can go directly to the analyst. Consider the domain context — a sparse input in a well-understood domain may not need enrichment if the analyst can infer context from existing artifacts (constitution, codebase analysis).

**Rationale**: Enrichment adds a full interaction round with the user. When the input already contains sufficient signal, skipping enrichment saves time without sacrificing quality. The analyst is capable of working with moderately detailed input.

### Produce-then-Validate

The primary pattern is: an agent produces an artifact, then a different agent (or gate) validates it. For specification, this means the analyst produces `spec.md`, the advocate reviews it. Resist the urge to skip validation even when the analyst report looks comprehensive.

**Rationale**: Self-review is unreliable. The analyst's blind spots are systematic — a separate reviewer with adversarial framing catches what the producer cannot see in their own work.

### Gap-Informed Revision

When the advocate identifies gaps, the next analyst pass should be informed by those specific gaps. The analyst should see what was flagged and focus revision effort there, not rewrite the entire spec. Use informed-by edges to carry gap context forward.

**Rationale**: Unfocused revision wastes effort on sections that were already adequate, and may introduce new issues in previously-clean areas. Targeted revision converges faster.

### Research Before User

When gaps are knowledge-based (factual unknowns about the codebase, existing protocols, technical constraints), targeted research often resolves them faster than asking the user. Try research first; escalate to user only if research is inconclusive or the question is genuinely about preference.

**Rationale**: Users should not be asked questions that the codebase can answer. Research is faster and more precise for factual questions. Reserve user interaction for genuine decisions.

## Anti-Patterns

- **Post-pass-1 enrichment**: Running enrichment after pass 1 — input is already established and enrichment adds no value
- **Uniform gap treatment**: Treating all gaps identically — knowledge, preference, and scope gaps need different responses
- **User-for-researchable**: Asking the user about things that could be researched from the codebase or documentation
- **Recurring-gap iteration**: Continuing to iterate when the advocate keeps flagging the same gaps across passes

## Guardrails

- Constitution must exist before specification work begins (INV-002)
- After 5 passes, surface the situation to the user with options (INV-004)
- Never skip the advocate gate — every analyst output must be validated
