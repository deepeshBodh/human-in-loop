---
name: spec-writing
description: Reference manual for writing high-quality feature specifications. Provides decision frameworks, quality examples, and procedural guidance. Can be referenced by any agent that works with specifications (spec-writer, clarify, checklist validators).
---

# Spec Writing Skill

## Purpose

Comprehensive guidance for generating consistent, testable specifications from natural language descriptions. This skill serves as a shared reference manual for any agent that writes, validates, or interprets specifications.

---

## Decision Frameworks

### Priority Assessment Framework (P1/P2/P3)

Use these signals to extract priority from feature descriptions:

| Priority | Signals | Examples |
|----------|---------|----------|
| **P1** | Blocks other features, MVP-critical, user cannot proceed without, explicitly requested as "must have" | "Users need to log in before..." (blocking), "Core feature for launch" |
| **P2** | Important for completeness, workaround exists, can ship without initially, "should have" language | "Would be nice to also show...", "Users expect to be able to..." |
| **P3** | Enhances experience, user-requested but not essential, "could have", future consideration | "Eventually we want...", "Nice to have...", "For power users..." |

**Extraction from vague descriptions:**

| Description | Extracted Priority | Reasoning |
|-------------|-------------------|-----------|
| "Add user authentication" | P1 | Blocking—nothing works without auth |
| "Let users customize their dashboard" | P2 | Important UX but app functions without |
| "Add keyboard shortcuts for power users" | P3 | Enhancement, not core functionality |

### Clarification Threshold Framework

Apply this decision tree when encountering ambiguity:

```
1. Does ambiguity significantly affect SCOPE?
   └─ YES → [NEEDS CLARIFICATION] with priority: scope
   └─ NO → Continue to step 2

2. Are there SECURITY or COMPLIANCE implications?
   └─ YES → [NEEDS CLARIFICATION] with priority: security
   └─ NO → Continue to step 3

3. Does an INDUSTRY STANDARD provide a sensible default?
   └─ YES → Make assumption, document it
   └─ NO → Continue to step 4

4. Is the choice EASILY REVERSIBLE?
   └─ YES → Make assumption, document it
   └─ NO → Continue to step 5

5. Do MULTIPLE EQUALLY VALID interpretations exist?
   └─ YES → [NEEDS CLARIFICATION] with priority: ux or technical
   └─ NO → Make assumption based on minimal user friction
```

**Good vs Bad Clarification Decisions:**

| Situation | Good Decision | Bad Decision |
|-----------|---------------|--------------|
| "Support social login" (which providers?) | Clarify—scope impact, not reversible | Assume all major providers—over-commits |
| "Show timestamps" (which timezone?) | Assume user's local timezone—industry standard | Clarify—has sensible default |
| "Validate email" (how strictly?) | Assume RFC 5322 basic—reversible | Clarify—technical detail, low impact |
| "Allow file uploads" (which types?) | Clarify—security implications | Assume all types—security risk |

### Requirement Strength Framework (MUST/SHOULD/MAY)

| Keyword | When to Use | Examples |
|---------|-------------|----------|
| **MUST** | User safety, data integrity, core functionality, legal/compliance, feature doesn't work without | "System MUST encrypt passwords", "Users MUST authenticate before accessing data" |
| **SHOULD** | Best practice, recommended UX, performance expectations, important but workaround exists | "System SHOULD display loading indicator", "Form SHOULD validate before submission" |
| **MAY** | Convenience features, optional enhancements, future extensibility, nice-to-have | "System MAY remember user preferences", "Users MAY customize notification frequency" |

**Calibration Examples:**

| Requirement | Strength | Why |
|-------------|----------|-----|
| "Validate email format before submission" | MUST | Core functionality—prevents bad data |
| "Show password strength indicator" | SHOULD | Best practice UX, but submission works without |
| "Allow users to change email display format" | MAY | Convenience, not essential |

---

## Quality Calibration (Good vs Bad Comparisons)

### User Stories

