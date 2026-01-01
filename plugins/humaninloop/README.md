# HumanInLoop Plugin

Implementation workflow: **plan → tasks → implement**

## Overview

The HumanInLoop plugin provides a multi-agent workflow for implementation planning and task generation. It consumes feature specifications (from `humaninloop-specs`) and produces implementation plans and actionable tasks.

**Core Workflows:**
- **Plan** - Generate implementation plans with research, data models, and API contracts
- **Tasks** - Generate actionable implementation tasks with dependency tracking and brownfield markers
- **Implement** - Execute tasks from the generated task list
- **Analyze** - Cross-artifact consistency validation

## Installation

Add the plugin to your Claude Code project:

```bash
claude-code plugins add humaninloop
```

## Prerequisites

This plugin requires:

1. **Project constitution** to be set up first:
```bash
claude-code plugins add humaninloop-constitution
/humaninloop-constitution:setup
```

2. **Feature specification** created using `humaninloop-specs`:
```bash
claude-code plugins add humaninloop-specs
/humaninloop-specs:specify <description>
```

## Commands

### `/humaninloop:plan`

Generate an implementation plan from an existing specification.

```
/humaninloop:plan
```

**Requires:** `spec.md` to exist (run `/humaninloop-specs:specify` first)

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

### `/humaninloop:analyze`

Perform cross-artifact consistency and quality analysis.

```
/humaninloop:analyze
```

### `/humaninloop:implement`

Execute tasks from the generated task list.

```
/humaninloop:implement
```

## Workflow Architecture

### Plan Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Codebase Discovery Agent** | Analyzes existing code for brownfield considerations |
| **Plan Research Agent** | Resolves technical unknowns and makes technology decisions |
| **Plan Domain Model Agent** | Extracts entities and creates data model |
| **Plan Contract Agent** | Designs API contracts and integration scenarios |
| **Plan Validator Agent** | Validates artifacts against check modules |

### Tasks Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Task Planner Agent** | Extracts from spec/plan/data-model/contracts, maps to user stories |
| **Task Generator Agent** | Generates `tasks.md` with format, phases, and brownfield markers |
| **Task Validator Agent** | Validates artifacts against phase-specific check modules |

### Validation Check Modules

**Plan Workflow Checks:**

| Module | Phase | Purpose |
|--------|-------|---------|
| `research-checks.md` | B0 | Validate research decisions and technology choices |
| `model-checks.md` | B1 | Validate entity coverage, relationships, attributes |
| `contract-checks.md` | B2 | Validate endpoint coverage, schemas, error handling |
| `final-checks.md` | B3 | Cross-artifact consistency and constitution sweep |

**Tasks Workflow Checks:**

| Module | Phase | Purpose |
|--------|-------|---------|
| `mapping-checks.md` | T1 | Validate story coverage, entity/endpoint mapping, brownfield analysis |
| `task-checks.md` | T2 | Validate task format, coverage, dependencies, parallel safety |

## Output Structure

```
specs/<###-feature-name>/
├── spec.md                    # Feature specification (from humaninloop-specs)
├── plan.md                    # Implementation plan summary
├── research.md                # Technology decisions
├── data-model.md              # Entity definitions
├── quickstart.md              # Integration scenarios
├── task-mapping.md            # Story-to-component mappings
├── tasks.md                   # Actionable task list
├── contracts/                 # API specifications (OpenAPI)
└── .workflow/
    ├── index.md              # Cross-workflow state
    ├── plan-context.md       # Plan workflow state
    └── tasks-context.md      # Tasks workflow state
```

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

## Related Plugins

- **humaninloop-specs** - Specification workflow (required for spec.md)
- **humaninloop-constitution** - Project constitution setup (required)

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
