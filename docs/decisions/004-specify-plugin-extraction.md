# ADR-004: Specify Plugin Extraction

**Status**: Accepted
**Date**: 2026-01-02
**Implemented**: 2026-01-02
**Decision**: Extract specify workflow into standalone `humaninloop-specs` plugin with lightweight/heavyweight modes

---

## Problem Statement

The current `humaninloop` plugin's specify workflow is built exclusively for feature development (user stories, functional requirements, success criteria). This model doesn't fit the reality of software work—bugs, chores, tech debt, refactors, and upgrades all need specification but don't match the feature-centric template. Extracting specify into a standalone plugin enables a fundamental rethink of what "specification" means across all work types.

## Context & Constraints

- **Current architecture**: `humaninloop` is a monolith with 14 agents spanning specify → plan → tasks → implement
- **Plugin ecosystem**: Claude Code plugins don't have robust shared-dependency primitives yet
- **User friction**: The goal is less ceremony for simple work, not more process for everything
- **Constitution dependency**: The specify workflow currently requires `.humaninloop/memory/constitution.md`

## Decision

### Key Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary driver | Scope expansion | The extraction is a vehicle for rethinking specify, not the goal itself |
| Work type handling | Lightweight vs heavyweight modes | Complexity/uncertainty distinction, not work-type taxonomy |
| Mode selection | Progressive disclosure | Start lightweight, expand when complexity detected—no upfront decision fatigue |
| Lightweight spec | Problem + Done only | Minimal viable spec—if you need more, that's a signal to expand |
| Expansion triggers | Hybrid (input signals + clarification count) | Parse input for complexity markers; if clarifications pile up (3+), offer expansion |
| Heavyweight structure | Core + optional sections | Mandatory: Problem, Requirements, Acceptance Criteria, Risks. Optional: User Stories, Migration Plan, etc. |
| Plugin relationship | Full extraction with dependency | `humaninloop-specs` is standalone; `humaninloop` becomes orchestrator |
| What gets extracted | Full specify chain including checklist | Clean boundary: everything needed to produce a validated spec |
| Plugin communication | Spec file as contract | No runtime dependency—just filesystem contract (`spec.md` in known location) |

### Lightweight vs Heavyweight Modes

Rather than creating separate workflows for features, bugs, chores, and tech debt (which leads to taxonomy explosion), the plugin uses two modes based on **complexity and uncertainty**:

**Lightweight Mode** (default):
- Two sections only: Problem + Done
- Fast path for simple work
- Can be completed in minutes

**Heavyweight Mode** (on expansion):
- Core sections (mandatory): Problem, Requirements, Acceptance Criteria, Risks
- Optional sections: User Stories, Migration Plan, Performance Targets, Rollback Strategy, Dependencies/Blockers
- Full validation with checklist and gap classification

### Progressive Disclosure

Single entry point (`/specify`) that starts everyone in lightweight mode. The system detects complexity via:

1. **Input signals**: Keywords like "integrate", "redesign", "new system"; multiple components mentioned; unclear done criteria
2. **Clarification count**: If 3+ clarifying questions emerge during lightweight flow, offer expansion

User always controls whether to expand or proceed lightweight.

### Plugin Architecture

```
┌─────────────────────────────┐      ┌─────────────────────────────┐
│   humaninloop-specs       │      │   humaninloop               │
├─────────────────────────────┤      ├─────────────────────────────┤
│ - scaffold-agent            │      │ - plan-* agents             │
│ - spec-writer               │      │ - task-* agents             │
│ - spec-clarify              │      │ - codebase-discovery        │
│ - checklist-context-analyzer│      │ - check-modules             │
│ - checklist-writer          │  ──► │                             │
│ - gap-classifier            │      │ Consumes spec.md            │
│                             │      │ from known location         │
│ Produces: spec.md           │      │                             │
└─────────────────────────────┘      └─────────────────────────────┘
        │                                      │
        │         Filesystem Contract          │
        └──────── specs/{id}/spec.md ──────────┘
```

**Communication**: Spec file as contract. No runtime dependency between plugins. `humaninloop-specs` produces `spec.md` and workflow files in `specs/{feature}/`. `humaninloop`'s `/plan` command expects those files to exist.

## Decision Trail

### 1. Primary Driver for Extraction
- **Options**: Modularity/reusability, Scope expansion, Both equally
- **Chosen**: Scope expansion
- **Reasoning**: The core tension is that the current workflow assumes "feature development." Extraction enables reimagining specify for all work types.

### 2. Handling Different Work Item Types
- **Options**: Unified template with conditional sections, Separate workflows per type, Lightweight + heavyweight modes
- **Chosen**: Lightweight + heavyweight modes
- **Reasoning**: Avoids taxonomy explosion. The real distinction is complexity/uncertainty, not category labels.

