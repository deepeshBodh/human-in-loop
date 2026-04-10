# Evolution Roadmap Template

This template defines the structure for gap analysis between current codebase state and constitution requirements.

---

```markdown
# Evolution Roadmap

> Generated: {{timestamp}}
> Based on: codebase-analysis.md, constitution.md
> Status: {{status}}

---

## Overview

This roadmap identifies gaps between current state and constitution requirements, organized by priority and dependency.

**Total Gaps**: {{total_count}}
- P1 (Critical): {{p1_count}}
- P2 (Important): {{p2_count}}
- P3 (Nice-to-have): {{p3_count}}

---

## Gap Summary

| ID | Title | Priority | Category | Blocks | Effort |
|----|-------|----------|----------|--------|--------|
| GAP-001 | {{title}} | P1 | Security | {{blocked_gaps}} | {{effort}} |
| GAP-002 | {{title}} | P2 | Testing | {{blocked_gaps}} | {{effort}} |
| ... | ... | ... | ... | ... | ... |

---

## Dependency Graph

```
[Foundation Layer]
    └── GAP-001: {{title}}
         ├── GAP-002: {{title}}
         │    └── GAP-005: {{title}}
         └── GAP-003: {{title}}

[Parallel Track: Testing]
    └── GAP-004: {{title}}
         └── GAP-006: {{title}}

[Independent]
    └── GAP-007: {{title}}
```

---

## Gap Cards

### GAP-001: {{title}}

| Aspect | Value |
|--------|-------|
| Priority | P1 |
| Category | Security |
| Blocks | {{what_this_prevents}} |
| Enables | {{what_fixing_unlocks}} |
| Relevant | {{when_this_gap_matters}} |
| Effort | Small \| Medium \| Large |

**Current state**: {{what_exists_now_from_codebase_analysis}}

**Target state**: {{what_constitution_requires}}

**Suggested approach**: {{how_to_address}}

**Related files**:
- `{{file_path_1}}`
- `{{file_path_2}}`

---

### GAP-002: {{title}}

| Aspect | Value |
|--------|-------|
| Priority | P2 |
| Category | Testing |
| Blocks | {{what_this_prevents}} |
| Enables | {{what_fixing_unlocks}} |
| Relevant | {{when_this_gap_matters}} |
| Effort | Small \| Medium \| Large |

**Current state**: {{what_exists_now}}

**Target state**: {{what_constitution_requires}}

**Suggested approach**: {{how_to_address}}

**Related files**:
- `{{file_path}}`

---

<!-- Additional gap cards follow same format -->

---

## Maintenance Protocol

### When Addressing Gaps

When working on features that address roadmap gaps:

1. **Note in commit**: Include "Addressed: GAP-XXX" in commit message
2. **Update gap status**: Mark gap as resolved (supervisor responsibility)
3. **Verify target state**: Confirm constitution requirement is now met

### When Discovering New Gaps

When agents discover issues not in roadmap:

1. **Note in report**: Include "Suggested gap: [description]"
2. **Supervisor decides**: Human reviews and approves roadmap updates
3. **Never auto-update**: Roadmap changes require explicit approval

### Gap Status Values

| Status | Meaning |
|--------|---------|
| `open` | Gap exists, not yet addressed |
| `in-progress` | Work underway to address |
| `resolved` | Gap closed, target state achieved |
| `deferred` | Explicitly deprioritized |
| `wont-fix` | Accepted as-is with justification |

---

## Priority Definitions

| Priority | Criteria | Action |
|----------|----------|--------|
| **P1** | Security gaps, blocking issues, constitution MUST violations | Address immediately |
| **P2** | Testing/Error Handling gaps, constitution SHOULD violations | Address in next sprint |
| **P3** | Observability, nice-to-haves, constitution MAY items | Address when convenient |

---

## Category Definitions

| Category | Scope |
|----------|-------|
| **Security** | Auth, secrets, validation, access control |
| **Testing** | Test coverage, CI gates, test infrastructure |
| **Error Handling** | Error types, context, status codes, recovery |
| **Observability** | Logging, metrics, tracing, monitoring |
| **Architecture** | Structure, patterns, dependencies |
| **Conventions** | Naming, formatting, style consistency |
```

---

## Usage Notes

1. **Status values**: `draft` (initial generation), `active` (in use), `archived` (superseded)
2. **Effort estimates**: `Small` (<1 day), `Medium` (1-3 days), `Large` (>3 days)
3. **This is a reference template** - Agent produces actual content following this structure
4. **Gap IDs are stable** - Once assigned, GAP-XXX should not be renumbered
