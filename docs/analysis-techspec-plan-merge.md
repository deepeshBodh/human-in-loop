# Techspec + Plan Merge Analysis Synthesis

## Problem Statement

The current pipeline has two separate workflow steps (`/humaninloop:techspec` and `/humaninloop:plan`) between specification and task generation. Analysis revealed significant artifact overlap (constraints↔research, integrations↔contracts, data-sensitivity↔data-model), redundant agent invocations, and an artificial handoff that forces context rebuilding. The separation does not align with natural decision boundaries, resulting in a workflow that feels repetitive and slow.

## Context & Constraints

- **DAG infrastructure stays**: hil-dag, passes, nodes, supervisor+agent orchestration pattern unchanged
- **Pipeline boundaries fixed**: `spec.md` remains input, `tasks.md` remains output
- **Constitution/governance layer**: unchanged
- **Current pain**: 10+ agent invocations across two workflows; artifacts re-tread covered ground; users experience repetitiveness and slowness

## Key Decisions

| Decision | Choice | Confidence | Rationale |
|----------|--------|------------|-----------|
| Merge techspec + plan into one workflow | Yes — single `/humaninloop:plan` command | Confident | Eliminates artificial handoff, reduces redundancy, keeps all design context unified |
| Number of phases | 2 (Analysis → Design) | Confident | Maps to natural decision flow: "what must be true" then "what we're building" |
| Primary agent | Technical Analyst absorbs Plan Architect | Confident | TA already handles harder analytical work; design skills are narrower and more mechanical once analysis is done |
| Principal Architect role | Keep — single feasibility gate after Phase 1 | Confident | Unique value: spotting contradictions at the intersection of individually valid artifacts |
| PA review focus | Feasibility intersection only (option C) | Confident | DA already checks individual artifact quality; PA catches impossible combinations across artifacts |
| Devil's Advocate role | Kept for both phases | Confident | Completeness review remains valuable per-phase |
| Merge constraints + research | Yes — single `constraints-and-decisions.md` | Confident | Constraints are facts, decisions are choices within those facts — two sides of same coin |
| Merge data-sensitivity into data-model | Yes — sensitivity as annotations on entities | Confident | Same data described from different angles; designing together produces better results |
| Merge integrations into contracts | Yes — external boundaries alongside API design | Confident | Integration points directly inform contract design; separating them fragments related decisions |
| Naming | `/humaninloop:plan` | Confident | Simpler; the end output is a plan |

## Decision Trail

### Technical Analyst vs Plan Architect as surviving agent

- **Options considered**: (A) Expand Technical Analyst with PA skills, (B) Keep TA name but restructure skills
- **Recommendation was**: Not given — user was asked preference
- **Chosen**: A — expand Technical Analyst
- **Key reasoning**: User asked if TA could absorb PA's responsibilities. Natural fit because TA already does the harder analytical work; PA's design skills (entity modeling, API contracts, technology decisions) are narrower and follow from the analytical foundation.

### Principal Architect — keep or drop

- **Options considered**: (A) Keep PA for single feasibility gate after Phase 1, (B) Fold feasibility into Devil's Advocate, (C) Drop entirely
- **Recommendation was**: Dropping it (to reduce invocations)
- **Chosen**: A — keep with single invocation
- **Key reasoning**: User challenged the recommendation. PA has a distinct lens — "can this actually be built given all constraints together?" — that neither TA nor DA naturally provides. Compromise: one invocation instead of per-phase.

### Principal Architect review scope

- **Options considered**: (A) Review everything in Phase 1, (B) Only analytical artifacts, (C) Feasibility intersection — contradictions across artifacts
- **Recommendation was**: C
- **Chosen**: C
- **Key reasoning**: DA already validates individual artifact quality. PA's unique value is catching impossible combinations (e.g., technology choice contradicts constraint, NFR target unachievable with chosen stack). One focused question: "given all three artifacts together, can this be built?"

