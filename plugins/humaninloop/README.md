# HumanInLoop Plugin

Specification-driven development workflow: **setup → specify → plan → tasks → implement**

## Overview

The HumanInLoop plugin provides a comprehensive multi-agent workflow for specification-driven development. It automates the entire feature development lifecycle from constitution setup to implementation.

**Core Workflows:**
- **Setup** - Create project constitution with enforceable governance principles
- **Specify** - Create feature specifications with integrated quality validation
- **Plan** - Translate business specifications into technical requirements, then design data models and API contracts
- **Tasks** - Generate actionable implementation tasks with dependency tracking and brownfield markers
- **Implement** - Execute implementation with DAG-based TDD discipline and cycle management

## Installation

### 1. Add the marketplace and install the plugin

```bash
/plugin marketplace add deepeshBodh/human-in-loop
/plugin install humaninloop
```

### 2. Install the `hil-dag` CLI (required for specify and implement)

The `/humaninloop:specify` and `/humaninloop:implement` workflows use the `hil-dag` CLI for deterministic DAG operations. Add it as a dev dependency in your project:

```bash
uv add --dev "humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"
```

**To upgrade to the latest version:**

```bash
uv add --dev --upgrade "humaninloop-brain @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop_brain"
```

Verify it works:

```bash
uv run hil-dag --help
```

**Note:** The `/humaninloop:setup`, `/humaninloop:plan`, and `/humaninloop:tasks` commands do NOT require `hil-dag` — they work immediately after plugin installation.

## Getting Started

First, set up your project constitution:

```bash
/humaninloop:setup
```

Then proceed with the specification workflow for your first feature.

## Commands

### `/humaninloop:setup`

Create or amend your project constitution with enforceable governance principles. Supports both greenfield and brownfield projects.

```
/humaninloop:setup
```

**Modes:**

| Mode | When to Use | Artefacts |
|------|-------------|-----------|
| **Brownfield** | Existing codebase (>5 source files) | `codebase-analysis.md`, `constitution.md`, `evolution-roadmap.md` |
| **Greenfield** | New project | `constitution.md` only |
| **Amend** | Update existing constitution | `constitution.md` (updated) |

**Brownfield Workflow:**
1. **Detection**: Analyze codebase for framework, entities, patterns
2. **Analysis**: Principal Architect produces `codebase-analysis.md` with:
   - Project inventory (factual): structure, patterns, entities
   - Assessment (judgment): strengths, inconsistencies, essential floor status
3. **Checkpoint**: User reviews and confirms analysis accuracy
4. **Constitution**: Create with essential floor + emergent ceiling (existing good patterns)
5. **Roadmap**: Generate `evolution-roadmap.md` with gap cards (P1/P2/P3 priorities)

**Essential Floor** (always included in constitution):
- **Security**: Auth at boundaries, secrets from env, input validation
- **Testing**: Automated tests, coverage measurement
- **Error Handling**: Explicit handling, context for debugging
- **Observability**: Structured logging, correlation IDs

**Output:**
- `.humaninloop/memory/constitution.md` - Project governance
- `.humaninloop/memory/codebase-analysis.md` - Codebase inventory (brownfield only)
- `.humaninloop/memory/evolution-roadmap.md` - Gap cards for improvement (brownfield only)

**Features:**
- Three-Part Principle Rule (Enforcement, Testability, Rationale)
- RFC 2119 keywords (MUST, SHOULD, MAY)
- Automatic CLAUDE.md synchronization
- Brownfield analysis with checkpoint for user confirmation
- Evolution roadmap with prioritized gap cards and dependency graph

### `/humaninloop:specify <description>`

Create a feature specification with integrated quality validation.

```
/humaninloop:specify Add user authentication with OAuth2 support
```

