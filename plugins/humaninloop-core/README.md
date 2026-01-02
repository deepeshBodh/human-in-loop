# humaninloop-core

Domain-agnostic capabilities for software engineering. This plugin provides foundational skills and agents that enhance Claude's ability to work with codebases, think deeply about problems, and validate quality.

## Overview

humaninloop-core is designed to be **valuable standalone**—you can install it without any other humaninloop plugins and immediately benefit from enhanced software engineering capabilities.

It also serves as the **foundation** for other humaninloop plugins (`humaninloop-specs`, `humaninloop`), which depend on these core capabilities.

## Installation

```bash
/plugin install humaninloop-core
```

## What's Included

### Skills

| Skill | Purpose |
|-------|---------|
| `iterative-analysis` | Deep thinking through progressive questioning with synthesis |
| `context-patterns` | Structured patterns for loading and managing context |
| `brownfield-patterns` | Patterns for understanding and working with existing codebases |
| `validation-expertise` | Quality validation patterns and gap classification |
| `codebase-understanding` | Techniques for analyzing and comprehending code structure |

### Agents

| Agent | Purpose |
|-------|---------|
| `codebase-discovery` | Explore and understand existing codebases systematically |

## Standalone Usage

Even without other humaninloop plugins, core provides:

- **Deep Analysis**: Use `iterative-analysis` for thorough problem exploration
- **Codebase Exploration**: Use `codebase-discovery` to understand unfamiliar code
- **Quality Thinking**: Apply `validation-expertise` patterns to any review task

## As a Dependency

Other humaninloop plugins compose core skills with their domain-specific skills:

```yaml
# Example: plan-builder agent in humaninloop plugin
skills: context-patterns, brownfield-patterns, research-expertise, domain-modeling
#       └─── from core ───┘  └─── from core ──┘  └─── from humaninloop ────────┘
```

## Dependency Marker

On first use, core creates `.humaninloop/core-installed` to signal availability to dependent plugins.

## Related

- [ADR-006: humaninloop-core Plugin](../../docs/decisions/006-humaninloop-core-plugin.md)
- [ADR-005: Hexagonal Multi-Agent Architecture](../../docs/decisions/005-hexagonal-agent-architecture.md)
