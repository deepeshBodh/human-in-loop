# Implement Command DAG Migration — Analysis Synthesis

## Problem Statement

Convert `plugins/humaninloop/commands/implement.md` from a procedural, linear execution engine into a DAG-orchestrated workflow using the same Supervisor/State Analyst/DAG Assembler architecture that `specify.md` uses. The goal is architectural consistency across all humaninloop commands while introducing structured progress tracking, retry semantics, and clear agent responsibility boundaries.

## Context & Constraints

- **Architectural consistency**: specify, plan, and implement should share the same Supervisor loop pattern (briefing → pick → assemble → execute → parse)
- **Existing DAG infrastructure**: `humaninloop_brain` already provides StrategyGraph, `hil-dag` CLI, catalog-driven assembly, and pass lifecycle — implement should consume, not reinvent
- **Testing-agent exists**: The `humaninloop:testing-agent` (Sonnet model) already handles TEST: verification tasks with auto-approval/human checkpoint logic — must integrate, not replace
- **Current implement.md is functional**: Migration must preserve all existing capabilities (TDD discipline, brownfield support, quality gates, cycle-based execution)

## Key Decisions

| # | Decision | Choice | Confidence | Rationale |
|---|----------|--------|------------|-----------|
| 1 | Cycle-to-pass mapping | One pass per cycle | Confident | Each cycle is a bounded unit with entry/exit gates — maps naturally to the pass lifecycle with briefing, execution, and freeze |
| 2 | carry_forward semantics | Written code + updated task checkboxes | Confident | Simple and concrete — no complex state transfer needed between cycles |
| 3 | Code execution model | New Staff Engineer agent | Confident | Maintains "Supervisor never does domain work" principle, consistent with specify's architecture |
| 4 | Dispatch granularity | Per-cycle (not per-task) | Confident | Staff Engineer receives full cycle task list, handles TDD ordering internally. Reduces dispatch overhead while keeping DAG visibility at cycle level |
| 5 | Per-cycle node pattern | Three nodes: execute-cycle → verify-cycle → checkpoint-gate | Confident | Full DAG visibility — Analyst can brief on implementation AND verification status separately. Testing-agent's human checkpoint mechanism stays clean (no nesting) |
| 6 | Project scaffolding | Pre-DAG Supervisor setup (not a catalog node) | Confident | Mirrors specify's pattern where mechanical setup (mkdir, create files, resolve paths) is pre-DAG and only domain validation enters the DAG as gates |
| 7 | Staff Engineer skills | `executing-tdd-cycle` + `brownfield-integration` | Confident | Two distinct types of guidance: TDD red/green/refactor discipline and EXTEND/MODIFY patterns for existing code |
| 8 | Parallel feature cycles | Sequential execution only (ignore [P] markers) | Confident | Simplifies architecture. DAG doesn't natively support concurrent passes. Can revisit later if needed |
| 9 | State Analyst role | Lightweight progress reports with cycle awareness | Confident | Cycle order is predetermined — Analyst determines current cycle from tasks.md and includes cycle task list in briefing. Earns its keep on retries (parsing failure reports) and convergence stall detection |
| 10 | Retry semantics | Checkpoint gate failure report carries forward (mirrors advocate-report in specify) | Confident | Checkpoint gate already has all failure information. Staff Engineer gets "fix these specific failures" context on retry. Max 3 retries per cycle before user escalation |
| 11 | Cycle-report format | Structured YAML frontmatter + prose markdown | Confident | Frontmatter gives checkpoint gate clean structured data to evaluate deterministically. Prose gives Analyst rich context for briefings and carry_forward. One artifact, two consumption patterns |
| 12 | Quality gate execution | Testing-agent runs quality gates (lint, build, tests) | Confident | Testing-agent already has infrastructure for running commands and capturing evidence. Keeps checkpoint gate as a pure deterministic evaluator of existing data, not a command executor |
| 13 | Retry task handling | Staff Engineer decides which tasks to re-do based on checkpoint failure report | Confident | Selective rework — traces failures to responsible tasks, re-opens only those. Avoids wasting tokens re-implementing working code. Guidance lives in `executing-tdd-cycle` skill |
| 14 | Cross-pass edges on retry | Single `triggered_by` edge from checkpoint gate only | Confident | Checkpoint report is self-contained — distills both cycle-report and verification-report. No `informed_by` edge to previous verify-cycle. Matches specify's pattern |
| 15 | Staff Engineer persona | "Make it work correctly, then make it clean" | Confident | TDD-disciplined, pragmatic, brownfield-aware, honest about blockers, scope-disciplined |
| 16 | Cycle-report format location | Reference file inside `executing-tdd-cycle` skill | Confident | Staff Engineer is the sole producer. Testing-agent has its own report format. No shared template needed |
| 17 | Brownfield integration skill depth | Lean (single SKILL.md, no reference files) | Confident | Core guidance is "read before write, follow what's there." Complexity is in agent judgment (persona), not procedural steps. Can enrich later if cycles fail on brownfield tasks |
| 18 | Cycle tracking ownership | State Analyst (via briefing), not Supervisor | Confident | Keeps Supervisor loop identical to specify's. Analyst reads tasks.md, determines current cycle, includes task list in briefing |
| 19 | Completion validation | Separate `final-validation` gate before milestone (7th node) | Confident | Full test suite, traceability check, and constitution alignment need independent verification. Keeps milestone as a pure state marker. If final validation fails, it's trackable and retryable through the DAG |
| 20 | Testing-agent quality gates | Expand `testing-end-user` skill (not a new skill) | Confident | Quality gates are conceptually verification work. Adding a "Quality Gates" section to the existing skill keeps dispatch simple (one invocation, one report). Reuses existing evidence capture infrastructure |
| 21 | Final-validation retry routing | "Fix pass" — unconstrained by cycle boundaries | Confident | Cross-cycle regressions don't belong to one cycle. A fix pass lets the Staff Engineer address specific failures without artificial cycle scoping. Mirrors how real teams handle integration test failures |

