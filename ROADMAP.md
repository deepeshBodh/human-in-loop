# Roadmap

This document outlines the vision and planned evolution of the HumanInLoop plugin.

## Vision

**Plan with humans. Build with AI. Ship sustainably.**

The humaninloop plugin enforces specification-driven development—ensuring architectural decisions are made by humans before AI writes code. Stop vibe coding. Ship software that lasts.

---

## Current State (v0.7.1)

The core specify → plan → tasks → implement workflow is complete and functional.

**6 Commands** for the full development lifecycle:
- `/humaninloop:setup` - Initialize your project constitution
- `/humaninloop:specify` - Transform vague requests into structured specifications
- `/humaninloop:plan` - Generate implementation plans with domain modeling
- `/humaninloop:tasks` - Create implementation tasks with vertical TDD slicing
- `/humaninloop:audit` - Analyze artifacts for quality and consistency
- `/humaninloop:implement` - Execute implementation with progress tracking

**13 Skills** that Claude invokes automatically when relevant (authoring, analysis, patterns, validation)

**5 Specialized Agents** with focused responsibilities

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
