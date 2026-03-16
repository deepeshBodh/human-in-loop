# Roadmap

This document outlines the vision and planned evolution of the HumanInLoop plugin.

## Vision

**Plan with humans. Build with AI. Ship sustainably.**

The humaninloop plugin enforces specification-driven development—ensuring architectural decisions are made by humans before AI writes code. Stop vibe coding. Ship software that lasts.

---

## Current State (v3.0.0)

The core specify → plan → tasks → implement workflow is complete and functional. The specify workflow uses v3 StrategyGraph-based execution with single-DAG iteration, deterministic graph infrastructure (`humaninloop_brain`), and a three-agent architecture (Supervisor + DAG Assembler + State Analyst).

**6 Commands** for the full development lifecycle:
- `/humaninloop:setup` - Initialize your project constitution (brownfield-aware)
- `/humaninloop:specify` - Transform vague requests into structured specifications (DAG-based)
- `/humaninloop:plan` - Unified analysis and design planning (requirements, constraints, decisions, data models, API contracts)
- `/humaninloop:tasks` - Create implementation tasks with vertical TDD slicing
- `/humaninloop:audit` - Analyze artifacts for quality and consistency
- `/humaninloop:implement` - Execute implementation with progress tracking

**27 Skills** that Claude invokes automatically when relevant (authoring, analysis, patterns, validation, testing, using, dag-operations, strategy)

**10 Specialized Agents** with focused responsibilities (requirements analyst, technical analyst, devil's advocate, plan architect, principal architect, task architect, testing agent, UI designer, DAG assembler, state analyst)

---

## Coming Next

- Example project with complete artifact walkthrough
- Improved onboarding documentation
- Website ↔ repo integration

---

## Enterprise

AI guardrails at scale for teams and organizations.

### Team Collaboration
- Shared specifications across team members
- Spec review and approval workflows
- Handoff documentation generation
- Integration with issue trackers (GitHub, Linear, Jira)

### Compliance & Control
- Audit logs for specification decisions
- SSO/SAML integration
- Custom validation rules and quality gates
- Role-based access controls

### Infrastructure
- Encrypted cloud sync for artifacts
- Custom SLAs and priority support
- On-premise deployment options

Interested in Enterprise? [Contact us](https://humaninloop.dev).

---

## On the Horizon

### Quality & Feedback
- Post-implementation validation against spec
- Drift detection (implementation vs plan)
- Quality metrics and reporting

---

## Feature Requests

To request a feature, [open an issue](https://github.com/deepeshBodh/human-in-loop/issues/new).

---

## Non-Goals

- **Tool-agnostic framework** - We are Claude Code native
- **Full automation** - Humans must be in the loop for architectural decisions

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