## Decision Trail

### D3: Code Execution Model — Agent vs. Supervisor-as-Executor

- **Options considered**: (A) New implementation agent, (B) Supervisor writes code directly, (C) Per-cycle executor agent
- **Recommendation was**: B (pragmatic, less indirection)
- **Chosen**: A — Staff Engineer agent with persona and skills
- **Key reasoning**: User wants architectural purity consistent with specify. Staff Software Engineer persona mirrors how principal-architect and requirements-analyst are designed. Associated skills provide reusable domain guidance. Breaks the "Supervisor does domain work" anti-pattern.

### D5: Per-Cycle Node Pattern

- **Options considered**: (A) Two nodes (execute + verify), (B) Staff Engineer dispatches testing-agent internally, (C) Three nodes (execute + verify + checkpoint-gate)
- **Recommendation was**: C
- **Chosen**: C
- **Key reasoning**: Three nodes give the DAG full visibility at every stage. State Analyst can brief on implementation status AND verification status separately. Testing-agent's human checkpoint mechanism stays clean without nesting. Checkpoint gate has structured inputs from both agent reports.

## Implementation Catalog Design

### Nodes (7 total)

```
┌──────────────────────────────────────────────────────────┐
│                  implement-catalog.json                    │
├───────────────────────────┬──────────┬────────────────────┤
│ Node                      │ Type     │ Agent / Dispatch    │
├───────────────────────────┼──────────┼────────────────────┤
│ tasks-complete            │ gate     │ none (deterministic)│
│ execute-cycle             │ task     │ humaninloop:staff-engineer │
│ verify-cycle              │ task     │ humaninloop:testing-agent  │
│ cycle-checkpoint          │ gate     │ none (deterministic)│
│ user-clarification        │ decision │ none (supervisor-owned)    │
│ final-validation          │ gate     │ none (deterministic)│
│ implementation-complete   │ milestone│ none               │
└───────────────────────────┴──────────┴────────────────────┘
```

### Node Details

**`tasks-complete`** (gate, deterministic, `carry_forward: true`)
- Consumes: `tasks.md`, `tasks-context.md`
- Evaluates: tasks workflow status is `completed`
- Verdict: `ready` / `critical-gaps`
- Analogous to: `constitution-gate` in specify

**`execute-cycle`** (task → Staff Engineer)
- Consumes: cycle task list from `tasks.md`, `plan.md`, `data-model.md` (if exists), `contracts/` (if exists), checkpoint-report (on retry), final-validation failure report (on fix pass)
- Produces: implemented code, updated `tasks.md` with completed checkboxes, `cycle-report.md`
- Agent invokes skills: `executing-tdd-cycle`, `brownfield-integration` (as needed)
- Supports two modes:
  - **Cycle mode** (normal): bound to a specific cycle's task list from Analyst briefing
  - **Fix mode** (after final-validation failure): unconstrained by cycle boundaries, scoped to specific failures from the final-validation report

