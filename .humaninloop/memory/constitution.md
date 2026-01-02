<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version Change: 1.0.0 → 1.1.0

Added Sections:
- VII. Hexagonal Layer Architecture (from ADR-005)
- VIII. Core Plugin Foundation (from ADR-006)

Modified Principles: N/A
Removed Sections: N/A

Templates Status: N/A (no project-local .humaninloop/templates/ exist)

Follow-up TODOs: None

Derived From: ADR-005 (Hexagonal Agent Architecture), ADR-006 (humaninloop-core Plugin)
================================================================================
-->

# HumanInLoop Marketplace Constitution

## Core Principles

### I. Spec-Driven Development

Every new feature MUST follow the specification-driven development workflow, dogfooding the HumanInLoop plugins:

1. Create GitHub issue describing the feature
2. Run `/humaninloop-specs:specify` → commit spec to `specs/in-progress/`
3. Run `/humaninloop:plan` → commit plan
4. Implement → PR references issue and spec
5. On merge → move spec to `specs/completed/`

**Rationale**: The marketplace builds tools for spec-driven development; we MUST use our own tools to validate their effectiveness and discover pain points.

### II. Multi-Agent Architecture

All plugins MUST use the multi-agent plugin architecture. This is a fundamental rearchitecture decision, not a migration from legacy approaches.

- Agents are specialized for specific workflow stages
- Agents hand off to each other with explicit context
- Each agent has clearly defined responsibilities

**Rationale**: Multi-agent architecture enables better separation of concerns, testability, and composability of workflow stages.

### III. Need-Based Migration

Migration from inspiration sources (e.g., speckit) MUST be selective and need-driven:

- NEVER assume behavioral parity with source material
- Only adopt concepts that serve HumanInLoop's specific needs
- Restructure adopted concepts for the multi-agent plugin architecture
- Source artefacts in `docs/speckit-artefacts/` are READ-ONLY references

**Rationale**: Inspiration is not specification. Direct ports create technical debt and miss opportunities for architectural improvement.

### IV. Conventional Commits

All commits MUST follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat(plugin): description` - New features
- `fix(plugin): description` - Bug fixes
- `docs: description` - Documentation changes
- `refactor(plugin): description` - Code restructuring
- `chore: description` - Maintenance tasks

**Rationale**: Standardized commits enable automated changelog generation, clear history, and semantic versioning alignment.

### V. GitHub-First Tooling

Use `gh` CLI for ALL GitHub-related tasks:

- Viewing repositories, issues, and pull requests
- Creating releases and managing workflows
- Never use web UI when CLI is available

**Rationale**: CLI-first ensures reproducibility, scriptability, and integration with automation.

### VI. Simplicity Over Abstraction

- Start simple; YAGNI (You Aren't Gonna Need It) principles apply
- Complexity MUST be justified and tracked (see Complexity Tracking in plan templates)
- No premature abstractions; three similar lines are better than a premature helper

**Rationale**: Unnecessary complexity slows development and obscures intent. Justify every layer of indirection.

### VII. Hexagonal Layer Architecture

The plugin architecture follows a three-layer hexagonal model where dependencies point inward only:

- **Skills (innermost)**: Pure domain knowledge—no procedures, no tools, no dependencies on other skills
- **Agents (middle)**: Procedures + context binding + judgment—compose skills via `skills:` declarations
- **Workflows (outermost)**: Orchestration + state management + adaptation—own all persistent state

Key rules:
- Dependencies MUST point inward: Workflows → Agents → Skills
- Agents are stateless functions: receive input, return output
- Workflows own state and decide what to persist
- Skills know nothing about agents or workflows

**Rationale**: Hexagonal architecture enables testable agents (pure functions), composable skills (atomic knowledge), and flexible orchestration (workflows can change without touching agents). See [ADR-005](docs/decisions/005-hexagonal-agent-architecture.md).

### VIII. Core Plugin Foundation

The `humaninloop-core` plugin provides domain-agnostic capabilities that other plugins depend on:

- Core skills are useful standalone (e.g., iterative-analysis, codebase-understanding)
- Workflow plugins (humaninloop, humaninloop-specs) MUST depend on core
- Dependency is enforced via filesystem convention (`.humaninloop/core-installed` marker)
- Skill composition: agents declare `skills:` mixing core and plugin-specific skills

Installation order: `humaninloop-constitution` → `humaninloop-core` → workflow plugins

**Rationale**: Shared capabilities maintained in one place avoid duplication and ensure consistency. Core provides standalone value, not just a "dependency tax." See [ADR-006](docs/decisions/006-humaninloop-core-plugin.md).

## Development Workflow

### Feature Development Process

1. **Issue First**: Every non-trivial feature MUST have a GitHub issue
2. **Specify**: Run `/humaninloop-specs:specify` to create formal specification
3. **Plan**: Run `/humaninloop:plan` to create implementation plan
4. **Implement**: Code against the specification and plan
5. **Review**: PR MUST reference issue and spec
6. **Archive**: On merge, move spec from `in-progress/` to `completed/`

### Bug Fix Process

1. Create GitHub issue describing the bug
2. Fix and reference issue in PR
3. Trivial fixes may skip issue creation with clear commit message

### Release Process

- Follow [RELEASES.md](RELEASES.md) for versioning strategy
- Update [CHANGELOG.md](CHANGELOG.md) with each release
- Each plugin maintains its own version in `plugin.json`
- Marketplace releases bundle plugin changes

## Governance

### Amendment Procedure

1. Amendments MUST be documented in a GitHub issue or PR
2. Amendments require explicit approval before merge
3. All template files MUST be updated to reflect constitutional changes
4. Migration plan MUST be provided for breaking changes

### Versioning Policy

This constitution follows semantic versioning:

- **MAJOR**: Backward-incompatible principle removals or redefinitions
- **MINOR**: New principles/sections added or materially expanded
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review

- All PRs MUST verify compliance with these principles
- The Constitution Check section in `plan-template.md` enforces validation
- Violations MUST be justified in the Complexity Tracking table

**Version**: 1.1.0 | **Ratified**: 2026-01-01 | **Last Amended**: 2026-01-02
