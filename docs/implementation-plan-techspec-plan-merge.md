# Implementation Plan: Techspec + Plan Merge

**Source**: [analysis-techspec-plan-merge.md](analysis-techspec-plan-merge.md)
**Status**: Draft
**Date**: 2026-03-16

---

## Overview

Merge `/humaninloop:techspec` and `/humaninloop:plan` into a single `/humaninloop:plan` command with 2 phases, 3 agents, 5 invocations, and 6 output artifacts.

### Target Architecture

```
/humaninloop:plan (unified command)

Phase 1: Analysis
  → Technical Analyst: requirements.md, constraints-and-decisions.md, nfrs.md
  → Principal Architect: feasibility intersection review (one-time gate)
  → Devil's Advocate: completeness review

Phase 2: Design
  → Technical Analyst: data-model.md, contracts/api.yaml, quickstart.md
  → Devil's Advocate: review

Completion: auto-generate plan.md summary
```

---

## Phase 1: Agent Modifications

Changes to agent definitions that enable the merged workflow.

### 1.1 Expand Technical Analyst Agent

**File**: `plugins/humaninloop/agents/technical-analyst.md`

**Changes**:
- Add Plan Architect's skills to skill list:
  - `patterns-technical-decisions` (technology choice evaluation, ADR-style records)
  - `patterns-entity-modeling` (entity extraction, relationships, state machines)
  - `patterns-api-contracts` (OpenAPI design, endpoint mapping, error patterns)
- Update identity section to include design responsibilities:
  - Current: "bridges business specifications and technical implementation"
  - New: "bridges business specifications and technical implementation through requirements analysis AND concrete design decisions"
- Add phase-driven behavior from Plan Architect:
  - Read context file to determine which phase (analysis/design)
  - Phase 1 (Analysis): produce requirements.md, constraints-and-decisions.md, nfrs.md
  - Phase 2 (Design): produce data-model.md, contracts/api.yaml, quickstart.md
- Add brownfield awareness from Plan Architect:
  - Check `.humaninloop/memory/codebase-analysis.md`
  - Use markers: `[NEW]`, `[EXTENDS EXISTING]`, `[REUSES EXISTING]`
  - Match existing patterns unless constitution requires change
- Add `constraints-and-decisions.md` artifact template guidance:
  - Section 1: Hard Constraints (facts — infrastructure, compatibility, regulatory, migration, organizational)
  - Section 2: Technology Decisions (choices — ADR-style with context, options, choice, consequences, rationale)
  - Each decision explicitly references which constraints shaped it

**Does NOT change**:
- Model: remains `opus`
- Color: remains `yellow`
- Existing skill: `authoring-technical-requirements` stays
- Quality standards: traceable, measurable, technology-agnostic, failure-aware, classified

### 1.2 Narrow Principal Architect Review Scope

**File**: `plugins/humaninloop/agents/principal-architect.md`

**Changes**:
- Add a new section or update existing review guidance for "Plan Feasibility Review" mode
- When invoked during `/humaninloop:plan`, the architect's review scope is **feasibility intersection only**:
  - Do constraints and technology decisions contradict each other?
  - Do NFR targets conflict with chosen technologies or hard constraints?
  - Do TR acceptance criteria assume capabilities not available under stated constraints?
  - Are there impossible combinations across the three Phase 1 artifacts?
