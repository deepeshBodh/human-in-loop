# HumanInLoop Plugin

Specification-driven development workflow: **specify → plan → tasks → implement**

## Overview

The HumanInLoop plugin provides a comprehensive multi-agent workflow for specification-driven development. It automates the entire feature development lifecycle from specification to implementation planning.

**Core Workflows:**
- **Specify** - Create feature specifications with integrated quality validation
- **Plan** - Generate implementation plans with research, data models, and API contracts

## Installation

Add the plugin to your Claude Code project:

```bash
claude-code plugins add humaninloop
```

## Prerequisites

This plugin requires a project constitution to be set up first:

```bash
claude-code plugins add humaninloop-constitution
/humaninloop-constitution:setup
```

## Commands

### `/humaninloop:specify <description>`

Create a feature specification with integrated quality validation.

```
/humaninloop:specify Add user authentication with OAuth2 support
```

**Workflow:**
1. Create a feature branch (e.g., `001-user-auth`)
2. Generate structured specification in `specs/001-user-auth/spec.md`
3. Run automatic quality validation via Priority Loop
4. Present gaps for clarification until resolved

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

## Workflow Architecture

### Specify Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Scaffold Agent** | Creates branch, directories, and initializes templates |
| **Spec Writer Agent** | Generates user stories, requirements, success criteria |
| **Checklist Context Analyzer** | Extracts signals for quality validation |
| **Checklist Writer Agent** | Generates validation checklists |
| **Gap Classifier Agent** | Groups and prioritizes specification gaps |
| **Spec Clarify Agent** | Applies user answers to resolve gaps |

### Plan Workflow Agents

| Agent | Purpose |
|-------|---------|
| **Codebase Discovery Agent** | Analyzes existing code for brownfield considerations |
| **Plan Research Agent** | Resolves technical unknowns and makes technology decisions |
| **Plan Domain Model Agent** | Extracts entities and creates data model |
| **Plan Contract Agent** | Designs API contracts and integration scenarios |
| **Plan Validator Agent** | Validates artifacts against check modules |

### Validation Check Modules

| Module | Phase | Purpose |
|--------|-------|---------|
| `research-checks.md` | 0 | Validate research decisions and technology choices |
| `model-checks.md` | 1 | Validate entity coverage, relationships, attributes |
| `contract-checks.md` | 2 | Validate endpoint coverage, schemas, error handling |
| `final-checks.md` | 3 | Cross-artifact consistency and constitution sweep |

## Output Structure

```
specs/<###-feature-name>/
├── spec.md                    # Feature specification
├── plan.md                    # Implementation plan summary
├── research.md                # Technology decisions
├── data-model.md              # Entity definitions
├── quickstart.md              # Integration scenarios
├── contracts/                 # API specifications (OpenAPI)
├── checklists/
│   └── requirements.md        # Quality validation checklist
└── .workflow/
    ├── index.md              # Cross-workflow state
    ├── specify-context.md    # Specify workflow state
    └── plan-context.md       # Plan workflow state
```

## Specification Format

Generated specifications include:

- **User Stories** - Prioritized (P1/P2/P3) with acceptance scenarios
- **Edge Cases** - Boundary conditions and error scenarios
- **Functional Requirements** - FR-XXX format with RFC 2119 keywords
- **Key Entities** - Domain concepts without implementation details
- **Success Criteria** - Measurable, technology-agnostic outcomes

## Configuration

The plugin uses:
- `${CLAUDE_PLUGIN_ROOT}/templates/` - Workflow templates
- `${CLAUDE_PLUGIN_ROOT}/check-modules/` - Validation check modules
- `.humaninloop/memory/constitution.md` - Project principles (user project)

## Related Plugins

- **humaninloop-constitution** - Project constitution setup (required)

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