**Workflow (DAG-based execution):**
1. Generate short name from description (2-4 words, e.g., `user-auth`)
2. Create feature branch and directory using `create-new-feature.sh` script
3. State Analyst produces workflow briefing from DAG history, catalog, and strategy skills
4. Supervisor makes assembly decision; DAG Assembler validates and builds graph node
5. Domain agents execute (Requirements Analyst produces spec, Devil's Advocate reviews)
6. State Analyst parses agent reports, records status + evidence + trace via `hil-dag record`
7. Loop until advocate verdict is `ready` or user accepts current state

**Branch Format:** `###-short-name` (e.g., `001-user-auth`)
- Branch name = spec directory name = feature ID
- Number auto-increments based on existing branches and specs

### `/humaninloop:plan`

Unified planning workflow that translates business specifications into technical requirements and concrete design artifacts through a multi-agent workflow.

```
/humaninloop:plan
```

**Requires:** `spec.md` to exist with completed specify workflow

**Workflow:**
1. **Phase P1 (Analysis)**: Technical Analyst produces requirements (`requirements.md`), constraints and decisions (`constraints-and-decisions.md`), and NFRs (`nfrs.md`). Principal Architect reviews cross-artifact feasibility. Devil's Advocate validates completeness (phase: P1)
2. **Phase P2 (Design)**: Technical Analyst produces data model (`data-model.md` with sensitivity annotations), API contracts (`contracts/api.yaml` with integration boundaries), and integration guide (`quickstart.md`). Devil's Advocate validates completeness with incremental cross-artifact consistency check (phase: P2)

**Output:**
```
specs/<###-feature-name>/
├── requirements.md              # TR-XXX technical requirements traced to FRs
├── constraints-and-decisions.md # C-XXX constraints + D-XXX technology decisions
├── nfrs.md                      # NFR-XXX with measurable targets
├── data-model.md                # Entity definitions with sensitivity annotations
├── contracts/
│   └── api.yaml                 # OpenAPI spec with x-integration boundaries
├── quickstart.md                # Integration guide
└── plan.md                      # Summary document
```

**Features:**
- Every technical requirement traces to a business functional requirement
- Constraints (facts) and decisions (choices) documented together with bidirectional cross-references
- Data sensitivity annotations embedded per entity attribute (not standalone)
- Integration boundaries documented as OpenAPI extensions with failure modes
- Principal Architect reviews cross-artifact feasibility (one-time gate after analysis)
- 5 agent invocations: TA → PA → DA → TA → DA
- Five artifact ID types: TR- (requirements), C- (constraints), D- (decisions), NFR- (non-functional), IP- (infrastructure)

### `/humaninloop:tasks`

Generate implementation tasks from an existing plan.

```
/humaninloop:tasks
```

**Requires:** `plan.md` to exist (run plan workflow first)

**Workflow:**
1. **Initialize**: Entry gate, create tasks-context.md
2. **Mapping**: Task Architect creates task-mapping.md (story → cycle mapping)
3. **Review**: Devil's Advocate reviews mapping for gaps
4. **Tasks**: Task Architect creates tasks.md with TDD cycle structure
5. **Review**: Devil's Advocate validates TDD structure and coverage

**Features:**
- **Vertical slicing**: Tasks grouped into independently testable cycles
- **TDD discipline**: Each cycle follows test-first ordering
- **Foundation + parallel**: Sequential foundation cycles, then parallel feature cycles
- **Brownfield markers**: `[EXTEND]`, `[MODIFY]` for existing code

### `/humaninloop:implement`

Execute the implementation plan using DAG-based workflow execution with TDD discipline.

```
/humaninloop:implement
```

**Requires:** `tasks.md` to exist (run tasks workflow first)

**Workflow (DAG-based execution):**
1. State Analyst produces implementation briefing from DAG history, catalog, and strategy skills
2. Supervisor makes assembly decision; DAG Assembler validates and builds graph node
3. Staff Engineer executes cycle tasks through strict red/green/refactor TDD discipline
4. QA Engineer verifies implementation with quality gates (lint, build, tests) and TEST: task execution
5. State Analyst parses reports, records status + evidence + trace via `hil-dag record`
6. Loop through cycles until all tasks complete, then run final-validation gate
7. Fix pass if final-validation fails (scoped to specific failures), escalate after 3 retries

**Features:**
- **DAG-based execution**: Same Supervisor + DAG Assembler + State Analyst architecture as specify
- **TDD discipline**: Each cycle follows test-first ordering via Staff Engineer
- **Execute-then-verify**: Every execution cycle paired with independent verification
- **Targeted retry**: Checkpoint failures trace to specific tasks, not full re-implementation
- **Brownfield support**: Handles `[EXTEND]` and `[MODIFY]` markers via brownfield-integration skill
- **Progress tracking**: Marks tasks complete (`[x]`) in tasks.md
- **Escalation**: Mandatory user escalation after 3 retry attempts

## Workflow Architecture

### Setup Workflow Agent

| Agent | Purpose |
|-------|---------|
| **Principal Architect** | Senior technical leader who creates enforceable project constitutions with governance judgment. In brownfield mode, analyzes existing codebase for essential floor coverage, produces codebase-analysis.md, and generates evolution-roadmap.md with prioritized gaps. Uses skills: `analysis-codebase`, `authoring-constitution`, `brownfield-constitution`, `validation-constitution`, `syncing-claude-md`, `authoring-roadmap` |

### Specify Workflow Agents

| Agent | Purpose |
|-------|---------|
| **DAG Assembler** | Pure graph mechanics: translates Supervisor decisions into validated DAG mutations via the `hil-dag` CLI. Constructs prompts for domain agents from catalog contracts. Uses skill: `dag-operations` |
| **State Analyst** | Reads DAG history, parses domain agent reports, and produces structured briefings and summaries for the Supervisor. Records analysis results atomically via `hil-dag record`. Uses skill: `dag-operations` |
| **Requirements Analyst** | Transforms feature requests into precise specifications with user stories, requirements, and acceptance criteria |
| **Devil's Advocate** | Adversarial reviewer who stress-tests specs, finds gaps, challenges assumptions, and generates clarifying questions |

### Plan Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Technical Analyst** | Senior technical analyst who translates business specifications into traceable technical artifacts (analysis phase: requirements, constraints-and-decisions, NFRs) and concrete design artifacts (design phase: data model, API contracts, integration guide). Uses skills: `authoring-technical-requirements`, `patterns-technical-decisions`, `patterns-entity-modeling`, `patterns-api-contracts` |
| **Principal Architect** | Reviews cross-artifact feasibility after analysis phase; identifies constraint-decision conflicts and NFR-constraint impossibilities |
| **Devil's Advocate** | Validates plan artifacts for completeness and traceability. Uses skill: `validation-plan-artifacts` (phases: P1, P2) |

### Tasks Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Task Architect** | Senior architect who transforms planning artifacts into implementation tasks through vertical slicing and TDD discipline. Uses skill: `patterns-vertical-tdd` |
| **Devil's Advocate** | Reviews task artifacts for gaps, validates TDD structure. Uses skill: `validation-task-artifacts` |

### Implement Workflow Agents

| Agent | Purpose |
|-------|---------|
| **DAG Assembler** | Pure graph mechanics: translates Supervisor decisions into validated DAG mutations via the `hil-dag` CLI. Constructs prompts for domain agents from catalog contracts. Uses skill: `dag-operations` |
| **State Analyst** | Reads DAG history, parses domain agent reports, and produces structured briefings for the Supervisor. Records analysis results atomically via `hil-dag record`. Uses skills: `dag-operations`, `strategy-core`, `strategy-implementation` |
| **Staff Engineer** | Implementation specialist who writes code through strict TDD discipline (red/green/refactor). Executes cycle task lists, handles retry and fix modes. Uses skills: `executing-tdd-cycle`, `brownfield-integration` |
| **QA Engineer** | Senior QA engineer who treats verification as an engineering discipline. Executes `TEST:` verification tasks, classifies them at runtime (CLI/GUI/SUBJECTIVE), captures evidence, and decides whether to auto-approve or present human checkpoints. Uses skill: `testing-end-user` |

### Design Workflow Agent

| Agent | Purpose |
|-------|---------|
| **UI Designer** | Senior interface designer who analyzes visual inspiration from existing apps to extract design patterns, build actionable design systems, and craft screen layouts and interaction flows. Uses skills: `analysis-screenshot`, `patterns-flow-mapping`, `authoring-design-system`, `patterns-interface-design` |

### Validation

**Plan Workflow:** Uses `validation-plan-artifacts` skill for phase-specific review criteria (phases P1, P2, P3).

**Tasks Workflow:** Uses `validation-task-artifacts` skill for:
- Vertical slice validation (cycles deliver testable value)
- TDD structure verification (test-first ordering)
- Story → Cycle → Tasks traceability

## Output Structure

**Project-Level (from setup):**
```
.humaninloop/memory/
├── constitution.md            # Project governance principles
├── codebase-analysis.md       # Codebase inventory and assessment (brownfield)
├── evolution-roadmap.md       # Gap cards for improvement (brownfield)
├── setup-context-*.md         # Setup workflow context (temporary)
└── architect-report.md        # Principal Architect report (temporary)
```

**Feature-Level (from specify → plan → tasks):**
```
specs/<###-feature-name>/
├── spec.md                        # Feature specification
├── requirements.md                # TR-XXX technical requirements
├── constraints-and-decisions.md   # C-XXX constraints + D-XXX decisions
├── nfrs.md                        # NFR-XXX non-functional requirements
├── data-model.md                  # Entity definitions with sensitivity annotations
├── contracts/                     # API specifications (OpenAPI)
│   └── api.yaml                   # Includes x-integration boundaries
├── quickstart.md                  # Integration guide
├── plan.md                        # Implementation plan summary
├── task-mapping.md                # Story-to-component mappings
├── tasks.md                       # Actionable task list
├── checklists/                    # Audit outputs (via /humaninloop:audit)
└── .workflow/
    ├── context.md                 # Specify workflow context
    ├── analyst-report.md          # Requirements Analyst output
    ├── advocate-report.md         # Devil's Advocate output
    ├── dags/                      # DAG history (one file per workflow)
    │   ├── specify-strategy.json  # Specify workflow StrategyGraph
    │   └── implement-strategy.json # Implement workflow StrategyGraph
    ├── plan-context.md            # Plan workflow state
    ├── techanalyst-report.md      # Technical Analyst output
    ├── architect-report.md        # Principal Architect feasibility report
    ├── tasks-context.md           # Tasks workflow state
    ├── cycle-report.md            # Staff Engineer cycle output (implement)
    ├── verification-report.md     # QA Engineer verification output (implement)
    ├── checkpoint-report.md       # Cycle checkpoint evaluation (implement)
    └── final-validation-report.md # Final validation gate result (implement)
```

## Specification Format

Generated specifications include:

- **User Stories** - Prioritized (P1/P2/P3) with acceptance scenarios
- **Edge Cases** - Boundary conditions and error scenarios
- **Functional Requirements** - FR-XXX format with RFC 2119 keywords
- **Key Entities** - Domain concepts without implementation details
- **Success Criteria** - Measurable, technology-agnostic outcomes

## Task Format

Tasks are organized into **cycles** - vertical slices that deliver testable value with TDD discipline.

**Cycle Structure:**

```markdown
### Cycle N: [Vertical slice description]

> Stories: US-X, US-Y
> Dependencies: C1, C2 (or "None")
> Type: Foundation | Feature [P]

- [ ] **TN.1**: Write failing test for [behavior] in tests/[path]
- [ ] **TN.2**: Implement [component] to pass test in src/[path]
- [ ] **TN.3**: Refactor and verify tests pass
- [ ] **TN.4**: Demo [behavior], verify acceptance criteria

**Checkpoint**: [Observable outcome when cycle is complete]
```

**Task ID Format:** `TN.X` where N = cycle number, X = task sequence (e.g., T1.1, T1.2, T2.1)

**Markers:**

| Marker | Meaning |
|--------|---------|
| `[P]` | Parallel-eligible (feature cycle can run alongside others) |
| `[EXTEND]` | Extends existing file (brownfield) |
| `[MODIFY]` | Modifies existing code (brownfield) |

**Verification Task Format (TEST:):**

Use the unified `TEST:` format for all verification tasks:

```markdown
- [ ] **TN.4**: **TEST:** - {Description}
  - **Setup**: {Prerequisites} (optional)
  - **Action**: {Command or instruction}
  - **Assert**: {Expected outcome}
  - **Capture**: {console, screenshot, logs} (optional)
```

The qa-engineer classifies tasks at runtime (CLI/GUI/SUBJECTIVE) and decides whether to auto-approve or present a human checkpoint. Legacy formats (`TEST:VERIFY`, `TEST:CONTRACT`, `HUMAN VERIFICATION`) are still supported.

Action modifiers: `(background)`, `(timeout Ns)`, `(in {path})`

Assert patterns: `Console contains "{text}"`, `File exists: {path}`, `Response status: {code}`

**Cycle Types:**

1. **Foundation Cycles** - Sequential, establish shared infrastructure
2. **Feature Cycles** - Parallel-eligible, deliver user value independently

### `/humaninloop:audit`

Comprehensive artifact analysis with two output modes.

```
/humaninloop:audit              # Full diagnostic mode (default)
/humaninloop:audit --review     # Reviewer-facing summary
/humaninloop:audit --security   # Domain-filtered analysis
```

**Modes:**

| Mode | Flag | Purpose |
|------|------|---------|
| Full | (default) | Deep diagnostics for authors/maintainers |
| Review | `--review` | Scannable summary for peer reviewers |

**Domain Filters:** `--security`, `--ux`, `--api`, `--performance`

**Features:**
- Phase-agnostic: works on whatever artifacts exist
- Leverages existing validation skills
- Coverage summary with flagged gaps
- Constitution alignment checks
- Cross-artifact consistency analysis

**Output (Review Mode):**
- Coverage table with status indicators
- Flagged issues (top 10)
- Metrics summary
- Recommendation (ready/caution/not ready)

**Output (Full Mode):**
- Complete findings table
- Requirement-to-task coverage mapping
- Constitution alignment issues
- Unmapped items
- Remediation suggestions

## Configuration

The plugin uses:
- `${CLAUDE_PLUGIN_ROOT}/templates/` - Workflow templates
- `${CLAUDE_PLUGIN_ROOT}/skills/` - Agent skills (validation, patterns, authoring)
- `${CLAUDE_PLUGIN_ROOT}/catalogs/` - Node catalogs defining available nodes, edge constraints, and system invariants for DAG-based workflows
- `.humaninloop/memory/constitution.md` - Project principles (user project)

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
