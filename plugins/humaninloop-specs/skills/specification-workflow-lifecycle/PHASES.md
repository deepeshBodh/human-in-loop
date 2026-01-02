# Workflow Phases

The three phases of the specification workflow lifecycle.

---

## Phase A: Initial Specification

Create the initial specification with validation and gap identification.

### A1: Scaffold

**Purpose**: Create branch, directories, and initialize workflow state.

**Agent**: scaffold-agent

**Inputs**:
- Feature description from user

**Outputs**:
- `feature_id`: e.g., "005-user-auth"
- `paths.spec_file`: e.g., "specs/005-user-auth/spec.md"
- `paths.index_file`: e.g., "specs/005-user-auth/.workflow/index.md"
- `paths.feature_dir`: e.g., "specs/005-user-auth/"

**State After**:
- `loop_status`: "scaffolding" -> "spec_writing"

**Failure Handling**:
- Report error and stop workflow
- Do not proceed if scaffold fails

---

### A2: Write Specification

**Purpose**: Generate spec content from user description.

**Agent**: spec-writer (create mode)

**Inputs**:
- Feature description
- Paths from scaffold

**Outputs**:
- `spec.md` content (as artifact)
- `user_story_count`
- `requirement_count`
- `clarifications`: Initial Q-S# questions (if any)

**State After**:
- `loop_status`: "spec_writing" -> "validating"
- `document_availability.spec`: "present"

---

### A3: Validate Spec Structure

**Purpose**: Check spec against quality checks module.

**Agent**: validator-agent (from humaninloop-core)

**Inputs**:
- `spec.md` path
- `spec-checks.md` check module
- `index.md` path

**Outputs**:
- `result`: pass | partial | fail
- `gaps`: { critical: [], important: [], minor: [] }
- `auto_resolved[]`: Gaps automatically fixed
- `pending_retry[]`: Gaps needing spec-writer retry

**Branching**:
- If `result == "fail"` with critical gaps: Re-run A2 with guidance
- If `result == "partial"` or "pass": Proceed to A4

---

### A4: Generate Requirements Checklist

**Purpose**: Create "unit tests for English" for requirement quality.

**Agent**: checklist-agent (create mode)

**Inputs**:
- `spec.md` content
- `index.md` path

**Outputs**:
- Checklist file (as artifact)
- `items`: Generated checklist items
- `signals`: Extracted domain keywords

**State After**:
- `document_availability.checklists`: "present"

---

### A5: Classify Gaps

**Purpose**: Group validation gaps into clarification questions.

**Agent**: gap-classifier

**Inputs**:
- Gaps from validator (A3 or A4)
- Current iteration

**Outputs**:
- `clarifications`: Grouped questions (max 3)
- `grouping_summary`: { original_gaps, after_grouping }

**Branching**:
- If Critical + Important > 0: Proceed to Phase B
- If only Minor gaps: Skip to Phase C

---

## Phase B: Priority Loop

Iteratively resolve gaps until completion conditions are met.

```python
iteration = 1
max_iterations = 10

WHILE has_unresolved_gaps() AND iteration <= max_iterations:
    # B1: Present clarifications
    # B2: Apply answers
    # B3: Re-validate
    # B4: Check termination
    # B5: Update state
    iteration++
```

---

### B1: Present Clarifications

**Purpose**: Show clarification questions to user.

**Tool**: AskUserQuestion

**Inputs**:
- Clarifications from gap-classifier (or previous B3)

**Format**:
```
AskUserQuestion(
  questions: clarifications.map(c => ({
    question: c.question,
    header: c.id,  // "C1.1", "C1.2", etc.
    options: c.options,
    multiSelect: false
  }))
)
```

**Outputs**:
- User answers (one per clarification)

---

### B2: Apply Answers

**Purpose**: Integrate user answers into spec.

**Agent**: spec-writer (update mode)

**Inputs**:
- User answers from B1
- Current iteration
- `spec.md` and `index.md` paths

**Outputs**:
- Updated `spec.md` (as artifact)
- `answers_applied`: Count
- `gaps_resolved`: Count
- `remaining_gaps`: Count

**State After**:
- Gap statuses updated in gap_priority_queue
- Gap resolution history updated

---

### B3: Re-Validate

**Purpose**: Check if gaps are resolved.

**Agent**: validator-agent

**Inputs**:
- Updated `spec.md`
- `spec-checks.md`
- Current iteration

**Outputs**:
- `result`: pass | partial | fail
- Updated gap status
- `staleness`: Any stale gaps detected

**If new gaps found**: Run gap-classifier to generate new clarifications.

---

### B4: Check Termination

**Purpose**: Determine if loop should end.

See [TERMINATION.md](TERMINATION.md) for full conditions.

**Quick Check**:
```python
if critical + important == 0:
    terminate("success")
elif iteration >= 10:
    terminate("max_iterations")
elif same_gaps_for_3_iterations:
    terminate("stale")
elif resolved_this_iteration == 0:
    ask_user_to_decide()
```

---

### B5: Update State

**Purpose**: Persist loop state to index.md.

**Updates**:
```markdown
| **Loop Status** | validating |
| **Current Iteration** | {iteration} / 10 |
| **Last Activity** | {timestamp} |
| **Stale Count** | {stale_count} / 3 |
```

---

## Phase C: Completion

Finalize the specification and report results.

---

### C1: Log Deferred Minor Gaps

**Purpose**: Document Minor gaps that were not addressed.

**Output in index.md**:
```markdown
## Known Minor Gaps (Deferred)

| Gap ID | Description | FR Reference |
|--------|-------------|--------------|
| G-012 | Theme color options | FR-045 |
```

---

### C2: Finalize Traceability Matrix

**Purpose**: Ensure all requirements have checklist coverage.

**Output in index.md**:
```markdown
### Requirements -> Checklist Coverage

| FR ID | CHK IDs | Coverage Status |
|-------|---------|-----------------|
| FR-001 | CHK001, CHK015 | Covered |
| FR-002 | CHK005 | Covered |
```

---

### C3: Generate Quality Report

**Purpose**: Summarize workflow results.

**Output**:
```markdown
## Specification Quality Report

**Feature**: 005-user-auth
**Branch**: feat/005-user-auth

### Validation Summary
| Metric | Value |
|--------|-------|
| Total Iterations | 3 |
| Termination Reason | success |
| Critical Gaps Resolved | 5 |
| Important Gaps Resolved | 8 |
| Minor Gaps Deferred | 2 |
| Traceability Coverage | 95% |

### Next Steps
1. Review the spec at specs/005-user-auth/spec.md
2. Run /humaninloop:plan to create implementation plan
```

---

### C4: Update Final State

**Purpose**: Mark workflow as completed.

**Updates**:
```markdown
## Priority Loop State

| Field | Value |
|-------|-------|
| **Loop Status** | completed |
| **Termination Reason** | success |
| **Final Iteration** | 3 / 10 |
```

**Workflow Status**:
```markdown
| specify | completed | 2024-01-15T12:00:00Z | supervisor |
```
