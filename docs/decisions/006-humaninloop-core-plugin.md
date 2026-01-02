# ADR-006: humaninloop-core Plugin

**Status**: Proposed
**Date**: 2026-01-02
**Decision**: Create a standalone `humaninloop-core` plugin containing domain-agnostic skills and shared agents that other humaninloop plugins depend on

---

## Problem Statement

The humaninloop plugin ecosystem needs shared foundation capabilities (skills and agents) that multiple workflow plugins use. Currently, these are either duplicated across plugins or bundled into monolithic skills. We need a clean separation where core capabilities live in one place, are valuable standalone, and can be composed by workflow-specific plugins.

## Context & Constraints

- **No formal plugin dependencies**: Claude Code has no `dependencies` field in plugin.json
- **Flat skill namespace**: Skills from all installed plugins are discoverable without namespace prefixes
- **ADR-005**: Established hexagonal architecture with skills as innermost layer, agents composing skills
- **Existing pattern**: `humaninloop-constitution` uses filesystem convention for dependency checking
- **Goal**: Core should be valuable standalone, not just a "dependency tax"

## Decision

### Create humaninloop-core Plugin

A new plugin containing domain-agnostic capabilities that make Claude better at software engineering work in general. Other humaninloop plugins depend on it via filesystem convention.

### Core Contains: Skills + Shared Agents

| Component Type | Included | Rationale |
|---------------|----------|-----------|
| Skills | Yes | Expensive to duplicate, need consistency |
| Agents | Yes (shared only) | Complex, need consistent behavior |
| Templates | No | Cheap to copy, often workflow-specific |

### Core Boundary Rule

**Domain-agnostic capabilities only**: Skills that teach Claude "how to work" rather than "what specific workflow to follow."

A skill belongs in core if: "It helps Claude with software work even outside humaninloop workflows."

### Core Skills (All Three Categories)

| Category | Skills | Purpose |
|----------|--------|---------|
| **General-Purpose AI** | `iterative-analysis` | Deep thinking through progressive questioning |
| **Software Engineering** | `brownfield-patterns`, `codebase-understanding` | Working with existing codebases |
| **Workflow Patterns** | `context-patterns`, `validation-expertise` | Structured context and quality validation |

### Core Agents

| Agent | Purpose | Why Core |
|-------|---------|----------|
| `codebase-discovery` | Explore and understand existing codebases | Used by specs, plan, and tasks workflows |

### What Stays in Workflow Plugins

| Plugin | Skills | Agents |
|--------|--------|--------|
| `humaninloop-specs` | `spec-writing`, `clarification-patterns` | spec-writer, spec-clarify, checklist-agent, scaffold-agent |
| `humaninloop` | `research-expertise`, `domain-modeling`, `contract-design`, `task-mapping`, `task-generation` | plan-builder, plan-validator, task-builder, task-validator |

### Dependency Enforcement

Filesystem convention with runtime checks:

1. Core creates marker: `.humaninloop/core-installed`
2. Dependent plugins check for marker at command startup
3. Clear error message if missing: "Install humaninloop-core first"

### Skill Composition

Skills are composed at the agent level (per ADR-005):

```yaml
# Agent in humaninloop plugin
name: plan-builder
skills: context-patterns, brownfield-patterns, research-expertise, domain-modeling, contract-design
#       └─── from core ───┘  └─── from core ──┘  └────────── from humaninloop ──────────────────┘
```

Claude's flat skill namespace automatically resolves skills from whichever plugin provides them.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        humaninloop-core                                  │
│  "Domain-agnostic capabilities for software engineering"                │
├─────────────────────────────────────────────────────────────────────────┤
│  SKILLS                                                                 │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐           │
│  │ iterative-      │ │ context-        │ │ brownfield-     │           │
│  │ analysis        │ │ patterns        │ │ patterns        │           │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘           │
│  ┌─────────────────┐ ┌─────────────────┐                               │
│  │ validation-     │ │ codebase-       │                               │
│  │ expertise       │ │ understanding   │                               │
│  └─────────────────┘ └─────────────────┘                               │
│                                                                         │
│  AGENTS                                                                 │
│  ┌─────────────────┐                                                   │
│  │ codebase-       │                                                   │
│  │ discovery       │                                                   │
│  └─────────────────┘                                                   │
│                                                                         │
│  MARKER: .humaninloop/core-installed                                   │
└─────────────────────────────────────────────────────────────────────────┘
                              ▲
                              │ depends on (filesystem check)
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│humaninloop-specs│ │  humaninloop    │ │humaninloop-     │
│ (specify)       │ │ (plan + tasks)  │ │constitution     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Rationale

### Why a Separate Core Plugin?

1. **Standalone value**: Users can install only core and get useful capabilities (iterative analysis, codebase understanding)
2. **Single source of truth**: Shared skills maintained in one place
3. **Clean dependencies**: Clear hierarchy instead of circular or implicit dependencies
4. **Composability**: Workflow plugins are lighter, focused on their specific domain

