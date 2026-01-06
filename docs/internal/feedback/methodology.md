# Feedback Triage Methodology

A repeatable process for collecting, categorizing, prioritizing, and tracking plugin feedback.

---

## Quick-Start Checklist

Use this checklist when processing a new round of feedback:

- [ ] **Collect**: Gather raw feedback from users (any format)
- [ ] **Anonymize**: Convert names to aliases using first + last letter (e.g., "John" → "Jn")
- [ ] **Categorize**: Assign type label and phase label to each item
- [ ] **Prioritize**: Use Pain × Effort matrix to assign P1/P2/P3
- [ ] **Document**: Copy `_template.md` → `round-N.md`, fill in categorized feedback
- [ ] **Identify Quick Wins**: Flag low-effort items for immediate action
- [ ] **Create GitHub Issue**: Use the tracking issue template from the round file
- [ ] **Create Labels**: Ensure all required labels exist in the repo
- [ ] **Spin Off Child Issues**: As work begins, create linked issues for individual items

---

## Full Rationale

### Why This Process Exists

Early-stage plugins benefit from structured feedback loops. This methodology ensures:
- Feedback isn't lost or forgotten
- Priority decisions are explicit and defensible
- Progress is visible to feedback providers
- The process scales as user count grows

### Categorization: Multi-Dimensional Labels

Each feedback item gets three labels:

**Type** (what kind of feedback):
| Label | Use When |
|-------|----------|
| `bug` | Something is broken or behaving incorrectly |
| `enhancement` | Improvement to existing functionality |
| `feature-request` | Net-new capability that doesn't exist |
| `performance` | Speed, efficiency, or resource usage issues |

**Phase** (where in the workflow):
| Label | Use When |
|-------|----------|
| `phase:setup` | Affects constitution creation, initial configuration |
| `phase:specify` | Affects requirements gathering, devil's advocate |
| `phase:plan` | Affects planning workflow, research, architecture |
| `phase:tasks` | Affects task generation, mapping |
| `phase:implement` | Affects code generation, PR creation |
| `phase:cross-cutting` | Affects multiple phases or the overall system |

**Priority** (when to address):
| Label | Meaning |
|-------|---------|
| `P1` | High pain, address first |
| `P2` | Medium priority, address after P1s |
| `P3` | Backlog, nice-to-have |

### Prioritization: Pain × Effort Matrix

Priority is determined by two factors:
- **User Pain**: How much does this issue hurt the user experience?
- **Implementation Effort**: How hard is this to fix/build?

```
                    │ Low Effort     │ High Effort
────────────────────┼────────────────┼────────────────
High Pain           │ P1 - Do First  │ P1 - Plan Carefully
────────────────────┼────────────────┼────────────────
Medium Pain         │ P2 - Quick Win │ P2 - Scheduled
────────────────────┼────────────────┼────────────────
Low Pain            │ P3 - Quick Win │ P3 - Backlog
```

**Quick Wins**: Items that are low effort regardless of pain level. Good for building momentum and showing responsiveness to feedback providers.

### User Anonymization Convention

To protect user privacy in public/semi-public documentation:

1. **Pattern**: First letter + last letter of first name
   - "John" → "Jn"
   - "Jane" → "Je"
   - "Sarah" → "Sh"
   - "Bob" → "Bb"

2. **Consistency**: The same user keeps the same alias across all rounds
   - Enables tracking whether a user's issues are being addressed over time
   - Example: "User Jn reported performance in Round 1; Round 3 shows no new performance complaints from Jn"

3. **Collision Handling**: If two users generate the same alias, append a number
   - "Jn" and "Jn" → "Jn1" and "Jn2"

4. **No Central Registry**: Alias mappings are not stored in the repo
   - Keep private notes if you need to remember who is who
   - The pattern is self-documenting for those who know the real names

### Documentation Structure

```
docs/internal/feedback/
├── methodology.md      # This file - the process
├── _template.md        # Copy for each new round
├── round-1.md          # First feedback round
├── round-2.md          # Second feedback round
└── ...
```

**Why round numbers, not dates or versions?**
- Feedback rounds are discrete events, not continuous
- Not necessarily tied to release cycles
- Simple, sequential, no gaps if you skip months

### GitHub Integration

**Structure**: Tracking issue + child issues
- One master issue per round with full categorized checklist
- Child issues spun off as work begins
- Links between master and children for traceability

**Why labels only (no project board)?**
- Right-sized for typical feedback volumes (< 50 items)
- Master tracking issue serves as the visual dashboard
- Avoids ceremony overhead
- Can graduate to project board if volume grows

**Label Creation Checklist**:
```
# Type labels
bug, enhancement, feature-request, performance

# Phase labels
phase:setup, phase:specify, phase:plan, phase:tasks, phase:implement, phase:cross-cutting

# Priority labels
P1, P2, P3
```

---

## Changelog

| Date | Change |
|------|--------|
| 2025-01-07 | Initial methodology created |
