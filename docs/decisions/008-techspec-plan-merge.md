# ADR-008: Merge Techspec and Plan into Unified Planning Workflow

**Status:** Accepted
**Date:** 2026-03-16

## Context

The humaninloop plugin had two separate workflow commands for translating business specifications into implementation-ready artifacts:

1. **`/humaninloop:techspec`** — Translated business FRs into technical requirements, constraints, NFRs, integration maps, and data sensitivity classifications (5 artifacts in `technical/` subdirectory). Used 3 agents (Technical Analyst, Principal Architect, Devil's Advocate) across 2 passes with 6+ invocations.

2. **`/humaninloop:plan`** — Transformed technical artifacts into design decisions, data models, API contracts, and integration guides. Used 2 agents (Plan Architect, Devil's Advocate) across 3 phases with 6+ invocations.

**Problems identified:**

- **Artifact overlap**: Constraints in techspec overlapped with research decisions in plan. Data sensitivity was a standalone artifact that logically belonged with the data model. Integration maps were separate from the API contracts they informed.
- **Excessive invocations**: 10+ agent invocations across both commands made the workflow slow and felt repetitive.
- **Fragmented ownership**: The Technical Analyst produced constraints but the Plan Architect made technology decisions shaped by those constraints — splitting a naturally coupled concern across two agents.
- **Redundant context**: Both commands had their own context files, brownfield checks, resume detection, and clarification loops — duplicating supervisor infrastructure.

## Decision

Merge `/humaninloop:techspec` and `/humaninloop:plan` into a single `/humaninloop:plan` command with two phases:

- **Phase 1 (Analysis)**: Technical Analyst produces `requirements.md`, `constraints-and-decisions.md`, `nfrs.md`. Principal Architect reviews cross-artifact feasibility. Devil's Advocate validates completeness.
- **Phase 2 (Design)**: Technical Analyst produces `data-model.md`, `contracts/api.yaml`, `quickstart.md`. Devil's Advocate validates completeness with incremental cross-artifact consistency check.

**Key design choices:**

1. **Technical Analyst absorbs Plan Architect** — One agent handles both analysis and design, gaining the Plan Architect's skills (`patterns-technical-decisions`, `patterns-entity-modeling`, `patterns-api-contracts`).
2. **Constraints and decisions merged** — `constraints.md` + `research.md` → `constraints-and-decisions.md` with bidirectional cross-references (C-XXX ↔ D-XXX).
3. **Data sensitivity embedded** — Standalone `data-sensitivity.md` → sensitivity annotations per entity attribute in `data-model.md`.
4. **Integration boundaries embedded** — Standalone `integrations.md` → `x-integration` OpenAPI extensions in `contracts/api.yaml`.
5. **Principal Architect gate once** — Feasibility intersection review after Phase 1 only (cross-artifact contradictions, not individual completeness).
6. **5 invocations total** — TA → PA → DA → TA → DA (down from 10+).

## Consequences

### Positive

- Faster workflow: 5 invocations instead of 10+, single context file, no inter-command handoff
- Unified artifact set: 6 artifacts at feature root (no `technical/` subdirectory)
- Natural coupling preserved: constraints and decisions live together; sensitivity lives with entities; integrations live with contracts
- Simpler mental model for users: one command from spec to plan

### Negative

- Technical Analyst agent has broader scope (mitigated by skill delegation)
- Plan Architect agent deprecated (responsibilities absorbed)
- Existing specs in old layout not migrated (accepted — historical records stay as-is)

### Neutral

- Devil's Advocate role unchanged (still reviews both phases)
- `/humaninloop:tasks` continues to work — reads the same `plan.md` output
- `/humaninloop:techspec` deprecated with redirect notice

## References

- Analysis document: `docs/analysis-techspec-plan-merge.md`
- Implementation plan: `docs/implementation-plan-techspec-plan-merge.md`
