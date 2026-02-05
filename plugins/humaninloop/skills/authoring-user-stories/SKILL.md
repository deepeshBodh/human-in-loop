---
name: authoring-user-stories
description: This skill MUST be invoked when the user says "write user stories", "define acceptance criteria", "prioritize features", "user story", "acceptance scenario", or "Given When Then". SHOULD also invoke when user mentions "priority", "P1", "P2", "P3", or "backlog". Produces prioritized user stories with independently testable acceptance scenarios.
---

# Authoring User Stories

**Violating the letter of the rules is violating the spirit of the rules.**

## Overview

Transform feature descriptions into testable user stories with clear business value, prioritized by impact. Each story MUST be independently testable with measurable acceptance criteria.

This is a discipline-enforcing skill. The structured format exists to ensure stories are unambiguous, testable, and properly prioritized. Shortcuts create ambiguous requirements that cause implementation failures.

## When to Use

- Transforming feature descriptions into testable requirements
- Breaking down large features into prioritized, independent stories
- When acceptance scenarios need Given/When/Then structure
- Creating backlog items with clear verification criteria
- When stakeholders need to understand what "done" means

## When NOT to Use

- **Technical implementation tasks** - Use task decomposition instead
- **Bug reports** - Use issue templates with reproduction steps
- **When requirements are already in user story format** - Don't duplicate work
- **Architecture decisions** - Use `humaninloop:patterns-technical-decisions` instead
- **API contract design** - Use `humaninloop:patterns-api-contracts` instead

## User Story Format

Generate 2-5 user stories per feature using this exact structure:

```markdown
### User Story N - [Brief Title] (Priority: P#)

[Describe this user journey in plain language]

**Why this priority**: [Explain the value and priority level]

**Independent Test**: [How this can be tested standalone]

**Acceptance Scenarios**:
1. **Given** [state], **When** [action], **Then** [outcome]
2. **Given** [state], **When** [action], **Then** [outcome]
```

## Priority Definitions

| Priority | Meaning | Criteria |
|----------|---------|----------|
| **P1** | Core functionality | MVP requirement, blocks other features, must ship |
| **P2** | Important | Complete experience but can ship without initially |
| **P3** | Nice to have | Enhances experience, future consideration |

See [PRIORITY-DEFINITIONS.md](references/PRIORITY-DEFINITIONS.md) for detailed guidance on priority assignment.

## Acceptance Scenario Guidelines

Each scenario follows the Given/When/Then pattern:

- **Given**: The initial state or precondition (context)
- **When**: The action the user takes (trigger)
- **Then**: The expected outcome (result)

**Rules:**
1. Each story needs 2-4 acceptance scenarios
2. Cover both happy path and key edge cases
3. Scenarios must be independently verifiable
4. Use concrete, observable outcomes (not implementation details)

**Good example:**
```
**Given** a user has an active subscription,
**When** they click "Cancel Subscription",
**Then** they see a confirmation dialog with the cancellation date
```

**Bad example:**
```
**Given** the database has the user record,
**When** the API receives a DELETE request,
**Then** the subscription_status column is set to "cancelled"
```

## Independent Test Requirement

Each user story must include an **Independent Test** description that explains:
- How QA can verify this story in isolation
- What data or setup is required
- What constitutes passing/failing

This enables parallel testing and clear verification.

## Quality Checklist

Before finalizing, verify each user story:

- [ ] Has a clear, descriptive title
- [ ] Priority is assigned with justification
- [ ] User journey is described in plain language
- [ ] Independent test is specified
- [ ] 2-4 acceptance scenarios using Given/When/Then
- [ ] No implementation details or technology references
- [ ] Outcomes are observable and measurable

## Validation Script

Validate user story format with the included script:

```bash
python scripts/validate-user-stories.py path/to/spec.md
```

The script checks:
- Priority markers (P1, P2, P3)
- Given/When/Then syntax completeness
- Independent test presence
- Priority justification
- Header format

See [EXAMPLES.md](references/EXAMPLES.md) for complete user story examples.

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Priority is obvious, don't need justification" | Obvious to you ≠ obvious to others. Stakeholders disagree on "obvious." Justify anyway. |
| "This story is too simple for Given/When/Then" | Simple stories still need testable criteria. Ambiguity causes implementation bugs. Format anyway. |
| "We can add acceptance scenarios later" | "Later" means never. Incomplete stories get misimplemented. Write them now. |
| "The user just wants quick stories" | Quick incomplete stories waste more time than complete ones. Do it right. |
| "Independent test is overkill for small features" | Small features still need verification. QA can't test what isn't specified. Include it. |
| "Everyone knows what P1 means" | P1 without justification is opinion, not prioritization. Explain the value. |

## Red Flags - STOP and Restart Properly

If you notice yourself thinking any of these, STOP immediately:

- "The priority is self-evident"
- "Given/When/Then is overkill for this"
- "Independent test isn't needed for simple stories"
- "The user just wants quick stories"
- "We'll refine the acceptance scenarios later"
- "This is just a placeholder story"

**All of these mean:** You are rationalizing. Write complete stories with all required sections.

**No exceptions:**
- Not for "simple" features
- Not for "we'll refine later"
- Not for "tight deadlines"
- Not even if user says "just give me quick stories"

## Common Mistakes

### Technical Stories Instead of User Stories
❌ "As a developer, I want to refactor the auth module"
✅ "As a user, I want to log in securely so my account is protected"

### Missing Priority Justification
❌ Just saying "P1" without explaining why
✅ "**Why this priority**: Core login flow - users cannot access any features without this"

### Implementation Details in Acceptance Scenarios
❌ "Then the React component re-renders with updated state"
✅ "Then the user sees the updated balance immediately"

### Vague Outcomes
❌ "Then the user is happy" or "Then it works correctly"
✅ "Then the user sees a confirmation message with order number"

### Compound Stories
❌ One story covering login, registration, AND password reset
✅ Separate stories for each distinct user journey

### Non-Testable Criteria
❌ "Then the system is performant"
✅ "Then the page loads within 2 seconds"