### Two phases vs three phases

- **Options considered**: (A) Keep 3 phases (Analysis → Design → Contracts), (B) Collapse to 2 (Analysis → Design), (C) Move artifacts between phases
- **Recommendation was**: B — data model and contracts are tightly coupled
- **Chosen**: B
- **Key reasoning**: Endpoints expose entities, schemas mirror model attributes. Designing them separately makes the contract phase mostly mechanical translation. Two phases also maps cleanly to "what must be true" vs "what we're building."

## Risks

- **Agent prompt complexity**: The expanded Technical Analyst carries skills for requirements decomposition, constraint analysis, NFR definition, entity modeling, API contract design, and technology decisions. The agent prompt may become too large for effective single-pass execution.
- **Phase 2 density**: Producing `data-model.md` + `contracts/api.yaml` + `quickstart.md` in one pass is a lot of design work. If quality suffers, Phase 2 may need to be split back into two.
- **Lost review checkpoint**: Current pipeline gives users a natural pause between techspec and plan to review requirements before design. The merged workflow's only checkpoint is the PA gate after Phase 1.

## New Workflow Structure

```
/humaninloop:plan (unified command)

Phase 1: Analysis
  Input:  spec.md, constitution, codebase-analysis (if brownfield)
  Agent:  Technical Analyst
  Output: requirements.md, constraints-and-decisions.md, nfrs.md
  Gate:   Principal Architect — feasibility intersection review
  Review: Devil's Advocate — completeness review

Phase 2: Design
  Input:  Phase 1 artifacts
  Agent:  Technical Analyst
  Output: data-model.md, contracts/api.yaml, quickstart.md
  Review: Devil's Advocate — completeness + cross-artifact consistency

Completion: auto-generate plan.md summary

Total invocations: 5 (TA → PA → DA → TA → DA)
Total artifacts:   6 + summary
```

### Artifact Summary

| Phase | Artifact | Contains |
|-------|----------|----------|
| 1 | `requirements.md` | FR→TR mapping, acceptance criteria |
| 1 | `constraints-and-decisions.md` | Hard boundaries (facts) + technology choices with rationale (decisions) |
| 1 | `nfrs.md` | Measurable quality targets |
| 2 | `data-model.md` | Entities, relationships, sensitivity annotations, state machines, validation rules |
| 2 | `contracts/api.yaml` | OpenAPI spec with integration boundaries baked in |
| 2 | `quickstart.md` | Integration guide, common flows, error handling patterns |
| — | `plan.md` | Summary document (auto-generated at completion) |

### Agent Roles

| Agent | Invocations | Responsibility |
|-------|-------------|----------------|
| Technical Analyst (expanded) | 2 | All artifact production — analysis and design |
| Principal Architect | 1 | Feasibility intersection: contradictions across Phase 1 artifacts |
| Devil's Advocate | 2 | Completeness and consistency review per phase |

## Open Questions

- How should the Technical Analyst agent prompt be restructured to handle the expanded scope without becoming unwieldy?
- Should the Devil's Advocate review after Phase 2 include a consistency check back to Phase 1 artifacts (incremental mode), or trust that the same TA that produced Phase 1 maintained consistency?
- What happens to existing `techspec` command, templates, context files, and report templates — deprecate or remove?

## Recommended Next Steps

1. **Write a technical specification** for the merged `/humaninloop:plan` command — define the supervisor workflow, phase gates, context template, and agent dispatch rules
2. **Redesign the Technical Analyst agent definition** — expand with Plan Architect's skills (entity modeling, API contracts, technology decisions) and update the identity/prompt
3. **Update the Principal Architect review criteria** — narrow scope to feasibility intersection checks only
4. **Update the Devil's Advocate Phase Checklists** — merge techspec and plan review phases into the new 2-phase structure
5. **Deprecate `/humaninloop:techspec`** — remove command, update CLAUDE.md pipeline documentation, update skill triggers