**`verify-cycle`** (task → testing-agent)
- Consumes: TEST: tasks from the cycle, implemented code on disk
- Produces: `verification-report.md` with structured decision JSON and quality gate results
- Expanded scope: runs quality gates (lint, build, tests) alongside TEST: verification via expanded `testing-end-user` skill
- Handles: auto-approval (CLI + 100% pass) or human checkpoint
- Verification-report frontmatter includes:
  ```yaml
  verification:
    test_tasks:
      total: 2
      passed: 2
    quality_gates:
      lint: pass
      build: pass
      tests:
        passed: 47
        failed: 0
        skipped: 2
  ```

**`cycle-checkpoint`** (gate, deterministic)
- Consumes: `cycle-report.md`, `verification-report.md`
- Evaluates: all cycle tasks complete + verification passed + quality gates passed (from verification-report)
- Verdict: `ready` (advance to next cycle) / `needs-revision` (retry cycle)
- On `needs-revision`: produces checkpoint-report that carries forward

**`user-clarification`** (decision, supervisor-owned)
- Consumes: Staff Engineer report flagging ambiguity
- Produces: `clarification-answers`
- Triggered when: Staff Engineer explicitly flags uncertainty

**`final-validation`** (gate, deterministic)
- Consumes: all `cycle-checkpoint` reports, full codebase state
- Evaluates: full test suite passes + traceability matrix coverage (all user stories have implementing cycles) + constitution alignment
- Verdict: `ready` / `needs-revision`
- On `needs-revision`: triggers a "fix pass" — Staff Engineer dispatched in fix mode (unconstrained by cycle boundaries) with the failure report. Does NOT route to a specific cycle.
- Runs after all cycles complete, and again after each fix pass

**`implementation-complete`** (milestone)
- Consumes: `final-validation` report
- Prerequisites: `final-validation` gate passed
- Achieved: all cycles done, all validations passed

### Invariants

| ID | Rule | Enforcement |
|----|------|-------------|
| INV-001 | Every execute-cycle output must pass through cycle-checkpoint and final-validation before milestone | Assembly-time |
| INV-002 | tasks-complete gate must pass before any execute-cycle node | Assembly-time |
| INV-003 | verify-cycle must follow execute-cycle within same pass | Assembly-time |
| INV-004 | Max 3 retry attempts per cycle (or fix pass) before mandatory user escalation | Runtime |
| INV-005 | depends-on edges must form a DAG (no cycles) | Assembly-time |

### Cross-Pass Edge Pattern

```
Pass N:   execute-cycle → verify-cycle → cycle-checkpoint [needs-revision]
                                                |
Pass N+1: execute-cycle ←── triggered_by ───────┘
```

Single `triggered_by` edge across passes. Checkpoint report is self-contained — no additional `informed_by` edges to previous pass nodes.

## Cycle-Report Format

The Staff Engineer produces a `cycle-report.md` with structured YAML frontmatter and prose sections. Format specification lives as a reference file inside the `executing-tdd-cycle` skill.

```markdown
---
cycle: 3
attempt: 1
tasks_total: 4
tasks_completed: 4
files_created:
  - src/routes/api.ts
  - src/routes/api.test.ts
files_modified:
  - src/models/user.ts
brownfield_tasks: 1
checkpoint_criteria_met: true
---

## Cycle 3: API Route Layer

### What Was Done
Implemented REST endpoints for user CRUD operations...

### Decisions Made
- Chose Express router over Koa because plan.md specifies Express...

### Notes for Next Cycle
- The `User` model was extended with `lastLogin` field — C4 should account
  for this in the auth middleware...
```

The checkpoint gate reads frontmatter fields deterministically. The State Analyst reads prose sections for briefings and carry_forward context.

## Staff Engineer Agent Design

### Persona: Staff Software Engineer

**Model**: opus
**Skills**: `executing-tdd-cycle`, `brownfield-integration`

**Core Identity** — "You think like an engineer who has..."
- Seen teams skip the red phase and end up with tests that pass for the wrong reasons — so you write genuinely failing tests first and verify they fail for the right reason
- Learned that the simplest implementation that passes the tests is almost always the right one — so you don't over-engineer or add abstractions the task didn't ask for
- Broken production by not reading existing code carefully enough — so when a task says EXTEND or MODIFY, you read the full file first and follow existing patterns
- Watched projects balloon because "while I'm in here I'll also fix..." — so you implement exactly what the task describes, nothing more
- Been burned by silent workarounds that masked real problems — so you flag blockers honestly rather than making assumptions

**What You Produce**:
1. Implemented code following TDD discipline
2. Updated tasks.md with completed task checkboxes
3. cycle-report.md with structured frontmatter and prose

