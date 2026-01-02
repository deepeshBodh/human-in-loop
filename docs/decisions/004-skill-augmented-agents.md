# ADR-004: Skill-Augmented Agents Architecture

**Status:** Proposed
**Date:** 2026-01-02

## Context

The humaninloop plugin uses 14 specialized agents (ADR-001) that contain embedded domain expertise: user story patterns, validation logic, API conventions, and more. This expertise is currently locked inside agent definitions, making it:

1. **Non-reusable** - The same patterns are duplicated across agents
2. **Non-discoverable** - Users can't leverage expertise outside workflows
3. **Token-inefficient** - Full agent context loads even when only part is needed
4. **Hard to maintain** - Updating a pattern requires editing multiple agents

Claude Code's Agent Skills system offers a solution: model-invoked, progressively-loaded knowledge packages that can be shared across agents and used independently.

The question: How should we integrate Agent Skills into our multi-agent architecture?

## Decision

Adopt a **Skill-Augmented Agents** architecture where:

- **Agents own workflow orchestration and state management**
- **Skills own reusable expertise and deterministic validation**

### Skill Organization

Use flat directory structure with category prefixes (required for plugin discovery):

```
skills/
├── iterative-analysis/           # Existing skill
├── authoring-user-stories/       # Authoring patterns
├── authoring-requirements/
├── validation-spec/              # Validation with scripts
├── validation-plan/
├── validation-task/
├── analysis-brownfield/          # Analytical capabilities
├── analysis-traceability/
├── patterns-api-design/          # Domain knowledge
└── patterns-entity-modeling/
```

### Skill Categories

| Category | Purpose | Examples |
|----------|---------|----------|
| `authoring-*` | Writing patterns and templates | user-stories, requirements, acceptance-criteria |
| `validation-*` | Check modules with scripts | spec, plan, task validation |
| `analysis-*` | Analytical capabilities | brownfield scanning, traceability |
| `patterns-*` | Reusable domain knowledge | api-design, entity-modeling |

### Progressive Disclosure Structure

Each skill follows this structure for token efficiency:

```
validation-task/
├── SKILL.md              # Index: what, when, quick start (< 200 lines)
├── FORMAT-CHECKS.md      # Loaded on demand
├── COVERAGE-CHECKS.md    # Loaded on demand
└── scripts/
    └── check-format.py   # Deterministic validation (output only enters context)
```

### Agent-Skill Integration

Agents reference skills via the `skills:` field in AGENT.md:

```yaml
---
name: plan-validator
skills: validation-plan, validation-spec
---
```

## Rationale

### Why Skill-Augmented Agents (vs alternatives)

| Alternative | Why Not |
|-------------|---------|
| **Skills replace agents** | Skills are stateless; our workflows require state management (.workflow/ context files) |
| **Agents embed all expertise** | Knowledge is trapped, duplicated, and can't be reused outside workflows |
| **Everything is a skill** | Loses workflow coordination; state management becomes fragmented |
| **Skill-augmented agents** | Best of both: workflow control (agents) + reusable expertise (skills) |

### Benefits

1. **Separation of concerns** - Agents focus on orchestration; skills focus on expertise
2. **Reusability** - Skills work inside workflows AND independently
3. **Token efficiency** - Progressive disclosure loads only what's needed
4. **Determinism** - Script-backed validation provides consistent results
5. **Maintainability** - Update a pattern once, all agents benefit
6. **Discoverability** - Users can invoke skills for ad-hoc tasks

### Why flat structure with naming conventions

Plugin discovery scans `skills/` for immediate child directories containing `SKILL.md`. Nested categories (e.g., `skills/validation/task/`) are not discovered.

Flat structure with `{category}-{name}` naming:
- Works with plugin discovery mechanism
- Provides alphabetical grouping by category
- Clear naming convention for discoverability

### Why script-backed validation

| Approach | Consistency | Token Cost | CI/CD Integration |
|----------|-------------|------------|-------------------|
| LLM-only validation | Variable | High | Difficult |
| Script-backed | Deterministic | Low (output only) | Native |

Scripts provide:
- Same result every run (no LLM variance)
- Only output enters context (token efficient)
- Can run in CI/CD pipelines (outside Claude)

## Consequences

### Positive

- Clear ownership: agents orchestrate, skills provide expertise
- Skills are reusable across agents and outside workflows
- Progressive disclosure minimizes context consumption
- Deterministic validation via scripts
- Easier testing of individual skills

### Negative

- More files to maintain (skill directories)
- Migration effort from embedded agent knowledge
- Need to document skill-agent contracts

### Neutral

- check-modules/ directory becomes deprecated (migrates to skills/validation-*)
- Skill naming convention must be followed consistently

## Migration Path

1. **Phase 1:** Convert check-modules to validation skills with scripts
2. **Phase 2:** Extract authoring patterns from spec-writer, checklist-writer
3. **Phase 3:** Add domain knowledge skills (api-design, entity-modeling)
4. **Phase 4:** Update agents to reference skills

## Related

- [ADR-001: Multi-Agent Architecture](./001-multi-agent-architecture.md)
- [Agent Skills Documentation](../agent-skills-documentation.md)
- [Claude Plugin Documentation](../claude-plugin-documentation.md)
- [iterative-analysis skill](../../plugins/humaninloop/skills/iterative-analysis/SKILL.md)
