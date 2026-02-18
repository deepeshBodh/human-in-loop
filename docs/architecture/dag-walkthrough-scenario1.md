# DAG Walkthrough: Scenario 1 — Skip Enrichment

Hand-simulated end-to-end trace validating the DAG Supervisor protocol before real execution.

**Scenario**: User provides detailed input with clear Who/Problem/Value. Enrichment is unnecessary. Expected path: `constitution-gate` -> `analyst-review` -> `advocate-review` -> `spec-complete`.

**Input**: `"Add dark mode — health-conscious developers need low-light UI for eye strain reduction during extended coding sessions"`

---

## Pre-Loop: Initial Setup

### Setup Step 1: Constitution Check

Supervisor checks `.humaninloop/memory/constitution.md` — file exists. Continue.

### Setup Step 2: Create Feature Directory

```bash
${CLAUDE_PLUGIN_ROOT}/scripts/create-new-feature.sh --json "Add dark mode for eye strain reduction"
```

**Output**:
```json
{"BRANCH_NAME": "042-dark-mode", "SPEC_FILE": "specs/042-dark-mode/spec.md", "FEATURE_NUM": "042"}
```

`feature_dir = "specs/042-dark-mode"`

### Setup Step 3: Initialize Workflow Structure

```bash
mkdir -p specs/042-dark-mode/.workflow/dags
```

- Write `specs/042-dark-mode/.workflow/context.md` from template
- Write `specs/042-dark-mode/spec.md` from template

### Setup Step 4: Create First DAG Pass

Supervisor invokes DAG Assembler to create the DAG file:

```
dag-create.sh specify 1 specs/042-dark-mode/.workflow/dags/pass-001.json
```

---

## Pass 1

### Step 1: Request Briefing

**Supervisor -> State Briefer**:
```json
{
  "request": "briefing",
  "workflow": "specify",
  "feature_id": "042-dark-mode",
  "pass_number": 1,
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "strategy_skills": ["strategy-core", "strategy-specification"],
  "dag_history_path": "specs/042-dark-mode/.workflow/dags/",
  "artifacts_dir": "specs/042-dark-mode/"
}
```

**State Briefer reads**:
- `specify-catalog.json` — 7 nodes, 5 invariants
- `strategy-core/SKILL.md` — validation, gap classification, pass evolution, halt escalation
- `strategy-specification/SKILL.md` — input assessment, produce-then-validate, guardrails
- `specs/042-dark-mode/` — checks for existing artifacts (only template spec.md and context.md exist)
- No DAG history (pass 1)

**State Briefer -> Supervisor**:
```json
{
  "state_summary": "Pass 1. No prior history. User input has clear Who (health-conscious developers), Problem (eye strain during extended coding), and Value (reduced eye fatigue). Raw input and constitution available.",

  "available_artifacts": [
    {"artifact": "spec.md", "source": "template (empty)", "status": "template"},
    {"artifact": "constitution.md", "source": "system", "status": "available"},
    {"artifact": "raw-input", "source": "user", "status": "available"}
  ],

  "gap_details": [],

  "viable_nodes": [
    {
      "id": "constitution-gate",
      "type": "gate",
      "agent": null,
      "contract": {"consumes": ["constitution.md"], "produces": []},
      "reason": "Constitution exists — gate should pass. Required before task nodes (INV-002)."
    },
    {
      "id": "input-enrichment",
      "type": "task",
      "agent": null,
      "skill": "analysis-iterative",
      "contract": {"consumes": ["raw-input"], "produces": ["enriched-input"]},
      "reason": "Available but input already has Who/Problem/Value."
    },
    {
      "id": "analyst-review",
      "type": "task",
      "agent": "requirements-analyst",
      "contract": {"consumes": ["enriched-input?", "raw-input?", "constitution.md"], "produces": ["spec.md", "analyst-report.md"]},
      "reason": "Available after constitution-gate passes. Can use raw-input directly."
    }
  ],

  "relevant_patterns": [
    "Detailed input with clear Who/Problem/Value can go directly to the analyst — enrichment may be unnecessary",
    "Constitution must exist before specification task nodes execute (INV-002)",
    "Every agent output should pass through a gate before milestone achievement"
  ],

  "relevant_anti_patterns": [
    "Don't skip the advocate gate even when analyst output looks comprehensive"
  ],

  "pass_context": "Pass 1 of 5 max. First pass — establishing structure."
}
```

