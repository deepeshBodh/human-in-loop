# Implementation Plan: Absorb DAG Assembler into State Analyst

**Source**: [analysis-merge-state-analyst-dag-assembler.md](analysis-merge-state-analyst-dag-assembler.md)
**Scope**: Eliminate the DAG Assembler agent by absorbing its functionality into the State Analyst
**Impact**: 29 files reference "DAG Assembler" — 6 substantial rewrites, 6 reference updates, 17 documentation checks

---

## Phase 1: Design New Action Vocabulary

**Goal**: Replace 5 separate actions across 2 agents with 4 combined actions on 1 agent.

### Current Actions (being replaced)

| Agent | Action | Purpose |
|-------|--------|---------|
| State Analyst | `briefing` | Read state, produce recommendations |
| State Analyst | `parse-and-recommend` | Parse report, record, recommend next |
| DAG Assembler | `assemble-and-prepare` | Resolve tags, mutate graph, construct prompt |
| DAG Assembler | `freeze-pass` | Freeze pass, create triggered_by edges |
| DAG Assembler | `update-status` | Update supervisor-owned nodes |

### New Actions

#### 1. `brief-and-assemble`

Replaces: `briefing` + `assemble-and-prepare` (first call of every pass)

**Input**:
```json
{
  "action": "brief-and-assemble",
  "workflow": "specify",
  "feature_id": "001-user-auth",
  "pass_number": 2,
  "dag_path": "specs/001-user-auth/.workflow/dags/specify-strategy.json",
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "feature_dir": "specs/001-user-auth"
}
```

**Process**:
1. Read DAG, catalog, strategy skills, artifacts (existing briefing logic)
2. Produce ranked recommendations with rationale (existing briefing logic)
3. Auto-select top recommendation
4. Call `hil-dag assemble` MCP tool to add node (absorbed from DAG Assembler)
5. Infer edges, validate invariants, auto-resolve carry_forward gates (all via MCP)
6. Construct NL prompt for domain agent (absorbed from DAG Assembler)
7. Return combined output

**Output**:
```json
{
  "briefing": {
    "state_summary": "...",
    "outcome_trajectory": "gaps: 7 → 5",
    "pass_context": "Pass 2 of 5 max."
  },
  "selected": {
    "intent": "...",
    "capability_tags": ["..."],
    "rationale": "..."
  },
  "alternatives": [
    {"intent": "...", "capability_tags": ["..."], "rationale": "...", "priority": 2}
  ],
  "assembled": {
    "node_id": "analyst-review",
    "status": "valid",
    "edges_inferred": 2
  },
  "dispatch": {
    "dispatch_mode": "agent",
    "agent_type": "humaninloop:requirements-analyst",
    "agent_prompt": "Read your instructions from: specs/001-user-auth/.workflow/context.md"
  }
}
```

The Supervisor dispatches based on `dispatch` directly. If the Supervisor disagrees with `selected`, it sends a `re-brief` with an override.

#### 2. `parse-and-advance`

Replaces: `parse-and-recommend` + (`assemble-and-prepare` OR `freeze-pass`)

**Input**:
```json
{
  "action": "parse-and-advance",
  "node_id": "advocate-review",
  "pass_number": 1,
  "dag_path": "specs/001-feature/.workflow/dags/specify-strategy.json",
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "feature_dir": "specs/001-feature"
}
```

**Process**:
1. Resolve node contract from catalog (know what artifacts to expect)
2. Read domain agent report from disk
3. Extract structured summary (existing report parsing logic)
4. Record analysis results via `hil-dag record` MCP tool (existing)
5. Synthesize recommendations (existing)
6. **Determine advance action** based on results:
   - If gate verdict `ready` → assemble milestone + freeze pass → return `completion`
   - If gate verdict `needs-revision` → freeze pass via `hil-dag freeze` → return `new_pass`
   - If gate verdict `critical-gaps` → return `escalate` (Supervisor presents to user)
   - If more nodes needed → auto-select top recommendation → assemble via `hil-dag assemble` → return next `dispatch`
7. Return combined output