| Good | Bad | Why |
|------|-----|-----|
| `### User Story 1 - Create Recurring Task (Priority: P1)`<br><br>`A user wants to set up tasks that automatically repeat on a schedule so they don't have to recreate routine items manually.`<br><br>`**Why this priority**: Core feature requested in description; without it users must manually duplicate tasks.`<br><br>`**Independent Test**: Create a daily recurring task, verify it appears the next day.`<br><br>`**Acceptance Scenarios**:`<br>`1. **Given** user is on task creation, **When** they select "Daily" recurrence, **Then** task appears each subsequent day`<br>`2. **Given** recurring task exists, **When** user completes today's instance, **Then** tomorrow's instance remains` | `User can create recurring tasks.` | Good version has INVEST criteria (Independent, testable), clear priority justification, specific acceptance scenarios with Given/When/Then. Bad version is vague, untestable, no priority. |

### Functional Requirements

| Good | Bad | Why |
|------|-----|-----|
| "**FR-001**: System MUST validate email format before form submission and display inline error message within 500ms of user stopping typing" | "System should handle emails properly" | Good: specific action, timing constraint, observable outcome. Bad: vague verb "handle", undefined "properly" |
| "**FR-002**: Users MUST be able to reset password via email link that expires after 24 hours and can only be used once" | "Password reset should work" | Good: measurable constraints (24h, single-use). Bad: undefined "work", no testable criteria |
| "**FR-003**: System SHOULD display loading indicator when any operation exceeds 200ms response time" | "Show loading when slow" | Good: specific threshold, clear trigger. Bad: subjective "slow", no threshold |

### Edge Cases

| Good | Bad | Why |
|------|-----|-----|
| "When user submits task description with exactly 10,000 characters (system limit), system accepts and saves without truncation" | "Large input handling" | Good: specific boundary value, expected behavior. Bad: vague category, no specific value |
| "When external OAuth provider returns timeout after 30 seconds, system displays 'Authentication service unavailable' and offers retry" | "Auth failures" | Good: specific failure condition, expected response. Bad: broad category, no specific scenario |
| "When two users edit the same task simultaneously, last save wins and first user sees 'Task was updated by [name]' on next load" | "Concurrent editing" | Good: specific conflict scenario, resolution strategy. Bad: just names a category |

### Success Criteria

| Good | Bad | Why |
|------|-----|-----|
| "**SC-001**: 80% of first-time users complete task creation flow without external assistance" | "Task creation is easy" | Good: measurable (80%), specific user group, observable outcome. Bad: subjective "easy" |
| "**SC-002**: Users locate the export feature within 10 seconds of actively searching" | "Export is discoverable" | Good: quantified time, specific user action. Bad: vague "discoverable" |
| "**SC-003**: Zero data loss during system maintenance windows" | "System is reliable" | Good: measurable (zero), specific scenario. Bad: subjective "reliable" |

---

## Specification Writing Procedures

### Phase 2: Writing Sections

#### Header Section
```markdown
- **Feature Branch**: {{feature_id}}
- **Created**: {{current_date}}
- **Status**: Draft
- **Input**: {{original_description_verbatim}}
```

#### User Scenarios & Testing (Mandatory)

Generate 2-5 user stories using this exact structure:

```markdown
### User Story N - [Brief Title] (Priority: P#)

[Describe this user journey in plain language - what they want to accomplish and why]

**Why this priority**: [Business value justification referencing P1/P2/P3 criteria]

**Independent Test**: [How this story can be verified in isolation]

**Acceptance Scenarios**:
1. **Given** [precondition/state], **When** [user action], **Then** [observable outcome]
2. **Given** [precondition/state], **When** [user action], **Then** [observable outcome]
```

#### Edge Cases (Mandatory)

Identify 3-5 boundary conditions from these categories:
- **System limits**: Maximum values, capacity boundaries (e.g., "10,000 character limit")
- **Invalid input**: Malformed data, empty fields, wrong types
- **External failures**: Third-party service timeouts, API errors
- **Concurrency**: Simultaneous access, race conditions
- **Permissions**: Unauthorized access attempts, role boundaries

#### Functional Requirements (Mandatory)

Format: `**FR-XXX**: [Subject] [MUST|SHOULD|MAY] [specific, testable action]`