### Step 2: Assembly Decision (constitution-gate)

Supervisor reads briefing. Relevant pattern: "Constitution must exist before specification task nodes execute (INV-002)." Selects `constitution-gate` as first node.

### Step 3: Assemble and Prepare (constitution-gate)

**Supervisor -> DAG Assembler**:
```json
{
  "action": "assemble-and-prepare",
  "next_node": "constitution-gate",
  "dag_path": "specs/042-dark-mode/.workflow/dags/pass-001.json",
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "feature_dir": "specs/042-dark-mode",
  "parameters": {}
}
```

**DAG Assembler process**:
1. Reads catalog: `constitution-gate` is type `gate`, agent `null`, consumes `constitution.md`
2. Runs `dag-assemble.sh pass-001.json catalog.json constitution-gate`
3. Runs `dag-validate.sh pass-001.json catalog.json` — valid
4. No agent — returns gate check details

**DAG Assembler -> Supervisor**:
```json
{
  "status": "valid",
  "node_added": {"id": "constitution-gate", "type": "gate", "status": "pending"},
  "edges_inferred": 0,
  "gate_type": "file-check",
  "check_path": ".humaninloop/memory/constitution.md",
  "check_description": "Verify project constitution exists"
}
```

### Step 4: Execute Node (constitution-gate)

Supervisor checks directly: `.humaninloop/memory/constitution.md` exists. Gate passes.

Updates node status via DAG Assembler: `dag-status.sh pass-001.json constitution-gate passed`

### Step 5: Parse Report (constitution-gate)

No report to parse — gate with no agent. Supervisor notes gate passed and moves on.

### Step 2 (again): Assembly Decision (analyst-review)

Supervisor decides: input has Who/Problem/Value (from briefing pattern). Skip enrichment. Select `analyst-review`.

**Key flexibility demonstrated**: Enrichment node NOT assembled. The Supervisor made a context-aware decision to skip it.

### Step 3: Assemble and Prepare (analyst-review)

**Supervisor -> DAG Assembler**:
```json
{
  "action": "assemble-and-prepare",
  "next_node": "analyst-review",
  "dag_path": "specs/042-dark-mode/.workflow/dags/pass-001.json",
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "feature_dir": "specs/042-dark-mode",
  "parameters": {
    "context": "First pass — create specification from detailed user input about dark mode for eye strain reduction"
  }
}
```

**DAG Assembler process**:
1. Reads catalog: `analyst-review` is type `task`, agent `requirements-analyst`
2. Infers edges: `constitution-gate` -> `analyst-review` (depends-on, since constitution-gate already in DAG)
3. Runs `dag-assemble.sh` and `dag-validate.sh` — valid
4. Updates `context.md` supervisor_instructions section:
   ```
   Create a feature specification based on the user input above.

   **Read**:
   - Spec template: ${CLAUDE_PLUGIN_ROOT}/templates/spec-template.md

   **Write**:
   - Spec: specs/042-dark-mode/spec.md
   - Report: specs/042-dark-mode/.workflow/analyst-report.md

   **Report format**: Follow ${CLAUDE_PLUGIN_ROOT}/templates/analyst-report-template.md
   ```

**DAG Assembler -> Supervisor**:
```json
{
  "status": "valid",
  "node_added": {"id": "analyst-review", "type": "task", "status": "pending"},
  "edges_inferred": 1,
  "agent_prompt": "Read your instructions from: specs/042-dark-mode/.workflow/context.md",
  "agent_type": "humaninloop:requirements-analyst"
}
```

### Step 4: Execute Node (analyst-review)

**Supervisor spawns domain agent**:
```
Task(
  subagent_type: "humaninloop:requirements-analyst",
  prompt: "Read your instructions from: specs/042-dark-mode/.workflow/context.md",
  description: "Write feature specification"
)
```

**Domain agent** (requirements-analyst):
- Reads `context.md` — gets user input, project context, file paths, supervisor instructions
- Reads spec template
- Writes `specs/042-dark-mode/spec.md` with user stories, functional requirements, edge cases
- Writes `specs/042-dark-mode/.workflow/analyst-report.md` with "What I Created", "Summary", "Assumptions Made"
- Returns brief status: "Completed. Spec written with 5 user stories and 12 functional requirements."

