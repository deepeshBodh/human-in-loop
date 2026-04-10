---
name: analysis-specifications
description: This skill MUST be invoked when the user says "review spec", "find gaps", "what's missing", or "clarify requirements". SHOULD also invoke when reviewing spec.md for completeness. Focuses on product decisions and generates clarifying questions with concrete options.
---

# Reviewing Specifications

## Overview

Find gaps in specifications and generate clarifying questions that a product owner or stakeholder can answer. Focus on WHAT is missing, not HOW to implement.

## When to Use

- Reviewing a spec.md before implementation begins
- Validating requirements completeness after specification phase
- Generating questions for stakeholder clarification
- Checking user stories for missing acceptance criteria
- Quality gate before planning phase begins
- When Devil's Advocate reviews specification artifacts

## When NOT to Use

- **Technical architecture review** - Use design review tools instead
- **Code review** - Different skill domain entirely
- **Implementation planning** - Focus on design, not spec gaps
- **Performance specifications** - Technical concern, not product
- **When spec doesn't exist yet** - Use `humaninloop:authoring-requirements` first

## Core Principle

**Ask product questions, not implementation questions.**

| Wrong (Technical) | Right (Product) |
|-------------------|-----------------|
| "What happens if the database connection fails?" | "What should users see if the system is temporarily unavailable?" |
| "Should we use optimistic or pessimistic locking?" | "Can two users edit the same item simultaneously?" |
| "What's the retry policy for failed API calls?" | "How long should users wait before seeing an error?" |
| "What HTTP status code for invalid input?" | "What message should users see for invalid input?" |

## Question Format

Every question must be framed as a decision the stakeholder can make:

```markdown
**Question**: [Clear product decision]

**Options**:
1. [Concrete choice] - [What this means for users]
2. [Concrete choice] - [What this means for users]
3. [Concrete choice] - [What this means for users]

**Why this matters**: [User or business impact]
```

## Gap Categories

Focus on these user-facing gaps:

| Category | Example Questions |
|----------|-------------------|
| **User expectations** | "What should users see when...?" |
| **Business rules** | "Is X allowed? Under what conditions?" |
| **Scope boundaries** | "Is Y in scope for this feature?" |
| **Success/failure states** | "What happens if the user...?" |
| **Permissions** | "Who can do X? Who cannot?" |

## What to Avoid

- Implementation details (databases, APIs, protocols)
- Technical edge cases (connection failures, race conditions)
- Architecture decisions (caching, queuing, scaling)
- Performance specifications (latency, throughput)

These are valid concerns but belong in the planning phase, not specification.

## Severity Classification

| Severity | Definition | Action |
|----------|------------|--------|
| **Critical** | Cannot build without this answer | Must ask now |
| **Important** | Will cause rework if not clarified | Should ask now |
| **Minor** | Polish issue, can defer | Log and continue |

## Output Format

```markdown
## Gaps Found

### Critical
- **Gap**: [What's missing]
  - **Question**: [Product decision needed]
  - **Options**: [2-3 choices]

### Important
- **Gap**: [What's missing]
  - **Question**: [Product decision needed]
  - **Options**: [2-3 choices]

### Minor (Deferred)
- [Gap description] - can be resolved during planning
```

## Review Process

1. **Read the full specification** before identifying gaps
2. **Check each user story** for completeness
3. **Verify success criteria** are measurable
4. **Identify missing edge cases** for each flow
5. **Classify gaps** by severity
6. **Generate questions** with concrete options
7. **Group related gaps** to avoid overwhelming stakeholders

## Quality Checklist

Before finalizing the review, verify:

- [ ] All user stories reviewed for completeness
- [ ] Success criteria checked for measurability
- [ ] Edge cases identified for each main flow
- [ ] Gaps classified by severity (Critical/Important/Minor)
- [ ] All questions are product-focused (not technical)
- [ ] Each question has 2-3 concrete options
- [ ] "Why this matters" explains user/business impact
- [ ] Related gaps grouped together
- [ ] No implementation details in questions

## Common Mistakes

### Technical Questions Instead of Product Questions
❌ "What retry policy should we use?"
✅ "How long should users wait before seeing an error?"

### Vague Questions
❌ "What about errors?"
✅ "What message should users see when payment fails?"

### Open-Ended Questions Without Options
❌ "How should we handle this case?"
✅ "Options: (1) Show warning and continue, (2) Block action, (3) Ask for confirmation"

### Too Many Gaps at Once
❌ Presenting 20+ gaps to stakeholders
✅ Limit to 5-7 critical/important gaps per review round

### Missing "Why This Matters"
❌ Just listing the gap without context
✅ Explain user or business impact for each question

### Implementation Bias
❌ "Should we cache this data?" (assumes caching)
✅ "How quickly should users see updated data?"

### Scope Creep Disguised as Gaps
❌ Adding new features as "missing requirements"
✅ Only clarify scope of existing features

### Ignoring Existing Context
❌ Asking questions already answered elsewhere
✅ Reference existing patterns and decisions before asking