**What You Reject**:
- Adding code the task didn't ask for
- Skipping the failing test step
- Modifying existing interfaces without explicit `[MODIFY]` marker
- Silent workarounds for missing dependencies or contradictory instructions

**What You Embrace**:
- Following existing code patterns even when you'd prefer different ones
- Writing tests that test behavior, not implementation details
- Flagging discrepancies between task descriptions and codebase reality
- Keeping cycle reports honest about what worked and what didn't

## Skill Designs

### `executing-tdd-cycle`

Primary skill for the Staff Engineer. Provides TDD discipline and cycle execution guidance.

```
skills/executing-tdd-cycle/
├── SKILL.md
└── references/
    ├── CYCLE-REPORT-FORMAT.md        # Frontmatter schema + prose sections
    ├── TASK-PARSING.md               # How to read task descriptions, file paths, markers
    └── TDD-ANTI-RATIONALIZATION.md   # Common shortcuts and why they're wrong
```

**SKILL.md sections**:

| Section | Content |
|---------|---------|
| Cycle Execution Sequence | Parse cycle tasks → red phase → green phase → refactor → mark complete |
| Task Parsing | How to read task descriptions, extract file paths, detect EXTEND/MODIFY markers |
| TDD Discipline | Write failing test → verify it fails for the right reason → implement → verify pass |
| Progress Tracking | Mark `[x]` in tasks.md, write cycle-report with frontmatter + prose |
| Retry Handling | Read checkpoint failure report, trace failures to responsible tasks, selectively re-open and fix |
| Anti-rationalization | Common shortcuts and why they're wrong (reference file) |

**TDD Anti-Rationalization content**:

| Rationalization | Why It's Wrong |
|----------------|---------------|
| "The test already passes so I'll skip writing it first" | You haven't verified it fails — you might be testing nothing |
| "I'll write all the code first and tests after" | Inverts TDD, tests become retroactive justification |
| "This task is trivial, no test needed" | The task plan says test first — follow the plan |
| "I'll refactor this existing code while I'm here" | Scope creep — note it in the report, don't act on it |
| "The task says EXTEND but I need to rewrite this" | Read existing code more carefully — extend means extend |

### `brownfield-integration`

Lean skill for EXTEND/MODIFY task guidance. Single SKILL.md, no reference files.

```
skills/brownfield-integration/
└── SKILL.md
```

**SKILL.md sections**:

| Section | Content |
|---------|---------|
| EXTEND vs. MODIFY Semantics | EXTEND = add new code following existing patterns. MODIFY = change existing behavior. Never MODIFY when task says EXTEND. |
| Read-Before-Write Checklist | 1. Read full file. 2. Identify naming conventions. 3. Identify error handling pattern. 4. Identify import style. 5. Follow all of them. |
| Interface Preservation | Don't change function signatures, export surfaces, or type contracts unless task explicitly says MODIFY |
| Conflict Detection | Search for name collisions before adding new functions/classes/variables |
| When to Flag | If existing code contradicts the task description, flag in cycle-report — don't silently resolve |

## Pass Lifecycle

```
Pre-DAG Setup (Supervisor):
  ├── Run check-prerequisites.sh
  ├── Load tasks.md, plan.md, context files
  ├── Create/verify ignore files (project scaffolding)
  └── Set dag_path, feature_dir, catalog_path

Pass 1 (Cycle 1, attempt 1):
  Briefing (Analyst determines: Cycle 1, tasks T1.1-T1.N)
    → tasks-complete gate (carry_forward on subsequent passes)
    → execute-cycle (Staff Engineer receives cycle 1 task list)
    → verify-cycle (testing-agent: TEST tasks + quality gates)
    → cycle-checkpoint gate
  If ready: freeze pass, advance to Cycle 2
  If needs-revision: freeze pass, retry Cycle 1

Pass 2 (Cycle 1 retry — or Cycle 2, attempt 1):
  Briefing (Analyst: carry_forward context, current cycle + task list)
    → execute-cycle → verify-cycle → cycle-checkpoint
  ...repeat per cycle...

Pass N (final cycle):
  Briefing → execute-cycle → verify-cycle → cycle-checkpoint [ready]
    → final-validation gate (full test suite, traceability, constitution)
  If ready: → implementation-complete milestone → freeze pass → Completion
  If needs-revision: freeze pass, start fix pass

Fix Pass (if final-validation failed):
  Briefing (Analyst: "Fix pass — here are the failures from final-validation")
    → execute-cycle (fix mode: unconstrained by cycle, scoped to failures)
    → verify-cycle (testing-agent re-runs full quality gates)
    → final-validation gate
  If ready: → implementation-complete milestone → freeze pass → Completion
  If needs-revision: freeze pass, retry fix pass (max 3 fix passes)

Completion:
  Update context status to completed. Output summary report.
```

