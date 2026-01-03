# Roadmap

This document outlines the vision and planned evolution of the HumanInLoop Marketplace.

## Vision

**Plan with humans. Build with AI. Ship sustainably.**

The HumanInLoop Marketplace provides Claude Code plugins that enforce specification-driven development—ensuring architectural decisions are made by humans before AI writes code.

## Current State (v0.6.0)

The marketplace is in active development. The core specify → plan → tasks workflow is functional with architectural parity across all commands.

### Available Now

**Commands:**
- `/humaninloop:specify` - Create structured specifications using 2-agent architecture
- `/humaninloop:plan` - Generate implementation plans with skill-augmented architecture
- `/humaninloop:tasks` - Generate implementation tasks with vertical TDD slicing **(v0.6.0 - refactored)**
- `/humaninloop:analyze` - Analyze codebase context
- `/humaninloop:checklist` - Generate implementation checklists
- `/humaninloop:implement` - Execute implementation with tracking
- `/humaninloop:setup` - Initialize project constitution
- `/humaninloop-experiments:specify` - Experimental specifications (sandbox for new patterns)

**Skills** (auto-invoked by Claude) - 13 total, organized by category:

*Authoring (writing patterns):*
- `authoring-requirements` - Write functional requirements using FR-XXX format with RFC 2119 keywords
- `authoring-user-stories` - Write user stories with P1/P2/P3 priorities and Given/When/Then acceptance
- `authoring-constitution` - Write enforceable constitution content with Enforcement/Testability/Rationale

*Analysis (analytical capabilities):*
- `analysis-codebase` - Analyze existing codebases for tech stack, entities, and collision risks
- `analysis-iterative` - Progressive brainstorming with recommendations and synthesis
- `analysis-specifications` - Review specs and find gaps with product-focused questions

*Patterns (domain knowledge):*
- `patterns-api-contracts` - RESTful API design with endpoint mapping and OpenAPI specs
- `patterns-entity-modeling` - DDD-style entity extraction with relationships and state machines
- `patterns-technical-decisions` - Evaluate technology alternatives and document decisions
- `patterns-vertical-tdd` - Vertical slicing with TDD discipline for task organization **(v0.6.0 - new)**

*Validation (artifact review):*
- `validation-plan-artifacts` - Review planning artifacts for quality and completeness
- `validation-task-artifacts` - Review task artifacts for TDD structure and coverage **(v0.6.0 - new)**

*Utilities:*
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
