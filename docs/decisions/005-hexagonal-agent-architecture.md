# ADR-005: Hexagonal Multi-Agent Architecture

**Status**: Proposed
**Date**: 2026-01-02
**Decision**: Adopt hexagonal/clean architecture with Skills (innermost), Agents (middle), Workflows (outermost) layers

---

## Problem Statement

The current multi-agent architecture lacks clear boundaries between layers. Skills bundle too much (procedures + knowledge + shared patterns), agents write directly to shared state files creating implicit coupling, and check-modules exist in an ambiguous location. This makes the system harder to maintain, test, and extend.

## Context & Constraints

- **Claude Code Skills**: Skills are flat (no skill-to-skill inheritance); composition happens at agent level via `skills: a, b, c`
- **Current Pain Points**:
  - `plan-workflow` skill bundles 6 files (CONTEXT, BROWNFIELD, RESEARCH, DOMAIN, CONTRACTS, VALIDATION)
  - Agents write directly to `plan-context.md` and `index.md`, creating implicit coupling
  - Check-modules blur the boundary between configuration and knowledge
- **Plugin Ecosystem**: ADR-001 established multi-agent architecture; this ADR refines the layer boundaries
- **Goal**: Atomic, composable primitives with clean dependency direction following hexagonal/clean architecture principles

## Decision

### Layer Architecture

Adopt a three-layer hexagonal architecture where dependencies point inward only:

```
┌─────────────────────────────────────────────────────────────────┐
│                        WORKFLOWS (outermost)                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - Orchestration (sequencing, branching, loops)          │   │
│  │ - State Management (reads/writes context files)         │   │
│  │ - Configuration (check-modules, phase mappings)         │   │
│  │ - Adaptation (retry, escalate, dynamic agent selection) │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              │ InputContract / OutputContract   │
│                              ▼                                  │
├─────────────────────────────────────────────────────────────────┤
│                         AGENTS (middle layer)                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - Procedures (step-by-step execution)                   │   │
│  │ - Context Binding (apply knowledge to specific task)    │   │
│  │ - Judgment (decisions within scope)                     │   │
│  │ - Tool Bindings (Read, Write, Grep, etc.)               │   │
│  │ - STATELESS: (input) → Agent → (output)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│                              │ skills: a, b, c                  │
│                              ▼                                  │
├─────────────────────────────────────────────────────────────────┤
│                         SKILLS (innermost)                      │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐      │
│  │ research  │ │  domain   │ │ contracts │ │validation │ ...  │
│  │ knowledge │ │  modeling │ │  design   │ │ expertise │      │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘      │
│                                                                 │
│  - Pure domain knowledge (no procedures, no tools)              │
│  - Atomic (no skill-to-skill dependencies)                      │
│  - Composable at agent level                                    │
└─────────────────────────────────────────────────────────────────┘

DEPENDENCY RULE: Dependencies point INWARD only
                 Workflows → Agents → Skills
                 Skills know nothing about agents or workflows
```

### Key Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill primitive | Domain Knowledge | Pure, declarative expertise—no procedures, no dependencies |
| Agent responsibility | Procedures + Context + Judgment | Application layer that knows HOW to apply knowledge |
| Workflow responsibility | Orchestration + State + Adaptation | Controls flow, owns state, makes runtime decisions |
| Dependency direction | Inward + Contracts | Layers communicate through explicit input/output contracts |
| State ownership | Workflows own all state | Agents are stateless functions; workflows handle persistence |
| Check-modules location | Workflow Configuration | Validation rules are config, not knowledge—passed to agents as input |
| Tool bindings | Agents define tools | Agents are execution layer; tools are execution concerns |

### Contract Patterns

**Agent Input Contract:**
```yaml
input:
  task: "extract-entities"
  context:
    spec: <spec content>
    constitution: <principles>
    prior_decisions: <from workflow state>
  config:              # Workflow-owned config passed in
    checks: <check-module if validator>
```

**Agent Output Contract:**
```yaml
output:
  success: true
  result: <primary output>
  artifacts:           # What agent produced
    - path: "data-model.md"
      content: <...>
  state_updates:       # Workflow applies these
    entity_registry: {...}
    gaps_found: [...]
  next_recommendation: "proceed" | "retry" | "escalate"
```

## Rationale

### Why Hexagonal/Clean Architecture?

1. **Testability**: Skills are pure knowledge (no side effects). Agents are pure functions `(input) → output`. Both can be tested in isolation.

2. **Composability**: Atomic skills can be mixed and matched. `spec-clarify` agent uses `skills: spec-writing, clarification-patterns` instead of one monolithic skill.

3. **Maintainability**: Changes to domain knowledge (skills) don't require changes to procedures (agents). Changes to orchestration (workflows) don't require changes to agents.

4. **Clear Ownership**:
   - Skills own "what is good" (domain expertise)
   - Agents own "how to do it" (procedures)
   - Workflows own "when to do it" (orchestration)

### Why Inward Dependencies + Contracts?

The current architecture has implicit coupling:
- Agents write to `plan-context.md` knowing other agents will read it
- Agents load check-modules directly, knowing which phase they're in
- Skills bundle shared patterns (CONTEXT.md) that blur boundaries

With contracts:
- Agents receive input, return output—no knowledge of workflow state
- Workflows decide what to pass to agents and what to do with results
- Skills are pure knowledge, referenced by agents but unaware of how they're used

### Why Workflows Own State?