**Output** (example: needs-revision flow):
```json
{
  "parse": {
    "node_id": "advocate-review",
    "status": "completed",
    "verdict": "needs-revision",
    "summary": "Advocate found 3 gaps: 2 knowledge, 1 preference.",
    "gaps_found": [...]
  },
  "advance": {
    "action_taken": "freeze_and_new_pass",
    "pass_frozen": true,
    "next_pass": 2
  }
}
```

**Output** (example: continue with next node):
```json
{
  "parse": {
    "node_id": "analyst-review",
    "status": "completed",
    "summary": "Analyst produced spec with 8 user stories."
  },
  "advance": {
    "action_taken": "assemble_next",
    "selected": {"intent": "...", "capability_tags": ["..."]},
    "alternatives": [...],
    "assembled": {"node_id": "advocate-review", "status": "valid"},
    "dispatch": {
      "dispatch_mode": "agent",
      "agent_type": "humaninloop:devils-advocate",
      "agent_prompt": "Read your instructions from: ..."
    }
  }
}
```

#### 3. `update-and-advance`

Replaces: `update-status` + (next `assemble-and-prepare`)

For supervisor-owned nodes (decisions, deterministic gates, milestones). After the Supervisor handles its part (e.g., collecting user input), it tells the State Analyst to update the node and advance.

**Input** (decision node — Supervisor collected answers):
```json
{
  "action": "update-and-advance",
  "node_id": "human-clarification",
  "dag_path": "...",
  "catalog_path": "...",
  "feature_dir": "...",
  "pass_number": 1,
  "status": "decided",
  "answers": {"Q1": "Option A"}
}
```

**Input** (deterministic gate — Analyst evaluates autonomously):
```json
{
  "action": "update-and-advance",
  "node_id": "constitution-gate",
  "dag_path": "...",
  "catalog_path": "...",
  "feature_dir": "...",
  "pass_number": 1
}
```

**Process**:
1. For deterministic gates: evaluate condition (file existence, frontmatter check, etc.)
2. For decisions: write answers to artifact path
3. For milestones: verify prerequisites complete
4. Update status via `hil-dag status` MCP tool
5. Synthesize recommendations for next step
6. Auto-select and assemble next node (if applicable)
7. Return combined output

**Output**: Same structure as `parse-and-advance` — `update` results + `advance` with next dispatch.

#### 4. `re-brief`

Replaces: `briefing` (on-demand, without auto-assembly)

Used when Supervisor overrides the auto-selected recommendation or needs a fresh briefing mid-pass.

**Input**:
```json
{
  "action": "re-brief",
  "workflow": "specify",
  "feature_id": "001-user-auth",
  "pass_number": 2,
  "dag_path": "...",
  "catalog_path": "...",
  "feature_dir": "...",
  "override_recommendation": {
    "intent": "Collect user preference on notification defaults",
    "capability_tags": ["user-clarification"]
  }
}
```

**Process**:
1. Produce full briefing (same as brief-and-assemble step 1-2)
2. If `override_recommendation` provided: assemble that instead of top-ranked
3. If no override: return briefing only (Supervisor picks manually)

**Output**: Same as `brief-and-assemble`, but with the override applied.

---

## Phase 2: Rewrite State Analyst Agent

**File**: `plugins/humaninloop/agents/state-analyst.md`

### 2.1 Update Frontmatter

```yaml
---
name: state-analyst
description: |
  Produces decision-ready briefings, manages DAG graph mechanics, and advances workflow state.
  Combines strategic analysis (briefings, report parsing, recommendations) with graph operations
  (node assembly, pass freezing, status updates). The Supervisor delegates all DAG operations
  and state analysis to this single agent.

  <example>
  Context: Supervisor needs a briefing and first node assembled at start of pass
  user: '{"action": "brief-and-assemble", "workflow": "specify", ...}'
  assistant: "I'll read the DAG, catalog, and strategy skills to produce a briefing,
  auto-select the top recommendation, assemble the node via hil-dag, construct the
  domain agent prompt, and return the combined result."
  </example>

  <example>
  Context: Domain agent finished; Supervisor needs results parsed and next node assembled
  user: '{"action": "parse-and-advance", "node_id": "analyst-review", ...}'
  assistant: "I'll read the analyst's report, extract structured data, record via hil-dag,
  determine the next action, assemble the next node, and return the dispatch prompt."
  </example>

  <example>
  Context: Supervisor collected user input for a decision node
  user: '{"action": "update-and-advance", "node_id": "human-clarification", "status": "decided", "answers": {...}}'
  assistant: "I'll write the answers to the artifact path, update the node status via hil-dag,
  and assemble the next recommended node."
  </example>
model: opus
color: cyan
mcpServers:
  - hil-dag
skills:
  - strategy-core
  - strategy-specification
  - strategy-implementation
---
```