### Step 5: Parse Report (analyst-review)

**Supervisor -> DAG Assembler**:
```json
{
  "action": "parse-report",
  "node_id": "analyst-review",
  "dag_path": "specs/042-dark-mode/.workflow/dags/pass-001.json",
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "feature_dir": "specs/042-dark-mode"
}
```

**DAG Assembler process**:
1. Reads catalog contract: `analyst-review` produces `spec.md` and `analyst-report.md`
2. Verifies both exist on disk — confirmed
3. Reads `analyst-report.md` from disk
4. Extracts: 5 user stories, 12 functional requirements, 3 assumptions made
5. Updates node status: `dag-status.sh pass-001.json analyst-review completed`

**DAG Assembler -> Supervisor**:
```json
{
  "node_id": "analyst-review",
  "status": "completed",
  "summary": "Created spec with 5 user stories and 12 functional requirements. 3 assumptions made about color palette preferences, system-level OS integration, and transition animation timing.",
  "artifacts_produced": ["spec.md", "analyst-report.md"],
  "verdict": null,
  "gaps_addressed": []
}
```

### Step 2 (again): Assembly Decision (advocate-review)

Supervisor follows produce-then-validate pattern: analyst produced, now advocate validates. Selects `advocate-review`.

### Step 3: Assemble and Prepare (advocate-review)

**Supervisor -> DAG Assembler**:
```json
{
  "action": "assemble-and-prepare",
  "next_node": "advocate-review",
  "dag_path": "specs/042-dark-mode/.workflow/dags/pass-001.json",
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "feature_dir": "specs/042-dark-mode",
  "parameters": {}
}
```

**DAG Assembler process**:
1. Reads catalog: `advocate-review` is type `gate`, agent `devils-advocate`
2. Infers edges: `analyst-review` -> `advocate-review` (validates edge, since advocate consumes spec.md produced by analyst)
3. Runs `dag-assemble.sh` and `dag-validate.sh` — valid
4. Updates `context.md` supervisor_instructions section:
   ```
   Review the specification and find gaps.

   **Read**:
   - Spec: specs/042-dark-mode/spec.md
   - Analyst report: specs/042-dark-mode/.workflow/analyst-report.md

   **Write**:
   - Report: specs/042-dark-mode/.workflow/advocate-report.md

   **Report format**: Follow ${CLAUDE_PLUGIN_ROOT}/templates/advocate-report-template.md
   ```

**DAG Assembler -> Supervisor**:
```json
{
  "status": "valid",
  "node_added": {"id": "advocate-review", "type": "gate", "status": "pending"},
  "edges_inferred": 1,
  "agent_prompt": "Read your instructions from: specs/042-dark-mode/.workflow/context.md",
  "agent_type": "humaninloop:devils-advocate"
}
```

### Step 4: Execute Node (advocate-review)

**Supervisor spawns domain agent**:
```
Task(
  subagent_type: "humaninloop:devils-advocate",
  prompt: "Read your instructions from: specs/042-dark-mode/.workflow/context.md",
  description: "Validate specification"
)
```

**Domain agent** (devils-advocate):
- Reads `context.md` — gets spec path, analyst report path, supervisor instructions
- Reads `spec.md` and `analyst-report.md`
- Reviews for gaps, edge cases, contradictions
- Writes `specs/042-dark-mode/.workflow/advocate-report.md` with verdict, gaps, clarifications
- Returns brief status: "Review complete. Verdict: ready."

### Step 5: Parse Report (advocate-review)

**Supervisor -> DAG Assembler**:
```json
{
  "action": "parse-report",
  "node_id": "advocate-review",
  "dag_path": "specs/042-dark-mode/.workflow/dags/pass-001.json",
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "feature_dir": "specs/042-dark-mode"
}
```

**DAG Assembler process**:
1. Reads catalog contract: `advocate-review` produces `advocate-report.md`
2. Verifies file exists on disk — confirmed
3. Reads `advocate-report.md` from disk
4. Extracts verdict: `ready`
5. Updates node status: `dag-status.sh pass-001.json advocate-review passed`

