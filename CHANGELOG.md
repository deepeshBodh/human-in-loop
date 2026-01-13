# Changelog

All notable changes to the HumanInLoop Marketplace are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.7.8] - 2026-01-13

Plan command performance optimization (#28) - 33-40% faster execution through codebase analysis reuse and incremental validation.

### humaninloop 0.7.8

#### Performance
- **Codebase analysis reuse** - Plan now reads cached analysis from `/humaninloop:setup` instead of re-running `analysis-codebase` 3x per planning session (~3-5 min saved)
- **Incremental validation** - Devil's Advocate uses full review only for new artifacts, consistency check for previous (~2-4 min saved)
- **Expected improvement**: Best case 38% faster, typical 33% faster, worst case 40% faster

#### New Features
- **Brownfield entry gate** - Plan command validates brownfield projects have required codebase analysis
- **Staleness warning** - Alerts if codebase analysis is >14 days old (visibility without blocking)
- **`project_type` field** - Constitution now records `brownfield` or `greenfield` for explicit workflow control

#### New Templates
- **cross-artifact-checklist.md** - Lightweight consistency checklist for incremental validation (entity names, requirement IDs, decision alignment)

#### Changed
- **plan.md** - Added brownfield check, updated advocate sections from "cumulative" to "incremental"
- **plan-architect.md** - Removed `analysis-codebase` skill invocation, reads cached file instead
- **devils-advocate.md** - Added incremental validation protocol with time budgets
- **validation-plan-artifacts/SKILL.md** - Added incremental review mode with report format
- **plan-context-template.md** - Added `project_type`, `codebase_analysis_path`, `codebase_analysis_age` fields
- **setup.md** - Added `project_type` field to constitution output

---

## [0.7.7] - 2026-01-07

Constitution skill modularization for better separation of concerns (#27).

### humaninloop 0.7.7

#### Changed
- **authoring-constitution skill** - Refactored into three modular skills for isolated changeability:
  - `authoring-constitution` (core) - Principle grammar, section templates, RFC 2119 keywords
  - `validation-constitution` (new) - Quality validation, checklists, anti-patterns
  - `brownfield-constitution` (new) - Essential Floor + Emergent Ceiling approach

#### New Skills
- **validation-constitution** - Validate constitution quality with checklists, anti-pattern detection, and version bump rules
  - Triggered by: "constitution review", "quality check", "version bump", "anti-patterns", "constitution audit"
  - Bundled resources: QUALITY-CHECKLIST.md, ANTI-PATTERNS.md
- **brownfield-constitution** - Write constitutions for existing codebases using Essential Floor + Emergent Ceiling
  - Triggered by: "brownfield", "existing codebase", "essential floor", "emergent ceiling", "evolution roadmap"
  - Extends authoring-constitution skill with cross-skill references
  - Bundled resources: ESSENTIAL-FLOOR.md, EMERGENT-CEILING-PATTERNS.md

#### Documentation
- Cross-skill references enable skill composition (brownfield extends authoring)
- Related Skills sections added to all three constitution skills
- Principal Architect agent updated with new skill references

---

## [0.7.6] - 2026-01-07

Constitution generation fixes and pattern strengthening from real-world usage feedback (#26).

### humaninloop 0.7.6

#### Fixed
- **Placeholder syndrome** - Constitution generation now produces actual tool names and commands instead of `[PLACEHOLDER]` syntax
- **Coverage thresholds** - Now uses numeric values (e.g., "≥80% warning, ≥60% blocking") instead of `[THRESHOLD]%`
- **Security tools** - Names specific tools (e.g., "Trivy + Snyk") instead of `[SECURITY_COMMAND]`

#### Added
- **Emergent Ceiling patterns** - 10+ new examples: Code Quality, Clean Architecture, Port Interfaces, Error Handling, Observability, Product Analytics, Naming Conventions
- **Mobile/frontend patterns** - Constitution patterns tailored for mobile and frontend codebases
- **CODEOWNERS detection** - Enhanced brownfield analysis detects CODEOWNERS files for governance
- **Version history tracking** - SYNC IMPACT REPORT now maintains rolling log of previous versions

#### Changed
- **authoring-constitution skill** - Major expansion with detailed Essential Floor requirements and Emergent Ceiling pattern examples
- **analysis-codebase skill** - Added CODEOWNERS detection and improved governance docs checklist
- **constitution-template** - Updated Quality Gates with realistic defaults, added Approvers section
- **setup command** - Added critical instructions to populate from analysis instead of using placeholders
- **CLAUDE.md sync mandate** - Enhanced with explicit synchronization process and enforcement rules

---

## [0.7.5] - 2026-01-07

Brownfield setup improvements for existing codebases (#23).

### humaninloop 0.7.5

#### New Skill
- **authoring-roadmap** - Create evolution roadmaps with prioritized gap cards for brownfield projects
  - Triggered by: "roadmap", "gap analysis", "evolution plan", "brownfield gaps"
  - Produces gap cards with P1/P2/P3 priorities and dependency graphs

#### New Templates
- **codebase-analysis-template.md** - Structure for brownfield codebase analysis (inventory + assessment)
- **evolution-roadmap-template.md** - Structure for gap analysis between current state and constitution

#### Changed
- **/humaninloop:setup** - Major rewrite with 5-phase brownfield-aware workflow
  - Phase 0: Brownfield detection with user confirmation
  - Phase 1: Codebase analysis producing `codebase-analysis.md`
  - Phase 2: Analysis checkpoint for user review
  - Phase 3: Constitution generation (greenfield/brownfield/amend modes)
  - Phase 4: Evolution roadmap producing `evolution-roadmap.md`
  - Phase 5: Finalize with mode-specific output
- **principal-architect agent** - Added Essential Floor knowledge and `authoring-roadmap` skill reference
- **plan-architect agent** - Added brownfield context file awareness
- **task-architect agent** - Added brownfield markers (`[GAP:XXX]`) and context file reading
- **analysis-codebase skill** - Added `setup-brownfield` mode with Essential Floor assessment (Security, Testing, Error Handling, Observability)
- **authoring-constitution skill** - Added brownfield mode with Essential Floor + Emergent Ceiling pattern

#### Documentation
- Updated plugin README with brownfield workflow documentation
- Added output structure for project-level brownfield artefacts

---

## [0.7.4] - 2026-01-05

Script bug fixes discovered during dogfooding.

### humaninloop 0.7.4

#### Fixed
- **check-prerequisites.sh** - `AVAILABLE_DOCS` now includes `spec.md`, `plan.md`, `task-mapping.md` (were silently omitted)
- **check-prerequisites.sh** - `--paths-only` output now includes all 11 path variables (was missing 5)
- **common.sh** - Added `TASK_MAPPING` variable definition
- **setup-plan.sh** - Added `--force` flag to prevent accidental `plan.md` overwrites
- **setup-plan.sh** - Fixed confusing output naming (`SPECS_DIR` → `FEATURE_DIR`)
- **create-new-feature.sh** - Added `specs/` directory as project marker for non-git repos
- **create-new-feature.sh** - Improved template lookup to check plugin directory before fallback

#### Removed
- **common.sh** - Removed unused `get_feature_dir()` function (dead code)

---

## [0.7.3] - 2026-01-04

Branch creation standardization and cross-command consistency.

### humaninloop 0.7.3

#### Changed
- **Specify command uses script-based branch creation** - Now uses `create-new-feature.sh` script matching speckit pattern
  - Fetches remote branches before creating new ones
  - Checks local branches, remote branches, AND specs directories for number conflicts
  - Branch format: `###-short-name` (e.g., `001-user-auth`) - no `feat/` prefix
  - Generates concise 2-4 word short names from feature descriptions
- **Consistent feature detection across commands** - Plan and tasks commands now explicitly document that branch name = feature ID
  - Detection order: explicit argument → current git branch → most recent spec by numeric prefix

#### Fixed
- **Branch/spec directory mismatch** - Previously specify.md didn't create branches, but plan.md expected to detect features from branches. Now both are aligned.

---

## [0.7.2] - 2026-01-04

Implement command overhaul and documentation completion.

### humaninloop 0.7.2

#### Changed
- **Implement command refactored** - Overhauled with cycle-based TDD execution model
  - Entry gate verification (tasks workflow must complete first)
  - Foundation cycles execute sequentially, feature cycles can parallelize
  - TDD discipline: each cycle starts with failing test
  - Checkpoint verification between cycles
  - Quality gates (lint, build, tests) after each cycle
- **Removed risky git commands** - Implement command no longer runs `git diff` or `git checkout`; version control left to user

#### Documentation
- **Plugin README completed** - Added missing `/humaninloop:implement` command documentation

---

## [0.7.1] - 2026-01-04

Repository rename and cleanup release.

### Repository Changes
- **Renamed repository** from `human-in-loop-marketplace` to `human-in-loop`
- **Marketplace display name** updated to `humaninloop-plugins`
- Updated all documentation with new repository references

### Removed
- **humaninloop-experiments plugin** - Removed entirely (functionality was consolidated into main humaninloop plugin in earlier releases)

### Documentation Fixes
- Fixed README.md: corrected agent count (5) and skill count (13)
- Fixed ROADMAP.md: removed stale `/humaninloop-experiments:specify` command reference
- Fixed CONTRIBUTING.md: updated plugin template instructions
- Fixed RELEASES.md: updated version example

---

## [0.7.0] - 2026-01-04

**BREAKING CHANGE**: Consolidate checklist and analyze commands into unified audit command.

### humaninloop 0.7.0

#### Breaking Changes
- **Commands consolidated** - `/humaninloop:checklist` and `/humaninloop:analyze` replaced by `/humaninloop:audit`
  - Previous checklist functionality: `audit --review`
  - Previous analyze functionality: `audit` (default mode)
- **Template removed** - `checklist-template.md` no longer exists

#### New Command
- **/humaninloop:audit** - Comprehensive artifact analysis with two output modes
  - Full mode (default): Deep diagnostics for authors/maintainers
  - Review mode (`--review`): Scannable summary for peer reviewers
  - Domain filters: `--security`, `--ux`, `--api`, `--performance`
  - Phase-agnostic: works on whatever artifacts exist
  - Leverages existing validation skills

#### Migration Guide
1. Replace `/humaninloop:checklist` with `/humaninloop:audit --review`
2. Replace `/humaninloop:analyze` with `/humaninloop:audit`
3. Domain filters work with both modes (e.g., `audit --review --security`)

---

## [0.6.0] - 2026-01-04

**BREAKING CHANGE**: Tasks workflow refactored to 2-agent pattern with vertical TDD slicing.

### humaninloop 0.6.0

#### Breaking Changes
- **Tasks workflow redesigned** - Replaced 3-agent pattern with streamlined 2-agent supervisor pattern
  - Old agents (removed): `task-planner`, `task-generator`, `task-validator`
  - New agent: `task-architect` - Senior architect for task mapping and generation
  - `devils-advocate` now handles task artifact validation
- **Check-modules removed** - All check-modules migrated to validation skills
  - Removed: `mapping-checks.md`, `task-checks.md`
  - Replaced by: `validation-task-artifacts` skill
- **Task format changed** - Tasks now organized into vertical TDD cycles
  - Old format: Horizontal task lists
  - New format: Cycles with test-first ordering and checkpoints

#### New Agent
- **task-architect** - Senior architect who transforms planning artifacts into implementation tasks through vertical slicing and TDD discipline
  - Uses `patterns-vertical-tdd` skill for cycle structure
  - Writes task-mapping.md and tasks.md artifacts

#### New Skills
- **patterns-vertical-tdd** - Guide for identifying vertical slices and structuring TDD cycles
  - Defines cycle structure (Foundation vs Feature cycles)
  - Enforces test-first ordering within each cycle
  - Includes slice identification heuristics and examples
- **validation-task-artifacts** - Review criteria for task artifacts
  - Phase-specific checklists (mapping, tasks)
  - Issue templates and severity classification
  - Replaces mapping-checks and task-checks modules

#### Changed
- **tasks.md workflow** - Now uses 4 phases: Initialize → Mapping → Tasks → Completion
- **tasks-context-template.md** - Simplified to mirror plan-context structure
- **tasks-template.md** - Updated to cycle-based TDD format with [P] parallel markers
- **devils-advocate** - Added `validation-task-artifacts` skill for task reviews

#### Task Format (New)

Tasks are now organized into **cycles** - vertical slices that deliver testable value:

```markdown
### Cycle N: [Vertical slice description]

> Stories: US-X, US-Y
> Dependencies: C1, C2 (or "None")
> Type: Foundation | Feature [P]

- [ ] **TN.1**: Write failing test for [behavior]
- [ ] **TN.2**: Implement [component] to pass test
- [ ] **TN.3**: Refactor and verify tests pass
- [ ] **TN.4**: Demo [behavior], verify acceptance criteria

**Checkpoint**: [Observable outcome]
```

- **Foundation cycles**: Sequential, establish shared infrastructure
- **Feature cycles**: Parallel-eligible (marked with `[P]`), deliver user value independently
- **Task IDs**: `TN.X` format (N = cycle number, X = task sequence)
- **Brownfield markers**: `[EXTEND]`, `[MODIFY]` for existing code

#### Migration Guide
1. Existing specs remain compatible; only tasks.md output changes
2. If resuming interrupted tasks workflow, recommend starting fresh
3. New tasks will use cycle-based TDD structure
4. Check-modules are gone; validation now via skills

---

## [0.5.0] - 2026-01-04

**BREAKING CHANGE**: Skills renamed to follow ADR-004 naming convention.

### humaninloop 0.5.0

#### Breaking Changes
- **Skills renamed** per ADR-004 category-based naming convention:
  - `analyzing-codebase` → `analysis-codebase`
  - `designing-api-contracts` → `patterns-api-contracts`
  - `iterative-analysis` → `analysis-iterative`
  - `making-technical-decisions` → `patterns-technical-decisions`
  - `modeling-domain-entities` → `patterns-entity-modeling`
  - `reviewing-plan-artifacts` → `validation-plan-artifacts`
  - `reviewing-specifications` → `analysis-specifications`

#### Skill Organization (ADR-004)
Skills now follow category-based naming:
- **authoring-*** : Writing patterns and templates (3 skills)
- **analysis-*** : Analytical capabilities (3 skills)
- **patterns-*** : Reusable domain knowledge (3 skills)
- **validation-*** : Check modules with scripts (1 skill)
- **syncing-*** : Synchronization utilities (1 skill)

#### Added
- **Validation scripts** for 4 additional skills (6/11 total now have scripts):
  - `analysis-codebase/scripts/detect-stack.sh` - Framework/stack detection
  - `patterns-api-contracts/scripts/validate-openapi.py` - OpenAPI validation
  - `patterns-entity-modeling/scripts/validate-model.py` - Data model validation
  - `validation-plan-artifacts/scripts/check-artifacts.py` - Artifact checks
- **Progressive disclosure** for 4 additional skills (10/11 total now have reference files)
- **Missing sections** added to `analysis-specifications` skill (Quality Checklist, Anti-Patterns)

#### Changed
- **Plan workflow refactored** to skill-augmented architecture
  - Removed: plan-research, plan-domain-model, plan-contract, plan-validator agents
  - Added: plan-architect agent with skill references
  - Check modules migrated to validation skills with scripts

#### Removed
- `analyzing-project-context` skill (merged into `analysis-codebase`)
- Plan workflow check-modules (replaced by validation skills)

#### Migration Guide
1. Update any custom references to skill names (see breaking changes above)
2. Skill invocation via `skills:` field in agents automatically uses new names
3. Scripts remain in same relative location: `skills/{name}/scripts/`

---

## [0.4.0] - 2026-01-03

**BREAKING CHANGE**: Constitution plugin merged into humaninloop.

### humaninloop 0.4.0

#### Breaking Changes
- **humaninloop-constitution merged into humaninloop** - All constitution functionality now part of main plugin
  - `/humaninloop-constitution:setup` is now `/humaninloop:setup`
  - No separate plugin installation required

#### Plugin Consolidation
- **New command**: `/humaninloop:setup` - Initialize project constitution (previously `/humaninloop-constitution:setup`)
- **New agent**: `principal-architect` - Senior technical leader for governance judgment
- **New skills**: `authoring-constitution`, `analyzing-project-context`, `syncing-claude-md`
- **New templates**: `constitution-template.md`, `constitution-context-template.md`

#### Migration Guide
1. If you had `humaninloop-constitution` installed separately, uninstall it
2. Update to `humaninloop` 0.4.0
3. Use `/humaninloop:setup` instead of `/humaninloop-constitution:setup`
4. Existing constitutions at `.humaninloop/memory/constitution.md` remain valid

---

## [0.3.0] - 2026-01-03

**BREAKING CHANGE**: Major architecture overhaul of the specify workflow.

### humaninloop 0.3.0

#### Breaking Changes
- **Specify workflow redesigned** - Replaced 6-agent Priority Loop architecture with streamlined 2-agent Supervisor pattern
  - Old architecture (removed): Scaffold Agent → Spec Writer → Checklist Context Analyzer → Checklist Writer → Gap Classifier → Spec Clarify
  - New architecture: Requirements Analyst ↔ Devil's Advocate (supervised loop)
- **Workflow artifacts changed** - New structure uses `context.md`, `analyst-report.md`, `advocate-report.md` instead of `index.md`, `specify-context.md`, and checklist files
- **Constitution still required** - Pre-flight check remains; run `/humaninloop:setup` first

#### New Agents
- **requirements-analyst** - Senior analyst who transforms vague feature requests into precise specifications with user stories, functional requirements, and acceptance criteria
- **devils-advocate** - Adversarial reviewer who stress-tests specifications by finding gaps, challenging assumptions, and identifying edge cases

#### New Skill
- **reviewing-specifications** - Review specs to find gaps and generate product-focused clarifying questions (not technical implementation questions)

#### New Templates
- `context-template.md` - Context artifact for supervisor-agent communication
- `analyst-report-template.md` - Report format for requirements analyst output
- `advocate-report-template.md` - Report format for devil's advocate output

#### Removed Agents
- `scaffold-agent.md` - Replaced by inline context creation in supervisor
- `spec-writer.md` - Replaced by requirements-analyst
- `spec-clarify.md` - Clarification now handled in supervisor loop
- `checklist-context-analyzer.md` - Checklist validation removed from specify
- `checklist-writer.md` - Checklist validation removed from specify
- `gap-classifier.md` - Gap classification now part of devil's advocate

#### Removed Templates
- `specify-context-template.md`
- `checklist-context-template.md`
- `workflow-index-template.md`
- `workflow-context-template.md`

#### Migration Guide
1. The `/humaninloop:checklist` command remains available for manual quality validation
2. Existing specs in `specs/` directory remain compatible
3. New specs will use the simpler `.workflow/` structure with context and reports
4. No changes to `/humaninloop:plan`, `/humaninloop:tasks`, or other commands

---

## [0.2.9] - 2026-01-03

Fix for humaninloop-experiments skills invocation.

### humaninloop-experiments 0.1.1

#### Fixes
- **Standardized skills invocation in agents** - Both agents now properly declare `skills:` in frontmatter
  - Added `skills: authoring-requirements, authoring-user-stories` to requirements-analyst
  - Added `skills: reviewing-specifications` to devils-advocate
  - Added "Skills Available" section with Skill tool guidance to devils-advocate
  - Removed duplicated content from devils-advocate that was already in reviewing-specifications skill

---

## [0.2.8] - 2026-01-03

New experimental plugin with decoupled agents architecture.

### humaninloop-experiments 0.1.0 (NEW)

#### New Plugin
- **humaninloop-experiments** - Experimental sandbox for testing new agent patterns
  - Implements decoupled two-agent specify workflow
  - Uses context-based communication between agents
  - Standalone plugin (does not require humaninloop)

#### New Commands
- `/humaninloop-experiments:specify` - Create specifications using Requirements Analyst + Devil's Advocate pattern

#### New Agents
- `requirements-analyst` - Transforms vague requests into precise specifications
- `devils-advocate` - Adversarial reviewer who stress-tests specs and finds gaps

#### New Skills
- `authoring-requirements` - Write functional requirements (standalone copy)
- `authoring-user-stories` - Write user stories (standalone copy)
- `reviewing-specifications` - Review specs and find gaps, ambiguities, and missing scenarios

---

## [0.2.7] - 2026-01-03

New authoring skills for specification writing and constitution decoupled architecture.

### humaninloop 0.2.7

#### New Skills
- **authoring-requirements** - Write functional requirements using FR-XXX format with RFC 2119 keywords
  - Triggered by: "functional requirements", "FR-", "SC-", "RFC 2119", "MUST SHOULD MAY"
  - Includes validation script and reference documentation
- **authoring-user-stories** - Write user stories with P1/P2/P3 priorities and Given/When/Then acceptance
  - Triggered by: "user story", "acceptance scenario", "Given When Then", "P1", "P2", "P3"
  - Includes validation script and example templates

#### Documentation
- Added ADR-004: Skill-Augmented Agents Architecture
- Added ADR-005: Decoupled Agents Architecture

### humaninloop-constitution 1.2.0

#### Architecture
- **Decoupled agent architecture** - Implemented per ADR-005
  - Plugin.json now uses explicit agent file paths instead of directory reference
  - Enables granular control over agent registration

#### New Agents
- **principal-architect** - Senior technical leader agent for governance judgment
  - Evaluates whether standards are enforceable, testable, and justified
  - Rejects vague aspirations in favor of actionable constraints
  - Uses opus model for deeper reasoning

### humaninloop-constitution 1.1.0

#### New Skills
- **authoring-constitution** - Write enforceable, testable constitution content
  - Triggered by: "constitution", "governance", "principles", "enforcement", "quality gates"
  - Enforces three-part principle rule: Enforcement, Testability, Rationale
  - Includes RFC 2119 keyword guidance
- **analyzing-project-context** - Infer project characteristics from codebase
  - Triggered by: "project context", "tech stack", "conventions", "architecture patterns"
  - Extracts tech stack, CI config, existing governance, and team signals
  - Generates Project Context Report for constitution authoring
- **syncing-claude-md** - Ensure CLAUDE.md mirrors constitution sections
  - Triggered by: "CLAUDE.md sync", "agent instructions", "propagate constitution"
  - Defines mandatory sync mapping between constitution and CLAUDE.md
  - Includes sync validation checklist and gap detection

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
- `plan-research` - Researches codebase for planning context
- `plan-contract` - Defines contracts between components
- `plan-domain-model` - Creates domain models
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

[0.7.4]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.4
[0.7.3]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.3
[0.7.2]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.2
[0.7.1]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.1
[0.7.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.0
[0.6.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.6.0
[0.5.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.5.0
[0.4.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.4.0
[0.3.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.3.0
[0.2.9]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.9
[0.2.8]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.8
[0.2.7]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.7
[0.2.6]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.6
[0.2.5]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.5
[0.2.3]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.3
[0.2.2]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.2
[0.2.1]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.1
[0.2.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.2.0
[0.1.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.1.0
[0.0.1]: https://github.com/deepeshBodh/human-in-loop/commits/main
