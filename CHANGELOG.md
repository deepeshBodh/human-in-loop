# Changelog

All notable changes to the HumanInLoop Marketplace are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [3.2.2] - 2026-03-17

### humaninloop 3.2.2

#### Fixed

- **Cross-workflow DAG collision** — Specify and implement workflows now use separate DAG files (`specify-strategy.json`, `implement-strategy.json`) instead of sharing `strategy.json`. Fixes implement workflow failing with "Cannot add nodes to a completed graph" when a specify DAG already exists
- **Agents using Bash for file reading** — Added Tool Usage guardrails to `dag-assembler` and `state-analyst` agents prohibiting `git show`, `cat`, `python3 -c`, and other Bash commands for file reading. Agents must use the `Read` tool, reducing unnecessary permission prompts
- **Late `hil-dag` CLI detection** — Added `--require-hil-dag` flag to `check-prerequisites.sh` and early checks in specify/implement commands. Users now get a clear error with install instructions immediately instead of after 3-16 minutes of agent work
- **Stale install instructions** — Updated all `hil-dag` installation references from `cd humaninloop_brain && uv sync` to `uv tool install` across README, dag-operations SKILL.md, and all 7 dag-operations scripts
- **Stale agent/skill counts in root README** — Updated agent count from 9 to 10, skill count from 27 to 30, command count from 7 to 6 (active)
- **`common.sh` missing `set -e`** — Added defensive error handling to sourced library script

---

## [3.2.1] - 2026-03-17

### humaninloop 3.2.1

#### Changed

- **Renamed `testing-agent` to `qa-engineer`** — Restructured as a persona agent following the same conventions as `requirements-analyst` and `principal-architect`. Model upgraded from sonnet to opus. Procedural content moved to skill, agent now focuses on identity, judgment, and quality standards.
- **Promoted `qa-engineer` to persona agent category** in AGENT-GUIDELINES.md (previously classified as executor agent)
- **Updated all references** across plugin.json, implement-catalog.json, dag-assembler, task-architect, README, AGENT-GUIDELINES, and 6 skill reference files

#### Fixed

- **testing-end-user skill SHOULD clause** — Updated from "when encountering" to RFC 2119 compliant "when the user says" format with quoted trigger phrases

---

## [3.2.0] - 2026-03-16

**BREAKING CHANGE**: `/humaninloop:implement` migrated to DAG-based architecture with Supervisor + DAG Assembler + State Analyst pattern.

### humaninloop 3.2.0

#### Breaking Changes

- **Implement command architecture** — `/humaninloop:implement` now uses DAG-based workflow execution with the same Supervisor + DAG Assembler + State Analyst infrastructure as `/humaninloop:specify`. The old sequential parse-and-execute architecture is replaced.

#### New Agents

- **Staff Engineer** — Implementation specialist who writes code through strict TDD discipline (red/green/refactor). Executes cycle task lists, handles retry after checkpoint failure, and fix mode after final-validation failure. Uses skills: `executing-tdd-cycle`, `brownfield-integration`

#### New Skills

- **`executing-tdd-cycle`** — TDD red/green/refactor discipline for cycle execution, task parsing, retry handling, fix mode, and cycle report generation
- **`brownfield-integration`** — EXTEND/MODIFY semantics, read-before-write checklist, interface preservation, and conflict detection for existing codebases
- **`strategy-implementation`** — Implementation-workflow patterns (cycle sequencing, execute-then-verify, targeted retry, escalation) consumed by the State Analyst for briefings

#### New Catalogs

- **`implement-catalog.json`** — Node catalog defining available nodes, edge constraints, and system invariants for the implement DAG-based workflow

#### Updated Agents

- **DAG Assembler** — Extended with NL prompt construction patterns for implement workflow nodes (execute-cycle, verify-cycle, cycle-checkpoint, final-validation, tasks-complete gate)
- **State Analyst** — Extended with implement workflow report parsing patterns (cycle-report.md, verification-report.md) and cycle awareness for implementation briefings
- **Staff Engineer** — Fixed coupling leaks (sibling awareness, sequencing knowledge, artifact path assumptions)

#### Updated Skills

- **`testing-end-user`** — Added quality gate execution sequence and report format for implementation cycle verification
- **`patterns-vertical-tdd`** — Updated cycle structure and slice identification for implement workflow integration
- **`brownfield-integration`** — Added RFC 2119 description format, foundational principle, rationalization table, and loophole closures
- **`executing-tdd-cycle`** — Added RFC 2119 description format, removed specific agent names from When NOT to Use, added loophole closures
- **`strategy-implementation`** — Restructured with all required sections (Overview, When to Use, When NOT to Use, Common Mistakes), RFC 2119 description format, removed specific agent names
- **`authoring-technical-requirements`** — Added loophole closures

