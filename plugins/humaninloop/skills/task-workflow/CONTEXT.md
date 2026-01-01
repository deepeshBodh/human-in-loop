# Context Loading & Updating

Shared patterns for reading and updating context files across all task phases.

---

## Context Loading (All Phases)

### Required Files

| File | Purpose | Read For |
|------|---------|----------|
| `spec.md` | Source requirements | User stories, FR-xxx, acceptance criteria |
| `plan.md` | Technical decisions | Tech stack, project structure, conventions |
| `tasks-context.md` | Workflow state | Previous phase outputs, handoffs |
| `index.md` | Cross-workflow | Document availability, sync state |

### Phase-Specific Files

| Phase | Additional Files |
|-------|-----------------|
| T1: Mapping | `data-model.md`, `contracts/`, `research.md`, `codebase-inventory.json` |
| T2: Generation | `task-mapping.md` (required), all T1 inputs |

### Retry Handling

On retry iterations (iteration > 1):
1. Read existing phase artifact (`task-mapping.md` or `tasks.md`)
2. Focus on `gaps_to_resolve` from input
3. Preserve correct content, fix gaps only

---

## Updating tasks-context.md

### Workflow Metadata Section

```markdown
| **Status** | {phase_status} |
| **Current Agent** | {agent_name} |
| **Last Updated** | {timestamp} |
```

Status values: `planning`, `generating`, `validating`, `complete`

### Agent Handoff Notes

```markdown
### From {Agent Name} (Phase {N})

- **Items processed**: [count]
- **Mappings created**: [count] (T1) or **Tasks generated**: [count] (T2)
- **Brownfield items**: [count]
- **Gaps found**: [count]
- **Ready for**: [Validator or next phase]
```

### Phase-Specific Context

| Phase | Context to Update |
|-------|-------------------|
| T1 | Story mappings, entity mappings, endpoint mappings, brownfield risks |
| T2 | Task counts, phase counts, parallel opportunities, brownfield markers applied |

---

## Syncing to index.md

### Document Availability Matrix

Update status for artifacts created:
```markdown
| task-mapping.md | present | {timestamp} |
| tasks.md | present | {timestamp} |
```

### Tasks Phase State

```markdown
| **Phase** | T1 | T2 | completed |
| **Phase Name** | Mapping | Generation | - |
| **Current Iteration** | {current} / 3 |
| **Total Iterations** | {total} / 6 |
| **Last Agent** | {agent_name} |
```

### Unified Decisions Log

Add major decisions:
```markdown
| {timestamp} | tasks | {agent} | {decision_summary} | {rationale} |
```

### Tasks Gap Queue

If gaps found during validation:
```markdown
| Priority | Gap ID | Phase | Artifact | Issue | Status |
|----------|--------|-------|----------|-------|--------|
| Critical | GAP-T1-001 | T1 | task-mapping.md | Unmapped entity | pending |
```

---

## Tasks Traceability

Maintain in index.md:

### User Stories -> Tasks

```markdown
| Story ID | Priority | Task IDs | Coverage |
|----------|----------|----------|----------|
| US1 | P1 | T006, T007, T008 | Full |
```

### Tasks -> Files

```markdown
| Task ID | File Path | Marker | Status |
|---------|-----------|--------|--------|
| T006 | src/models/task.py | [EXTEND] | pending |
```

---

## Context Sync Checklist

Before returning, verify:
- [ ] tasks-context.md status updated
- [ ] tasks-context.md handoff notes written
- [ ] index.md document availability updated
- [ ] index.md tasks phase state updated
- [ ] index.md tasks gap queue updated (if gaps)
- [ ] index.md tasks traceability updated
- [ ] index.md last_sync timestamp updated
