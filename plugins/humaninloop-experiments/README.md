# HumanInLoop Experiments Plugin

Experimental sandbox for testing new agent patterns with decoupled architecture. This plugin serves as a testing ground before promoting patterns to production plugins.

## Decoupled Agents Architecture

This plugin implements the **Decoupled Agents Architecture**:

1. **Agents are pure domain experts** - They have domain knowledge, not workflow knowledge
2. **Supervisors communicate via files** - Context artifacts contain all context
3. **Artifacts are self-describing** - Agents read input from artifacts, not supervisor prompts
4. **Supervisor owns the loop** - All routing and iteration decisions live in the command

## Current Experiment: Decoupled Specify

A two-agent specification workflow replacing the complex 6-agent specify command.

```
SUPERVISOR (commands/specify.md)
    │
    ├── Creates context + spec file
    ├── Invokes agents with minimal prompts
    ├── Parses structured prose outputs
    ├── Updates context between iterations
    └── Owns all routing decisions

AGENTS (independent, no workflow knowledge)
    │
    ├── Requirements Analyst → Writes spec.md
    └── Devil's Advocate → Reviews spec.md, finds gaps
```

### Agent Archetypes

| Agent | Archetype | Role |
|-------|-----------|------|
| Requirements Analyst | Senior BA | Transforms vague requests into precise specs |
| Devil's Advocate | Adversarial Reviewer | Stress-tests specs, finds gaps, asks hard questions |

### Communication Pattern

Agents communicate via files, not direct handoffs:

```
specs/{feature-id}/
├── spec.md                          # The deliverable
└── .workflow/
    ├── context.md                  # Context + instructions
    ├── analyst-report.md            # Requirements Analyst output
    └── advocate-report.md           # Devil's Advocate output
```

## Installation

```bash
/plugin install humaninloop-experiments
```

> **Note**: This plugin is **standalone** and does not require the main `humaninloop` plugin. Skills like `authoring-requirements` and `authoring-user-stories` are intentionally duplicated to allow independent experimentation.

## Usage

### Create a Specification

```
/humaninloop-experiments:specify <feature description>
```

The command will:
1. Create context and directory structure
2. Invoke Requirements Analyst to write initial spec
3. Invoke Devil's Advocate to review and find gaps
4. Present clarifications to user
5. Loop until spec is ready (or user accepts)

### Example

```
/humaninloop-experiments:specify User authentication with email/password and OAuth
```

## Plugin Structure

```
humaninloop-experiments/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── requirements-analyst.md    # Domain expert for spec writing
│   └── devils-advocate.md         # Adversarial reviewer
├── commands/
│   └── specify.md                 # Supervisor command (owns the loop)
└── README.md
```

## Decoupled Agent Pattern

### Supervisor (commands/specify.md)

The supervisor:
- Creates the context artifact with all context
- Spawns agents with minimal prompts pointing to context
- Parses structured prose output from report files
- Updates context between iterations
- Uses judgment for termination (not hard-coded rules)
- Owns the iteration loop

### Agents

Each agent:
- Reads context from the context artifact
- Applies domain expertise
- Writes deliverable (spec.md) or report (analyst-report.md, advocate-report.md)
- Reports back with structured prose sections
- Has NO workflow knowledge

### Communication Flow

```
Supervisor --> Requirements Analyst:
  "Create a feature specification.
   Read your instructions from: specs/001-auth/.workflow/context.md"

Analyst --> (writes spec.md, analyst-report.md)

Supervisor --> Devil's Advocate:
  "Review the feature specification and find gaps.
   Read your instructions from: specs/001-auth/.workflow/context.md"

Advocate --> (writes advocate-report.md with verdict)

Supervisor: Parse verdict, route accordingly
```

### Structured Prose Output

**Requirements Analyst reports:**
```markdown
## What I Created
- User Stories: 5
- Functional Requirements: 12
- Acceptance Criteria: 18

## Assumptions Made
- Assumed OAuth means Google and GitHub only
- Assumed password requirements follow OWASP guidelines
```

**Devil's Advocate reports:**
```markdown
## Gaps Found
| ID | Type | Description | Severity |
|----|------|-------------|----------|
| G1 | Missing | No password reset flow defined | Critical |
| G2 | Ambiguous | "Session timeout" not quantified | Important |

## Clarifications Needed
1. How should password reset work? (Email link / Security questions / Admin reset)
2. What should the session timeout be? (15 min / 1 hour / 24 hours)

## Verdict
needs-clarification
```

## Key Differences from Production Specify

| Aspect | Production (humaninloop) | Experiment |
|--------|-------------------------|------------|
| Agents | 6 specialized agents | 2 agents (Analyst + Advocate) |
| Coupling | Agents aware of workflow phases | Agents have zero workflow knowledge |
| Communication | Mixed (prompt injection + files) | Pure file-based via context |
| Termination | Hard-coded conditions | Supervisor judgment |
| Validation | Separate checklist agents | Devil's Advocate self-contained |

## Output Location

```
specs/
└── {feature-id}/
    ├── spec.md                    # Final specification
    └── .workflow/
        ├── context.md            # Workflow state and context
        ├── analyst-report.md      # Analyst's structured output
        └── advocate-report.md     # Advocate's review and verdict
```

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
