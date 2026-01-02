# Clarification Question Generation

Patterns for generating clarification questions from grouped gaps.

---

## Clarification ID Formats

| Format | Source | When Used |
|--------|--------|-----------|
| `Q-S{n}` | Spec writing phase | Initial spec creation (Phase A2) |
| `C{iter}.{n}` | Gap classification | Priority Loop (Phase B) |

### Examples

```markdown
Q-S1, Q-S2, Q-S3        <- During initial spec writing
C1.1, C1.2, C1.3        <- Iteration 1 of Priority Loop
C2.1, C2.2              <- Iteration 2 of Priority Loop
```

---

## Single Gap Question Format

When a group contains only one gap:

```markdown
[NEEDS CLARIFICATION: C1.1]
**Question**: {gap.question}
**Options**:
1. {option_1}
2. {option_2}
3. {option_3}
**Source**: CHK{chk_id} validating FR-{fr_ref}
**Priority**: {Critical|Important}
```

### Example

```markdown
[NEEDS CLARIFICATION: C1.1]
**Question**: What should happen when authentication fails?
**Options**:
1. Display inline error message
2. Redirect to error page
3. Lock account after 3 attempts
**Source**: CHK015 validating FR-003
**Priority**: Critical
```

---

## Multiple Gap Question Format (Compound)

When a group contains multiple related gaps:

```markdown
[NEEDS CLARIFICATION: C1.2]
**Question**: Regarding {domain}, please clarify:
- {gap_1.question}
- {gap_2.question}
- {gap_3.question}
**Combined Options**:
For {sub_question_1}: {options}
For {sub_question_2}: {options}
**Source**: CHK{ids} validating FR-{refs}
**Priority**: {highest_priority_in_group}
```

### Example

```markdown
[NEEDS CLARIFICATION: C1.2]
**Question**: Regarding authentication error handling, please clarify:
- What message should display on authentication failure?
- How many failed attempts before account lockout?
- What is the lockout duration?
**Combined Options**:
For error message: 1. Generic "Invalid credentials" 2. Specific "Incorrect password" 3. Custom text
For lockout attempts: 1. 3 attempts 2. 5 attempts 3. No lockout
For lockout duration: 1. 15 minutes 2. 1 hour 3. Until admin unlock
**Source**: CHK015, CHK016, CHK017 validating FR-003
**Priority**: Critical
```

---

## Option Generation Guidelines

### Provide Meaningful Options

Options should:
- Cover common choices
- Be mutually exclusive (unless specified)
- Include a "custom" or "other" escape hatch

```markdown
**Options**:
1. [Common choice A]
2. [Common choice B]
3. [Alternative approach]
4. Other (please specify)
```

### Domain-Specific Option Patterns

#### Authentication Domain

```markdown
Error handling options:
1. Display inline error, keep form data
2. Redirect to login page with message
3. Lock account and require password reset

Timeout options:
1. 15 minutes (high security)
2. 1 hour (balanced)
3. 24 hours (convenience)
4. Never expire (session-based)
```

#### API Domain

```markdown
Error response options:
1. HTTP status code only
2. JSON error body with code and message
3. Detailed error with stack trace (dev only)

Rate limiting options:
1. 100 requests/minute
2. 1000 requests/hour
3. Custom (specify)
```

#### Data Domain

```markdown
Validation options:
1. Client-side only
2. Server-side only
3. Both client and server
4. Real-time validation

Storage options:
1. Permanent until deleted
2. Time-limited (specify duration)
3. Session-only
```

---

## Question Quality Checklist

Before presenting a clarification question, verify:

| Check | Requirement |
|-------|-------------|
| Clear | Question is unambiguous |
| Actionable | User can provide a definitive answer |
| Complete | All necessary context provided |
| Options | 2-4 meaningful options offered |
| Traceable | Source CHK/FR clearly identified |
| Prioritized | Priority level indicated |

---

## Stale Question Refinement

When a question has been asked before (stale_count >= 2):

```markdown
[NEEDS CLARIFICATION: C3.1] ⚠️ (Attempt 3 of 3)
**Question**: What should happen when authentication fails?
**Previous Answer**: "Show an error"
**Why Insufficient**: Need specific error message text and display location

Please provide more specific details:
- Exact error message text
- Where the message should appear (modal, inline, toast)
- Whether form data should be preserved

**Options**:
1. Inline message: "The email or password you entered is incorrect. Please try again."
2. Modal popup with retry button
3. Custom (please specify exact text and location)

**Source**: CHK015 validating FR-003
**Priority**: Critical
```

---

## State Updates After Question Generation

### Update Gap Priority Queue

```markdown
| Priority | Gap ID | CHK Source | FR Reference | Question | Status | Clarification ID |
|----------|--------|------------|--------------|----------|--------|------------------|
| Critical | G-001 | CHK015 | FR-003 | Auth failure | clarifying | C1.1 |
| Important | G-004 | CHK022 | FR-007 | Session timeout | clarifying | C1.2 |
```

### Update Pending Questions

```markdown
## Pending Questions

| ID | Question Summary | Gaps | Status |
|----|------------------|------|--------|
| C1.1 | Auth failure handling | G-001, G-002, G-003 | awaiting_answer |
| C1.2 | Session management | G-004, G-005 | awaiting_answer |
```

### Update Priority Loop State

```markdown
## Priority Loop State

| Field | Value |
|-------|-------|
| **Loop Status** | clarifying |
| **Current Iteration** | 1 / 10 |
| **Pending Clarifications** | 2 (C1.1, C1.2) |
| **Last Activity** | 2024-01-15T10:30:00Z |
```

---

## Output Contract

The gap classifier returns:

```json
{
  "success": true,
  "clarifications_needed": true,
  "clarifications": [
    {
      "id": "C1.1",
      "priority": "Critical",
      "domain": "authentication",
      "question": "What should happen when authentication fails?",
      "sub_questions": [],
      "options": ["Display inline error", "Redirect to error page", "Lock account"],
      "source_gaps": ["G-001"],
      "source_chks": ["CHK015"],
      "fr_refs": ["FR-003"]
    },
    {
      "id": "C1.2",
      "priority": "Critical",
      "domain": "authentication",
      "question": "Regarding authentication error handling, please clarify:",
      "sub_questions": [
        "Error message text?",
        "Lockout after how many attempts?",
        "Lockout duration?"
      ],
      "options": {
        "error_message": ["Generic", "Specific", "Custom"],
        "lockout_attempts": ["3", "5", "No lockout"],
        "lockout_duration": ["15 min", "1 hour", "Admin unlock"]
      },
      "source_gaps": ["G-002", "G-003", "G-004"],
      "source_chks": ["CHK016", "CHK017", "CHK018"],
      "fr_refs": ["FR-003"]
    }
  ],
  "deferred_minor_gaps": 5,
  "grouping_summary": {
    "original_gaps": 8,
    "after_grouping": 2
  }
}
```