### 3. Mode Selection Mechanism
- **Options**: User declares explicitly, Heuristic with override, Progressive disclosure
- **Chosen**: Progressive disclosure
- **Reasoning**: Users don't always know complexity upfront. Starting lightweight and growing matches natural problem exploration.

### 4. Lightweight Spec Contents
- **Options**: Problem + Done, Problem + Context + Done, Problem + Approach + Done + Risks
- **Chosen**: Problem + Done
- **Reasoning**: True minimum viable spec. If you need context/approach upfront, that's a signal for heavyweight mode.

### 5. Expansion Triggers
- **Options**: Input complexity signals, Clarification count threshold, Hybrid approach
- **Chosen**: Hybrid
- **Reasoning**: Neither signal alone is reliable. Hybrid catches obvious complexity upfront AND discovered complexity during the flow.

### 6. Heavyweight Spec Structure
- **Options**: Reuse current feature spec, Simplified heavyweight, Adaptive based on work nature
- **Chosen**: Core + optional sections (adapted from current)
- **Reasoning**: Keep the rigor of current spec, but adapt sections to be flexible for non-feature work.

### 7. Plugin Architecture
- **Options**: Full extraction with dependency, Fork and diverge, Shared core with extensions
- **Chosen**: Full extraction with dependency
- **Reasoning**: Single source of truth for specification logic. Improvements benefit everyone.

### 8. What Gets Extracted
- **Options**: Specify agents only, Full specify chain with checklist, Rethink checklist as shared utility
- **Chosen**: Full specify chain with checklist
- **Reasoning**: Clean boundary—everything needed to produce a validated spec.

### 9. Plugin Communication
- **Options**: Command invocation, Shared agent access, Spec file as contract
- **Chosen**: Spec file as contract
- **Reasoning**: Maximum decoupling. Users can even hand-write specs. Plan just needs the file.

## Consequences

### Positive
- Simple work gets simple specs (lightweight mode)
- Users can install just `humaninloop-specs` without the full workflow
- Cleaner mental model: complexity determines process, not work-type labels
- Decoupled architecture allows independent evolution
- Hand-written specs are fully supported

### Negative
- Two plugins to maintain instead of one
- Migration effort for existing users
- Shared templates need a home (or duplication)
- Constitution dependency needs resolution for lightweight mode

### Risks
- Progressive disclosure detection might be too aggressive or too passive
- "Lightweight vs heavyweight" language might confuse users expecting work-type categories

## Open Questions (Resolved)

- **Constitution dependency**: ✅ **Resolved**: Constitution is fully optional for lightweight specs, required for heavyweight specs.
- **Command naming**: ✅ **Resolved**: Using `/humaninloop-specs:specify` as the command.
- **Handoff metadata**: ✅ **Resolved**: Produces `spec.md` + `index.md` + `specify-context.md`. Plan reads spec.md and index.md.
- **Backward compatibility**: ✅ **Resolved**: `/humaninloop:specify` removed immediately (breaking change accepted).
- **Shared templates**: ✅ **Resolved**: Duplicated with simplification - humaninloop-specs has `specify-index-template.md` without plan/tasks sections.

## Implementation Notes

### Implementation Date: 2026-01-02

### Plugin Structure Created

```
plugins/humaninloop-specs/
├── .claude-plugin/plugin.json
├── commands/specify.md, checklist.md
├── agents/
│   ├── scaffold-agent.md (mode-aware)
│   ├── spec-writer.md (lightweight/heavyweight)
│   ├── spec-clarify.md
│   ├── checklist-context-analyzer.md
│   ├── checklist-writer.md
│   └── gap-classifier.md
├── skills/
│   ├── complexity-detection/ (NEW)
│   ├── spec-writing/
│   ├── spec-clarify/
│   ├── scaffold-workflow/
│   └── iterative-analysis/
├── templates/
│   ├── spec-lightweight-template.md (NEW)
│   ├── spec-template.md
│   ├── specify-index-template.md (simplified)
│   └── ...
└── scripts/
```

### Changes to humaninloop Plugin

- Removed: 6 specify agents, 4 specify skills, specify.md command, checklist.md command
- Updated: plugin.json (v0.3.0), agents list reduced to 8
- Kept: plan and tasks workflows, codebase-discovery, analyze command

### Key Implementation Decisions

1. **Complexity Detection**: Signal-based scoring with threshold of 3 for suggesting heavyweight
2. **Expansion Trigger**: 3+ clarifications discovered during lightweight triggers expansion offer
3. **Templates Duplicated**: Each plugin owns its templates, no shared dependencies
4. **Breaking Change**: Old `/humaninloop:specify` removed; users must use new plugin