### Why Filesystem Convention for Dependencies?

1. **No platform support**: Claude Code lacks formal plugin dependencies
2. **Proven pattern**: Already used for constitution plugin
3. **Runtime safety**: Clear error messages guide users to install missing dependencies
4. **Simple**: No complex versioning or resolution logic needed

### Why Skills + Agents but Not Templates?

1. **Skills**: Domain knowledge that's expensive to keep in sync if duplicated
2. **Agents**: Complex autonomous workers that need consistent behavior
3. **Templates**: Cheap markdown files, often need workflow-specific customization

### Why Composition at Agent Level?

1. **Flat namespace**: Claude discovers all skills from all installed plugins
2. **No skill-to-skill dependencies**: Skills don't reference each other
3. **Explicit composition**: Agent's `skills:` field clearly shows what it uses
4. **Aligns with ADR-005**: Agents are the "application layer" that composes domain knowledge

## Decision Trail

### 1. Dependency Enforcement
- **Options**: Filesystem convention, Skill duplication, Documentation only
- **Chosen**: Filesystem convention
- **Reasoning**: Runtime checks with clear errors; avoids duplication; proven with constitution

### 2. What Core Provides
- **Options**: Skills only, Skills + Agents, Skills + Agents + Templates
- **Chosen**: Skills + Agents
- **Reasoning**: Both are expensive to duplicate and need consistency; templates are cheap

### 3. Core Boundary
- **Options**: Minimal (universal only), Cross-workflow (2+ plugins), Standalone-valuable
- **Chosen**: Standalone-valuable
- **Reasoning**: Core should provide value on its own, not be a dependency tax

### 4. Skill Interaction
- **Options**: Composition at agent level, Skill references, Layered loading
- **Chosen**: Composition at agent level
- **Reasoning**: Flat namespace makes this work; keeps skills atomic; explicit in agent definition

## Consequences

### Positive

- **Standalone value**: Core is useful even without other humaninloop plugins
- **DRY**: Shared capabilities maintained in one place
- **Clear hierarchy**: Core → Workflow plugins dependency is explicit
- **Lighter plugins**: Workflow plugins contain only domain-specific code
- **Easier testing**: Core skills/agents can be tested independently

### Negative

- **Installation friction**: Users must install two plugins instead of one
- **Coordination overhead**: Changes to core may affect multiple plugins
- **Discovery complexity**: Users need to know core exists

### Risks

- **Skill naming conflicts**: Two plugins providing same-named skill (documented Claude Code gap)
- **Version drift**: Core and dependent plugins could become incompatible
- **Over-extraction**: Temptation to move too much into core

## Implementation Roadmap

### Phase 1: Create Plugin Structure

```
plugins/humaninloop-core/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── codebase-discovery.md
├── skills/
│   ├── iterative-analysis/
│   │   ├── SKILL.md
│   │   └── SYNTHESIS.md
│   ├── context-patterns/
│   │   └── SKILL.md
│   ├── brownfield-patterns/
│   │   └── SKILL.md
│   ├── validation-expertise/
│   │   └── SKILL.md
│   └── codebase-understanding/
│       └── SKILL.md
├── scripts/
│   └── install-marker.sh
└── README.md
```

### Phase 2: Extract/Create Skills

1. Move `iterative-analysis` from humaninloop
2. Extract `context-patterns` from plan-workflow/CONTEXT.md
3. Extract `brownfield-patterns` from plan-workflow/BROWNFIELD.md
4. Extract `validation-expertise` from plan-workflow/VALIDATION.md
5. Create `codebase-understanding` (generalized from codebase-discovery patterns)

### Phase 3: Move Shared Agent

1. Move `codebase-discovery` agent from humaninloop to core
2. Update agent to use core skills

### Phase 4: Add Dependency Checks

1. Core creates `.humaninloop/core-installed` on first command run
2. Update humaninloop commands to check for marker
3. Update humaninloop-specs commands to check for marker

### Phase 5: Refactor Dependent Plugins

1. Remove extracted skills from humaninloop
2. Update agent skill declarations to reference core skills
3. Delete bundled plan-workflow and task-workflow skills
4. Create atomic domain-specific skills

## Open Questions

- **Marker format**: File (`.humaninloop/core-installed`) or directory with metadata (`.humaninloop/core/`)?
- **Version compatibility**: How to detect/handle version mismatches between core and dependents?
- **Installation UX**: Should marketplace recommend core when installing dependents?
- **Constitution relationship**: Should constitution also depend on core, or remain independent?

## Related

- [ADR-005: Hexagonal Multi-Agent Architecture](./005-hexagonal-agent-architecture.md) - Layer boundaries that core implements
- [ADR-004: Specify Plugin Extraction](./004-specify-plugin-extraction.md) - Plugin separation pattern
- [ADR-001: Multi-Agent Architecture](./001-multi-agent-architecture.md) - Foundation for agent composition
