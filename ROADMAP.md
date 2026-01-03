# Roadmap

This document outlines the vision and planned evolution of the HumanInLoop Marketplace.

## Vision

**Plan with humans. Build with AI. Ship sustainably.**

The HumanInLoop Marketplace provides Claude Code plugins that enforce specification-driven development—ensuring architectural decisions are made by humans before AI writes code.

## Current State (v0.3.0)

The marketplace is in active development. The core specify → plan → tasks workflow is functional.

### Available Now

**Commands:**
- `/humaninloop:specify` - Create structured specifications using 2-agent architecture **(v0.3.0 - redesigned)**
- `/humaninloop:plan` - Generate implementation plans
- `/humaninloop:tasks` - Generate implementation tasks
- `/humaninloop:analyze` - Analyze codebase context
- `/humaninloop:checklist` - Generate implementation checklists
- `/humaninloop:implement` - Execute implementation with tracking
- `/humaninloop:setup` - Initialize project constitution **(v0.4.0)**
- `/humaninloop-experiments:specify` - Experimental specifications (sandbox for new patterns)

**Skills** (auto-invoked by Claude):
- `authoring-requirements` - Write functional requirements using FR-XXX format with RFC 2119 keywords
- `authoring-user-stories` - Write user stories with P1/P2/P3 priorities and Given/When/Then acceptance
- `iterative-analysis` - Progressive brainstorming with recommendations and synthesis
- `reviewing-specifications` - Review specs and find gaps **(v0.3.0 - added)**
- `authoring-constitution` - Write enforceable constitution content with Enforcement/Testability/Rationale
- `analyzing-project-context` - Infer project characteristics from codebase for constitution authoring
- `syncing-claude-md` - Ensure CLAUDE.md mirrors constitution sections per sync mapping

---

## Phases

### Phase 1: Core Workflow (Current)
Complete the specify → plan → tasks → implement cycle.

- [x] Specification workflow with multi-agent validation
- [x] Planning workflow with domain modeling
- [x] Task generation with brownfield support
- [x] Implementation tracking and completion validation
- [ ] Workflow state persistence across sessions

### Phase 2: Quality & Feedback
Close the loop between implementation and specification.

- [ ] Post-implementation validation against spec
- [ ] Drift detection (implementation vs plan)
- [ ] Automated spec updates from implementation learnings
- [ ] Quality metrics and reporting

### Phase 3: Collaboration
Support team workflows and shared specifications.

- [ ] Spec review workflows
- [ ] Multi-user plan collaboration
- [ ] Handoff documentation generation
- [ ] Integration with issue trackers

### Phase 4: Enterprise Features
Features for larger teams and compliance requirements.

- [ ] Audit trails for specification decisions
- [ ] Approval workflows
- [ ] Access controls
- [ ] Custom validation rules

---

## Feature Requests

See [planned specs](./specs/planned/) for detailed feature specifications.

To request a feature, [open an issue](https://github.com/deepeshBodh/human-in-loop-marketplace/issues/new).

---

## Non-Goals

Things this project intentionally does not do:

- **Tool-agnostic framework** - We are Claude Code native. Other tools should use their own integrations.
- **Full automation** - Humans must be in the loop for architectural decisions.
- **Speckit compatibility** - This is a rearchitecture, not a port. Behavioral parity is not a goal.

---

## Contributing

Want to help build the future of spec-driven development? See [CONTRIBUTING.md](./CONTRIBUTING.md).
