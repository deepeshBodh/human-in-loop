# Brownfield Handling

Guidelines for task phases when working with existing codebases.

---

## Detection

Brownfield mode applies when:
```
brownfield.has_inventory == true AND brownfield.is_greenfield == false
```

If greenfield (no existing codebase), skip brownfield considerations and generate tasks as new.

---

## Phase T1: Mapping - Risk Analysis

### Reading Codebase Inventory

Load `codebase-inventory.json` for:
- Existing entities and their file paths
- Existing endpoints and their file paths
- Collision risks already identified
- Domain vocabulary

### Entity Collision Detection

For each entity in data-model.md:
```
IF entity.name IN codebase_inventory.entities:
  → Check if adding fields (EXTEND) or changing fields (MODIFY)
  → Record existing file path
  → Flag high-risk if conflicting structure
```

### Endpoint Collision Detection

For each endpoint in contracts/:
```
IF endpoint.path IN codebase_inventory.endpoints:
  → Check if adding params (EXTEND) or changing behavior (MODIFY)
  → Record existing file path
  → Flag high-risk if incompatible change
```

### Risk Level Classification

| Scenario | Risk Level | Recommended Action |
|----------|------------|-------------------|
| Entity exists, adding fields | Low | EXTEND |
| Entity exists, changing fields | Medium | MODIFY |
| Entity exists, conflicting structure | High | CONFLICT - escalate |
| Endpoint exists, adding params | Low | EXTEND |
| Endpoint exists, changing behavior | Medium | MODIFY |
| Endpoint exists, incompatible change | High | CONFLICT - escalate |

### Recording in task-mapping.md

For each brownfield item, record:
```markdown
### Brownfield Analysis

| Entity/Endpoint | File Path | Risk Level | Recommended Action |
|-----------------|-----------|------------|-------------------|
| Task | src/models/task.py | Low | EXTEND |
| POST /api/tasks | src/routes/tasks.py | Medium | MODIFY |
```

---

## Phase T2: Generation - Marker Application

### Marker Types

| Marker | Meaning | When to Use |
|--------|---------|-------------|
| `[EXTEND]` | Adding to existing file | New fields, new methods, additional functionality |
| `[MODIFY]` | Changing existing code | Altering behavior, updating validation |
| `[CONFLICT]` | Needs manual resolution | High-risk collision, user decision required |

### Application Rules

For each task that touches files identified in brownfield analysis:

1. Check if file exists in `brownfield_risks` from task-mapping.md
2. Apply appropriate marker based on risk level:
   - Low risk → `[EXTEND]`
   - Medium risk → `[MODIFY]`
   - High risk → `[CONFLICT]`

### Task Format with Markers

```markdown
- [ ] T006 [EXTEND] [US1] Add priority field to Task model in src/models/task.py
- [ ] T012 [MODIFY] [US2] Update TaskService with filter in src/services/task_service.py
- [ ] T015 [CONFLICT] [US3] Resolve validation conflict in src/routes/tasks.py
```

### Marker Placement

Markers appear after Task ID, before story label:
```
- [ ] T### [BROWNFIELD_MARKER] [PARALLEL_FLAG?] [STORY_LABEL?] Description
```

Order: `[EXTEND|MODIFY|CONFLICT]` → `[P]` → `[US#]`

---

## Escalation Handling

### High-Risk Collisions

When `[CONFLICT]` marker needed:
1. Task cannot be auto-generated
2. Must be flagged for user decision
3. Supervisor will present options via AskUserQuestion

### Escalation Options Template

For each conflict, provide:
```json
{
  "type": "endpoint",
  "item": "POST /api/tasks",
  "conflict": "Existing validation logic incompatible with new priority field",
  "options": [
    {"action": "extend", "description": "Add priority as optional field"},
    {"action": "replace", "description": "Replace validation entirely"},
    {"action": "version", "description": "Create /v2/tasks endpoint"}
  ],
  "recommendation": "extend"
}
```

---

## Documentation Requirements

### In task-mapping.md (Phase T1)

- Brownfield Analysis section with all risks
- Collision resolutions applied
- High-risk items flagged

### In tasks.md (Phase T2)

- Brownfield markers on affected tasks
- Brownfield Summary section:
```markdown
## Brownfield Summary

| Marker | Count | Files |
|--------|-------|-------|
| [EXTEND] | 3 | src/models/task.py, ... |
| [MODIFY] | 2 | src/services/task_service.py, ... |
| [CONFLICT] | 1 | src/routes/tasks.py |
```

### In tasks-context.md

- Collision risks from T1
- Marker application decisions from T2
- User resolutions for conflicts