### 2.2 Merge Prompt Content

**Structure of new State Analyst prompt** (target: under 600 lines):

```
# State Analyst

## Role
[Combined role description — strategic analysis + graph mechanics]

## Actions
### brief-and-assemble
[Input/Process/Output — from Phase 1 design]

### parse-and-advance
[Input/Process/Output — from Phase 1 design]

### update-and-advance
[Input/Process/Output — from Phase 1 design]

### re-brief
[Input/Process/Output — from Phase 1 design]

## Recommendation Structure
[Keep existing — shared across all actions]

## Evidence Construction
[Keep existing from current State Analyst]

## Trace Entry Construction
[Keep existing from current State Analyst]

## Report Parsing Patterns
[Keep existing from current State Analyst]

## NL Prompt Construction Patterns
[Absorb from DAG Assembler — all node-type templates]

## Artifact Path Convention
[Keep ONE copy — deduplicated from both agents]

## Operational Rules
[Merge both agents' rules, deduplicated]

## Tool Usage (CRITICAL)
[Merge both agents' tool usage — now includes ALL hil-dag tools]

## Skill Boundary
[Remove — no longer applies since agent uses all tools]

## Error Protocol
[Merge both agents' error protocols]
```

### 2.3 Sections to Absorb from DAG Assembler

| DAG Assembler Section | Destination in State Analyst | Notes |
|---|---|---|
| NL Prompt Construction Patterns (all 12 patterns) | New "NL Prompt Construction Patterns" section | Verbatim — these templates are well-tested |
| Dispatch modes table | Inline in `brief-and-assemble` and `parse-and-advance` output docs | Simplify — State Analyst now constructs these directly |
| Invariant auto-resolution logic | Inline in assembly steps | Brief description — MCP tool handles the mechanics |
| Operational Rules | Merge into State Analyst Operational Rules | Deduplicate rules that overlap |
| Error Protocol (assembly-specific) | Merge into State Analyst Error Protocol | Add assembly error cases |

### 2.4 Sections to Remove/Simplify

| Section | Action | Rationale |
|---|---|---|
| "Skill Boundary" (current State Analyst) | Remove | Agent now uses all hil-dag tools, not just `record` |
| Duplicate "Artifact Path Convention" | Keep one copy | Currently duplicated verbatim across both agents |
| Duplicate "Tool Usage (CRITICAL)" | Merge into one | Both agents had nearly identical tool usage rules |
| `assembler_response` forwarding language | Remove | No longer passing opaque objects between agents |

### 2.5 Line Budget

| Section | Estimated Lines |
|---|---|
| Frontmatter + Role | 50 |
| Actions (4 actions with I/O contracts) | 200 |
| Recommendation Structure | 30 |
| Evidence + Trace Construction | 50 |
| Report Parsing Patterns | 60 |
| NL Prompt Construction Patterns | 120 |
| Artifact Path Convention | 30 |
| Operational Rules | 20 |
| Tool Usage | 15 |
| Error Protocol | 25 |
| **Total** | **~600** |

---

## Phase 3: Update Supervisor Commands

Both `specify.md` and `implement.md` need the same structural changes.

### 3.1 Changes to `specify.md`

#### Replace "Three Outbound Verbs" with "Two Outbound Verbs"

