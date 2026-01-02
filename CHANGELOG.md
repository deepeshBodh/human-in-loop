# Changelog

All notable changes to the HumanInLoop Marketplace are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### humaninloop-specs 0.1.0 (NEW PLUGIN)

Extracted specification workflow into dedicated plugin for cleaner separation of concerns.

#### New Commands
- `/humaninloop-specs:specify` - Create feature specifications with integrated Priority Loop validation
- `/humaninloop-specs:checklist` - Generate requirements quality checklists ("Unit Tests for English")

#### New Agents
- `scaffold-agent` - Creates feature branches and directory structure
- `spec-writer` - Dual-mode agent for spec creation and clarification updates
- `checklist-agent` - Generates requirements quality checklists with signal extraction
- `gap-classifier` - Groups validation gaps into clarification questions (max 3 per iteration)

#### New Skills
- `spec-writing/` - Specification writing patterns, templates, and frameworks
- `clarification-patterns/` - Gap classification and answer application patterns
- `requirements-quality-validation/` - Quality dimensions for requirements checklists
- `spec-gap-prioritization/` - Gap filtering, grouping, and staleness detection
- `scaffold-workflow/` - Feature scaffolding procedures and scripts
- `specification-workflow-lifecycle/` - Workflow phases, state, and recovery patterns

#### Architecture
- Implements ADR-005 hexagonal architecture (skills → agents → workflows)
- Implements ADR-007 agent communication schema (standardized input/output envelopes)
- Unified index.md for cross-agent state sharing
- Priority Loop with max 10 iterations and 3 clarifications per iteration

### humaninloop-core 1.1.0

#### New Agents
- `validator-agent` - Generic validation for any artifact type against check modules

### humaninloop

#### Changed
- **Task agent consolidation (3→2)**: Merged `task-planner` and `task-generator` into single `task-builder` agent
  - `task-builder` is now phase-aware: phase 1 for mapping, phase 2 for generation
  - Matches the `plan-builder` pattern for architectural consistency
  - Uses Opus model (consistent with all builder agents)
- Added `skills/task-workflow/` with modular skill files:
  - `SKILL.md` - Entry point and quick reference
  - `CONTEXT.md` - Shared context loading patterns
  - `BROWNFIELD.md` - Brownfield handling guidelines
  - `MAPPING.md` - Phase T1 procedures
  - `TASKS.md` - Phase T2 procedures
  - `VALIDATION.md` - Validation coordination

#### Fixed
- Added missing `dependencies: ["humaninloop-core"]` to plugin.json
- Fixed agent namespace consistency: all agents now use full `{plugin}:{agent}` pattern
  - `codebase-discovery` → `humaninloop-core:codebase-discovery`
  - `plan-builder` → `humaninloop:plan-builder`
  - `task-builder` → `humaninloop:task-builder`

#### Removed
- `task-planner` agent (consolidated into `task-builder`)
- `task-generator` agent (consolidated into `task-builder`)

---

## [0.2.6] - 2026-01-01

Fix skill description parsing for proper model-invoked triggering.

### humaninloop 0.2.6

#### Fixes
- **iterative-analysis skill** - Fixed YAML multi-line description format that prevented skill from triggering
  - Changed from multi-line YAML (`description: |`) to single-line format
  - Claude Code's YAML parser doesn't correctly handle multi-line descriptions
  - Skill now properly triggers on "brainstorm", "deep analysis", "let's think through", etc.

---

## [0.2.5] - 2026-01-01

New iterative-analysis skill for progressive brainstorming.

### humaninloop 0.2.5

#### New Skills
- **iterative-analysis** - Progressive deep analysis through one-by-one questioning with recommendations
  - Triggered by: "brainstorm", "deep analysis", "let's think through", "analyze this with me"
  - Presents 2-3 options per question with clear recommendation and reasoning
  - Challenges disagreement to strengthen thinking
  - Concludes with structured synthesis document

### humaninloop-constitution 1.0.0

#### Milestone
- **First stable release** - The constitution plugin has reached feature parity with speckit and is now production-ready
- Stable API with semantic versioning guarantees going forward
- Tested and validated for all core constitution setup workflows

---

## [0.2.3] - 2026-01-01

Improved UX for empty input workaround - users can now re-enter input in the terminal.

### humaninloop 0.2.3

#### Fixes
- Improved empty-input detection UX: added explicit "Re-enter input" option
- When selected, command waits for user to type input in the terminal (better @ file reference support)
- "Continue without input" option remains for proceeding without input

