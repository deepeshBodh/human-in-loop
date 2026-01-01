# HumanInLoop Constitution Plugin

Project constitution setup for HumanInLoop workflows. Establishes project principles that govern all specification-driven development activities.

## Overview

The Constitution plugin helps you define and maintain your project's core principles, governance rules, and development standards. These principles serve as guardrails for all HumanInLoop workflows, ensuring consistency and quality across feature development.

## Installation

Add the plugin to your Claude Code project:

```bash
claude-code plugins add humaninloop-constitution
```

## Usage

### Initial Setup

Create your project constitution:

```
/humaninloop-constitution:setup
```

The command will:
1. Create the `.humaninloop/memory/` directory if needed
2. Copy the constitution template
3. Guide you through defining your project principles
4. Generate a versioned constitution document

### Update Existing Constitution

Modify principles or governance rules:

```
/humaninloop-constitution:setup Add a new principle for accessibility compliance
```

The workflow handles version management automatically:
- **MAJOR**: Breaking changes to governance or principle removals
- **MINOR**: New principles or expanded guidance
- **PATCH**: Clarifications and wording improvements

## Constitution Structure

The generated constitution includes:

### Core Principles
Define 3-7 non-negotiable principles for your project:
- Test-First Development
- API Design Standards
- Security Requirements
- Code Quality Gates
- Documentation Standards

### Governance
Rules for maintaining and amending the constitution:
- Amendment procedures
- Compliance verification
- Version management

### Additional Sections
Customize based on your project needs:
- Technology constraints
- Performance standards
- Review processes

## Output Location

```
.humaninloop/
└── memory/
    └── constitution.md    # Your project constitution
```

## Integration with Other Plugins

The constitution is used by:

| Plugin | How It Uses Constitution |
|--------|-------------------------|
| **humaninloop** (specify) | Validates specifications against principles |
| **humaninloop-plan** | Checks technical decisions for compliance |
| **humaninloop-implement** | Ensures implementation follows governance |

## Example Constitution

```markdown
# TaskFlow Constitution

## Core Principles

### I. User-Centric Design
All features MUST be justified by clear user value.
User stories MUST be independently testable.

### II. Test-First Development
TDD is mandatory: Tests → Approval → Implementation.
Coverage MUST exceed 80% for all new code.

### III. API Consistency
All endpoints MUST follow RESTful conventions.
Breaking changes MUST be versioned.

## Governance

- All PRs must verify constitutional compliance
- Amendments require team approval
- Version changes follow semantic versioning

**Version**: 1.0.0 | **Ratified**: 2025-01-01
```

## Why a Constitution?

A project constitution provides:

1. **Consistency** - Same principles applied across all features
2. **Quality Guardrails** - Automated checks against defined standards
3. **Team Alignment** - Clear expectations for all contributors
4. **Audit Trail** - Versioned history of governance decisions

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
