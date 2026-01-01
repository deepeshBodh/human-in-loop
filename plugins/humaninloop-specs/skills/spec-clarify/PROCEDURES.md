# Clarification Procedures

Detailed procedures for each phase of the clarification workflow.

---

## Phase 1: Context Loading

1. Read **index.md** to understand cross-workflow state and unified pending questions
2. Read **specify-context.md** to understand pending clarifications and previous decisions
3. Read the current specification file and locate all `[NEEDS CLARIFICATION: ...]` markers
4. Match each marker to the corresponding answer ID from user input

---

## Phase 2: Answer Application

For each user answer:
1. Locate the exact `[NEEDS CLARIFICATION: ...]` marker in the spec
2. Replace the marker with naturally integrated content reflecting the user's answer
3. Expand abbreviations and ensure formatting consistency with surrounding text

See [PATTERNS.md](PATTERNS.md) for application examples.

---

## Phase 3: Cascading Updates

Check if answers affect other specification sections:
- **User Stories**: Scope or priority changes
- **Other Requirements**: Implied additional requirements
- **Success Criteria**: Measurement criteria changes
- **Edge Cases**: Newly revealed scenarios

Apply minimal, justified cascading updates only.

---

## Phase 4: Issue Scanning

After applying answers, scan for:
- Remaining `[NEEDS CLARIFICATION]` markers
- New ambiguities introduced by applied answers
- Inconsistencies between specification sections
- Requirements invalidated by new information

If new clarifications emerge and round < 3, add maximum 3 new clarifications to pending context.

---

## Phase 5: Quality Validation

Verify against quality criteria:
- No implementation details in specification
- All requirements are testable
- Success criteria are measurable
- User stories are independently testable
- No remaining `[NEEDS CLARIFICATION]` markers (or documented assumptions in round 3)

---

## Phase 6: Context Updates

### Update specify-context.md

1. Move applied clarifications from Pending to Resolved with location references
2. Add timestamped decision log entries
3. Set appropriate status: `ready`, `clarifying`, or `ready` with assumptions
4. Update current_agent to `spec-clarify`
5. Increment clarification round
6. Write detailed handoff notes documenting changes and remaining issues

### Sync to index.md

1. Move resolved questions from Unified Pending Questions to Unified Decisions Log:
   - Add entry: "Resolved Q-S{n}: {answer summary}"
2. Update Workflow Status Table:
   - Set specify status to `clarifying` or `validating`
   - Set specify last_run to current timestamp
   - Set specify agent to `spec-clarify`
3. Update Priority Loop State:
   - Keep loop_status as `clarifying`
   - Last activity timestamp
4. Update Gap Priority Queue:
   - Mark resolved gaps with status `resolved`
   - Keep unresolved gaps as `pending`
5. Update Gap Resolution History:
   - Add entries for each resolved gap with full details
   - Include iteration number and resolution method
6. Update Traceability Matrix:
   - Update coverage status for affected FRs
   - Change `⚠ Gap Found` to `✓ Covered` when gaps resolved
7. Add any new clarifications to Unified Pending Questions (if within Priority Loop)
8. Update Feature Readiness section if spec is now ready
9. Update last_sync timestamp

---

## Phase 7: Checklist Updates

Update the requirements checklist to reflect:
- Resolved clarification items (checked)
- Any remaining issues or assumptions
