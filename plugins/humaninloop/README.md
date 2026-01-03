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

Create or amend your project constitution with enforceable governance principles.

```
/humaninloop:setup
```

**Workflow:**
1. Detect project context (tech stack, conventions, architecture)
2. Principal Architect drafts constitution with principles
3. User answers clarifying questions
4. Constitution finalized with enforcement mechanisms
5. CLAUDE.md synchronized with constitution

**Output:** `.humaninloop/memory/constitution.md`

**Features:**
- Three-Part Principle Rule (Enforcement, Testability, Rationale)
- RFC 2119 keywords (MUST, SHOULD, MAY)
- Automatic CLAUDE.md synchronization
- Support for amending existing constitutions

### `/humaninloop:specify <description>`

Create a feature specification with integrated quality validation.

```
/humaninloop:specify Add user authentication with OAuth2 support
```

**Workflow:**
1. Create feature directory (e.g., `specs/001-user-auth/`)
2. Requirements Analyst generates structured specification
3. Devil's Advocate reviews and finds gaps
4. User answers clarifying questions
5. Loop until specification is ready or user accepts

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
1. **Phase T1**: Task planning - extract from design artifacts, map to user stories
2. **Validation T1**: Verify story coverage, entity mapping, brownfield analysis
3. **Phase T2**: Task generation - create tasks.md with proper format
4. **Validation T2**: Verify format, coverage, dependencies, brownfield markers

**Features:**
- **Brownfield markers**: `[EXTEND]`, `[MODIFY]`, `[CONFLICT]` for existing code
- **Parallel flags**: `[P]` marks tasks that can run concurrently
- **Story labels**: `[US#]` maps each task to its user story
- **Phase structure**: Setup → Foundational → User Stories → Polish

## Workflow Architecture

### Setup Workflow Agent

| Agent | Purpose |
|-------|---------|
| **Principal Architect** | Senior technical leader who creates enforceable project constitutions with governance judgment |

### Specify Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Requirements Analyst** | Transforms feature requests into precise specifications with user stories, requirements, and acceptance criteria |
| **Devil's Advocate** | Adversarial reviewer who stress-tests specs, finds gaps, challenges assumptions, and generates clarifying questions |

### Plan Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Plan Architect** | Senior architect who transforms specifications into implementation plans through research, domain modeling, and API contract design. Uses skills: `analysis-codebase`, `patterns-technical-decisions`, `patterns-entity-modeling`, `patterns-api-contracts` |
| **Devil's Advocate** | Reviews plan artifacts for gaps and quality. Uses skill: `validation-plan-artifacts` |

### Tasks Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Task Planner Agent** | Extracts from spec/plan/data-model/contracts, maps to user stories |
| **Task Generator Agent** | Generates `tasks.md` with format, phases, and brownfield markers |
| **Task Validator Agent** | Validates artifacts against phase-specific check modules |

### Validation

**Plan Workflow:** Uses `validation-plan-artifacts` skill with `check-artifacts.py` script for automated validation.

**Tasks Workflow Checks:**

| Module | Phase | Purpose |
|--------|-------|---------|
| `mapping-checks.md` | T1 | Validate story coverage, entity/endpoint mapping, brownfield analysis |
| `task-checks.md` | T2 | Validate task format, coverage, dependencies, parallel safety |

## Output Structure

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
├── checklists/                # Manual quality checklists (via /humaninloop:checklist)
└── .workflow/
    ├── scaffold.md            # Specify workflow context
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

Generated tasks follow this format:

```
- [ ] T### [Marker?] [P?] [US#] Description with file path
```

**Components:**
- `T###` - Sequential task ID (T001, T002, ...)
- `[EXTEND]` / `[MODIFY]` / `[CONFLICT]` - Brownfield markers (optional)
- `[P]` - Parallel flag for concurrent execution (optional)
- `[US#]` - User story label (required for story phases)
- Description with specific file path (required)

**Brownfield Markers:**

| Marker | Meaning | Behavior |
|--------|---------|----------|
| (none) | New file | Create file (greenfield default) |
| `[EXTEND]` | Add to existing | Append new functionality |
| `[MODIFY]` | Change existing | Update existing logic |
| `[CONFLICT]` | Manual resolution | Stop for user review |

**Phase Structure:**

1. **Setup** - Project initialization, no story labels
2. **Foundational** - Core infrastructure blocking all stories
3. **User Story N** - Independent, testable story implementation
4. **Polish** - Cross-cutting concerns, documentation

## Configuration

The plugin uses:
- `${CLAUDE_PLUGIN_ROOT}/templates/` - Workflow templates
- `${CLAUDE_PLUGIN_ROOT}/check-modules/` - Validation check modules
- `.humaninloop/memory/constitution.md` - Project principles (user project)

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
