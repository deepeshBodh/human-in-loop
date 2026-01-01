# Clarification Patterns

Application patterns, gap-derived handling, and round 3 special procedures.

---

## Answer Application Patterns

### Basic Replacement

```markdown
# Before
- **FR-003**: System MUST support authentication via [NEEDS CLARIFICATION: Which OAuth providers?]

# After (user answered: "Google only")
- **FR-003**: System MUST support authentication via Google OAuth2
```

### Multiple Options Answered

```markdown
# Before
- **FR-005**: Users [NEEDS CLARIFICATION: How often can they export? Options: Once daily, Unlimited, 5 per day]

# After (user answered: "5 per day")
- **FR-005**: Users MUST be able to export data up to 5 times per day
```

---

## Gap-Derived Clarification Handling

When processing clarifications from the Priority Loop (C{iteration}.{number} format):

### Identification

1. Read the Gap Priority Queue to find the source CHK and FR
2. Locate the original requirement referenced by the gap

### Application Pattern

```markdown
# Before (gap identified by CHK015 for FR-003)
- **FR-003**: System MUST support user authentication

# User answers C1.1: "Lock account after 3 failed attempts, notify admin"

# After
- **FR-003**: System MUST support user authentication
- **FR-003a**: System MUST lock user account after 3 consecutive failed login attempts
- **FR-003b**: System MUST notify admin when an account is locked due to failed login attempts
```

### Update Gap Priority Queue

```markdown
| Priority | Gap ID | CHK Source | FR Reference | Question | Status |
|----------|--------|------------|--------------|----------|--------|
| Critical | G-001 | CHK015 | FR-003 | Auth failure handling | resolved |
```

### Update Gap Resolution History

```markdown
| Gap ID | CHK Source | Original Gap | Priority | Resolution | Resolved Via | Iteration | Timestamp |
|--------|------------|--------------|----------|------------|--------------|-----------|-----------|
| G-001 | CHK015 | Auth failure handling | Critical | FR-003a, FR-003b added | C1.1 | 1 | {timestamp} |
```

---

## Round 3 Special Handling

When processing round 3 (final round):

### Core Rules

1. **Make reasonable assumptions** for any remaining unresolved markers
2. **Document assumptions explicitly** in the spec
3. **Mark spec as ready** regardless of remaining ambiguity
4. **List all assumptions prominently** in context handoff notes
5. **Never introduce new `[NEEDS CLARIFICATION]` markers**

### Assumption Format

```markdown
> **Assumption**: User timezone defaults to browser-detected timezone. Can be revised during planning.
```

### Example: Resolving with Assumption

```markdown
# Before (round 3, user didn't answer this one)
- **FR-007**: System [NEEDS CLARIFICATION: Should notifications be real-time or batched?]

# After (assumption made)
- **FR-007**: System SHOULD send notifications in real-time
> **Assumption**: Real-time notifications preferred over batched. Can be revised during planning.
```

### Handoff Notes for Round 3

```markdown
### From Spec Clarify Agent (Round 3 - Final)
- Answers applied: 5 of 7
- Assumptions made: 2
  - FR-007: Real-time notifications assumed
  - FR-009: Daily digest frequency assumed
- Spec marked as READY with documented assumptions
- Ready for: Plan workflow
```

---

## Cascading Update Guidelines

### When to Cascade

| Answer Type | Check For Updates In |
|-------------|---------------------|
| Scope change | User stories, success criteria |
| New constraint | Edge cases, related requirements |
| Priority change | User story priorities, success criteria |
| Security decision | Edge cases, requirements |

### Minimal Update Principle

Only add updates that are:
- Directly implied by the answer
- Necessary for spec consistency
- Not speculative additions
