# Validation Procedures

Procedures for validating task workflow artifacts (task-validator agent).

---

## Mission

Validate task workflow artifacts against phase-specific check modules. Execute checks, classify gaps by severity, apply tiered behavior, and determine next action.

---

## Check Modules

| Phase | Check Module | Artifacts Validated |
|-------|--------------|---------------------|
| T1 | mapping-checks.md | task-mapping.md |
| T2 | task-checks.md | tasks.md, task-mapping.md |

---

## Check Execution

For each check in the module:

### 1. Parse Check Definition
- ID (MC-xxx for mapping, TC-xxx for tasks)
- Description
- Tier (auto-resolve, auto-retry, escalate)

### 2. Execute Check Logic
Compare artifact against criteria

### 3. Classify Gap (if failed)

| Priority | Description |
|----------|-------------|
| Critical | Blocks downstream phases |
| Important | Should be fixed before proceeding |
| Minor | Can be deferred |

### 4. Apply Tiered Behavior

| Tier | Action |
|------|--------|
| `auto-resolve` | Attempt fix, log action, mark resolved |
| `auto-retry` | Mark pending, provide guidance for task-builder |
| `escalate` | Mark escalating, prepare user-facing question |

---

## Phase T1: Mapping Checks

Key validations for task-mapping.md:

| Check | Priority | Tier |
|-------|----------|------|
| All P1/P2 stories present | Critical | auto-retry |
| All entities mapped to stories | Important | auto-retry |
| All endpoints mapped to stories | Important | auto-retry |
| Brownfield analysis complete | Important | auto-retry |
| High-risk collisions escalated | Critical | escalate |
| No orphaned entities | Minor | auto-resolve |
| No orphaned endpoints | Minor | auto-resolve |

---

## Phase T2: Task Checks

Key validations for tasks.md:

| Check | Priority | Tier |
|-------|----------|------|
| All tasks have checkbox | Critical | auto-retry |
| All tasks have Task ID | Critical | auto-retry |
| All tasks have file path | Important | auto-retry |
| Sequential Task IDs | Minor | auto-resolve |
| Brownfield markers applied | Important | auto-retry |
| Parallel flags valid | Minor | auto-resolve |
| Story labels in correct phases | Important | auto-retry |
| Dependencies valid (no cycles) | Critical | auto-retry |
| All mapped items have tasks | Critical | auto-retry |

---

## Result Determination

| Result | Condition | Next Action |
|--------|-----------|-------------|
| `pass` | 0 Critical, 0 Important | Proceed to next phase |
| `partial` | 0 Critical, >0 Important (all auto-resolved) | Proceed to next phase |
| `fail` | >0 Critical OR >0 Important (not resolved) | Loop back or escalate |

---

## Gap Queue Updates

For each gap found, add to index.md Tasks Gap Queue:

```markdown
| Priority | Gap ID | Check Source | Phase | Artifact | Description | Tier | Status |
|----------|--------|--------------|-------|----------|-------------|------|--------|
| Critical | GAP-T1-001 | MC-001 | T1 | task-mapping.md | Story US3 not mapped | auto-retry | pending |
| Important | GAP-T2-002 | TC-005 | T2 | tasks.md | T012-T015 missing paths | auto-retry | pending |
```

---

## Handoff Notes Format

```markdown
### From Validator (Phase {N})

**Check Module**: {module_name}
**Result**: {pass|partial|fail}

**Summary**:
- Total checks: {count}
- Passed: {count}
- Failed: {count}

**Gaps Found**:
- Critical: {count}
- Important: {count} ({auto_resolved_count} auto-resolved)
- Minor: {count}

**Tiered Actions**:
- Auto-resolved: {count}
- Auto-retry: {count}
- Escalated: {count}

**Next Action**: {proceed|retry|escalate}
**Loop Back To**: {task-builder} (if retry)
```

---

## Stale Detection

Track iteration progress:
```
current_gap_hash = hash(gaps.map(g => g.gap_id).sort().join(","))
if (current_gap_hash == previous_gap_hash):
  stale_count++
  if (stale_count >= 2):
    → Escalate to user
```

---

## Quality Checklist

- [ ] All checks from module executed
- [ ] Every failed check has gap entry
- [ ] Gap priority and tier correctly assigned
- [ ] Auto-resolved gaps have resolution details
- [ ] Escalated gaps have user-facing questions
- [ ] tasks-context.md has validator handoff notes
- [ ] index.md Tasks Gap Queue updated
- [ ] Next action correctly determined
- [ ] Stale count tracked (if applicable)
