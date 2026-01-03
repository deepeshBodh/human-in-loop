---
name: authoring-user-stories
description: Write user stories with P1/P2/P3 priorities, Given/When/Then acceptance scenarios, and independent tests. Use when writing user stories, feature specifications, acceptance criteria, or when you see "user story", "acceptance scenario", "Given When Then", "priority", "P1", "P2", or "P3".
---

# Authoring User Stories

## Purpose

Transform feature descriptions into testable user stories with clear business value, prioritized by impact. Each story should be independently testable with measurable acceptance criteria.

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

See [PRIORITY-DEFINITIONS.md](PRIORITY-DEFINITIONS.md) for detailed guidance on priority assignment.

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

See [EXAMPLES.md](EXAMPLES.md) for complete user story examples.

## Anti-Patterns to Avoid

- **Technical stories**: "As a developer, I want to refactor the auth module"
- **Missing priority justification**: Just saying "P1" without explaining why
- **Implementation in acceptance**: "Then the React component re-renders"
- **Vague outcomes**: "Then the user is happy" or "Then it works correctly"
- **Compound stories**: One story covering multiple distinct features
- **Non-testable criteria**: "Then the system is performant"