**DAG Assembler -> Supervisor**:
```json
{
  "node_id": "advocate-review",
  "status": "completed",
  "summary": "Advocate approved specification. Minor suggestions noted but no blocking gaps.",
  "artifacts_produced": ["advocate-report.md"],
  "verdict": "ready",
  "gaps_found": []
}
```

### Step 6: Evaluate

Verdict is `ready`. Supervisor proceeds to assemble milestone and freeze pass.

### Assemble spec-complete Milestone

**Supervisor -> DAG Assembler**:
```json
{
  "action": "assemble-and-prepare",
  "next_node": "spec-complete",
  "dag_path": "specs/042-dark-mode/.workflow/dags/pass-001.json",
  "catalog_path": "${CLAUDE_PLUGIN_ROOT}/catalogs/specify-catalog.json",
  "feature_dir": "specs/042-dark-mode",
  "parameters": {}
}
```

**DAG Assembler -> Supervisor**:
```json
{
  "status": "valid",
  "node_added": {"id": "spec-complete", "type": "milestone", "status": "pending"},
  "edges_inferred": 2,
  "milestone_type": "completion",
  "required_artifacts": ["spec.md", "advocate-report.md"]
}
```

Supervisor verifies both artifacts exist. Marks milestone achieved.

### Freeze Pass

**Supervisor -> DAG Assembler**:
```json
{
  "action": "freeze-pass",
  "dag_path": "specs/042-dark-mode/.workflow/dags/pass-001.json",
  "outcome": "completed",
  "outcome_detail": "advocate-verdict-ready",
  "rationale": "Advocate approved specification. Milestone achieved."
}
```

**DAG Assembler -> Supervisor**:
```json
{
  "pass_frozen": true,
  "dag_path": "specs/042-dark-mode/.workflow/dags/pass-001.json",
  "outcome": "completed",
  "outcome_detail": "advocate-verdict-ready",
  "nodes_executed": 4,
  "edges_total": 3
}
```

---

## Completion

Supervisor outputs:

```markdown
## Specification Complete

**Feature**: 042-dark-mode
**Passes**: 1
**Final Verdict**: ready

### Files Created
- Spec: `specs/042-dark-mode/spec.md`
- Workflow: `specs/042-dark-mode/.workflow/`
- DAG history: `specs/042-dark-mode/.workflow/dags/`

### Summary
5 user stories, 12 functional requirements

### Next Steps
1. Review the spec at `specs/042-dark-mode/spec.md`
2. Run `/humaninloop:plan` to create implementation plan
```

---

## Call Count Summary

| Step | Agent | Call Type |
|------|-------|-----------|
| 1 | State Briefer | Briefing request |
| 2 | DAG Assembler | assemble-and-prepare (constitution-gate) |
| 3 | DAG Assembler | assemble-and-prepare (analyst-review) |
| 4 | Requirements Analyst | Domain agent execution |
| 5 | DAG Assembler | parse-report (analyst-review) |
| 6 | DAG Assembler | assemble-and-prepare (advocate-review) |
| 7 | Devil's Advocate | Domain agent execution |
| 8 | DAG Assembler | parse-report (advocate-review) |
| 9 | DAG Assembler | assemble-and-prepare (spec-complete) |
| 10 | DAG Assembler | freeze-pass |

**Totals**: 1 State Briefer + 7 DAG Assembler + 2 domain agents = **10 subagent calls**

**Supervisor decisions**: 4 (select constitution-gate, select analyst-review, select advocate-review, evaluate verdict -> done)

---

## Flexibility Demonstrated

1. **Enrichment skipped**: The `input-enrichment` node was listed as viable but NOT assembled. The Supervisor made a context-aware decision based on the briefing pattern "Detailed input with clear Who/Problem/Value can go directly to the analyst."

2. **Constitution gate present**: INV-002 satisfied by assembling `constitution-gate` before task nodes.

3. **Edges auto-inferred**: The DAG Assembler inferred `constitution-gate` -> `analyst-review` and `analyst-review` -> `advocate-review` edges from contract matching — the Supervisor never specified edges.

4. **Context protected**: Full spec.md and reports stayed on disk. Supervisor only received structured summaries (verdict, metrics, gap lists).
