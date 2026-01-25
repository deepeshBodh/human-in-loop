# HumanInLoop Plugin

Specification-driven development workflow: **setup → specify → plan → tasks → implement**

## Overview

The HumanInLoop plugin provides a comprehensive multi-agent workflow for specification-driven development. It automates the entire feature development lifecycle from constitution setup to implementation.

**Core Workflows:**
- **Setup** - Create project constitution with enforceable governance principles
- **Specify** - Create feature specifications with integrated quality validation
- **Plan** - Generate implementation plans with research, data models, and API contracts
- **Tasks** - Generate actionable implementation tasks with dependency tracking and brownfield markers

## Installation

Add the plugin to your Claude Code project:

```bash
claude-code plugins add humaninloop
```

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

**Workflow:**
1. Generate short name from description (2-4 words, e.g., `user-auth`)
2. Create feature branch and directory using `create-new-feature.sh` script
3. Requirements Analyst generates structured specification
4. Devil's Advocate reviews and finds gaps
5. User answers clarifying questions
6. Loop until specification is ready or user accepts

**Branch Format:** `###-short-name` (e.g., `001-user-auth`)
- Branch name = spec directory name = feature ID
- Number auto-increments based on existing branches and specs

### `/humaninloop:plan`

Generate an implementation plan from an existing specification.

```
/humaninloop:plan
```

**Requires:** `spec.md` to exist (run specify workflow first)

**Workflow:**
1. **Phase A0**: Codebase discovery (detects existing code conflicts)
2. **Phase B0**: Technical research for unknowns
3. **Phase B1**: Domain model and entity design
4. **Phase B2**: API contracts and integration scenarios
5. **Phase B3**: Final validation and constitution sweep

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

Execute the implementation plan by processing all tasks defined in tasks.md.

```
/humaninloop:implement
```

**Requires:** `tasks.md` to exist (run tasks workflow first)

**Workflow:**
1. **Entry Gate**: Verify tasks workflow completed successfully
2. **Project Setup**: Create/verify ignore files for tech stack
3. **Parse Structure**: Extract cycles, tasks, dependencies from tasks.md
4. **Execute Foundation**: Complete foundation cycles sequentially (C1 → C2 → C3)
5. **Execute Features**: Run feature cycles (parallel where marked `[P]`)
6. **Verify Checkpoints**: Validate each cycle's checkpoint criteria
7. **Quality Gates**: Run lint, build, tests after each cycle

**Features:**
- **Cycle-based execution**: Foundation cycles sequential, feature cycles can parallelize
- **TDD discipline**: Each cycle starts with failing test (TN.1), then implements
- **Checkpoint verification**: Validates done criteria between cycles
- **Brownfield support**: Handles `[EXTEND]` and `[MODIFY]` markers
- **Progress tracking**: Marks tasks complete (`[x]`) in tasks.md
- **User-controlled git**: Does not run git commands - leaves version control to user

## Workflow Architecture

### Setup Workflow Agent

| Agent | Purpose |
|-------|---------|
| **Principal Architect** | Senior technical leader who creates enforceable project constitutions with governance judgment. In brownfield mode, analyzes existing codebase for essential floor coverage, produces codebase-analysis.md, and generates evolution-roadmap.md with prioritized gaps. Uses skills: `analysis-codebase`, `authoring-constitution`, `brownfield-constitution`, `validation-constitution`, `syncing-claude-md`, `authoring-roadmap` |

### Specify Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Requirements Analyst** | Transforms feature requests into precise specifications with user stories, requirements, and acceptance criteria |
| **Devil's Advocate** | Adversarial reviewer who stress-tests specs, finds gaps, challenges assumptions, and generates clarifying questions |

### Plan Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Plan Architect** | Senior architect who transforms specifications into implementation plans through research, domain modeling, and API contract design. Uses skills: `patterns-technical-decisions`, `patterns-entity-modeling`, `patterns-api-contracts` |
| **Devil's Advocate** | Reviews plan artifacts for gaps and quality. Uses skill: `validation-plan-artifacts` |

### Tasks Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Task Architect** | Senior architect who transforms planning artifacts into implementation tasks through vertical slicing and TDD discipline. Uses skill: `patterns-vertical-tdd` |
| **Devil's Advocate** | Reviews task artifacts for gaps, validates TDD structure. Uses skill: `validation-task-artifacts` |

### Implement Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Testing Agent** | Collaborative QA partner that executes `TEST:` verification tasks, classifies them at runtime (CLI/GUI/SUBJECTIVE), captures evidence, and decides whether to auto-approve or present human checkpoints. Uses skill: `testing-end-user` |

### Validation

**Plan Workflow:** Uses `validation-plan-artifacts` skill for phase-specific review criteria.

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
├── spec.md                    # Feature specification
├── plan.md                    # Implementation plan summary
├── research.md                # Technology decisions
├── data-model.md              # Entity definitions
├── quickstart.md              # Integration scenarios
├── task-mapping.md            # Story-to-component mappings
├── tasks.md                   # Actionable task list
├── contracts/                 # API specifications (OpenAPI)
├── checklists/                # Audit outputs (via /humaninloop:audit)
└── .workflow/
    ├── context.md             # Specify workflow context
    ├── analyst-report.md      # Requirements Analyst output
    ├── advocate-report.md     # Devil's Advocate output
    ├── plan-context.md        # Plan workflow state
    └── tasks-context.md       # Tasks workflow state
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

The testing-agent classifies tasks at runtime (CLI/GUI/SUBJECTIVE) and decides whether to auto-approve or present a human checkpoint. Legacy formats (`TEST:VERIFY`, `TEST:CONTRACT`, `HUMAN VERIFICATION`) are still supported.

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
- `.humaninloop/memory/constitution.md` - Project principles (user project)

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