## New Artifacts Required

| Artifact | Type | Location | Description |
|----------|------|----------|-------------|
| `implement-catalog.json` | Catalog | `plugins/humaninloop/catalogs/` | 7 nodes, edge constraints, invariants |
| `staff-engineer.md` | Agent | `plugins/humaninloop/agents/` | Staff Software Engineer persona, 2 skills |
| `executing-tdd-cycle/SKILL.md` | Skill | `plugins/humaninloop/skills/` | TDD discipline, cycle execution, report format |
| `executing-tdd-cycle/references/` | References | `plugins/humaninloop/skills/` | CYCLE-REPORT-FORMAT.md, TASK-PARSING.md, TDD-ANTI-RATIONALIZATION.md |
| `brownfield-integration/SKILL.md` | Skill | `plugins/humaninloop/skills/` | EXTEND/MODIFY patterns, lean single-file skill |
| `implement.md` (rewrite) | Command | `plugins/humaninloop/commands/` | DAG-based Supervisor loop replacing procedural execution |

## Risks

- **Context window pressure**: Per-cycle Staff Engineer dispatch means the agent gets a fresh context each cycle, losing accumulated understanding of the codebase. Mitigation: cycle-report.md captures key decisions and patterns for the next cycle's carry_forward.
- **Testing-agent skill expansion**: The `testing-end-user` skill needs a new "Quality Gates" section. The existing skill was designed around TEST: marker tasks with Setup/Action/Assert structure — quality gates are structurally different (command execution with pass/fail, always auto-resolve). The expansion needs to feel cohesive, not bolted on.
- **Retry overhead**: Three agent dispatches per cycle attempt (briefing + Staff Engineer + testing-agent) plus Assembler/Analyst calls. If a cycle needs 2-3 retries, that's significant token usage. Mitigation: max 3 retries with user escalation.
- **Fix pass scope creep**: The fix pass is unconstrained by cycle boundaries — the Staff Engineer could make sweeping changes. Mitigation: the fix pass is scoped to the specific failures in the final-validation report, not a license to refactor. The `executing-tdd-cycle` skill's scope discipline guidance applies.

## Resolved Questions

### Testing-agent quality gates (formerly open)
**Decision**: Expand the existing `testing-end-user` skill with a "Quality Gates" section rather than creating a new skill. Quality gates are conceptually verification work — the testing-agent already has command execution and evidence capture infrastructure. The verification-report frontmatter gains a `quality_gates` section alongside `test_tasks`. Quality gate results always auto-resolve (no human checkpoint needed for "did lint pass?").

### Final-validation retry routing (formerly open)
**Decision**: Use a "fix pass" model. When `final-validation` fails, the Analyst's briefing creates a fix pass where the Staff Engineer is dispatched in **fix mode** — unconstrained by any specific cycle's task list, scoped to the specific failures from the final-validation report. This mirrors how real teams handle integration failures (create a fix ticket, not re-open a sprint). The fix pass uses the same three-node pattern (execute-cycle in fix mode → verify-cycle → final-validation), and INV-004 applies (max 3 fix passes before user escalation).

## Recommended Next Steps

1. **Design `implement-catalog.json`**: Define all 7 nodes with contracts (consumes/produces), edge constraints, and invariants. Use `specify-catalog.json` as the structural template. Include `execute-cycle` mode support (cycle vs. fix) in the node contract.
2. **Create the Staff Engineer agent**: Write `staff-engineer.md` with persona, skills roster, core identity, and quality standards. Model after `principal-architect.md` structure.
3. **Author `executing-tdd-cycle` skill**: Write SKILL.md with process guidance and 3 reference files (cycle-report format, task parsing, anti-rationalization). Include fix-mode execution guidance.
4. **Author `brownfield-integration` skill**: Write lean single-file SKILL.md with EXTEND/MODIFY semantics and checklists.
5. **Expand `testing-end-user` skill**: Add "Quality Gates" section covering lint/build/test execution and evidence capture. Update verification-report format to include `quality_gates` frontmatter.
6. **Rewrite `implement.md`**: Convert from procedural to DAG-based Supervisor loop. Use `specify.md` as structural template, adding cycle-awareness via Analyst briefings and fix-pass routing after final-validation failure.