Current pain: `plan-builder` writes to `plan-context.md`, creating implicit dependency on `plan-validator` reading it. This couples agents.

With workflow-owned state:
- Agent returns `state_updates: {...}`
- Workflow decides where to persist
- Next agent receives relevant state as input
- Agents become pure functions, easy to test and reason about

### Why Check-Modules as Workflow Config?

Check-modules are declarative rules (WHAT to check), not domain knowledge (HOW to reason about quality). The workflow already decides which check-module applies to which phase:

```
Phase 0 → research-checks.md
Phase 1 → model-checks.md
Phase 2 → contract-checks.md
```

This is orchestration logic. The validator agent becomes generic: `validate(artifact, checks) → gaps[]`.

## Decision Trail

### 1. Fundamental Unit of Knowledge (Skills)
- **Options**: Procedure, Domain Knowledge, Capability (bundled)
- **Chosen**: Domain Knowledge
- **Reasoning**: Keeps skills pure and dependency-free. Procedures belong in agents; tools are execution concerns. Mirrors clean architecture's domain layer.

### 2. Agent Responsibility
- **Options**: Procedure Application, Context Binding, Both + Judgment
- **Chosen**: Both + Judgment
- **Reasoning**: Real agents make decisions (when to escalate, retry, deviate). Pure procedure application is too mechanical.

### 3. Workflow Responsibility
- **Options**: Sequencing, Orchestration + State, Orchestration + State + Adaptation
- **Chosen**: Orchestration + State + Adaptation
- **Reasoning**: Current workflows already branch, loop, and adapt. Static pipelines can't express this.

### 4. Dependency Direction
- **Options**: Strict Inward, Inward + Contracts, Pragmatic Coupling
- **Chosen**: Inward + Contracts
- **Reasoning**: Pragmatic coupling causes current pain. Contracts give rigor while allowing state flow.

### 5. State Ownership
- **Options**: Workflow Owns State, New State Layer, Agents Own Their State
- **Chosen**: Workflow Owns State
- **Reasoning**: Agents become pure functions. 4th layer adds complexity; fragmented state loses single source of truth.

### 6. Check-Modules Location
- **Options**: Check-modules ARE Skills, Workflow Configuration, Agent Configuration
- **Chosen**: Workflow Configuration
- **Reasoning**: Check-modules are declarative rules, not knowledge. Workflow already decides which checks apply to which phase.

### 7. Tool Bindings
- **Options**: Skills Define Tools, Agents Define Tools, Workflows Inject Tools
- **Chosen**: Agents Define Tools
- **Reasoning**: Agents are the execution layer. Tool concerns shouldn't pollute skills (domain) or workflows (orchestration).

## Consequences

### Positive

- **Testable agents**: Pure functions with no side effects
- **Composable skills**: Atomic skills that can be mixed and matched
- **Clear boundaries**: Each layer has well-defined responsibilities
- **Reduced coupling**: Agents don't know about each other or workflow state
- **Flexible orchestration**: Workflows can be changed without touching agents
- **Generic validators**: Validator agents work with any check-module passed to them

### Negative

- **Refactoring effort**: Current bundled skills need to be split into atomic units
- **Contract overhead**: Need to define and maintain input/output contracts
- **Workflow complexity**: Workflows become more complex as they own all state management
- **Migration path**: Existing agents need to be refactored to be stateless

### Risks

- **Over-atomization**: Skills could become too granular, losing cohesion
- **Contract drift**: Input/output contracts could diverge from actual usage
- **Performance**: Additional indirection through workflows could add latency

## Implementation Roadmap

### Phase 1: Define Contracts
1. Create `contracts/` directory with input/output schemas
2. Document agent contracts in a shared location
3. Define standard contract patterns (validation, building, etc.)

### Phase 2: Atomize Skills
1. Split `plan-workflow` into atomic skills:
   - `research-knowledge` (Phase 0 domain expertise)
   - `domain-modeling` (Phase 1 domain expertise)
   - `contract-design` (Phase 2 domain expertise)
   - `validation-expertise` (cross-phase validation knowledge)
2. Extract shared patterns into foundation skills:
   - `context-patterns` (how to read/structure context)
   - `brownfield-patterns` (how to reason about existing code)
3. Update agents to compose atomic skills

### Phase 3: Stateless Agents
1. Refactor agents to return `state_updates` instead of writing files
2. Update agent output format to match contracts
3. Remove direct file I/O from agents

### Phase 4: Workflow State Management
1. Update workflow commands to handle state persistence
2. Move check-modules to workflow config location
3. Pass check-modules to validators as input

## Open Questions

- **Skill granularity**: How small should atomic skills be? One file per skill, or can a skill have 2-3 tightly-coupled files?
- **Cross-cutting concerns**: Where do shared patterns (context loading, brownfield handling) live? Separate foundation skills?
- **Constitution location**: Is constitution workflow config, a special skill, or a cross-cutting concern accessible to all layers?
- **Agent-to-agent communication**: Can agents invoke sub-agents, or must all orchestration go through workflows?

## Related

- [ADR-001: Multi-Agent Architecture](./001-multi-agent-architecture.md) - Establishes multi-agent approach; this ADR refines layer boundaries
- [ADR-004: Specify Plugin Extraction](./004-specify-plugin-extraction.md) - Plugin separation that aligns with layer boundaries
- [Plugin structure](../../plugins/humaninloop/README.md)
- [Agent Skills Documentation](../agent-skills-documentation.md)
