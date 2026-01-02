# HumanInLoop Specs Plugin

Specification and requirements workflow: **specify → checklist validation**

## Overview

The HumanInLoop Specs plugin provides a multi-agent workflow for creating feature specifications with integrated quality validation. It focuses exclusively on the specification phase, producing validated `spec.md` files ready for implementation planning.

**Key Features:**
- Create structured specifications from natural language descriptions
- Automatic quality validation via "unit tests for requirements"
- Priority Loop ensures all Critical and Important gaps are resolved
- Produces specs ready for the `humaninloop` plugin's plan workflow

## Installation

Add the plugin to your Claude Code project:

```bash
claude-code plugins add humaninloop-specs
```

## Prerequisites

This plugin requires:

1. **humaninloop-core** for foundational capabilities:
```bash
claude-code plugins add humaninloop-core
```

2. **Project constitution** to be set up first:
```bash
claude-code plugins add humaninloop-constitution
/humaninloop-constitution:setup
```

## Commands

### `/humaninloop-specs:specify <description>`

Create a feature specification with integrated quality validation.

```
/humaninloop-specs:specify Add user authentication with OAuth2 support
```

**Workflow:**
1. Create a feature branch (e.g., `001-user-auth`)
2. Generate structured specification in `specs/001-user-auth/spec.md`
3. Run automatic quality validation via Priority Loop
4. Present gaps for clarification until resolved
5. Produce validated spec ready for planning

### `/humaninloop-specs:checklist [theme]`

Generate a custom quality checklist for the current feature.

```
/humaninloop-specs:checklist security
```

**Checklist Types:**
- `ux` - Visual hierarchy, interaction states, accessibility
- `security` - Authentication, authorization, data protection
- `api` - Endpoint coverage, response formats, error handling
- `performance` - Load requirements, metrics, degradation

**Important:** Checklists are "unit tests for requirements" - they validate the quality of your specification, NOT implementation correctness.

## Workflow Architecture

This plugin follows **hexagonal (clean) architecture** with three layers where dependencies point inward only:
- **Skills** (innermost): Pure domain knowledge, no procedures
- **Agents** (middle): Compose skills, execute procedures, return output
- **Workflows** (outermost): Own state, orchestrate agents

### Agents

| Agent | Purpose | Skills | Source |
|-------|---------|--------|--------|
| **Scaffold Agent** | Creates branch, directories, and initializes templates | scaffold-workflow | local |
| **Spec Writer Agent** | Generates user stories, requirements, success criteria | spec-writing, context-patterns, quality-thinking | local |
| **Checklist Context Analyzer** | Extracts signals for quality validation | context-patterns, quality-thinking | local |
| **Checklist Writer Agent** | Generates validation checklists, classifies gaps | quality-thinking, validation-expertise, clarification-patterns | local |
| **Gap Classifier Agent** | Groups and prioritizes specification gaps | prioritization-patterns, clarification-patterns | local |
| **Spec Clarify Agent** | Applies user answers to resolve gaps | clarification-patterns, spec-clarify, context-patterns | local |

### Priority Loop

The specify workflow uses a Priority Loop to ensure specification quality:

1. **Initial Validation** - Checklist writer identifies gaps in requirements
2. **Gap Classification** - Gaps are prioritized as Critical, Important, or Minor
3. **Clarification** - User answers questions to resolve gaps
4. **Re-validation** - Spec is re-checked until Critical+Important gaps = 0
5. **Completion** - Minor gaps can be deferred, spec marked ready

Maximum 10 iterations, maximum 3 clarifications per iteration.

## Output Structure

```
specs/<###-feature-name>/
├── spec.md                    # Feature specification
├── checklists/
│   └── requirements.md        # Quality validation checklist
└── .workflow/
    ├── index.md              # Workflow state
    └── specify-context.md    # Specify workflow state
```

## Specification Format

Generated specifications include:

- **User Stories** - Prioritized (P1/P2/P3) with acceptance scenarios
- **Edge Cases** - Boundary conditions and error scenarios
- **Functional Requirements** - FR-XXX format with RFC 2119 keywords
- **Key Entities** - Domain concepts without implementation details
- **Success Criteria** - Measurable, technology-agnostic outcomes

## Integration with humaninloop Plugin

After completing a specification with `humaninloop-specs`, use the `humaninloop` plugin to continue:

```bash
/humaninloop:plan   # Create implementation plan from spec
/humaninloop:tasks  # Generate tasks from plan
```

The `spec.md` file at `specs/{feature-id}/spec.md` serves as the contract between plugins.

## Related Plugins

- **humaninloop-core** - Foundational skills and agents (required)
- **humaninloop-constitution** - Project constitution setup (required)
- **humaninloop** - Plan and tasks workflows (optional, for implementation)

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
