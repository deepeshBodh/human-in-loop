# Implementation Plan: Plan Command Performance Optimization

**Issue**: [#28](https://github.com/deepeshBodh/human-in-loop/issues/28)
**Related Feedback**: [#22](https://github.com/deepeshBodh/human-in-loop/issues/22) - [F1] Plan takes too long to run

## Overview

The `/humaninloop:plan` command has performance bottlenecks resulting in:
- **Best case**: ~7-8 min
- **Worst case**: ~20-30 min (with clarification iterations)

This plan implements two surgical quick wins that preserve devil's advocate rigor while eliminating waste.

---

## Quick Win 1: Reuse Setup's Codebase Analysis (REVISED)

### Problem

`analysis-codebase` skill is invoked in all 3 phases (research, datamodel, contracts), adding ~2-4 min of wasted computation. The codebase is static during planning—rerunning provides no value.

### Solution (Revised)

Instead of creating a new caching mechanism, **reuse the analysis artifact already created by `/humaninloop:setup`**:

1. Setup already creates `.humaninloop/memory/codebase-analysis.md` for brownfield projects
2. Setup now writes `project_type: brownfield|greenfield` to constitution
3. Plan reads constitution → if brownfield, requires analysis file exists
4. Plan reads cached analysis instead of invoking skill
5. If analysis missing for brownfield project → block with clear message

### Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Reuse vs. separate cache | **Reuse setup's** | Single source of truth, no duplication |
| Missing analysis behavior | **Require setup first** | Clean workflow enforcement over convenience |
| Brownfield detection | **Explicit flag in constitution** | `project_type` field—explicit over heuristic |
| Stale analysis handling | **Warn but proceed** | Visibility (>14 days warning) without blocking |

### Benefits Over Original Proposal

| Aspect | Original (feature-scoped cache) | Revised (reuse setup) |
|--------|--------------------------------|----------------------|
| Analysis artifacts | 2 locations | 1 location |
| New code | Cache mechanism + reading | Entry gate check only |
| Workflow coupling | Loose | Explicit (clean) |
| Staleness handling | Not addressed | Warning if >14 days |

### Implementation

#### Step 1: Add project_type to Constitution (setup.md)

**File**: `plugins/humaninloop/commands/setup.md`

Add `project_type: brownfield` or `project_type: greenfield` to constitution output in Phase 3.

- Brownfield mode: `project_type: brownfield`
- Greenfield mode: `project_type: greenfield`

#### Step 2: Add Brownfield Entry Gate (plan.md)

**File**: `plugins/humaninloop/commands/plan.md`

After existing entry gate (spec.md check), add brownfield check:

1. Read constitution → extract `project_type`
2. If brownfield:
   - Check `.humaninloop/memory/codebase-analysis.md` exists
   - If missing → block with AskUserQuestion directing to setup
   - If found → check age, warn if >14 days, proceed
3. If greenfield → proceed (no analysis needed)

#### Step 3: Update Phase Instructions (plan.md)

Remove `analysis-codebase` skill references from phases 2, 3, 4.
Add brownfield context reading instructions instead.

#### Step 4: Update Plan Architect (plan-architect.md)

**File**: `plugins/humaninloop/agents/plan-architect.md`

Update each phase's skill section to:
- Remove `analysis-codebase` skill invocation
- Add note to read from `.humaninloop/memory/codebase-analysis.md`
- Reference existing "Brownfield Context Files" section

#### Step 5: Update Context Template (plan-context-template.md)

**File**: `plugins/humaninloop/templates/plan-context-template.md`

Add fields:
- `project_type`: brownfield|greenfield
- `codebase_analysis_path`: path to cached analysis
- `codebase_analysis_age`: age in days for visibility

---

## Quick Win 2: Incremental + Checklist Validation

### Problem

Devil's Advocate fully re-reads ALL previous artifacts each phase, causing cumulative slowdown. By Phase 3, it reads spec + research + data-model + contracts.

### Solution

1. Fully validate only the **new** artifact each phase
2. Cross-check previous artifacts via lightweight consistency checklist
3. Preserve rigor users value while eliminating redundant full re-reads

### Implementation

#### Step 1: Create Cross-Artifact Consistency Checklist

**New File**: `plugins/humaninloop/templates/cross-artifact-checklist.md`

```markdown
# Cross-Artifact Consistency Checklist

Use this lightweight checklist to verify previous artifacts remain consistent with the new artifact, without re-reading them in full.

## Quick Consistency Checks

### Entity Name Consistency
- [ ] New artifact uses same entity names as data-model.md
- [ ] No new entities introduced that aren't in data-model.md
- [ ] Spelling/casing matches exactly

### Requirement Traceability
- [ ] New artifact references FR-XXX / US-XXX IDs correctly
- [ ] No orphaned requirements (mentioned but not addressed)
- [ ] No invented requirements (addressed but not in spec)

### Decision Consistency
- [ ] New artifact honors decisions from research.md
- [ ] No contradictions with chosen technologies/approaches
- [ ] Rationale still applies

### Naming Conventions
- [ ] API endpoints follow patterns established in research
- [ ] Field names match data model attributes
- [ ] Error codes are consistent

## How to Use

1. **Scan for entity mentions** in new artifact
2. **Cross-reference against data-model.md entity list**
3. **Spot-check 2-3 requirement IDs** trace correctly
4. **Flag inconsistencies** as Important issues

This checklist replaces full re-read of previous artifacts. It takes ~1-2 minutes vs ~5-10 minutes for full review.
```

#### Step 2: Create Incremental Review Skill Enhancement

**File**: `plugins/humaninloop/skills/validation-plan-artifacts/SKILL.md`

Add new section after "Review Process" (around line 68):

```markdown
## Incremental Review Mode

For phases after the first artifact (data-model, contracts), use incremental review:

### Full Review (New Artifact Only)
- Execute ALL phase-specific checks from PHASE-CHECKLISTS.md
- Document issues with full evidence
- This is your primary focus

### Consistency Check (Previous Artifacts)
- Use the cross-artifact checklist (NOT full re-read)
- Spot-check entity names, requirement IDs, decision references
- Flag only inconsistencies between artifacts
- Time budget: 1-2 minutes maximum

### When to Escalate to Full Re-Review
- If 2+ consistency issues found → re-read that specific artifact
- If contradictions detected → flag for supervisor
- If unsure → note uncertainty in report, recommend targeted review

### Report Format (Incremental Mode)

```markdown
## Review Summary

| Aspect | Status |
|--------|--------|
| **New Artifact** | {artifact} - FULL REVIEW |
| **Previous Artifacts** | CONSISTENCY CHECK ONLY |

## New Artifact Issues
{Full issue documentation}

## Cross-Artifact Consistency
| Check | Status | Notes |
|-------|--------|-------|
| Entity names | ✓/✗ | {any mismatches} |
| Requirement IDs | ✓/✗ | {any gaps} |
| Decision alignment | ✓/✗ | {any contradictions} |
```
```

#### Step 3: Update Devil's Advocate Instructions

**File**: `plugins/humaninloop/agents/devils-advocate.md`

Add section after "Plan Artifact Reviews" (around line 117):

```markdown
## Incremental Validation Protocol

To optimize review time while maintaining rigor:

### Phase 1 (Research): Full Review
- Full review of research.md against spec.md
- No previous artifacts to check

### Phase 2 (Data Model): Incremental
- **Full review**: data-model.md
- **Consistency check**: research.md (entity names, decision references)
- Use cross-artifact checklist, NOT full re-read

### Phase 3 (Contracts): Incremental
- **Full review**: contracts/api.yaml + quickstart.md
- **Consistency check**: research.md, data-model.md
- Use cross-artifact checklist for previous artifacts

### What This Means in Practice

| Phase | Full Review | Consistency Check |
|-------|-------------|-------------------|
| Research | spec → research | — |
| Data Model | research → data-model | research (1-2 min) |
| Contracts | data-model → contracts | research + data-model (2-3 min) |

### Consistency Check Protocol

1. Extract entity list from current artifact
2. Grep data-model.md for those entity names
3. Verify 3-5 random requirement references trace correctly
4. Check any technology choices match research decisions
5. Flag mismatches as Important issues

Time budget: 1-2 minutes per previous artifact (not 5-10 for full re-read)
```

#### Step 4: Update Plan Command Supervisor Instructions

**File**: `plugins/humaninloop/commands/plan.md`

Update the Advocate Review sections for Phases 3 and 4 to specify incremental mode.

**Phase 3: Data Model - Section 3.5** (around line 339):

Change the supervisor instructions to:

```markdown
### 3.5 Advocate Review (Incremental)

Update context for advocate:

```markdown
**Phase**: Data Model Review (INCREMENTAL MODE)

**Full Review** the data model for completeness and quality.
**Consistency Check** research.md using cross-artifact checklist.

**Full Review**:
- Data Model: `specs/{feature-id}/data-model.md`
- Planner report: `specs/{feature-id}/.workflow/planner-report.md`

**Consistency Check Only**:
- Research: `specs/{feature-id}/research.md` (entity names, decision references)

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: datamodel, mode: incremental)

**Time Budget**:
- Data model full review: unlimited
- Research consistency check: 1-2 minutes max
```
```

**Phase 4: Contracts - Section 4.5** (around line 426):

```markdown
### 4.5 Advocate Review (Incremental)

Update context for advocate:

```markdown
**Phase**: Contracts Review (INCREMENTAL MODE)

**Full Review** API contracts for completeness and consistency with data model.
**Consistency Check** previous artifacts using cross-artifact checklist.

**Full Review**:
- Contracts: `specs/{feature-id}/contracts/api.yaml`
- Quickstart: `specs/{feature-id}/quickstart.md`
- Planner report: `specs/{feature-id}/.workflow/planner-report.md`

**Consistency Check Only**:
- Research: `specs/{feature-id}/research.md` (1-2 min)
- Data Model: `specs/{feature-id}/data-model.md` (1-2 min)

**Write**:
- Report: `specs/{feature-id}/.workflow/advocate-report.md`

**Use Skills**:
- `validation-plan-artifacts` (phase: contracts, mode: incremental)

**Time Budget**:
- Contracts full review: unlimited
- Previous artifacts consistency check: 2-3 minutes total
```
```

---

## Files to Modify

| File | Change Type | Description |
|------|-------------|-------------|
| `plugins/humaninloop/commands/setup.md` | Edit | Add `project_type` field to constitution output |
| `plugins/humaninloop/commands/plan.md` | Edit | Add brownfield entry gate check, update phase skill references |
| `plugins/humaninloop/templates/plan-context-template.md` | Edit | Add project_type and codebase analysis fields |
| `plugins/humaninloop/agents/plan-architect.md` | Edit | Update skill sections to read cache, not invoke |
| `plugins/humaninloop/agents/devils-advocate.md` | Edit | Add incremental validation protocol |
| `plugins/humaninloop/skills/validation-plan-artifacts/SKILL.md` | Edit | Add incremental review mode section |
| `plugins/humaninloop/templates/cross-artifact-checklist.md` | Create | New lightweight consistency checklist |

---

## Expected Impact

| Scenario | Before | After | Savings |
|----------|--------|-------|---------|
| Best case | ~7-8 min | ~4-5 min | ~3 min (38%) |
| Typical (1 iter/phase) | ~12-15 min | ~8-10 min | ~4-5 min (33%) |
| Worst case | ~20-30 min | ~12-18 min | ~8-12 min (40%) |

### Breakdown

| Optimization | Time Saved |
|--------------|------------|
| Reuse setup's codebase analysis (3 calls → 0) | ~3-5 min |
| Incremental validation (phases 2-3) | ~2-4 min |
| **Total** | ~5-9 min |

---

## Testing Plan

1. **Unit test**: Run plan command on greenfield project (no caching needed)
2. **Brownfield test**: Run plan command on project with existing code
   - Verify cache file created on first phase
   - Verify cache read (not recreated) on subsequent phases
3. **Resume test**: Interrupt mid-plan, resume, verify cache still used
4. **Timing test**: Compare before/after on same feature spec
5. **Quality test**: Verify devil's advocate still catches real issues

---

## Rollback Plan

If issues discovered:
1. Remove cache section from plan.md (reverts to per-phase analysis)
2. Remove incremental mode from advocate instructions (reverts to full review)
3. Both changes are additive—no destructive modifications

---

## Deferred Items

Not in this implementation (measure first, add if needed):

- Iteration caps (2 max per phase)
- Context log trimming
- Phase parallelization (requires rearchitecture)

These will be evaluated after measuring real-world impact of quick wins.
