# Task Checks (Phase T2)

> Validation checks for tasks.md artifact.
> Used by Task-Validator Agent during Phase T2 of the tasks workflow.

---

## Overview

This module validates the tasks.md artifact produced by the Task-Generator agent. It ensures proper task format, complete coverage, valid dependencies, and correct brownfield marker application.

---

## Check Categories

### Format Validation

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| TC-001 | `format_correct` | All tasks follow `- [ ] T### [markers] description path` format | auto-retry |
| TC-002 | `ids_sequential` | Task IDs are sequential (T001, T002, ...) | auto-resolve |
| TC-003 | `paths_specified` | Every task has a specific file path | auto-retry |

### Coverage Validation

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| TC-004 | `stories_covered` | Every P1/P2 story from mapping has implementation tasks | auto-retry |
| TC-005 | `entities_covered` | All mapped entities have corresponding tasks | auto-retry |
| TC-006 | `endpoints_covered` | All mapped endpoints have corresponding tasks | auto-retry |

### Structure Validation

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| TC-007 | `phases_structured` | Setup → Foundational → Stories → Polish order | auto-retry |
| TC-008 | `story_labels_correct` | User story phase tasks have [US#] labels | auto-retry |
| TC-009 | `foundation_no_labels` | Setup/Foundational/Polish tasks do NOT have story labels | auto-resolve |

### Dependency Validation

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| TC-010 | `dependencies_valid` | No circular dependencies, referenced tasks exist | auto-retry |
| TC-011 | `parallel_safe` | [P] tasks don't modify same files | auto-retry |

### Brownfield Validation

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| TC-012 | `brownfield_markers_applied` | Markers match brownfield analysis from mapping | auto-retry |
| TC-013 | `conflict_tasks_flagged` | [CONFLICT] tasks have clear resolution guidance | escalate |

---

## Gap Classification

| Priority | Check IDs | Rationale |
|----------|-----------|-----------|
| **Critical** | TC-001, TC-003, TC-004, TC-013 | Format errors or missing coverage block implementation |
| **Important** | TC-005, TC-006, TC-007, TC-008, TC-010, TC-011, TC-012 | Quality issues affecting task execution |
| **Minor** | TC-002, TC-009 | Cosmetic issues, can auto-fix |

---

## Detailed Check Specifications

### TC-001: format_correct

**Description**: Every task must follow the exact format specification.

**Required Format**:
```
- [ ] T### [Marker?] [P?] [Story?] Description with file path
```

**Components**:
- `- [ ]` - Checkbox (required)
- `T###` - Sequential ID (required)
- `[EXTEND]`/`[MODIFY]`/`[CONFLICT]` - Brownfield marker (optional)
- `[P]` - Parallel flag (optional)
- `[US#]` - Story label (required for story phases only)
- Description with file path (required)

**Validation Process**:
1. Parse each line starting with `- [ ]`
2. Extract Task ID (must match T\d{3} pattern)
3. Verify file path present in description

**Pass Condition**: All tasks match format

**Fail Output**:
```json
{
  "gap_id": "GAP-T2-001",
  "check_id": "TC-001",
  "priority": "Critical",
  "description": "Task {task_id} has invalid format: {issue}",
  "affected": "{task_id}",
  "guidance": "Fix format: - [ ] T### description with path/to/file.ext"
}
```

### TC-003: paths_specified

**Description**: Every task must include a file path.

**Validation Process**:
1. For each task, extract description text
2. Search for file path pattern (contains `/` and file extension)
3. Verify path is specific (not "various files" or similar)

**Pass Condition**: All tasks have specific file paths

### TC-004: stories_covered

**Description**: Every P1/P2 user story must have corresponding implementation tasks.

**Validation Process**:
1. Read task-mapping.md, get list of P1/P2 stories
2. For each story, verify tasks.md has a phase for that story
3. Verify the phase contains implementation tasks

**Pass Condition**: All P1/P2 stories have task phases

### TC-007: phases_structured

**Description**: Phases must be in correct order.

**Required Order**:
1. Phase 1: Setup
2. Phase 2: Foundational
3. Phases 3+: User Stories (in priority order P1, P2, P3)
4. Final Phase: Polish

**Validation Process**:
1. Parse all phase headers
2. Verify Setup comes first
3. Verify Foundational comes second
4. Verify Stories are in priority order
5. Verify Polish comes last

**Pass Condition**: Phase order matches specification

### TC-010: dependencies_valid

**Description**: Task dependencies must be valid.

**Validation Process**:
1. Parse Dependencies section
2. For each dependency (T### requires T###):
   - Verify both tasks exist
   - Check for circular references
3. Build dependency graph and check for cycles

**Pass Condition**: No circular deps, all referenced tasks exist

### TC-011: parallel_safe

**Description**: Tasks marked [P] must not conflict.

**Validation Process**:
1. Find all tasks with [P] marker
2. Group by phase/section
3. For each group, check file paths
4. Flag if multiple [P] tasks modify same file

**Pass Condition**: No file conflicts in parallel groups

### TC-012: brownfield_markers_applied

**Description**: Brownfield markers must match analysis.

**Validation Process**:
1. Read task-mapping.md Brownfield Analysis section
2. For each flagged file, find corresponding task(s)
3. Verify task has correct marker ([EXTEND], [MODIFY], [CONFLICT])

**Pass Condition**: All brownfield tasks have correct markers

### TC-013: conflict_tasks_flagged

**Description**: [CONFLICT] tasks need resolution guidance.

**Validation Process**:
1. Find all tasks with [CONFLICT] marker
2. Verify each has associated resolution guidance
3. If no guidance, escalate for user decision

**Pass Condition**: All [CONFLICT] tasks have guidance OR none exist

**Fail Output**:
```json
{
  "gap_id": "GAP-T2-xxx",
  "check_id": "TC-013",
  "priority": "Critical",
  "tier": "escalate",
  "description": "Task {task_id} has [CONFLICT] marker but no resolution guidance",
  "affected": "{task_id}",
  "user_question": "How should the conflict in {task_description} be resolved?",
  "options": ["Skip task", "Provide manual guidance", "Remove conflict marker"]
}
```

---

## Tier Behavior

### auto-resolve

For Minor gaps that can be fixed trivially:
- Renumber task IDs to be sequential
- Remove story labels from Setup/Foundational phases

### auto-retry

For Important/Critical gaps that need agent correction:
- Return gap list to Supervisor
- Supervisor re-invokes Task-Generator with gap context
- Maximum 3 iterations before escalation

### escalate

For decisions requiring user input:
- [CONFLICT] tasks without guidance
- Ambiguous coverage requirements
- Supervisor uses AskUserQuestion

---

## Example Validation Report

```json
{
  "check_module": "task-checks",
  "phase": "T2",
  "checks": [
    {"id": "TC-001", "name": "format_correct", "result": "pass"},
    {"id": "TC-002", "name": "ids_sequential", "result": "pass"},
    {"id": "TC-003", "name": "paths_specified", "result": "fail", "gap": "GAP-T2-001"},
    {"id": "TC-004", "name": "stories_covered", "result": "pass"},
    {"id": "TC-005", "name": "entities_covered", "result": "pass"},
    {"id": "TC-006", "name": "endpoints_covered", "result": "pass"},
    {"id": "TC-007", "name": "phases_structured", "result": "pass"},
    {"id": "TC-008", "name": "story_labels_correct", "result": "pass"},
    {"id": "TC-009", "name": "foundation_no_labels", "result": "pass"},
    {"id": "TC-010", "name": "dependencies_valid", "result": "pass"},
    {"id": "TC-011", "name": "parallel_safe", "result": "pass"},
    {"id": "TC-012", "name": "brownfield_markers_applied", "result": "pass"},
    {"id": "TC-013", "name": "conflict_tasks_flagged", "result": "pass"}
  ],
  "summary": {
    "total": 13,
    "passed": 12,
    "failed": 1,
    "critical": 1,
    "important": 0,
    "minor": 0
  }
}
```
