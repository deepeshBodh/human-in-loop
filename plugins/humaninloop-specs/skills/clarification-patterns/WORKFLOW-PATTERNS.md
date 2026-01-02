# Clarification Workflow Patterns

Patterns for gap classification and answer application workflows.

---

## Agent Responsibilities

The clarification lifecycle is handled by two agents:

| Agent | Mode/Action | When | Input | Output |
|-------|-------------|------|-------|--------|
| Gap Classifier | `classify_gaps` | After checklist validation | Gaps from validator | Clarification questions |
| Spec Writer | `update` | After user responds | User answers | Updated spec |

---

## Gap Classification Patterns

### Filter and Group Pattern

1. Filter to Critical + Important gaps only (Minor gaps are deferred)
2. Group related gaps using [GAP-CLASSIFICATION.md](GAP-CLASSIFICATION.md) rules
3. Prioritize groups (max 3 clarifications per iteration)

### Clarification Generation

For each group, generate clarification question:
- See [GAP-CLASSIFICATION.md](GAP-CLASSIFICATION.md) - Question Generation

### State Update Pattern

After classification:
1. Update Gap Priority Queue with `clarifying` status
2. Update Priority Loop State (loop_status = clarifying)
3. Add to Unified Pending Questions
4. Update Traceability Matrix

---

## Round 3 Finality Pattern

When iteration reaches 3:

1. Apply all available answers normally
2. For unanswered clarifications, make reasonable assumptions
3. Document each assumption in the spec
4. Mark spec as READY with documented assumptions
5. Log all assumptions in handoff notes
6. Never introduce new `[NEEDS CLARIFICATION]` markers

See [APPLICATION.md](APPLICATION.md) - Round 3 Special Handling.

---

## Error Handling Patterns

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