**Before**:
```markdown
| Verb | Target | Actions |
|------|--------|---------|
| **Ask the Analyst** | `humaninloop:state-analyst` | `briefing`, `parse-and-recommend` |
| **Tell the Assembler** | `humaninloop:dag-assembler` | `assemble-and-prepare`, `freeze-pass`, `update-status` |
| **Dispatch the agent** | Domain agent / Skill | Execute with NL prompt from Assembler |
```

**After**:
```markdown
| Verb | Target | Actions |
|------|--------|---------|
| **Ask the Analyst** | `humaninloop:state-analyst` | `brief-and-assemble`, `parse-and-advance`, `update-and-advance`, `re-brief` |
| **Dispatch the agent** | Domain agent / Skill | Execute with NL prompt from Analyst |
```

#### Replace Supervisor Loop

**Before** (6-step Pick → Assemble → Execute → Parse):
```
1. Briefing → State Analyst
2. Pick recommendation
3. Assemble → DAG Assembler
4. Dispatch domain agent
5. Parse → State Analyst
6. Route (freeze → DAG Assembler if needed)
```

**After** (2-step happy path):
```
START OF PASS:
  1. State Analyst.brief-and-assemble()
     → Returns: briefing + auto-selected recommendation + assembled prompt
     → If Supervisor disagrees: State Analyst.re-brief(override_recommendation)

PER NODE LOOP:
  2. Dispatch domain agent with prompt from Analyst
  3. State Analyst.parse-and-advance()
     → Returns: parse results + next action:
       - "assemble_next": loop back to step 2 with new prompt
       - "freeze_and_new_pass": go to START OF PASS
       - "completion": go to Completion
       - "escalate": present to user
       - "supervisor_owned": Supervisor handles, then update-and-advance
```

#### Simplify Lifecycle Rules

Rules 1-2 (gate verdicts) no longer require the Supervisor to orchestrate freeze separately — the State Analyst handles freeze inside `parse-and-advance`. Simplify to:

```markdown
**Rule 1 — `parse-and-advance` returns `freeze_and_new_pass`**: New pass needed.
Return to Start of Every Pass.

**Rule 2 — `parse-and-advance` returns `completion`**: Go to Completion.

**Rule 3 — `parse-and-advance` returns `escalate`**: Present to user with options.

**Rule 4 — `parse-and-advance` returns `supervisor_owned`**: Handle the action
(collect input via AskUserQuestion), then State Analyst.update-and-advance(answers).

**Rule 5 — Convergence stall** (from briefing.outcome_trajectory): Surface to user.

**Rule 6 — 5 passes reached** (from briefing.pass_context): Surface to user.

**Rule 7 — Unexpected situation**: State Analyst.parse-and-advance() returns
appropriate error. Present to user.
```

#### Update Responsibility Boundaries Table

Remove all DAG Assembler rows. Merge into State Analyst:

```markdown
| Operation | Owner | Mechanism |
|-----------|-------|-----------|
| Override recommendation | Supervisor | `re-brief` with override |
| Dispatch domain agents | Supervisor | Task tool with prompt from Analyst |
| Collect human input | Supervisor | `AskUserQuestion` |
| Watch convergence | Supervisor | `outcome_trajectory` from Analyst |
| Briefings + assembly | State Analyst | `brief-and-assemble` |
| Report parsing + advance | State Analyst | `parse-and-advance` |
| Status updates + advance | State Analyst | `update-and-advance` |
| Pass freezing | State Analyst | Inside `parse-and-advance` |
| Prompt construction | State Analyst | Inside assembly steps |
| Graph invariant validation | State Analyst | Via `hil-dag` MCP tools |
```

#### Update Context Protection

Remove references to DAG Assembler:
```markdown
- **NEVER call `hil-dag` directly** — zero CLI usage. All DAG operations go through
  the State Analyst's actions.
- **NEVER read domain agent reports directly** — all report content enters via
  `parse-and-advance`.
```

#### Update Initial Setup

Remove reference to DAG Assembler for constitution verification:
```markdown
The Supervisor delegates environment concerns to the State Analyst — constitution
verification is handled by invariant auto-resolution (INV-002 + `carry_forward`)
during assembly.
```

