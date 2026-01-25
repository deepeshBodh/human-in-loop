# Output Templates

Select template based on configured `output-[mode]`. Generate output at conclusion phase.

---

## output-synthesis

Full structured document with complete decision trail. Use for complex analyses needing audit trail.

```markdown
# [Topic] Analysis Synthesis

## Problem Statement

[1-2 sentences describing the problem as refined through discussion.
Reflect evolved understanding, not just original framing.]

## Context & Constraints

- **[Constraint 1]**: [Description]
- **[Constraint 2]**: [Description]
- **[Constraint 3]**: [Description]

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Decision area 1] | [What was decided] | [Why - brief reasoning] |
| [Decision area 2] | [What was decided] | [Why - brief reasoning] |
| [Decision area 3] | [What was decided] | [Why - brief reasoning] |

## Decision Trail

### [First major decision]
- **Options considered**: [A], [B], [C]
- **Recommendation was**: [X]
- **Chosen**: [Y]
- **Key reasoning**: [Why this choice was made]

### [Second major decision]
- **Options considered**: [A], [B], [C]
- **Recommendation was**: [X]
- **Chosen**: [Y]
- **Key reasoning**: [Why this choice was made]

[Continue for each significant decision point]

## Recommended Next Steps

1. **[Action 1]**: [What to do and why it's the logical next move]
2. **[Action 2]**: [What to do and why it's the logical next move]
3. **[Action 3]**: [What to do and why it's the logical next move]

## Open Questions

[List questions that emerged but weren't resolved. Omit if none.]

- [Question 1]
- [Question 2]
```

**Guidelines:**
- Problem Statement: Reframe based on learning. Starting problem is rarely the real problem.
- Key Decisions Table: Capture essence. Someone should skim and understand direction.
- Decision Trail: Show thinking, especially where user disagreed with recommendations.
- Next Steps: Be specific. "Research X" is weak. "Evaluate [options] against [criteria] by [date]" is strong.
- Open Questions: Honest acknowledgment builds trust.

---

## output-bullets

Concise bullet point summary. Use for quick reference or sharing with others.

```markdown
# [Topic] - Key Takeaways

**Problem**: [One-line refined problem statement]

**Key Decisions**:
- [Decision 1]: [Choice] - [One-line rationale]
- [Decision 2]: [Choice] - [One-line rationale]
- [Decision 3]: [Choice] - [One-line rationale]

**Trade-offs Accepted**:
- [Trade-off 1 acknowledged and why it's acceptable]
- [Trade-off 2 acknowledged and why it's acceptable]

**Next Steps**:
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Open Questions**:
- [Question 1]
```

**Guidelines:**
- Maximum 15-20 bullet points total
- Each bullet is one line
- No nested bullets beyond one level
- Prioritize decisions over process

---

## output-matrix

Decision comparison matrix. Use when comparing multiple options across criteria.

```markdown
# [Topic] - Decision Matrix

## Options Evaluated

| Option | Description |
|--------|-------------|
| **A) [Name]** | [Brief description] |
| **B) [Name]** | [Brief description] |
| **C) [Name]** | [Brief description] |

## Evaluation Criteria

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| [Criterion 1] | High/Med/Low | [Why this matters] |
| [Criterion 2] | High/Med/Low | [Why this matters] |
| [Criterion 3] | High/Med/Low | [Why this matters] |

## Comparison Matrix

| Criterion | Option A | Option B | Option C |
|-----------|----------|----------|----------|
| [Criterion 1] | [Rating + note] | [Rating + note] | [Rating + note] |
| [Criterion 2] | [Rating + note] | [Rating + note] | [Rating + note] |
| [Criterion 3] | [Rating + note] | [Rating + note] | [Rating + note] |

## Recommendation

**Recommended**: Option [X]

**Rationale**: [2-3 sentences explaining why this option best fits the weighted criteria]

**Key trade-off**: [What you give up by choosing this option]

## Decision

**Chosen**: Option [Y]

**User rationale**: [If different from recommendation, capture why]
```

**Guidelines:**
- Use consistent rating scale (e.g., Strong/Good/Weak or 1-5)
- Weight criteria based on user priorities discovered in questioning
- Always include recommendation even if user chose differently
- Capture user's rationale if they deviated from recommendation

---

## output-actions

Numbered action items only. Use for implementation focus.

```markdown
# [Topic] - Action Items

**Context**: [One sentence summary of what was decided]

## Immediate Actions (This Week)

1. [ ] **[Action]** - [Brief description of what and why]
2. [ ] **[Action]** - [Brief description of what and why]
3. [ ] **[Action]** - [Brief description of what and why]

## Near-Term Actions (This Month)

4. [ ] **[Action]** - [Brief description of what and why]
5. [ ] **[Action]** - [Brief description of what and why]

## Future Considerations

- [Item to revisit later and trigger condition]
- [Item to revisit later and trigger condition]

## Dependencies

- Action [N] requires [prerequisite]
- Action [N] blocked until [condition]
```

**Guidelines:**
- Each action starts with a verb
- Actions are specific and testable for completion
- Include "why" to prevent future confusion
- Group by timeframe, not by topic
- Dependencies section prevents blockers

---

## output-enrichment

Who/Problem/Value structure for feature specification. Use with `mode:specification-input`.

```markdown
## Enriched Feature Description

**Actor**: [The user/role who needs this feature]
**Problem**: [The pain point or need being addressed]
**Value**: [Why solving this matters]
**Out of Scope**: [Explicit boundaries for v1]
**Success Criteria**: [How we'll know it's working]

### Summary

[Actor] needs this feature because [problem]. This matters because [value]. Success will be measured by [success criteria].

### Original Input

> [Original user input preserved verbatim]
```

**Guidelines:**
- **Actor**: Be specific. "Users" is vague; "end users of the mobile app" is better.
- **Problem**: State the pain point, not the solution. "Need dark mode" is solution; "eye strain in low light" is problem.
- **Value**: Connect to outcomes. Why does the business or user care?
- **Out of Scope**: List what's NOT in v1. Prevents scope creep.
- **Success Criteria**: Make observable. "Better UX" is vague; "users report less eye fatigue" is observable.
- **Summary**: Complete narrative for downstream consumers.
- **Original Input**: Always preserve. May contain context enrichment missed.

### Example

For input: "Add dark mode"

```markdown
## Enriched Feature Description

**Actor**: End users of the application
**Problem**: Eye strain during extended use, especially in low-light environments
**Value**: Improved user satisfaction and increased evening usage
**Out of Scope**: System-wide theme sync, scheduled auto-switching, custom color schemes
**Success Criteria**: User feedback indicating reduced eye fatigue; increased usage during evening hours

### Summary

End users need this feature because they experience eye strain during extended use in low-light environments. This matters because it improves user satisfaction and enables evening usage. Success will be measured by user feedback indicating reduced eye fatigue.

### Original Input

> Add dark mode
```

---

## Selecting the Right Output

| Situation | Recommended Output |
|-----------|-------------------|
| Complex multi-stakeholder decision | `output-synthesis` |
| Quick standup or status update | `output-bullets` |
| Choosing between vendors or approaches | `output-matrix` |
| Sprint planning or task breakdown | `output-actions` |
| Feature intake from sparse request | `output-enrichment` |

When no mode specified, default to `output-synthesis`.