- Explicitly note what is **out of scope** for this review:
  - Individual artifact completeness (that's Devil's Advocate's job)
  - Whether alternatives were properly considered (Devil's Advocate)
  - Whether NFRs are individually measurable (Devil's Advocate)
- Update report template reference to use feasibility-focused format

**Does NOT change**:
- Model, color, skill list (constitution/governance skills stay — PA serves other workflows too)
- Three-Part Rule identity
- Verdict options: feasible / needs-revision / infeasible

### 1.3 Update Devil's Advocate Phase Checklists

**File**: `plugins/humaninloop/agents/devils-advocate.md`

**Changes**:
- Update skill reference from separate techspec/plan phase awareness to unified plan phases
- The agent itself doesn't change much — it already supports both `validation-plan-artifacts` and `analysis-specifications`
- Main change is in the validation skill and checklists (see Phase 2 below)

### 1.4 Deprecate Plan Architect Agent

**File**: `plugins/humaninloop/agents/plan-architect.md`

**Action**: Mark as deprecated. Do NOT delete yet — other workflows or documentation may reference it.

**Changes**:
- Add deprecation notice at top of file
- Note that responsibilities have been absorbed by Technical Analyst
- Reference this implementation plan

---

## Phase 2: Skill & Template Modifications

### 2.1 Create `constraints-and-decisions` Artifact Template

**New content in**: `plugins/humaninloop/skills/authoring-technical-requirements/references/ARTIFACT-TEMPLATES.md`

**Changes**:
- Add template for `constraints-and-decisions.md` that combines:
  - Current `constraints.md` structure (C-XXX entries with type, source, severity, impact, verification)
  - Current `research.md` structure (ADR-style decision records with context, options, choice, consequences)
- Add cross-referencing rules:
  - Each decision record MUST reference constraints that shaped the choice
  - Constraint impact fields SHOULD reference decisions they influence
- Update traceability patterns in `TRACEABILITY-PATTERNS.md`:
  - Add C-XXX ↔ D-XXX (constraint-decision) bidirectional links
  - Remove separate research.md traceability (absorbed)

### 2.2 Merge Data Sensitivity into Data Model Template

**File**: `plugins/humaninloop/skills/authoring-technical-requirements/references/ARTIFACT-TEMPLATES.md`

**Changes**:
- Remove standalone `data-sensitivity.md` template
- Add to `data-model.md` entity template:
  - `### Data Sensitivity` section per entity (or per attribute for mixed-classification entities)
  - Fields: Classification level, Encryption at Rest, Encryption in Transit, Retention Period, Access Control, Audit, Masking
  - Compliance Mapping table (per entity, not per data element)
- Add classification summary table at top of data-model.md:
  - `| Entity | Attribute | Classification | Compliance |`
- Update traceability: DS-XXX IDs become annotations within entity definitions rather than standalone artifact references

### 2.3 Merge Integrations into Contracts Template

**File**: `plugins/humaninloop/skills/patterns-api-contracts/references/OPENAPI-TEMPLATE.yaml`

**Changes**:
- Add `x-integrations` extension section per endpoint that wraps an external system:
  - External system name, protocol, API version, criticality
  - Failure modes with detection, impact, fallback
  - Authentication details
- Alternatively, add an `## External Integrations` section to `quickstart.md` for integration details that don't fit OpenAPI extensions
- Update `SKILL.md` to include integration mapping as part of contract design responsibility

### 2.4 Update Validation Plan Artifacts Skill

**File**: `plugins/humaninloop/skills/validation-plan-artifacts/SKILL.md`

**Changes**:
- Rename phases from B0/B1/B2 to P1/P2 (two phases)
- **Phase P1 (Analysis) checklist**:
  - Merge current techspec Phase 2 (core) checks: FR coverage, orphan TRs, testable criteria, sourced constraints
  - Merge current techspec Phase 3 (supplementary) checks: NFR measurability, coverage
  - Add new checks for merged constraints-and-decisions: decision-constraint cross-references, alternatives documented
- **Phase P2 (Design) checklist**:
  - Merge current plan Phase B1 (data model) checks: entity coverage, attribute completeness, relationships, PII, state machines
  - Add data sensitivity checks (previously separate): classification completeness, encryption requirements, retention policies
  - Merge current plan Phase B2 (contracts) checks: endpoint coverage, schema completeness, error handling
  - Add integration checks (previously separate): failure modes, fallback strategies, criticality
  - Incremental mode: consistency check back to Phase 1 artifacts (1-2 min max)

**File**: `plugins/humaninloop/skills/validation-plan-artifacts/references/PHASE-CHECKLISTS.md`

**Changes**: Rewrite to reflect P1/P2 structure with merged checks as above.

**File**: `plugins/humaninloop/skills/validation-plan-artifacts/scripts/check-artifacts.py`

**Changes**:
- Update artifact path expectations (no more `technical/` subdirectory for some artifacts)
- Add `constraints-and-decisions.md` validation (check for both C-XXX and D-XXX entries)
- Add data sensitivity validation within `data-model.md` (check for classification annotations)
- Add integration validation within `contracts/api.yaml` (check for failure mode documentation)
- Remove references to standalone `data-sensitivity.md` and `integrations.md`

### 2.5 Create Unified Plan Context Template

**New file**: Replace `plugins/humaninloop/templates/plan-context-template.md`

**Changes**:
- Merge fields from `techspec-context-template.md` and current `plan-context-template.md`
- Frontmatter:
  ```yaml
  type: plan-request
  phase: {analysis | design | completed}
  status: {awaiting-analyst | awaiting-architect | awaiting-advocate | awaiting-user | completed}
  iteration: {number}
  feature_id: {feature-id}
  created: {ISO date}
  updated: {ISO date}
  analysis_status: {pending | complete}
  design_status: {pending | complete}
  ```
- Body sections:
  - Feature Context (from both templates)
  - File Paths with status (unified list — 6 artifacts + summary)
  - Constitution Principles
  - Codebase Context (brownfield)
  - Supervisor Instructions (phase-specific, dynamic)
  - Clarification Log (grows during workflow)

**Deprecate**: `plugins/humaninloop/templates/techspec-context-template.md` — mark as deprecated

### 2.6 Update Report Templates

**File**: `plugins/humaninloop/templates/techanalyst-report-template.md`

**Changes**:
- Rename to reflect expanded role (or keep name since agent is still "Technical Analyst")
- Add Phase 2 (Design) sections:
  - Entity count, relationship count
  - Endpoint count, schema count
  - Integration points catalogued
- Add Decision count to Phase 1 section (alongside TR and Constraint counts)

**File**: `plugins/humaninloop/templates/architect-report-template.md`

**Changes**:
- Update to reflect narrowed scope (feasibility intersection only)
- Remove individual artifact quality sections
- Add explicit "Cross-Artifact Contradiction" table:
  ```
  | Artifact A | Artifact B | Contradiction | Severity |
  ```
- Keep verdict options: feasible / needs-revision / infeasible

**File**: `plugins/humaninloop/templates/plan-template.md`

**Changes**:
- Update to reflect merged artifact set:
  - Key Decisions from `constraints-and-decisions.md` (not separate research.md)
  - Entities from `data-model.md` (including sensitivity summary)
  - Endpoints from `contracts/api.yaml` (including integration points)
  - Remove references to `data-sensitivity.md` and `integrations.md` as standalone files

**Deprecate**:
- `plugins/humaninloop/templates/planner-report-template.md` — absorbed into techanalyst-report-template
- `plugins/humaninloop/templates/plan-advocate-report-template.md` — use unified advocate-report-template

### 2.7 Update Traceability Patterns

**File**: `plugins/humaninloop/skills/authoring-technical-requirements/references/TRACEABILITY-PATTERNS.md`

**Changes**:
- Add C-XXX ↔ D-XXX (constraint ↔ decision) bidirectional links
- Update DS-XXX references to point to data-model.md entity annotations instead of standalone file
- Update INT-XXX references to point to contracts/api.yaml extensions instead of standalone file
- Add entity → endpoint traceability (data model to API contract)
- Consolidate forward/backward traceability validation to work across the unified artifact set

---

## Phase 3: Command Rewrite

### 3.1 Rewrite `/humaninloop:plan` Command

**File**: `plugins/humaninloop/commands/plan.md`

**This is the largest single change.** Rewrite the supervisor command to implement the merged workflow.

**Entry Gates** (merged from both commands):
1. Feature detection (from `$ARGUMENTS` or branch name)
2. Spec validation: `specs/{feature-id}/spec.md` exists, context status = completed
3. Brownfield check: `.humaninloop/memory/codebase-analysis.md` exists if brownfield
4. Resume detection: check for existing `specs/{feature-id}/.workflow/plan-context.md`
5. **Remove**: techspec completion gate (no longer a prerequisite — it's been absorbed)

**Phase 1: Analysis** (steps ~2.1-2.8):
- 2.1: Create/update plan-context.md with phase=analysis, status=awaiting-analyst
- 2.2: Populate supervisor instructions for analysis phase
- 2.3: Invoke Technical Analyst → produces requirements.md, constraints-and-decisions.md, nfrs.md
- 2.4: Update status to awaiting-architect
- 2.5: Invoke Principal Architect → feasibility intersection review
- 2.6: Route on verdict:
  - `feasible` → proceed to 2.7
  - `needs-revision` → Feasibility Rejection Loop (present concerns, collect user decisions, re-invoke TA, re-submit to PA)
  - `infeasible` → escalate to user
- 2.7: Update status to awaiting-advocate
- 2.8: Invoke Devil's Advocate → completeness review
- 2.9: Route on verdict:
  - `ready` → mark analysis_status=complete, proceed to Phase 2
  - `needs-revision` / `critical-gaps` → Clarification Loop (present gaps, collect answers, re-invoke TA, route back to PA only if structural changes)

**Phase 2: Design** (steps ~3.1-3.6):
- 3.1: Update plan-context.md with phase=design, status=awaiting-analyst
- 3.2: Populate supervisor instructions for design phase
- 3.3: Invoke Technical Analyst → produces data-model.md, contracts/api.yaml, quickstart.md
- 3.4: Update status to awaiting-advocate
- 3.5: Invoke Devil's Advocate → completeness + cross-artifact consistency review (incremental mode for Phase 1 artifacts)
- 3.6: Route on verdict:
  - `ready` → proceed to completion
  - `needs-revision` / `critical-gaps` → Clarification Loop

**Completion** (steps ~4.1-4.2):
- 4.1: Auto-generate plan.md summary from all artifacts
- 4.2: Update plan-context.md with phase=completed, status=completed
- 4.3: Display completion report with artifact summary and "Run `/humaninloop:tasks`" next step

**Loop Mechanisms** (carried from both commands):
- Feasibility Rejection Loop (PA verdict handling)
- Clarification Loop (DA verdict handling)
- Supervisor judgment points (exit early, offer finalization, route to user)

**Estimated size**: ~500 lines (current plan.md is 452 lines, current techspec.md is ~600 lines; merged should be smaller than sum due to shared infrastructure)

### 3.2 Deprecate `/humaninloop:techspec` Command

**File**: `plugins/humaninloop/commands/techspec.md`

**Action**: Mark as deprecated with notice pointing to `/humaninloop:plan`.

**Changes**:
- Add deprecation notice at top
- Optionally: redirect to `/humaninloop:plan` if invoked (print message and exit)
- Do NOT delete yet — allow transition period

---

## Phase 4: Catalog & Configuration Updates

### 4.1 Update Plugin Manifest

**File**: `plugins/humaninloop/.claude-plugin/plugin.json`

**Changes**:
- Remove techspec command registration (or mark deprecated)
- Verify plan command registration points to updated command file

### 4.2 Update Catalogs (if techspec has its own)

**File**: `plugins/humaninloop/catalogs/specify-catalog.json`

**Changes**:
- Review if this catalog references techspec-specific nodes
- Update capability tags and node definitions to reflect merged workflow
- Ensure plan workflow nodes are properly defined

### 4.3 Update Scripts

**File**: `plugins/humaninloop/scripts/create-new-feature.sh`

**Changes**:
- Remove techspec step from feature creation flow
- Update workflow sequence: specify → plan → tasks → implement

**File**: `plugins/humaninloop/scripts/setup-plan.sh`

**Changes**:
- Update to create unified plan-context.md instead of separate techspec + plan contexts
- Update artifact directory structure expectations

---

## Phase 5: Documentation & Governance Updates

### 5.1 Update CLAUDE.md

**File**: `/Users/deepeshadmin/Documents/GitHub/human-in-loop/CLAUDE.md`

**Changes**:
- Update "Feature Development" workflow:
  - Remove step 2 (techspec)
  - Renumber: specify → plan → implement
- Update pipeline description throughout
- Update any references to techspec command or artifacts
- Update Quality Gates table if techspec-specific gates exist

### 5.2 Update Plugin README

**File**: `plugins/humaninloop/README.md`

**Changes**:
- Update workflow documentation
- Remove techspec section
- Update plan section to reflect merged scope
- Update artifact descriptions

### 5.3 Update Skill Trigger Documentation

Multiple skill files reference techspec in their trigger conditions. Update:

- `plugins/humaninloop/skills/authoring-technical-requirements/SKILL.md` — update "when to invoke" context
- Any other skills that mention "techspec" in their descriptions

### 5.4 Write ADR

**New file**: `docs/decisions/ADR-008-techspec-plan-merge.md`

**Contents**:
- Context: techspec and plan had significant artifact overlap causing redundant invocations
- Decision: merge into single `/humaninloop:plan` with 2 phases
- Consequences: fewer invocations, unified context, expanded Technical Analyst role
- Reference: `docs/analysis-techspec-plan-merge.md`

---

## Phase 6: Output Artifact Structure Changes

### 6.1 New Artifact Directory Layout

Current layout (per feature):
```
specs/{feature-id}/
├── spec.md                          (from specify — unchanged)
├── technical/
│   ├── requirements.md              (from techspec)
│   ├── constraints.md               (from techspec)
│   ├── nfrs.md                      (from techspec)
│   ├── integrations.md              (from techspec)
│   └── data-sensitivity.md          (from techspec)
├── research.md                      (from plan)
├── data-model.md                    (from plan)
├── contracts/
│   └── api.yaml                     (from plan)
├── quickstart.md                    (from plan)
├── plan.md                          (from plan)
└── .workflow/
    ├── context.md                   (specify context)
    ├── techspec-context.md          (techspec context)
    └── plan-context.md              (plan context)
```

New layout:
```
specs/{feature-id}/
├── spec.md                          (from specify — unchanged)
├── requirements.md                  (from plan Phase 1)
├── constraints-and-decisions.md     (from plan Phase 1 — merged)
├── nfrs.md                          (from plan Phase 1)
├── data-model.md                    (from plan Phase 2 — includes sensitivity)
├── contracts/
│   └── api.yaml                     (from plan Phase 2 — includes integrations)
├── quickstart.md                    (from plan Phase 2)
├── plan.md                          (auto-generated summary)
└── .workflow/
    ├── context.md                   (specify context — unchanged)
    └── plan-context.md              (unified plan context)
```

**Key changes**:
- `technical/` subdirectory eliminated — artifacts at feature root
- `techspec-context.md` eliminated — single `plan-context.md`
- `constraints.md` + `research.md` → `constraints-and-decisions.md`
- `data-sensitivity.md` absorbed into `data-model.md`
- `integrations.md` absorbed into `contracts/api.yaml`

### 6.2 Migration Consideration

If any existing specs exist in `specs/` with the old layout, decide:
- **Option A**: Leave old specs as-is (they're historical records)
- **Option B**: Provide a migration script
- **Recommended**: Option A — old specs are completed work, no need to reformat

---

## Implementation Order & Dependencies

```
Phase 1: Agent Modifications          (no dependencies)
  1.1 Expand Technical Analyst
  1.2 Narrow Principal Architect
  1.3 Update Devil's Advocate
  1.4 Deprecate Plan Architect

Phase 2: Skill & Template Mods        (depends on Phase 1 for agent skill lists)
  2.1 Constraints-and-decisions template
  2.2 Merge data sensitivity into data model
  2.3 Merge integrations into contracts
  2.4 Update validation skill + checklists
  2.5 Unified plan context template
  2.6 Update report templates
  2.7 Update traceability patterns

Phase 3: Command Rewrite              (depends on Phase 1 + Phase 2)
  3.1 Rewrite /humaninloop:plan
  3.2 Deprecate /humaninloop:techspec

Phase 4: Config Updates               (depends on Phase 3)
  4.1 Plugin manifest
  4.2 Catalogs
  4.3 Scripts

Phase 5: Documentation                (depends on Phase 3)
  5.1 CLAUDE.md
  5.2 Plugin README
  5.3 Skill triggers
  5.4 ADR

Phase 6: Artifact Structure           (defined in Phase 2/3, documented here)
  6.1 New layout (implemented via command rewrite)
  6.2 Migration decision
```

---

## Risk Mitigations

| Risk | Mitigation |
|------|------------|
| Expanded TA agent prompt too large | Keep skill references lean — skills carry the detail, agent prompt carries identity + phase-routing logic only |
| Phase 2 (Design) too dense for single pass | Monitor quality in first few runs; if artifacts suffer, split Design into two sub-phases (data model → contracts) without adding another review cycle |
| Lost review checkpoint between analysis and design | PA gate after Phase 1 serves as explicit checkpoint; user sees feasibility verdict before design begins |
| Breaking existing specs | Don't migrate old specs; new layout applies only to new features |
| Transition confusion | Keep techspec command with deprecation redirect for one release cycle |

---

## Validation Criteria

The merge is successful when:

1. `/humaninloop:plan` produces all 6 artifacts + summary in a single workflow run
2. Total agent invocations = 5 (TA → PA → DA → TA → DA)
3. No references to `/humaninloop:techspec` remain in active code paths
4. Devil's Advocate review catches the same class of issues previously caught across two separate workflows
5. Principal Architect feasibility review catches cross-artifact contradictions
6. Existing `/humaninloop:tasks` workflow accepts the new artifact layout as input without modification (verify tasks command reads the correct paths)
7. End-to-end run completes faster than sequential techspec + plan
