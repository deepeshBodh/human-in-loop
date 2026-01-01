# Clarification Procedures

Complete workflow procedures for gap classification and answer application.

---

## Mode Selection

The spec-clarify agent operates in two modes:

| Mode | When | Input | Output |
|------|------|-------|--------|
| `classify_gaps` | After checklist validation | Gaps from checklist-agent | Clarification questions |
| `apply_answers` | After user responds | User answers | Updated spec |

---

## Gap Classification Mode

### Step 1: Load Inputs

Read the checklist-agent output (passed from supervisor):

```json
{
  "gaps": {
    "critical": [...],
    "important": [...],
    "minor": [...],
    "summary": { "critical": N, "important": N, "minor": N }
  }
}
```

Read current state from index.md:
- Current Gap Priority Queue
- Current iteration count
- Traceability Matrix state

### Step 2: Filter and Group

1. Filter to Critical + Important gaps only
2. Group related gaps using [GAP-CLASSIFICATION.md](GAP-CLASSIFICATION.md) rules
3. Prioritize groups (max 3 clarifications)

### Step 3: Generate Clarifications

For each group, generate clarification question:
- See [GAP-CLASSIFICATION.md](GAP-CLASSIFICATION.md) - Question Generation

### Step 4: Update State

1. Update Gap Priority Queue with `clarifying` status
2. Update Priority Loop State (loop_status = clarifying)
3. Add to Unified Pending Questions
4. Update Traceability Matrix

### Step 5: Return Results

```json
{
  "mode": "classify_gaps",
  "success": true,
  "clarifications_needed": true,
  "clarifications": [...],
  "deferred_minor_gaps": N
}
```

---

## Answer Application Mode

### Phase 1: Context Loading

1. Read **index.md** to understand cross-workflow state
2. Read the current specification file
3. Locate all `[NEEDS CLARIFICATION: ...]` markers
4. Match each marker to the corresponding answer ID from user input

### Phase 2: Answer Application

For each user answer:

1. Locate the exact `[NEEDS CLARIFICATION: ...]` marker in the spec
2. Replace the marker with naturally integrated content
3. Expand abbreviations and ensure formatting consistency

See [APPLICATION.md](APPLICATION.md) for patterns.

### Phase 2b: Gap-Derived Clarifications

For Priority Loop clarifications (C{iter}.{n} format):

1. Read the Gap Priority Queue to find source CHK and FR
2. Locate the original requirement
3. Apply answer as new sub-requirements or refinements
4. Update Gap Priority Queue status to `resolved`
5. Add entry to Gap Resolution History

### Phase 3: Cascading Updates

Check if answers affect other specification sections:

- **User Stories**: Scope or priority changes
- **Other Requirements**: Implied additional requirements
- **Success Criteria**: Measurement criteria changes
- **Edge Cases**: Newly revealed scenarios

Apply minimal, justified cascading updates only.

### Phase 4: Issue Scanning

After applying answers, scan for:

- Remaining `[NEEDS CLARIFICATION]` markers
- New ambiguities introduced by applied answers
- Inconsistencies between specification sections
- Requirements invalidated by new information

If new clarifications emerge and round < 3:
- Add maximum 3 new clarifications to pending

### Phase 5: Quality Validation

Verify against quality criteria:

- No implementation details in specification
- All requirements are testable
- Success criteria are measurable
- User stories are independently testable
- No remaining markers (or documented assumptions in round 3)

### Phase 6: State Updates

#### Update index.md

1. Update Gap Priority Queue:
   - Mark resolved gaps with status `resolved`
   - Keep unresolved gaps as `pending`

2. Update Gap Resolution History:
   - Add entries for each resolved gap
   - Include iteration number and resolution method

3. Update Traceability Matrix:
   - Update coverage status for affected FRs
   - Change `Gap Found` to `Covered` when resolved

4. Update Priority Loop State:
   - Update loop_status as appropriate
   - Update last activity timestamp

5. Update Unified Pending Questions:
   - Move resolved questions to answered
   - Add any new clarifications if within limits

6. Add entries to Unified Decisions Log

7. Update Feature Readiness if spec is now ready

8. Update last_sync timestamp

### Phase 7: Return Results

```json
{
  "mode": "apply_answers",
  "success": true,
  "answers_applied": N,
  "gaps_resolved": N,
  "remaining_gaps": N,
  "spec_ready": true|false,
  "assumptions_made": [...],  // Round 3 only
  "index_updated": true
}
```

---

## Round 3 Finality

When iteration reaches 3:

1. Apply all available answers normally
2. For unanswered clarifications, make reasonable assumptions
3. Document each assumption in the spec
4. Mark spec as READY with documented assumptions
5. Log all assumptions in handoff notes
6. Never introduce new `[NEEDS CLARIFICATION]` markers

See [APPLICATION.md](APPLICATION.md) - Round 3 Special Handling.

---

## Error Handling

### No Gaps to Process

```json
{
  "mode": "classify_gaps",
  "success": true,
  "clarifications_needed": false,
  "message": "No Critical or Important gaps. Workflow can complete."
}
```

### Max Clarifications Exceeded

```json
{
  "success": true,
  "clarifications": [...],  // Only first 3
  "overflow_gaps": N,
  "message": "Additional gaps will be addressed in next iteration"
}
```

### Stale Gaps Detected

```json
{
  "success": true,
  "stale_gaps": [...],
  "escalation_required": true,
  "message": "Gap unresolved after 3 iterations. User decision required."
}
```