```markdown
- **FR-001**: System MUST [specific capability with measurable criteria]
- **FR-002**: Users MUST be able to [specific action with observable outcome]
- **FR-003**: System SHOULD [recommended behavior with clear trigger]
- **FR-004**: Users MAY [optional capability]
```

#### Key Entities (If Data Involved)

Describe conceptually without implementation:
```markdown
**[Entity Name]**
- Purpose: [What this entity represents in the domain]
- Key attributes: [What information it holds, not data types]
- Relationships: [How it relates to other entities]
```

#### Success Criteria (Mandatory)

Format: `**SC-XXX**: [Measurable, user-focused outcome]`

Requirements:
- Technology-agnostic (no API response times, database metrics)
- User or business outcome focused
- Quantifiable where possible

### Phase 3: Clarification Handling

1. **First, make informed assumptions** based on:
   - Industry standards and common patterns
   - The project's existing features and conventions
   - Reasonable defaults that minimize user friction

2. **Only use [NEEDS CLARIFICATION]** when:
   - The choice significantly impacts scope, timeline, or UX
   - Multiple equally valid interpretations exist
   - No sensible default can be determined
   - Security or compliance implications are unclear

3. **Maximum 3 clarification markers** - prioritize by impact:
   - `scope` (highest): Affects what gets built
   - `security`: Affects data protection or access control
   - `ux`: Affects user experience significantly
   - `technical` (lowest): Implementation considerations

4. **Clarification format:**
   ```
   [NEEDS CLARIFICATION: Specific question? Options: A, B, C]
   ```

### Phase 4: Artifact Updates

#### Update specify-context.md

1. Set status to `writing`
2. Set current_agent to `spec-writer`
3. Update Specification Progress table with section statuses and counts
4. Add decision log entries for assumptions made
5. Add clarifications to Pending section:
   ```markdown
   | C1.1 | FR-003 | Which OAuth providers? | Google only, Google+GitHub, All major | scope |
   ```
6. Add handoff notes:
   ```markdown
   ### From Spec Writer Agent
   - Sections completed: [list]
   - Assumptions made: [list key assumptions]
   - Clarifications needed: [count] items
   - Ready for: Clarify Agent (if clarifications) or Validation
   ```

#### Sync to index.md

1. Update Document Availability Matrix:
   - Set spec.md status to `present`
   - Set spec.md last_modified to current timestamp
2. Update Workflow Status Table:
   - Set specify status to `writing` (or `validating` if proceeding)
   - Set specify last_run to current timestamp
   - Set specify agent to `spec-writer`
3. Initialize Priority Loop State:
   - Set loop_status to `spec_writing`
   - Set iteration_count to `0 / 10`
   - Set stale_count to `0 / 3`
4. Initialize Traceability Matrix:
   - Create Requirements -> Checklist Coverage table with all FR-xxx
   - Format: `| FR-001 | (none) | ○ No validation | - |`
5. Add decisions to Unified Decisions Log
6. Add clarifications to Unified Pending Questions (ID format: `Q-S{number}`)
7. Update last_sync timestamp

#### Create Validation Checklist

Create `{{feature_dir}}/checklists/requirements.md` with:
- Content Quality checks
- Requirement Completeness checks
- Feature Readiness checks

---

## Common Anti-Patterns

| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| **Technology leakage** | "Store in PostgreSQL", "Use React components" | Describe what, not how: "Persist user preferences", "Display interactive elements" |
| **Untestable requirements** | "System should be fast", "UX should be intuitive" | Add metrics: "Response within 2 seconds", "80% complete flow unassisted" |
| **Over-clarification** | 5+ [NEEDS CLARIFICATION] markers | Max 3; make assumptions for lower-impact decisions |
| **Implementation in spec** | "API endpoint returns JSON with fields..." | Describe capability: "System provides task data for external integrations" |
| **Vague acceptance criteria** | "User can do the thing" | Given/When/Then with specific states and outcomes |
| **Missing edge cases** | Only happy path described | Always include: limits, invalid input, failures, concurrency |
