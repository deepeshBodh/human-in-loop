# Mapping Checks (Phase T1)

> Validation checks for task-mapping.md artifact.
> Used by Task-Validator Agent during Phase T1 of the tasks workflow.

---

## Overview

This module validates the task-mapping.md artifact produced by the Task-Planner agent. It ensures all user stories are extracted, components are properly mapped, and brownfield analysis is complete.

---

## Check Categories

### Story Coverage

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| MC-001 | `stories_complete` | All P1/P2 user stories from spec.md present in mapping | auto-retry |
| MC-002 | `priorities_valid` | Story priorities (P1, P2, P3) correctly extracted from spec | auto-retry |
| MC-003 | `stories_have_criteria` | Each story has acceptance criteria documented | auto-resolve |

### Entity Mapping

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| MC-004 | `entities_mapped` | All entities from data-model.md mapped to ≥1 story | auto-retry |
| MC-005 | `no_orphan_entities` | No entities without story assignment | auto-resolve |

### Endpoint Mapping

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| MC-006 | `endpoints_mapped` | All endpoints from contracts/ mapped to ≥1 story | auto-retry |
| MC-007 | `no_orphan_endpoints` | No endpoints without story assignment | auto-resolve |

### Brownfield Analysis

| ID | Check Name | Description | Tier |
|----|------------|-------------|------|
| MC-008 | `brownfield_identified` | If inventory exists, risks are documented | auto-retry |
| MC-009 | `high_risk_escalated` | High-risk collisions flagged for user review | escalate |
| MC-010 | `collision_actions_assigned` | Each collision has recommended action | auto-retry |

---

## Gap Classification

| Priority | Check IDs | Rationale |
|----------|-----------|-----------|
| **Critical** | MC-001, MC-002, MC-009 | Missing stories or unhandled collisions block task generation |
| **Important** | MC-004, MC-006, MC-008, MC-010 | Incomplete mapping affects task coverage |
| **Minor** | MC-003, MC-005, MC-007 | Quality issues, can auto-resolve or log |

---

## Detailed Check Specifications

### MC-001: stories_complete

**Description**: All P1 and P2 priority user stories from spec.md must be present in task-mapping.md.

**Validation Process**:
1. Read spec.md, extract all user stories with priorities
2. Filter for P1 and P2 stories
3. Read task-mapping.md, extract User Stories section
4. Compare: every P1/P2 from spec must exist in mapping

**Pass Condition**: All P1/P2 stories from spec are in mapping

**Fail Output**:
```json
{
  "gap_id": "GAP-T1-001",
  "check_id": "MC-001",
  "priority": "Critical",
  "description": "User story {story_id} ({priority}) from spec.md not found in mapping",
  "affected": "{story_id}",
  "guidance": "Add {story_id} to task-mapping.md with entity and endpoint mappings"
}
```

### MC-002: priorities_valid

**Description**: Story priorities must match spec.md exactly.

**Validation Process**:
1. For each story in mapping, check priority against spec.md
2. Verify format is P1, P2, or P3

**Pass Condition**: All priorities match spec.md

### MC-004: entities_mapped

**Description**: Every entity in data-model.md must be mapped to at least one user story.

**Validation Process**:
1. Read data-model.md, extract entity list
2. For each entity, verify it appears in at least one story's Mapped Components
3. If data-model.md doesn't exist, skip this check (pass)

**Pass Condition**: All entities from data-model appear in mapping

### MC-006: endpoints_mapped

**Description**: Every endpoint in contracts/ must be mapped to at least one user story.

**Validation Process**:
1. Read contracts/ directory, extract all endpoint definitions
2. For each endpoint, verify it appears in at least one story's Mapped Components
3. If contracts/ doesn't exist, skip this check (pass)

**Pass Condition**: All endpoints from contracts appear in mapping

### MC-008: brownfield_identified

**Description**: If codebase-inventory.json exists, brownfield analysis must be complete.

**Validation Process**:
1. Check if codebase-inventory.json exists
2. If exists, verify Brownfield Analysis section is populated
3. Verify existing entities and endpoints are listed

**Pass Condition**: Brownfield section complete OR no inventory exists

### MC-009: high_risk_escalated

**Description**: High-risk collisions must be flagged for user escalation.

**Validation Process**:
1. Check Brownfield Analysis section
2. For any item with Risk Level = "high", verify it's in High-Risk Collisions table
3. Verify resolution options are provided

**Pass Condition**: All high-risk items are flagged with options

**Fail Output**:
```json
{
  "gap_id": "GAP-T1-xxx",
  "check_id": "MC-009",
  "priority": "Critical",
  "tier": "escalate",
  "description": "High-risk collision on {item} requires user decision",
  "affected": "{item}",
  "user_question": "How should we handle the collision on {item}?",
  "options": ["{option1}", "{option2}", "{option3}"]
}
```

---

## Tier Behavior

### auto-resolve

For Minor gaps that can be fixed trivially:
- Add missing acceptance criteria from spec.md
- Log orphaned items as warnings

### auto-retry

For Important/Critical gaps that need agent correction:
- Return gap list to Supervisor
- Supervisor re-invokes Task-Planner with gap context
- Maximum 3 iterations before escalation

### escalate

For decisions requiring user input:
- High-risk collisions
- Ambiguous mappings
- Supervisor uses AskUserQuestion

---

## Example Validation Report

```json
{
  "check_module": "mapping-checks",
  "phase": "T1",
  "checks": [
    {"id": "MC-001", "name": "stories_complete", "result": "pass"},
    {"id": "MC-002", "name": "priorities_valid", "result": "pass"},
    {"id": "MC-003", "name": "stories_have_criteria", "result": "pass"},
    {"id": "MC-004", "name": "entities_mapped", "result": "fail", "gap": "GAP-T1-001"},
    {"id": "MC-005", "name": "no_orphan_entities", "result": "pass"},
    {"id": "MC-006", "name": "endpoints_mapped", "result": "pass"},
    {"id": "MC-007", "name": "no_orphan_endpoints", "result": "pass"},
    {"id": "MC-008", "name": "brownfield_identified", "result": "pass"},
    {"id": "MC-009", "name": "high_risk_escalated", "result": "pass"},
    {"id": "MC-010", "name": "collision_actions_assigned", "result": "pass"}
  ],
  "summary": {
    "total": 10,
    "passed": 9,
    "failed": 1,
    "critical": 0,
    "important": 1,
    "minor": 0
  }
}
```
