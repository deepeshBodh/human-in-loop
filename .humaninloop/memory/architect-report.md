# Architect Report: Evolution Roadmap (v3.0.0)

> Phase: Evolution Roadmap
> Date: 2026-02-19
> Agent: Principal Architect
> Constitution: v3.0.0
> Codebase Analysis: 2026-02-19

---

## Gap Summary

Gap analysis of the HumanInLoop codebase against the v3.0.0 constitution (12 principles) identified **5 gaps**. This is a significant reduction from the v2 roadmap (7 gaps), with GAP-001 (CI) resolved, GAP-004 (ratchet) superseded, and GAP-005 (validator migration) out of scope.

| Priority | Count | Gaps |
|----------|-------|------|
| P1 (Critical) | 0 | -- |
| P2 (Important) | 2 | GAP-003, GAP-008 |
| P3 (Nice-to-have) | 3 | GAP-009, GAP-010, GAP-011 |

**10 of 12 principles are fully compliant.** The two partial-compliance principles are:
- Principle I (Security): Missing secret scanning in CI (GAP-003)
- Principle XI (Layer Dependency): Import hierarchy is clean but lacks an automated enforcement test (GAP-008)

---

## Critical Gaps (P1)

None. The project has no critical gaps. All P1 items from the v2 roadmap (GAP-001: CI workflow, GAP-002: CLAUDE.md sync) have been resolved.

---

## Important Gaps (P2)

### GAP-003: Add secret scanning to CI

- **Principle**: I (Security by Default)
- **Category**: Security (Essential Floor)
- **Status**: Carried forward from v1.0.0 -- the longest-standing open gap in the project
- **Impact**: Only remaining Essential Floor gap. Without secret scanning, accidental credential commits rely on `.gitignore` patterns and manual review
- **Effort**: Small -- add a step to the existing `.github/workflows/ci.yml`
- **Blocker removed**: GAP-001 (CI) is resolved, so this can proceed immediately

### GAP-008: Add layer dependency enforcement test

- **Principle**: XI (Layer Dependency Discipline)
- **Category**: Testing/Architecture
- **Status**: New gap identified in v3.0.0 analysis
- **Impact**: The `entities -> graph -> validators -> passes -> cli` import hierarchy is currently clean (verified by grep), but compliance depends on code review alone. A pytest test would catch violations automatically before review
- **Effort**: Small -- single test file scanning imports against a rules table

---

## Dependency Chain

No blocking dependencies exist between any gaps. All 5 gaps can be addressed independently and in parallel.

```
[All Independent -- no blocking relationships]
    GAP-003: Add secret scanning to CI ............... P2, Small
    GAP-008: Add layer dependency enforcement test .... P2, Small
    GAP-009: Resolve specs/ directory reference ........ P3, Small
    GAP-010: Update constitution skill counts .......... P3, Small
    GAP-011: Add CODEOWNERS file ...................... P3, Small
```

This is a significant improvement from the v2 roadmap where GAP-001 (CI) blocked GAP-003 and GAP-004. With CI resolved, the entire dependency chain is flattened.

**Recommended order**: GAP-003 and GAP-008 first (parallel), then P3 items in any order.

---

## What Changed from v2 Roadmap

| v2 Gap | Status | Disposition |
|--------|--------|-------------|
| GAP-001: CI workflow | Resolved | `.github/workflows/ci.yml` exists with tests, coverage, syntax, commit lint |
| GAP-002: CLAUDE.md sync | Resolved | Synchronized with constitution v3.0.0 |
| GAP-003: Secret scanning | Carried forward | Blocker removed (CI exists), priority unchanged (P2) |
| GAP-004: Coverage ratchet | Superseded | Constitution v3.0.0 removed ratchet; 90% flat floor only |
| GAP-005: Validator migration | Out of scope | Constitution v3.0.0 removed plugin validators from governance |
| GAP-006: specs/ directory | Renumbered to GAP-009 | Carried forward as P3 |
| GAP-007: CODEOWNERS | Renumbered to GAP-011 | Carried forward as P3 |
| GAP-008: Layer test | -- | New gap identified in v3.0.0 analysis |
| GAP-010: Skill counts | -- | New gap identified in v3.0.0 analysis |

---

## Operational Notes

1. **Coverage baseline mismatch**: `.coverage-baseline` contains `98` and CI enforces a ratchet against it. Constitution v3.0.0 removed the ratchet -- 90% flat floor is authoritative. The ratchet step is not a gap (it is stricter than required) but could cause CI failures if coverage dips below 98%. Consider removing the ratchet step or documenting it as a voluntary operational standard.

2. **Skill count drift pattern**: Two skills added without updating constitution counts suggests the amendment process may be too heavyweight for PATCH-level changes. Consider whether exact counts belong in the constitution or whether Principle VII should reference the skill directory as source of truth.

---

## Artifacts Produced

| Artifact | Location |
|----------|----------|
| Evolution Roadmap | `.humaninloop/memory/evolution-roadmap.md` |
| Architect Report | `.humaninloop/memory/architect-report.md` |

Both artifacts are based on:
- Codebase analysis at `.humaninloop/memory/codebase-analysis.md`
- Constitution at `.humaninloop/memory/constitution.md` (v3.0.0)
- CI workflow at `.github/workflows/ci.yml`
- Verified: layer imports (grep, zero violations), skill directories (27 count), ADRs (7 files), test suite (381 tests), quality gates (all automated except secret scanning)