### humaninloop-constitution 0.1.3

#### Fixes
- Same UX improvement for `setup` command

---

## [0.2.2] - 2026-01-01

Workaround for Claude Code `@` file reference parsing bug affecting plugin command inputs.

### humaninloop 0.2.2

#### Fixes
- Added empty-input detection to all 6 commands (`specify`, `plan`, `tasks`, `analyze`, `checklist`, `implement`)
- When input is empty, commands now prompt user with AskUserQuestion to check if input was lost due to Claude Code's `@` parsing bug
- Users can re-enter input or continue without input

### humaninloop-constitution 0.1.2

#### Fixes
- Added empty-input detection to `setup` command with same workaround

---

## [0.2.1] - 2026-01-01

Plugin manifest fix for Claude Code compatibility.

### humaninloop 0.2.1

#### Fixes
- Fixed plugin.json to use explicit agent file paths instead of directory reference
- Removed unsupported `checkModules` field from plugin manifest

---

## [0.2.0] - 2026-01-01

Tasks workflow release: Generate implementation tasks from plans with brownfield support.

### humaninloop 0.2.0

#### New Commands
- `/humaninloop:tasks` - Generate implementation tasks from spec and plan artifacts
- `/humaninloop:analyze` - Analyze codebase for implementation context
- `/humaninloop:checklist` - Generate implementation checklists
- `/humaninloop:implement` - Execute implementation with task tracking

#### New Agents
- `task-planner` - Plans task breakdown from spec/plan artifacts
- `task-generator` - Generates tasks.md with brownfield markers
- `task-validator` - Validates task artifacts for completeness

#### New Check Modules
- `mapping-checks` - Validates story coverage and entity mapping
- `task-checks` - Validates task format, coverage, and dependencies

#### New Templates
- `plan-template.md` - Structured plan output format
- `tasks-template.md` - Task list format with brownfield markers
- `codebase-inventory-schema.json` - Schema for codebase analysis

#### New Scripts
- `setup-plan.sh` - Plan stage initialization

### humaninloop-constitution 0.1.1

#### Fixes
- Fixed outdated plugin references in documentation

---

## [0.1.0] - 2026-01-01

Initial marketplace release with core specification-driven workflow.

### humaninloop 0.1.0

#### New Commands
- `/humaninloop:specify` - Create feature specifications through guided workflow
- `/humaninloop:plan` - Generate implementation plans from specifications

#### New Agents
- `spec-writer` - Writes structured specifications
- `spec-clarify` - Clarifies ambiguous requirements
- `plan-builder` - Builds plan artifacts (research, domain model, contracts) for any phase
- `plan-validator` - Validates plan completeness
- `codebase-discovery` - Discovers existing codebase patterns
- `gap-classifier` - Classifies implementation gaps
- `scaffold-agent` - Scaffolds new components
- `checklist-writer` - Writes implementation checklists
- `checklist-context-analyzer` - Analyzes context for checklists

### humaninloop-constitution 0.1.0

#### New Commands
- `/humaninloop-constitution:setup` - Initialize project constitution

#### New Templates
- `constitution-template.md` - Project constitution structure

---

## [0.0.1] - 2026-01-01

Initial marketplace scaffold.

### Added
- Marketplace manifest structure
- Plugin installation framework
- Documentation scaffolding

---

[0.2.6]: https://github.com/deepeshBodh/human-in-loop-marketplace/releases/tag/v0.2.6
[0.2.5]: https://github.com/deepeshBodh/human-in-loop-marketplace/releases/tag/v0.2.5
[0.2.4]: https://github.com/deepeshBodh/human-in-loop-marketplace/releases/tag/v0.2.4
[0.2.3]: https://github.com/deepeshBodh/human-in-loop-marketplace/releases/tag/v0.2.3
[0.2.2]: https://github.com/deepeshBodh/human-in-loop-marketplace/releases/tag/v0.2.2
[0.2.1]: https://github.com/deepeshBodh/human-in-loop-marketplace/releases/tag/v0.2.1
[0.2.0]: https://github.com/deepeshBodh/human-in-loop-marketplace/releases/tag/v0.2.0
[0.1.0]: https://github.com/deepeshBodh/human-in-loop-marketplace/releases/tag/v0.1.0
[0.0.1]: https://github.com/deepeshBodh/human-in-loop-marketplace/commits/main
