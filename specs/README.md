# Feature Specifications

This folder contains specifications for humaninloop marketplace features, organized by status.

## Structure

```
specs/
├── planned/       # Features we intend to build (the living roadmap)
├── in-progress/   # Features currently being implemented
└── completed/     # Shipped features (proof the workflow works)
```

## Workflow

1. **New feature identified** → Create spec in `planned/`
2. **Work begins** → Move spec to `in-progress/`
3. **Feature ships** → Move spec to `completed/`

## Creating Specifications

Specifications are created using the `/humaninloop:specify` command. This ensures:
- Structured format with required sections
- Multi-agent validation
- Consistent quality

See the [humaninloop plugin](../plugins/humaninloop/README.md) for details.

## Why Track Specs Here?

1. **Dogfooding** - We use our own tools to build our tools
2. **Transparency** - The roadmap is visible through planned specs
3. **Proof of concept** - Completed specs demonstrate the workflow
4. **Historical record** - Decision rationale preserved with each feature

## Spec File Naming

Use kebab-case with descriptive names:
- `workflow-state-persistence.md`
- `drift-detection.md`
- `multi-user-collaboration.md`
