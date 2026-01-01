# Quality Calibration Examples

Good vs bad comparisons for calibrating specification quality. Use these to understand what "testable" and "specific" look like in practice.

---

## User Stories

| Good | Bad | Why |
|------|-----|-----|
| `### User Story 1 - Create Recurring Task (Priority: P1)`<br><br>`A user wants to set up tasks that automatically repeat on a schedule so they don't have to recreate routine items manually.`<br><br>`**Why this priority**: Core feature requested in description; without it users must manually duplicate tasks.`<br><br>`**Independent Test**: Create a daily recurring task, verify it appears the next day.`<br><br>`**Acceptance Scenarios**:`<br>`1. **Given** user is on task creation, **When** they select "Daily" recurrence, **Then** task appears each subsequent day`<br>`2. **Given** recurring task exists, **When** user completes today's instance, **Then** tomorrow's instance remains` | `User can create recurring tasks.` | Good version has INVEST criteria (Independent, testable), clear priority justification, specific acceptance scenarios with Given/When/Then. Bad version is vague, untestable, no priority. |

---

## Functional Requirements

| Good | Bad | Why |
|------|-----|-----|
| "**FR-001**: System MUST validate email format before form submission and display inline error message within 500ms of user stopping typing" | "System should handle emails properly" | Good: specific action, timing constraint, observable outcome. Bad: vague verb "handle", undefined "properly" |
| "**FR-002**: Users MUST be able to reset password via email link that expires after 24 hours and can only be used once" | "Password reset should work" | Good: measurable constraints (24h, single-use). Bad: undefined "work", no testable criteria |
| "**FR-003**: System SHOULD display loading indicator when any operation exceeds 200ms response time" | "Show loading when slow" | Good: specific threshold, clear trigger. Bad: subjective "slow", no threshold |

---

## Edge Cases

| Good | Bad | Why |
|------|-----|-----|
| "When user submits task description with exactly 10,000 characters (system limit), system accepts and saves without truncation" | "Large input handling" | Good: specific boundary value, expected behavior. Bad: vague category, no specific value |
| "When external OAuth provider returns timeout after 30 seconds, system displays 'Authentication service unavailable' and offers retry" | "Auth failures" | Good: specific failure condition, expected response. Bad: broad category, no specific scenario |
| "When two users edit the same task simultaneously, last save wins and first user sees 'Task was updated by [name]' on next load" | "Concurrent editing" | Good: specific conflict scenario, resolution strategy. Bad: just names a category |

---

## Success Criteria

| Good | Bad | Why |
|------|-----|-----|
| "**SC-001**: 80% of first-time users complete task creation flow without external assistance" | "Task creation is easy" | Good: measurable (80%), specific user group, observable outcome. Bad: subjective "easy" |
| "**SC-002**: Users locate the export feature within 10 seconds of actively searching" | "Export is discoverable" | Good: quantified time, specific user action. Bad: vague "discoverable" |
| "**SC-003**: Zero data loss during system maintenance windows" | "System is reliable" | Good: measurable (zero), specific scenario. Bad: subjective "reliable" |

---

## Pattern Summary

**Good specifications have:**
- Specific numbers and thresholds
- Observable behaviors
- Given/When/Then structure for scenarios
- Measurable success metrics

**Bad specifications have:**
- Vague adjectives ("fast", "easy", "properly")
- Undefined behaviors ("should work", "handle X")
- Missing boundaries and limits
- Subjective criteria