#### Documentation

- README updated with DAG-based implement workflow description and all implement workflow agents
- ROADMAP updated to reflect 10 agents, 30 skills, and DAG-based implement workflow

---

## [3.1.1] - 2026-03-16

### humaninloop 3.1.1

#### Fixed

- **Infrastructure requirements silently dropped** — Constraints (C-XXX) and NFRs implying platform provisioning (deployment, CI/CD, monitoring, environment config) are now captured as IP-XXX items in Part 3 of `constraints-and-decisions.md` and threaded through the entire workflow pipeline (issue #79)
- **Platform foundation missing from task cycles** — Vertical TDD skill now distinguishes platform foundation (IP-XXX items) from application foundation, with platform cycles preceding application cycles

#### Changed

- **`authoring-technical-requirements` skill** — Added Section 3 (Infrastructure Requirements) with IP-XXX template, traceability rules, and quality checklist items; added namespace-qualified cross-references; added loophole closures for key rules
- **`patterns-vertical-tdd` skill** — Added C0 platform infrastructure cycle to foundation example; updated foundation identification to include "in production" qualifier; fixed second-person writing to imperative style
- **`validation-plan-artifacts` checklists** — Added Critical checks for infrastructure coverage (IP-XXX) and IP-NFR coverage
- **`validation-task-artifacts` checklists** — Added Critical checks for IP-XXX task coverage, platform-app ordering, and constraint-task traceability
- **Technical Analyst agent** — Added infrastructure-aware quality standard and constraint-to-infrastructure tracing; refactored brownfield awareness to character traits
- **Task Architect agent** — Added IP-XXX mapping and platform ordering to success criteria
- **Plan command** — Added infrastructure planning block, constraint actionability advocate check, and infrastructure-design alignment consistency check
- **Plan template** — Added Infrastructure Requirements summary table
- **ARTIFACT-TEMPLATES.md** — Added Part 3 template with IP-XXX field definitions and infrastructure type taxonomy

---

## [3.1.0] - 2026-03-16

**BREAKING CHANGE**: `/humaninloop:techspec` merged into `/humaninloop:plan` as a unified two-phase workflow.

### humaninloop 3.1.0

#### Breaking Changes

- **Techspec command deprecated** — `/humaninloop:techspec` is deprecated; all functionality absorbed into `/humaninloop:plan` with Phase 1 (Analysis) and Phase 2 (Design)
- **Artifact layout changed** — `technical/` subdirectory eliminated; `constraints.md` + `research.md` merged into `constraints-and-decisions.md`; `data-sensitivity.md` absorbed into `data-model.md`; `integrations.md` absorbed into `contracts/api.yaml` as `x-integration` extensions
- **Plan Architect agent removed** — responsibilities absorbed by expanded Technical Analyst agent
- **Techspec context file removed** — `techspec-context.md` replaced by unified `plan-context.md`

#### New Features

- **Unified `/humaninloop:plan` command** — Single command with 2 phases, 3 agents, 5 invocations producing 6 artifacts + summary
  - Phase P1 (Analysis): Technical Analyst → Principal Architect (feasibility gate) → Devil's Advocate
  - Phase P2 (Design): Technical Analyst → Devil's Advocate
- **Constraints-and-decisions artifact** — Unified document with C-XXX constraints and D-XXX technology decisions with bidirectional cross-references
- **Embedded data sensitivity** — Per-entity/per-attribute sensitivity classifications within `data-model.md`
- **Embedded integration boundaries** — `x-integration` OpenAPI extensions in `contracts/api.yaml` with failure modes and fallback strategies
- **Narrowed Principal Architect scope** — Feasibility intersection review only (cross-artifact contradictions, not individual completeness)

#### Updated Skills

- `authoring-technical-requirements` — Updated for three-artifact analysis output (requirements, constraints-and-decisions, NFRs)
- `validation-plan-artifacts` — Rewritten with P1/P2 phase checklists replacing B0/B1/B2
- `patterns-api-contracts` — Added `x-integration` extension guidance

#### Updated Templates

- `plan-context-template.md` — Unified template with `analysis_status`/`design_status` tracking
- `techanalyst-report-template.md` — Added Phase 2 (Design) sections
- `architect-report-template.md` — Narrowed to feasibility intersection format
- `plan-template.md` — Updated for merged artifact references

#### Documentation

- ADR-008: Techspec-plan merge decision documented
- Agent count corrected to 9 (plan-architect removed)
- README and ROADMAP updated for unified workflow

---

## [3.0.0] - 2026-02-19

**BREAKING CHANGE**: Complete v3 architecture redesign. Single-DAG iteration model replaces per-pass DAGPass. StrategyGraph is the new top-level entity. Constitution v3.0.0.

### humaninloop 3.0.0

#### Breaking Changes

- **StrategyGraph replaces DAGPass** — Single persistent DAG with multi-pass iteration replaces the v2 per-pass model. All CLI commands operate on `StrategyGraph` JSON
- **Constitution v3.0.0** — 12 governance principles (added XI: Layer Dependency Discipline, XII: Catalog-Driven Assembly). Two-tier deterministic infrastructure. Single governed codebase (`humaninloop_brain` only)
- **v3 entity model throughout** — `PassEntry` replaces `DAGPass`, `GateLifecycleStatus` replaces `GateStatus`, `NodeHistoryEntry` and `ExecutionTraceEntry` are new. 11 enums, 14 models, 7 entity modules
- **Specify workflow rewritten** — DAG-based execution with goal-oriented Supervisor, DAG Assembler for graph mechanics, and State Analyst for briefings/report parsing

#### New Infrastructure

- **StrategyGraph model** — Single-DAG entity with `passes`, `nodes`, `edges`, and lifecycle status tracking
- **triggered_by edge type** — Edges that fire when prerequisite nodes complete, enabling reactive node assembly
- **Gate verdict/lifecycle enums** — `GateVerdict` (pass/fail/conditional/halted) and `GateLifecycleStatus` (pending/active/passed/failed) for gate node semantics
- **Capability tag resolution** — `hil-dag assemble` now resolves catalog capabilities to infer edges automatically
- **v3 lifecycle functions** — `bootstrap_graph()`, `add_evidence()`, `record_analysis()` for StrategyGraph management

#### Changed: humaninloop_brain

- **Entities** — Extended with v3 fields: `history` on nodes, `verdict`/`lifecycle` on gates, `capabilities` on catalog entries. `NodeHistoryEntry` tracks all state transitions
- **Graph operations** — Generalized for StrategyGraph: loader, views, sort, guard, and inference all operate on the new schema
- **Validators** — Updated for v3 semantics: structural validator, contract checker, and invariant enforcer all validate StrategyGraph
- **CLI** — All 7 `hil-dag` subcommands migrated to StrategyGraph schema with backwards-incompatible JSON output
- **Passes** — Lifecycle functions rewritten for single-DAG iteration model

#### Changed: Agents

- **dag-assembler** — Rewritten for v3: single-DAG bootstrap, auto-resolution via capability tags, `triggered_by` edge support, 3 actions (assemble-and-prepare, freeze-pass, bootstrap)
- **state-analyst** — Rewritten for v3: parse-and-recommend action with ranked recommendations, Opus model for deeper analysis
- **specify.md** — Rewritten as v3 goal-oriented supervisor with DAG-based execution, State Analyst briefings, and structured responsibility boundaries

#### Architecture Documentation

- **v3 architecture design documents** — Complete redesign docs in `docs/architecture/v3/`
- **Milestone prerequisite edges** — Clarified edge types and pass 1 carry-forward behavior

#### Fixed

- 28 v3 architecture violations resolved across multiple severity levels (critical, high, medium, low)
- Capability tag vocabulary and semantic fallback alignment
- Constitution-gate verdict vocabulary consistency
- DAG Assembler action count assertions
- Agent and brain infrastructure alignment with v3 contracts

#### Tests

- 381 tests pass, 97.41% coverage (18 new tests covering v3-specific feature gaps)

---

## [2.2.0] - 2026-02-18

State Analyst redesign: cleaner responsibility split between graph mechanics and content analysis.

### humaninloop 2.2.0

#### New Agent

- **state-analyst** — Renamed from state-briefer. Now owns all "read and understand" work: workflow briefings (unchanged) and report parsing (moved from DAG Assembler). Records analysis results atomically via `hil-dag record`

#### New Infrastructure

- **`hil-dag record` CLI command** — Atomic status + evidence + trace writes for a single node. Used by the State Analyst's `parse-report` action instead of separate `hil-dag status` calls
- **`dag-record.sh` shell script** — Shell wrapper for `hil-dag record` in the `dag-operations` skill (8 scripts total)
- **`add_evidence()` lifecycle function** — Append evidence attachments to a node in the DAG pass
- **`record_analysis()` lifecycle function** — Compound operation: update status + append evidence + add trace entry atomically

#### Changed

- **dag-assembler** — Slimmed to pure graph mechanics: only `assemble-and-prepare` and `freeze-pass` actions remain. `parse-report` action moved to State Analyst
- **specify.md** — All `parse-report` calls routed to `humaninloop:state-analyst` instead of `humaninloop:dag-assembler`. Responsibility Boundaries table updated with 13 operations across Supervisor, DAG Assembler, and State Analyst
- **dag-operations SKILL.md** — Added `record` operation (8 operations total). Updated overview to mention State Analyst alongside DAG Assembler
- **strategy-core SKILL.md** — "State Briefer" → "State Analyst" in description and body
- **strategy-specification SKILL.md** — "State Briefer" → "State Analyst" in description and body
- **README.md** — Updated Specify Workflow Agents table and workflow description

#### Removed

- **state-briefer.md** — Renamed to `state-analyst.md`

#### Tests

- 281 tests pass, 97.89% coverage (17 new tests for `add_evidence`, `record_analysis`, `cmd_record`, and spec consistency)

---

## [2.1.2] - 2026-02-18

Patch release: Align specify.md with DAG architecture design documents after dry run.

### humaninloop 2.1.2

#### Fixed

- **specify.md**: Enforce mandatory `parse-report` after every domain agent execution (was being skipped entirely)
- **specify.md**: Enforce mandatory State Briefer briefing at start of every pass, not just pass 1
- **specify.md**: Route all domain node status updates through DAG Assembler's `parse-report`, not direct `hil-dag status` CLI
- **specify.md**: Route all pass freezing through DAG Assembler's `freeze-pass` action, not direct `hil-dag freeze` CLI
- **specify.md**: Route clarification question extraction through parse-report `unresolved` field, not direct report reading

#### Added

- **specify.md**: Context Protection section with 5 NEVER/ALWAYS rules preventing Supervisor context window pollution
- **specify.md**: Responsibility Boundaries table mapping 11 operations to Supervisor/DAG Assembler/State Briefer ownership
- **specify.md**: Recurring gap escalation at pass 3+ when convergence stalls (from `strategy-core` Pass Evolution pattern)
- **specify.md**: Supervisor halt escape hatch for unexpected situations with `outcome: "halted"` freeze pattern
- **specify.md**: On-demand State Briefer re-briefing option mid-pass after unexpected results
- **specify.md**: New Pass Procedure with lettered steps (A-D) replacing ambiguous inline CLI blocks

---

## [2.1.1] - 2026-02-18

Patch release: 8 bug fixes from first end-to-end dry run of the specify workflow.

### humaninloop 2.1.1

#### Fixed

- **specify.md**: Auto-resolve `hil-dag` PATH from venv instead of hard-failing when CLI not on PATH
- **specify.md**: Use absolute `$PROJECT_ROOT` paths for all subagent invocations (prevents files created in wrong directory)
- **specify.md**: Add `hil-dag` CLI reference section with exact command signatures for all 7 subcommands
- **specify.md**: Add explicit freeze/create syntax in pass-transition instructions with correct flag names
- **specify.md**: Re-add `constitution-gate` on new passes to satisfy INV-002 invariant
- **specify.md**: Instruct Read-then-Edit for `spec.md` (already created by `create-new-feature.sh`)
- **dag-assembler.md**: Fix `outcome_detail` → `detail` field naming to match `hil-dag freeze --detail` CLI flag
- **specify-catalog.json**: Remove `spec.md` from `spec-complete` milestone consumes to fix INV-001 invariant violation (route through advocate gate instead)
- **dag-operations scripts**: Add `hil-dag` availability guard with structured JSON error to all 7 shell scripts

#### Changed

- **ui-designer agent**: Add `patterns-interface-design` skill to skills list
- **README.md**: Add Design Workflow section documenting the ui-designer agent

---

## [2.1.0] - 2026-02-18

DAG-first infrastructure: deterministic graph execution replaces hardcoded supervisor loops.

### humaninloop 2.1.0

#### New Package: humaninloop_brain

- **humaninloop_brain** - Deterministic DAG infrastructure package for workflow execution
  - Pydantic entity models for nodes, edges, DAG passes, catalogs, validation results
  - NetworkX-backed graph operations: loading, subgraph views, topological sort, acyclicity guard, edge inference
  - 9-step structural validator with invariant and contract checking
  - Pass lifecycle management: creation, node assembly, status updates, freeze
  - `hil-dag` CLI with 7 subcommands producing JSON output
  - 262 tests, 98% coverage
  - Constitution v2.0.0 with Principle IX (Deterministic Infrastructure) and Principle X (Pydantic Entity Modeling)

#### New Agents

- **dag-assembler** - Deterministic graph assembly specialist that translates Supervisor decisions into validated DAG mutations via the `hil-dag` CLI. Constructs natural-language prompts for domain agents from catalog contracts. Uses skill: `dag-operations`
- **state-briefer** - Reads DAG history, current pass state, strategy skills, and catalog to produce structured workflow briefings for the Supervisor. Informs assembly decisions without making them

#### New Skills

- **dag-operations** - Shell wrappers for the `hil-dag` CLI: create, assemble, validate, sort, status, freeze, catalog-validate. 7 scripts with structured JSON output
- **strategy-core** - Universal workflow patterns (validation gates, gap classification, pass evolution, halt escalation) consumed by the State Briefer to inform Supervisor briefings
- **strategy-specification** - Specification-workflow patterns (input assessment, produce-then-validate, gap-informed revision, research-before-user) consumed by the State Briefer

#### New Infrastructure

- `catalogs/` directory with `specify-catalog.json` - Node catalog for the specify workflow (7 nodes, 5 invariants, artifact contracts)
- `docs/architecture/` - DAG-first architecture synthesis documents
- ADR-007: DAG-First Infrastructure
- Constitution v2.0.0 with brownfield analysis and 10 governance principles

#### Changed

- **/humaninloop:specify** - Rewritten from 2-agent supervisor loop to DAG-based execution with assembly decisions informed by State Briefer briefings. DAG Assembler handles all graph mechanics; Supervisor focuses on routing and judgment
- **advocate-report-template.md** - Added `halted` verdict option for scope gaps

#### Fixed

- **Task catalog node statuses** - Added `halted` status to task nodes from run-3 scenario testing
- **CLI output alignment** - Aligned CLI output, catalog contracts, and agent spec from scenario testing

---

## [2.0.0] - 2026-02-17

**BREAKING CHANGE**: New techspec workflow stage required between specify and plan.

### humaninloop 2.0.0

#### Breaking Changes
- **plan.md now requires techspec completion** - The `/humaninloop:plan` command entry gate validates that all 5 technical artifacts exist before proceeding. Users who previously ran `specify → plan` must now run `specify → techspec → plan`.

#### Migration Guide
1. For new features: run `/humaninloop:techspec` after `/humaninloop:specify` and before `/humaninloop:plan`
2. For in-progress features with existing `spec.md` but no `technical/` directory: run `/humaninloop:techspec` to generate the required artifacts before continuing with `/humaninloop:plan`

#### New Command
- **/humaninloop:techspec** - Multi-agent technical specification workflow with three agents and validation loops
  - Phase T0 (Core): Technical Analyst produces requirements and constraints, Principal Architect reviews feasibility, Devil's Advocate validates completeness
  - Phase T1 (Supplementary): Technical Analyst produces NFRs, integration maps, and data sensitivity, Principal Architect reviews feasibility, Devil's Advocate validates completeness
  - Two-pass production with incremental validation between passes
  - Entry gate validates spec completion before proceeding

#### New Agent
- **technical-analyst** - Senior technical analyst who translates business specifications into traceable technical artifacts
  - Produces five artifact types: TR- (technical requirements), C- (constraints), NFR- (non-functional requirements), INT- (integration maps), DS- (data sensitivity classifications)
  - Uses `authoring-technical-requirements` skill
  - AGENT-GUIDELINES compliant with `<example>` invocation blocks

#### New Skill
- **authoring-technical-requirements** - Translate business specifications into five traceable technical artifacts
  - Triggered by: "write technical requirements", "define constraints", "define NFRs", "map integrations", "classify data sensitivity"
  - Reference files: ARTIFACT-TEMPLATES.md, TRACEABILITY-PATTERNS.md

#### New Templates
- `techspec-context-template.md` - Context artifact for techspec supervisor-agent communication
- `techanalyst-report-template.md` - Report format for technical analyst output
- `architect-report-template.md` - Report format for plan architect techspec review

#### Changed
- **plan.md** - Added techspec entry gate; plan command now validates that techspec workflow has completed before proceeding
- **plan-context-template.md** - Added technical artifact rows for techspec outputs

---

## [1.1.1] - 2026-02-08

### humaninloop 1.1.1

#### Changed
- **devils-advocate agent** - Refactored to AGENT-GUIDELINES compliance (#66)
  - Added `<example>` invocation examples in description for Task tool triggering
  - Replaced inline phase-specific review criteria with skill delegation
  - Added structured "What You Produce", "Quality Standards", and "Adversarial Calibration" sections
  - Skill references now use `humaninloop:` namespace prefix

---

## [1.1.0] - 2026-02-07

### humaninloop 1.1.0

#### Added
- **ui-designer agent** - Senior interface designer who analyzes visual inspiration from existing apps to extract design patterns, build actionable design systems, and craft screen layouts and interaction flows
- **analysis-screenshot skill** - Step-by-step process for extracting design tokens, components, and layout structure from screenshot images with `references/implementation-templates.md`
- **patterns-flow-mapping skill** - Procedure for connecting multiple analyzed screenshots into coherent interaction flows with navigation logic and journey definitions
- **authoring-design-system skill** - Procedure for synthesizing extractions from multiple screenshots into a unified design system with `references/implementation-output-templates.md`

---

## [1.0.0] - 2026-02-06

**First stable release.** Specification-driven development workflow is production-ready.

This milestone marks API stability for the humaninloop plugin. The core workflow (setup → specify → plan → tasks → implement) is complete, tested, and ready for production use.

### humaninloop 1.0.0

#### Changed
- **analysis-iterative skill** - Rewritten from rigid prescriptive phases to principle-based adaptive behavior (#64)
  - New phase model: Opening → Discovery → Adaptive Questioning → Conclusion
  - Three question formats: structured options, open probes, confirmations
  - Confidence signal reading and smart wrap-up
  - New `references/ADAPTIVE-EXAMPLES.md` with annotated conversations

#### Highlights Since 0.1.0
- **6 Commands**: setup, specify, plan, tasks, audit, implement
- **6 Specialized Agents**: requirements-analyst, devils-advocate, plan-architect, task-architect, principal-architect, testing-agent
- **20 Skills**: authoring, analysis, patterns, validation, testing, and utility skills
- **Brownfield Support**: Essential Floor + Emergent Ceiling approach for existing codebases
- **Vertical TDD**: Cycle-based task generation with test-first ordering
- **Human Verification**: Testing agent with checkpoint gates

---

## [0.8.10] - 2026-02-05

Complete SKILL-GUIDELINES v1.2.0 compliance (#63).

### humaninloop 0.8.10

#### Fixed
- **2 remaining skills** - Aligned with SKILL-GUIDELINES v1.2.0 compliance:
  - Fixed RFC 2119 invocation format ("MUST be invoked when user says")
  - Renamed Core Mandate → Overview section (patterns-interface-design)

  Skills updated:
  - patterns-interface-design
  - using-git-worktrees

All 20 skills now comply with SKILL-GUIDELINES v1.2.0.

---

## [0.8.9] - 2026-02-05

Skill compliance audit for SKILL-GUIDELINES v1.2.0 (#62).

### humaninloop 0.8.9

#### Fixed
- **17 skills** - Aligned with SKILL-GUIDELINES v1.2.0 compliance:
  - Fixed RFC 2119 invocation format ("MUST be invoked when user says")
  - Renamed Purpose → Overview sections
  - Added When to Use / When NOT to Use sections
  - Renamed Anti-Patterns → Common Mistakes with expanded examples
  - Moved reference files to references/ subdirectory

  Skills updated:
  - authoring-requirements, authoring-user-stories
  - validation-plan-artifacts, validation-task-artifacts
  - patterns-vertical-tdd, patterns-technical-decisions
  - patterns-entity-modeling, patterns-api-contracts
  - analysis-specifications, analysis-iterative, analysis-codebase
  - testing-end-user, syncing-claude-md
  - authoring-constitution, brownfield-constitution, validation-constitution
  - authoring-roadmap

#### Documentation
- README: Added ASCII workflow and command diagrams
- README: Added agent descriptions to command diagrams
- README: Replaced hero banner with compact header

---

## [0.8.8] - 2026-01-26

Research option in clarification flow and skill YAML compliance.

### humaninloop 0.8.8

#### Added
- **Research this option** - Clarification questions in /specify, /plan, and /tasks now offer "Research this" option (#58)
  - Supervisor can research answers using codebase exploration, web search, or documentation lookup
  - Clarification log tracks source (user vs research) for answers
  - User confirms or overrides research findings before proceeding

#### Fixed
- **8 skills** - Convert multi-line YAML descriptions to single-line format for reliable model triggering
  - `analysis-codebase`, `authoring-constitution`, `authoring-roadmap`, `brownfield-constitution`
  - `syncing-claude-md`, `testing-end-user`, `using-git-worktrees`, `validation-constitution`

---

## [0.8.7] - 2026-01-26

Skill audit compliance and /specify workflow improvements.

### humaninloop 0.8.7

#### Fixed
- **8 skills** - Address audit compliance issues with improved structure
  - `authoring-roadmap`, `using-git-worktrees`, `syncing-claude-md`, `analysis-codebase`
  - `validation-constitution`, `brownfield-constitution`, `authoring-constitution`, `testing-end-user`
- **/humaninloop:specify** - Reorder semantic detection to run before user prompt display
- **/humaninloop:specify** - Add enrichment continuation to parse skill output and proceed to Phase 1

---

## [0.8.6] - 2026-01-26

Skill auto-invocation fix for user-invoked skills.

### humaninloop 0.8.6

#### Fixed
- **using-github-issues skill** - Added RFC 2119 keywords for reliable auto-invocation (#55)
  - Skill now uses `MUST` keyword: "This skill MUST be invoked when the user says..."
  - Follows ADR-006 pattern for user-invoked skills vs agent-invoked skills

#### Documentation
- **ADR-006** - RFC 2119 Keywords for Skill Auto-Invocation pattern documented

---

## [0.8.5] - 2026-01-26

Unified verification format with runtime classification.

### humaninloop 0.8.5

#### Changed
- **Unified TEST: marker** - All verification tasks now use single `**TEST:**` format
  - Replaces `TEST:VERIFY`, `TEST:CONTRACT`, and `HUMAN VERIFICATION` markers
  - Legacy formats remain supported for backward compatibility
- **Runtime classification** - Testing-agent now classifies tasks at execution time
  - CLI tasks with backtick commands and measurable asserts
  - GUI tasks with UI actions or screenshot captures
  - SUBJECTIVE tasks with qualitative terms (looks, feels)
- **Auto-approval gate** - CLI tasks may auto-approve when:
  - Classification is CLI
  - 100% assertions pass
  - No errors or timeouts
  - No `**Human-Review**:` field
- **testing-agent.md** - Added classification logic and checkpoint ownership
- **implement.md** - Simplified routing, removed checkpoint presentation
- **task-architect.md** - Simplified to unified format, removed decision guide
- **CYCLE-STRUCTURE.md** - Updated all examples to unified format
- **testing-end-user skill** - Updated marker documentation
- **TASK-PARSING.md** - Added legacy format support section
- **PHASE-CHECKLISTS.md** - Updated validation examples

---

## [0.8.4] - 2026-01-25

New UI/interface design skill.

### humaninloop 0.8.4

#### New Skill
- **patterns-interface-design** - UI component and interface design patterns
  - Discovery process: domain exploration, color world, signature element, default replacement
  - Surface and token architecture with primitive foundation
  - Dark mode and elevation patterns
  - Reference files: CRAFT-PRINCIPLES.md, VALIDATION-CHECKS.md

---

## [0.8.3] - 2026-01-25

New skill and skill rename.

### humaninloop 0.8.3

#### New Skill
- **using-git-worktrees** - Git worktree workflow management for parallel feature development
  - Worktree creation, listing, and cleanup patterns
  - Best practices for branch-per-worktree workflows
  - Example scripts: `worktree-setup.sh`, `worktree-list.sh`, `worktree-cleanup.sh`

#### Changed
- **using-github-issues** - Renamed from `tooling-github-issues` to align with `using-` prefix convention

---

## [0.8.2] - 2026-01-25

Skills update: new GitHub issues management skill and testing-end-user skill rebuild.

### humaninloop 0.8.2

#### New Skill
- **using-github-issues** - GitHub issue management with quality standards enforcement
  - Bug report, feature request, task, and security advisory templates
  - Pre-creation checklist with duplicate and security checks
  - Lifecycle management (search, triage, status updates, batch operations)
  - Common rationalizations and red flags sections
  - Reference: `examples/` and `references/gh-cli-commands.md`

#### Changed
- **testing-end-user** - Rebuilt for guideline compliance
  - Restructured with "When NOT to Use", "Common Rationalizations", "Red Flags", "Common Mistakes" sections
  - Added testing evidence documentation (RED/GREEN/REFACTOR cycle)
  - Reference files: TASK-PARSING.md, EVIDENCE-CAPTURE.md, REPORT-TEMPLATES.md

---

## [0.8.1] - 2026-01-25

Skill structure compliance release: bring all constitution-related skills into alignment with SKILL.md guidelines.

### humaninloop 0.8.1

#### Fixed
- **analysis-codebase** - Added "When NOT to Use" and "Common Mistakes" sections per skill guidelines
- **authoring-constitution** - Restructured with "When NOT to Use" and "Common Mistakes" sections
- **authoring-roadmap** - Added "Common Rationalizations" and "Red Flags" sections
- **brownfield-constitution** - Added "Common Mistakes" section with detailed problem/fix guidance
- **syncing-claude-md** - Added "Common Mistakes" section per skill guidelines
- **validation-constitution** - Added "Common Rationalizations" and explicit loophole closures
- **marketplace README** - Updated stale skill and agent counts

---

## [0.8.0] - 2026-01-24

Testing agent with human verification gate for test-driven implementation cycles (#43).

### humaninloop 0.8.0

#### New Agent
- **testing-agent** - Collaborative QA partner that executes verification tasks, captures evidence, and presents checkpoints for human review
  - Routes `TEST:VERIFY` tasks to automated execution
  - Captures console output, timing, file states
  - Generates adaptive reports (minimal for pass, rich for fail)
  - Presents human checkpoint before cycle completion

#### New Skill
- **testing-end-user** - End-user verification testing against real infrastructure
  - Parses `TEST:VERIFY` task format with Setup/Action/Assert/Capture/Human-Review fields
  - Executes commands with modifiers: `(background)`, `(timeout Ns)`, `(in {path})`
  - Assert patterns: `Console contains`, `File exists`, `Response status`
  - Reference files: TASK-PARSING.md, EVIDENCE-CAPTURE.md, REPORT-TEMPLATES.md

#### Changed
- **task-architect.md** - Added `TEST:VERIFY` task format generation
  - New testable verification format with field markers
  - Decision guide for TEST:VERIFY vs HUMAN VERIFICATION selection
- **CYCLE-STRUCTURE.md** - Added testable verification task documentation
  - Complete format specification with examples
  - Action modifiers and assert patterns
- **implement.md** - Added testing-agent routing for TEST:VERIFY tasks
  - Detection and routing logic for TEST:* markers
  - Human approval gates cycle completion
  - Retry support with adjustments

---

## [0.7.12] - 2026-01-24

Housekeeping release: skill description format standardization and documentation sync.

### humaninloop 0.7.12

#### Changed
- **All skills** - Standardized descriptions to third-person format for consistency
- **README.md** - Removed stale `analysis-codebase` reference from plan-architect (per 0.7.8 optimization)

#### Fixed
- **marketplace.json** - Version now syncs correctly with plugin.json

---

## [0.7.11] - 2026-01-21

Relax hexagonal architecture constraints to allow approved gold standard libraries in domain layer (#40).

### humaninloop 0.7.11

#### New Resources
- **approved-domain-deps.md** - Registry template for approved domain layer dependencies
  - Qualification criteria (>80% ubiquity + domain-relevance)
  - Libraries by language: Python (pydantic, attrs), TypeScript (zod, decimal.js, uuid), Go, Rust, Java
  - Addition process and linter enforcement guidance

#### Changed
- **RECOMMENDED-PATTERNS.md** - Updated hexagonal architecture layer rules
  - Domain layer now allows "Standard library + approved domain deps" (was "Standard library only")
  - Added "Approved Domain Dependencies" section with qualification criteria
  - Updated enforcement with domain allowlist and CI blocking rules
  - Added "Domain Allowlist Config" column to tooling table
- **EMERGENT-CEILING-PATTERNS.md** - Updated brownfield patterns for consistency
  - Domain layer now allows "stdlib + approved domain deps"
  - Added "Domain Layer Dependencies" subsection with cross-reference
  - Updated testability criteria for registry validation
- **constitution-template.md** - Added domain layer note referencing registry template

---

## [0.7.10] - 2026-01-20

Greenfield constitution enhancements with recommended architectural patterns.

### humaninloop 0.7.10

#### New Resources
- **RECOMMENDED-PATTERNS.md** - Architectural patterns guide for greenfield constitutions
  - Hexagonal Architecture (Ports & Adapters)
  - Single Responsibility & Module Boundaries
  - Dependency Discipline
  - Stack-specific tooling guidance (Python, TypeScript, Go, Rust, Java)

#### Changed
- **/humaninloop:setup** - Greenfield mode now recommends architectural principles (V-VII) beyond the Essential Floor (I-IV)
- **authoring-constitution skill** - Added Greenfield Recommendation section with architectural pattern references
- **Constitution output** - Greenfield reports now include "Architectural Principles" section

---

## [0.7.9] - 2026-01-14

Smart input detection and brainstorm pre-processor for /specify command (#37).

### humaninloop 0.7.9

#### New Features
- **Smart input detection** - /specify now analyzes input for Who/Problem/Value triad completeness
- **Brainstorm pre-processor** - Sparse inputs automatically routed to `analysis-iterative` skill for enrichment
- **`--skip-brainstorm` flag** - Bypass automatic enrichment when input is known to be complete

#### New Skill Resources
- **SPECIFICATION-INPUT.md** - Focused mode for input enrichment in `analysis-iterative` skill
- **ENRICHMENT.md** - Template for enriched feature descriptions

#### Changed
- **/humaninloop:specify** - Added Phase 0.5 for input guidance and enrichment
- **analysis-iterative skill** - Extended description to include /specify integration

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

[3.0.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v3.0.0
[2.2.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v2.2.0
[2.1.2]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v2.1.2
[2.1.1]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v2.1.1
[2.1.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v2.1.0
[2.0.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v2.0.0
[1.1.1]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v1.1.1
[1.1.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v1.1.0
[1.0.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v1.0.0
[0.8.10]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.10
[0.8.9]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.9
[0.8.8]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.8
[0.8.7]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.7
[0.8.6]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.6
[0.8.5]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.5
[0.8.4]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.4
[0.8.3]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.3
[0.8.2]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.2
[0.8.1]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.1
[0.8.0]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.8.0
[0.7.12]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.12
[0.7.11]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.11
[0.7.10]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.10
[0.7.9]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.9
[0.7.8]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.8
[0.7.7]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.7
[0.7.6]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.6
[0.7.5]: https://github.com/deepeshBodh/human-in-loop/releases/tag/v0.7.5
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
