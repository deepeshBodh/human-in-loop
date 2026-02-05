---
name: authoring-requirements
description: This skill MUST be invoked when the user says "write requirements", "define success criteria", "identify edge cases", or "functional requirements". SHOULD also invoke when user mentions "FR-", "SC-", "RFC 2119", "MUST SHOULD MAY", or "edge cases". Produces technology-agnostic requirements in FR-XXX format with measurable success criteria.
---

# Authoring Requirements

## Overview

Write technology-agnostic functional requirements, identify edge cases, and define measurable success criteria. Focus on WHAT the system does and WHY, never HOW it's implemented.

## When to Use

- Starting a new feature specification
- Documenting acceptance criteria for user stories
- Defining API contracts at the business logic level
- Creating requirements for stakeholder review
- When existing requirements are vague or missing structure
- Translating informal feature requests into formal requirements

## When NOT to Use

- **Implementation planning** - Use design docs or architecture decisions instead
- **Technical architecture decisions** - Use ADRs or technical design documents
- **When requirements already exist and are validated** - Don't duplicate work
- **API endpoint specifications** - Use `humaninloop:patterns-api-contracts` instead
- **Data model design** - Use `humaninloop:patterns-entity-modeling` instead
- **User story authoring** - Use `humaninloop:authoring-user-stories` instead (this skill focuses on the underlying requirements)

## Functional Requirements Format

Write requirements using the FR-XXX format with RFC 2119 keywords:

```markdown
## Functional Requirements

- **FR-001**: System MUST [specific capability]
- **FR-002**: Users MUST be able to [specific action]
- **FR-003**: System SHOULD [recommended behavior]
- **FR-004**: System MAY [optional capability]
```

### RFC 2119 Keywords

| Keyword | Meaning |
|---------|---------|
| **MUST** | Absolute requirement; no exceptions |
| **SHOULD** | Recommended; valid exceptions may exist |
| **MAY** | Optional; implementation choice |

See [RFC-2119-KEYWORDS.md](references/RFC-2119-KEYWORDS.md) for detailed usage guidance.

### FR Numbering Rules

1. Sequential numbering: FR-001, FR-002, FR-003...
2. No gaps in sequence
3. Three-digit padding (001, not 1)
4. Group related requirements together

### Writing Technology-Agnostic Requirements

**Good (what):**
- "System MUST notify users when their subscription expires"
- "Users MUST be able to export their data in a portable format"

**Bad (how):**
- "System MUST send email via SendGrid when subscription expires"
- "Users MUST be able to download a JSON export from the /api/export endpoint"

## Edge Cases

Identify 3-5 boundary conditions that need explicit handling:

```markdown
## Edge Cases

1. **System limits**: What happens at maximum capacity?
2. **Invalid input**: How are malformed requests handled?
3. **External failures**: What if dependencies are unavailable?
4. **Concurrent access**: How are race conditions prevented?
5. **Permission boundaries**: What happens with unauthorized access?
```

### Edge Case Categories

| Category | Examples |
|----------|----------|
| **System limits** | Max items, file size limits, rate limits |
| **Invalid input** | Empty fields, wrong types, boundary values |
| **External failures** | Network timeouts, service unavailable |
| **Concurrency** | Simultaneous edits, duplicate submissions |
| **Permissions** | Unauthorized access, expired tokens |

See [EDGE-CASES.md](references/EDGE-CASES.md) for detailed patterns.

## Success Criteria Format

Define 3-5 measurable outcomes using SC-XXX format:

```markdown
## Success Criteria

- **SC-001**: Users complete the task creation flow in under 2 minutes
- **SC-002**: 95% of users successfully create their first recurring task
- **SC-003**: Support tickets related to task scheduling decrease by 50%
```

### Success Criteria Rules

1. **Technology-agnostic**: No API metrics, database stats, or code coverage
2. **User/business focused**: Observable by stakeholders
3. **Measurable**: Quantifiable where possible
4. **Outcome-oriented**: What changes, not what's built

**Good:**
- "Users complete the workflow in under 2 minutes"
- "Error rate for task creation drops below 5%"
- "User satisfaction score increases to 4.5/5"

**Bad:**
- "API responds in under 200ms"
- "Database queries execute in under 50ms"
- "Code coverage exceeds 80%"

## Key Entities (Optional)

When the feature involves data, describe entities conceptually:

```markdown
## Key Entities

### RecurringPattern
Represents the schedule for a repeating task.

**Attributes:**
- Frequency (how often: daily, weekly, monthly)
- Interval (every N occurrences)
- End condition (never, after N times, on date)

**Relationships:**
- Belongs to one Task
- Generates many TaskInstances
```

### Entity Description Rules

- Describe purpose, not schema
- List attributes as concepts, not columns
- Focus on relationships, not foreign keys
- No data types, constraints, or indexes

## Validation Script

Validate requirement format with the included script:

```bash
python scripts/validate-requirements.py path/to/spec.md
```

The script checks:
- FR-XXX format and sequential numbering
- RFC 2119 keywords present
- SC-XXX format and sequential numbering
- Technology-agnostic language

## Quality Checklist

Before finalizing, verify:

- [ ] All FRs use RFC 2119 keywords (MUST/SHOULD/MAY)
- [ ] FR numbers are sequential with no gaps
- [ ] No technology or implementation details mentioned
- [ ] 3-5 edge cases identified
- [ ] All SCs are measurable outcomes
- [ ] SCs focus on user/business value
- [ ] Entities described conceptually (if applicable)

## Common Mistakes

### Technology Leakage
❌ "System MUST use PostgreSQL for storage"
✅ "System MUST persist data durably"

### Implementation Details
❌ "MUST implement using the Observer pattern"
✅ "System MUST notify relevant components when state changes"

### Unmeasurable Criteria
❌ "System MUST be fast" or "MUST be user-friendly"
✅ "Users MUST complete the flow in under 2 minutes"

### Missing RFC 2119 Keywords
❌ "System will notify users"
✅ "System MUST notify users" (use MUST/SHOULD/MAY)

### Technical Metrics as Success Criteria
❌ "API latency MUST be under 100ms"
✅ "Users MUST perceive responses as instantaneous"

### Confusing Requirements with User Stories
❌ "As a user, I want to see my balance"
✅ "System MUST display current balance to authenticated users" (FR) + separate user story

### Scope Creep in Edge Cases
❌ Listing 20+ edge cases covering every hypothetical
✅ Focus on 3-5 high-impact boundary conditions
