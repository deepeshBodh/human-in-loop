# Specification Writing Procedures

Detailed procedures for writing specifications and updating workflow artifacts.

---

## Phase 2: Writing Sections

### Header Section

```markdown
- **Feature Branch**: {{feature_id}}
- **Created**: {{current_date}}
- **Status**: Draft
- **Input**: {{original_description_verbatim}}
```

### User Scenarios & Testing (Mandatory)

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

### Edge Cases (Mandatory)

Identify 3-5 boundary conditions from these categories:
- **System limits**: Maximum values, capacity boundaries (e.g., "10,000 character limit")
- **Invalid input**: Malformed data, empty fields, wrong types
- **External failures**: Third-party service timeouts, API errors
- **Concurrency**: Simultaneous access, race conditions
- **Permissions**: Unauthorized access attempts, role boundaries

### Functional Requirements (Mandatory)

Format: `**FR-XXX**: [Subject] [MUST|SHOULD|MAY] [specific, testable action]`

```markdown
- **FR-001**: System MUST [specific capability with measurable criteria]
- **FR-002**: Users MUST be able to [specific action with observable outcome]
- **FR-003**: System SHOULD [recommended behavior with clear trigger]
- **FR-004**: Users MAY [optional capability]
```

### Key Entities (If Data Involved)

Describe conceptually without implementation:

```markdown
**[Entity Name]**
- Purpose: [What this entity represents in the domain]
- Key attributes: [What information it holds, not data types]
- Relationships: [How it relates to other entities]
```

### Success Criteria (Mandatory)

Format: `**SC-XXX**: [Measurable, user-focused outcome]`

Requirements:
- Technology-agnostic (no API response times, database metrics)
- User or business outcome focused
- Quantifiable where possible

---

## Phase 3: Clarification Handling

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

---

## Phase 4: Artifact Updates

### Update specify-context.md

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

### Sync to index.md

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

### Create Validation Checklist

Create `{{feature_dir}}/checklists/requirements.md` with:
- Content Quality checks
- Requirement Completeness checks
- Feature Readiness checks
