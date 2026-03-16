# HumanInLoop

**Stop vibe coding. Ship software that lasts.**

[Website](https://humaninloop.dev) • [Quick Start](#quick-start) • [Roadmap](./ROADMAP.md) • [Changelog](./CHANGELOG.md)

---

## What is HumanInLoop?

HumanInLoop is a Claude Code plugin that enforces **specification-driven development**—ensuring architectural decisions are made by humans before AI writes code.

Instead of letting AI improvise your architecture, you guide it through a structured workflow:

```
Idea → Specification → Technical Spec → Plan → Tasks → Implementation
```

Every step produces artifacts you can review, refine, and approve before moving forward.

---

## The Workflow

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────┐  ┌───────┐  ┌───────────┐             │
│  │  SETUP  │─▶│ SPECIFY │─▶│ TECHSPEC │─▶│ PLAN │─▶│ TASKS │─▶│ IMPLEMENT │             │
│  └─────────┘  └─────────┘  └──────────┘  └──────┘  └───────┘  └───────────┘             │
│       │            │            │             │          │            │                   │
│       ▼            ▼            ▼             ▼          ▼            ▼                   │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────┐  ┌───────┐  ┌───────────┐             │
│  │ consti- │  │  spec   │  │technical/│  │ plan │  │ tasks │  │   code    │             │
│  │ tution  │  │   .md   │  │ 5 files  │  │  .md │  │  .md  │  │  changes  │             │
│  └─────────┘  └─────────┘  └──────────┘  └──────┘  └───────┘  └───────────┘             │
│       │            │            │             │          │            │                   │
│       └────────────┴────────────┴─────────────┴──────────┴────────────┘                   │
│                                        │                                                 │
│                                  ┌─────▼─────┐                                           │
│                                  │   AUDIT   │                                           │
│                                  │  (review) │                                           │
│                                  └───────────┘                                           │
│                                                                                          │
│  ○────────○────────○────────○────────○────────○  Human review checkpoints               │
│                                                                                          │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

| Stage | Command | What You Get |
|-------|---------|--------------|
| **Setup** | `/humaninloop:setup` | Project constitution with your standards |
| **Specify** | `/humaninloop:specify` | Structured spec with user stories and requirements |
| **Plan** | `/humaninloop:plan` | Technical requirements, constraints, decisions, data models, API contracts |
| **Tasks** | `/humaninloop:tasks` | Ordered task list with TDD cycles |
| **Audit** | `/humaninloop:audit` | Quality analysis across all artifacts |
| **Implement** | `/humaninloop:implement` | Guided implementation with progress tracking |

Each command produces artifacts you review before the next step. You stay in control.

### Command Details

<details open>
<summary><strong>Specify</strong> - Create feature specification (DAG-based)</summary>

```
┌─────────────────────────────────────────────────────────────────────┐
│                         /humaninloop:specify                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  SUPERVISOR  │ ◄─── You invoke the command                       │
│  └──────┬───────┘                                                   │
│         │  ┌──────────────────┐     ┌──────────────────┐            │
│         ├─▶│  State Analyst   │────▶│  briefing +      │            │
│         │  └──────────────────┘     │  recommendations │            │
│         │                           └────────┬─────────┘            │
│         │                                    │                      │
│         │  ┌──────────────────┐              │                      │
│         ├─▶│  DAG Assembler   │◄─────────────┘                      │
│         │  └──────┬───────────┘  (assembly decisions)               │
│         │         │                                                 │
│         │         ▼                                                 │
│         │  ┌──────────────────┐     ┌───────────────────┐           │
│         │  │   Requirements   │────▶│   Devil's         │           │
│         │  │   Analyst        │     │   Advocate        │           │
│         │  └────────┬─────────┘     └─────────┬─────────┘           │
│         │           │                         │                     │
│         │           ▼                         ▼                     │
│         │      ┌─────────┐         ┌────────────────────┐           │
│         │      │ spec.md │         │ gaps? → new pass   │           │
│         │      └─────────┘         └────────────────────┘           │
│         │                                                           │
│         ▼  Deterministic DAG tracks all nodes, edges, and status    │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │  StrategyGraph JSON  (single DAG, multi-pass iteration)  │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Output**: `specs/{feature}/spec.md` + StrategyGraph JSON

**Agents**:
- **DAG Assembler** — Pure graph mechanics; translates Supervisor decisions into validated DAG mutations
- **State Analyst** — Reads DAG state and parses domain agent reports into structured briefings
- **Requirements Analyst** — Transforms feature requests into structured specs; no implementation details
- **Devil's Advocate** — Reviews for gaps and ambiguity; asks clarifying questions

</details>

<details>
<summary><strong>Plan</strong> - Unified analysis and design planning</summary>

```
┌─────────────────────────────────────────────────────────────────────┐
│                          /humaninloop:plan                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  SUPERVISOR  │ ◄─── Reads spec.md                                │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                Phase P1 (Analysis)                       │
│  ┌──────────────────┐  ┌───────────────────┐  ┌─────────────────┐   │
│  │   Technical      │─▶│   Principal       │─▶│   Devil's       │   │
│  │   Analyst        │  │   Architect       │  │   Advocate      │   │
│  └────────┬─────────┘  └───────────────────┘  └────────┬────────┘   │
│           │            (feasibility gate)               │           │
│           ▼                                            ▼           │
│  ┌──────────────┐ ┌───────────────────┐ ┌─────────┐ ┌────────┐     │
│  │requirements  │ │constraints-and-   │ │ nfrs.md │ │ gaps?  │     │
│  │    .md       │ │  decisions.md     │ │         │ └────────┘     │
│  └──────────────┘ └───────────────────┘ └─────────┘                │
│                                                                     │
│         │                Phase P2 (Design)                         │
│         ▼                                                           │
│  ┌──────────────────┐     ┌─────────────────┐                       │
│  │   Technical      │────▶│   Devil's       │                       │
│  │   Analyst        │     │   Advocate      │                       │
│  └────────┬─────────┘     └────────┬────────┘                       │
│           │                        │                               │
│           ▼                       ▼                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐               │
│  │  data-   │ │contracts/│ │quickstart│ │  gaps?   │               │
│  │ model.md │ │ api.yaml │ │   .md    │ └──────────┘               │
│  └──────────┘ └──────────┘ └──────────┘                             │
│           │          │           │                                  │
│           └──────────┴───────────┘                                  │
│                      │                                              │
│                      ▼                                              │
│                ┌──────────┐                                         │
│                │ plan.md  │                                         │
│                └──────────┘                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Output**: `specs/{feature}/plan.md` + 6 supporting artifacts

**Agents**:
- **Technical Analyst** — Produces analysis artifacts (requirements, constraints-and-decisions, NFRs) and design artifacts (data model, API contracts, integration guide)
- **Principal Architect** — Reviews cross-artifact feasibility after analysis phase (one-time gate)
- **Devil's Advocate** — Validates completeness, traceability, and cross-artifact consistency

</details>

<details>
<summary><strong>Tasks</strong> - Generate implementation tasks</summary>

```
┌─────────────────────────────────────────────────────────────────────┐
│                         /humaninloop:tasks                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  SUPERVISOR  │ ◄─── Reads plan artifacts                         │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────────┐     ┌───────────────────┐                     │
│  │     Task         │────▶│   Devil's         │                     │
│  │     Architect    │     │   Advocate        │                     │
│  └────────┬─────────┘     └─────────┬─────────┘                     │
│           │                         │                               │
│           ▼                         ▼                               │
│  ┌────────────────┐          ┌──────────┐                           │
│  │ task-mapping.md│          │  gaps?   │──── yes ──┐               │
│  └────────────────┘          └──────────┘           │               │
│           │                       │                 ▼               │
│           ▼                      no          ┌────────────┐         │
│     ┌──────────┐                  │          │ clarify w/ │         │
│     │ tasks.md │                  ▼          │    user    │         │
│     └──────────┘            ┌──────────┐     └─────┬──────┘         │
│                             │   done   │           │                │
│                             └──────────┘     ◄─────┘ (loop)         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Output**: `specs/{feature}/tasks.md` with TDD cycles

**Agents**:
- **Task Architect** — Maps requirements to vertical slices with TDD structure; no implementation
- **Devil's Advocate** — Ensures coverage, proper ordering, and testable increments

</details>

<details>
<summary><strong>Setup</strong> - Create project constitution</summary>

```
┌─────────────────────────────────────────────────────────────────────┐
│                         /humaninloop:setup                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  SUPERVISOR  │                                                   │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────────┐     Brownfield?                               │
│  │ Detect Codebase  │────────┬──────────────┐                       │
│  └──────────────────┘        │              │                       │
│                             yes             no                      │
│                              │              │                       │
│                              ▼              │                       │
│                    ┌──────────────────┐     │                       │
│                    │    Principal     │     │                       │
│                    │    Architect     │     │                       │
│                    └────────┬─────────┘     │                       │
│                             │               │                       │
│         ┌───────────────────┼───────────────┤                       │
│         ▼                   ▼               ▼                       │
│  ┌────────────┐    ┌────────────────┐  ┌────────────┐               │
│  │  codebase- │    │  constitution  │  │constitution│               │
│  │analysis.md │    │     .md        │  │    .md     │               │
│  └────────────┘    └────────────────┘  └────────────┘               │
│         │                   │                                       │
│         ▼                   │                                       │
│  ┌────────────┐             │                                       │
│  │ evolution- │             │                                       │
│  │ roadmap.md │             │                                       │
│  └────────────┘             │                                       │
│         └───────────────────┘                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Output**: `.humaninloop/memory/constitution.md`

**Agents**:
- **Principal Architect** — Defines governance principles and quality gates; enforces RFC 2119 keywords

</details>

<details>
<summary><strong>Audit</strong> - Analyze artifacts for quality</summary>

```
┌─────────────────────────────────────────────────────────────────────┐
│                         /humaninloop:audit                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  SUPERVISOR  │ ◄─── No agents, direct analysis                   │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                    Load Artifacts                         │       │
│  │  spec.md │ plan.md │ tasks.md │ data-model │ contracts   │       │
│  └──────────────────────────┬───────────────────────────────┘       │
│                             │                                       │
│         ┌───────────────────┼───────────────────┐                   │
│         ▼                   ▼                   ▼                   │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐             │
│  │   Spec     │      │   Plan     │      │   Task     │             │
│  │  Analysis  │      │  Validation│      │ Validation │             │
│  └────────────┘      └────────────┘      └────────────┘             │
│         │                   │                   │                   │
│         └───────────────────┴───────────────────┘                   │
│                             │                                       │
│                             ▼                                       │
│                    ┌────────────────┐                               │
│                    │  Audit Report  │                               │
│                    │ (stdout/file)  │                               │
│                    └────────────────┘                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Output**: Coverage report + flagged issues

**Agents**: None — direct analysis using validation skills

</details>

<details>
<summary><strong>Implement</strong> - Execute the task plan</summary>

```
┌─────────────────────────────────────────────────────────────────────┐
│                       /humaninloop:implement                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │  SUPERVISOR  │ ◄─── Reads tasks.md                               │
│  └──────┬───────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │               Foundation Cycles (Sequential)              │       │
│  │   C1 ──▶ C2 ──▶ C3 ──▶ ...                               │       │
│  └──────────────────────────┬───────────────────────────────┘       │
│                             │                                       │
│                             ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │                Feature Cycles (Can Parallel)              │       │
│  │   C4 ──┬──▶ C5                                           │       │
│  │        └──▶ C6 [P]                                       │       │
│  └──────────────────────────┬───────────────────────────────┘       │
│                             │                                       │
│  For each cycle:            │                                       │
│  ┌──────────────────────────┴───────────────────────────────┐       │
│  │  T1 (test) ──▶ T2 (impl) ──▶ T3 (impl) ──▶ Checkpoint    │       │
│  │       │                                                   │       │
│  │       ▼ (if TEST: marker)                                │       │
│  │  ┌─────────────────┐                                     │       │
│  │  │  Testing Agent  │ ──▶ auto-approve or human checkpoint│       │
│  │  └─────────────────┘                                     │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Output**: Implemented code + marked tasks

**Agents**:
- **Testing Agent** — Executes verification tasks and captures evidence; auto-approves or presents checkpoints

</details>

---

## What's Included

### 7 Commands
The full specify → plan → tasks → implement lifecycle.

### 27 Skills
Claude automatically invokes these when relevant—authoring requirements, technical specifications, analyzing codebases, designing APIs, running verification tests, managing GitHub issues, DAG operations, workflow strategy, and more.

### 10 Specialized Agents
Focused responsibilities: requirements analyst, technical analyst, devil's advocate, plan architect, principal architect, task architect, testing agent, UI designer, DAG assembler, state analyst.

See the [plugin documentation](./plugins/humaninloop/README.md) for full details.

---

## Quick Start

### 1. Add the marketplace

```bash
/plugin marketplace add deepeshBodh/human-in-loop
```

### 2. Install the plugin

```bash
/plugin install humaninloop
```

### 3. Set up your project

```bash
/humaninloop:setup
```

This creates your project constitution—the standards and conventions that guide all future specifications.

### 4. Create your first spec

```bash
/humaninloop:specify add user authentication with email and password
```

---

## Documentation

| Resource | Description |
|----------|-------------|
| [Roadmap](./ROADMAP.md) | Vision and planned features |
| [Changelog](./CHANGELOG.md) | Release history |
| [Plugin README](./plugins/humaninloop/README.md) | Detailed command and skill reference |

---

## For Plugin Developers

This repository serves as a reference implementation for Claude Code plugins. If you're building your own plugins, you can learn from:

### Repository Structure

```
human-in-loop/
├── humaninloop_brain/                # Deterministic DAG infrastructure (Python)
│   ├── src/humaninloop_brain/        # Package source
│   │   ├── entities/                 # Pydantic models (11 enums, 14 models)
│   │   ├── graph/                    # NetworkX graph operations
│   │   ├── validators/               # Structural + contract validators
│   │   ├── passes/                   # Pass lifecycle management
│   │   └── cli/                      # hil-dag CLI (7 subcommands)
│   └── tests/                        # 381 tests, 97% coverage
├── plugins/humaninloop/
│   ├── .claude-plugin/plugin.json    # Plugin manifest
│   ├── commands/                     # Slash command definitions
│   ├── agents/                       # 10 specialized agent definitions
│   ├── skills/                       # 27 model-invoked skills
│   ├── catalogs/                     # Node catalogs for DAG workflows
│   ├── templates/                    # Workflow templates
│   └── scripts/                      # Shell utilities
├── docs/
│   ├── decisions/                    # Architecture Decision Records (7 ADRs)
│   ├── architecture/                 # DAG-first + v3 architecture docs
│   ├── claude-plugin-documentation.md
│   └── agent-skills-documentation.md
└── specs/                            # Feature specifications (dogfooding)
```

### Key Resources

- [Claude Code Plugin Documentation](./docs/claude-plugin-documentation.md) - Complete technical reference
- [Agent Skills Documentation](./docs/agent-skills-documentation.md) - How skills work
- [Architecture Decisions](./docs/decisions/) - ADRs explaining design choices

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## License

MIT - See [LICENSE](./LICENSE)