### 3.2 Changes to `implement.md`

Same structural changes as `specify.md` with these implement-specific adjustments:

- **Rule 8 (Cycle advancement)**: After `parse-and-advance` returns `freeze_and_new_pass`, the next `brief-and-assemble` identifies the next cycle from `tasks.md` (unchanged logic, just routed through Analyst)
- **Rule 9 (Fix pass routing)**: After `parse-and-advance` for final-validation returns `freeze_and_new_pass`, the next `brief-and-assemble` creates a fix pass (Analyst's strategy-implementation skill handles this)
- **Rule 10 (carry_forward)**: `tasks-complete` auto-resolution happens inside `brief-and-assemble` (transparent to Supervisor, same as before)

---

## Phase 4: Update Tests

**File**: `humaninloop_brain/tests/test_cli/test_spec_consistency.py`

### 4.1 Refactor `TestDAGAssemblerCatalogConsistency`

Rename to `TestStateAnalystAssemblyConsistency`. Update all references from `DAG_ASSEMBLER` path to `STATE_ANALYST` path:

```python
# Remove
DAG_ASSEMBLER = PLUGIN_ROOT / "agents" / "dag-assembler.md"

# Update class
class TestStateAnalystAssemblyConsistency:
    """State Analyst spec aligns with catalog contracts (assembly functions)."""

    @pytest.fixture
    def analyst_text(self) -> str:
        return STATE_ANALYST.read_text()

    def test_four_actions_documented(self, analyst_text):
        """State Analyst documents its 4 actions."""
        assert "brief-and-assemble" in analyst_text
        assert "parse-and-advance" in analyst_text
        assert "update-and-advance" in analyst_text
        assert "re-brief" in analyst_text

    def test_artifact_path_convention_covers_catalog(self, analyst_text, catalog):
        """Artifact path convention covers all catalog artifacts."""
        # Same logic, but reads from STATE_ANALYST instead of DAG_ASSEMBLER
        ...

    def test_all_agent_nodes_have_prompt_pattern(self, catalog, analyst_text):
        """Every catalog node with an agent has a NL prompt pattern in State Analyst."""
        # Moved from TestCrossAgentRoutingCoverage
        ...
```

### 4.2 Update `TestCrossAgentRoutingCoverage`

- Remove `assembler_text` fixture
- Move `test_all_agent_nodes_have_assembler_prompt_pattern` to `TestStateAnalystAssemblyConsistency` (renamed to `test_all_agent_nodes_have_prompt_pattern`)
- Move `test_skill_based_nodes_have_skill_reference` to `TestStateAnalystAssemblyConsistency`
- Keep `test_dispatch_modes_in_routing_table` (reads from `specify.md`)

### 4.3 Update `TestCatalogTemplateConsistency`

- Remove `assembler_text` fixture (no longer needed)

### 4.4 New Test: Verify DAG Assembler Agent Deleted

```python
def test_dag_assembler_removed():
    """DAG Assembler agent file should not exist after merge."""
    assert not (PLUGIN_ROOT / "agents" / "dag-assembler.md").exists()
```

---

## Phase 5: Update Plugin Manifest

**File**: `plugins/humaninloop/.claude-plugin/plugin.json`

Remove DAG Assembler from agents array:

```json
"agents": [
    "./agents/devils-advocate.md",
    "./agents/principal-architect.md",
    "./agents/requirements-analyst.md",
    "./agents/staff-engineer.md",
    "./agents/task-architect.md",
    "./agents/technical-analyst.md",
    "./agents/qa-engineer.md",
    "./agents/ui-designer.md",
    "./agents/state-analyst.md"
]
```

Agent count: 10 → 9.

---

## Phase 6: Documentation Updates

### 6.1 Must Update (structural references)

| File | Change |
|---|---|
| `README.md` | Update architecture diagram and agent table — remove DAG Assembler, show State Analyst with expanded role |
| `ROADMAP.md` | Change "three-agent architecture" to "two-agent architecture (Supervisor + State Analyst)" |
| `CHANGELOG.md` | Add entry for the merge under next release |
| `humaninloop_brain/README.md` | Update agent references — State Analyst is now sole MCP consumer agent |

### 6.2 Should Update (design context)

| File | Change |
|---|---|
| `docs/architecture/v3/v3-architecture-design.md` | Update "DAG Assembler" section to note it was absorbed into State Analyst |
| `docs/architecture/v3/state-analyst-dag-assembler-redesign-synthesis.md` | Add note that this design was superseded by the merge |
| `docs/architecture/v3/goal-oriented-supervisor-synthesis.md` | Update role descriptions |

### 6.3 No Change Needed (historical records)

These files document what was true at a point in time. Do NOT modify:

- `docs/architecture/dag-supervisor-design-synthesis.md` (pre-v3)
- `docs/architecture/dag-specialist-subagents-synthesis.md` (pre-v3)
- `docs/architecture/dag-specialist-subagents-v2-synthesis.md` (pre-v3)
- `docs/architecture/dag-json-schema-synthesis.md` (pre-v3)
- `docs/architecture/dag-infrastructure-buildout-synthesis.md` (pre-v3)
- `docs/architecture/dag-strategy-skills-synthesis.md` (pre-v3)
- `docs/architecture/dag-walkthrough-scenario1.md` (pre-v3)
- `docs/decisions/007-dag-first-infrastructure.md` (ADR — immutable)
- `docs/analysis-implement-dag-migration.md` (historical)
- `docs/analysis-mcp-server-migration.md` (historical)
- `docs/analysis-openspec-vs-humaninloop.md` (historical)

### 6.4 Codebase Analysis Memory

| File | Change |
|---|---|
| `.humaninloop/memory/codebase-analysis.md` | Update agents inventory — remove DAG Assembler |

---

## Phase 7: Delete DAG Assembler

**After all other phases complete and tests pass:**

```bash
git rm plugins/humaninloop/agents/dag-assembler.md
```

This must be the last step — the test in Phase 4.4 (`test_dag_assembler_removed`) should be added only after the file is deleted.

---

## Execution Order

```
Phase 1: Design actions        ← This document (done)
    │
Phase 2: Rewrite State Analyst ← Core work — new agent prompt
    │
Phase 3: Update Supervisors    ← specify.md + implement.md
    │                             (can start after Phase 2 actions are stable)
    │
Phase 4: Update Tests          ← Spec consistency tests
    │                             (can run in parallel with Phase 3)
    │
Phase 5: Update Manifest       ← plugin.json (trivial, do with Phase 7)
    │
Phase 6: Documentation         ← README, ROADMAP, CHANGELOG, etc.
    │                             (can run in parallel with Phase 3-4)
    │
Phase 7: Delete DAG Assembler  ← Last step, after all tests pass
```

**Critical path**: Phase 2 → Phase 3 → Phase 7

**Parallelizable**: Phases 4, 5, 6 can run in parallel with Phase 3 once Phase 2 is stable.

---

## Validation Checklist

- [ ] State Analyst agent has 4 documented actions: `brief-and-assemble`, `parse-and-advance`, `update-and-advance`, `re-brief`
- [ ] State Analyst frontmatter lists all `hil-dag` MCP tools (previously split between two agents)
- [ ] State Analyst contains all 12 NL Prompt Construction Patterns (from DAG Assembler)
- [ ] State Analyst contains single Artifact Path Convention table (deduplicated)
- [ ] State Analyst prompt is under 600 lines
- [ ] `specify.md` has "Two Outbound Verbs" (not three)
- [ ] `specify.md` Supervisor Loop uses 2-call happy path
- [ ] `implement.md` has matching structural changes
- [ ] `plugin.json` agents array has 9 entries (not 10)
- [ ] `dag-assembler.md` file is deleted
- [ ] All spec consistency tests pass: `cd humaninloop_brain && uv run pytest tests/test_cli/test_spec_consistency.py -v`
- [ ] Full test suite passes: `cd humaninloop_brain && uv run pytest --tb=short`
- [ ] No remaining references to "DAG Assembler" in active code (agents, commands, manifest) — only in historical docs and changelog
