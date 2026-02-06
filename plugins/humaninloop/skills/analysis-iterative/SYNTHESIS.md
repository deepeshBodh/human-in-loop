# Synthesis Document Template

Use this template when concluding an iterative analysis session. Include only sections with substantive content — omit any section that would be empty or add no value.

## Section Inclusion Guidelines

| Section | Include When |
|---------|-------------|
| Problem Statement | Always |
| Context & Constraints | Constraints were discussed or surfaced |
| Key Decisions | Any decisions were made during the session |
| Decision Trail | A decision involved notable deliberation, pushback, or trade-off exploration |
| Risks | Risks surfaced naturally during conversation |
| Open Questions | Unresolved questions remain at session end |
| Recommended Next Steps | Always |

**Principle:** If a section would contain only placeholder text, omit it entirely. A lean synthesis for a lean conversation is correct behavior.

## Confidence Indicators

Use these indicators in the Key Decisions table to reflect what was observed during the conversation — not the skill's own judgment of the decision quality.

| Indicator | Meaning |
|-----------|---------|
| `Confident` | User gave a clear, reasoned choice with no hesitation |
| `Assumed` | Decision was inferred from context but never explicitly confirmed |
| `Contested` | User disagreed with recommendation; final choice was deliberate |
| `Unsure` | User expressed uncertainty; decision made provisionally |
| `Deferred` | Explicitly postponed — not enough information to decide now |

**Assigning confidence:** Base indicators on observable conversation signals. Crisp, immediate answers with reasoning → `Confident`. Hedging, "I think maybe" → `Unsure`. Explicit "let's decide this later" → `Deferred`. User picking against recommendation after pushback → `Contested`.

## Template

```markdown
# [Topic] Analysis Synthesis

## Problem Statement

[1-2 sentences describing the problem as refined through discussion.
Reflect the evolved understanding, not just the original framing.]

## Context & Constraints

- **[Constraint 1]**: [Description]
- **[Constraint 2]**: [Description]

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| [Decision area 1] | [What was decided] | Confident | [Why — brief reasoning] |
| [Decision area 2] | [What was decided] | Unsure | [Why — brief reasoning] |
| [Decision area 3] | [What was decided] | Deferred | [Why — brief reasoning] |

## Decision Trail

### [Decision with notable deliberation]
- **Options considered**: [A], [B], [C]
- **Recommendation was**: [X]
- **Chosen**: [Y]
- **Key reasoning**: [Why this choice was made]

[Continue for each decision that involved pushback, disagreement, or significant trade-off exploration. Omit decisions that were straightforward.]

## Risks

- **[Risk 1]**: [Description and potential impact]
- **[Risk 2]**: [Description and potential impact]

## Open Questions

- [Question 1]
- [Question 2]

## Recommended Next Steps

1. **[Action 1]**: [What to do and why it's the logical next move]
2. **[Action 2]**: [What to do and why it's the logical next move]
```

## Guidelines

1. **Problem Statement**: Reframe based on what emerged. The starting problem is rarely the real problem.

2. **Key Decisions Table**: Include the Confidence column. Someone skimming should understand both the direction and how settled each decision is.

3. **Decision Trail**: Show the thinking, especially where the user disagreed with recommendations. This creates a record of deliberate choices. Omit trail entries for straightforward, confident decisions — the table captures those sufficiently.

4. **Risks**: Only include risks that emerged organically from the conversation. Do not invent risks for completeness.

5. **Next Steps**: Be specific and actionable. "Research X" is weak. "Evaluate [specific options] against [specific criteria]" is strong.

6. **Open Questions**: Honest acknowledgment of unknowns builds trust. Do not pretend everything is resolved if it is not.

7. **Output scales with conversation**: A 3-question brainstorm produces a lean synthesis (Problem Statement, Key Decisions, Next Steps). A 10-question deep exploration produces a comprehensive one. Never pad.
