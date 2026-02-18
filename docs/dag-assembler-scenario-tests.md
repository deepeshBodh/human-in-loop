# DAG Assembler Scenario Tests

> Last run: 2026-02-18 | Branch: `feat/dag-first-infrastructure` | All 191 unit tests passing

## Overview

Scenario tests validating the `dag-assembler` agent specification against the `hil-dag` CLI infrastructure. Tests cover all three agent actions (`assemble-and-prepare`, `parse-report`, `freeze-pass`), all four node types, error paths, invariant enforcement, and spec consistency.

Two test runs performed:
- **Run 1**: Initial CLI validation (scenarios 1–7h). Found and fixed findings 1–4.
- **Run 2**: Comprehensive 4-suite parallel test (topology, errors, spec-CLI consistency, internal consistency). Found and fixed findings 5–12.

## Test Matrix

### Run 1: CLI Validation

| # | Scenario | Action | Node Type | Result | Finding |
|---|----------|--------|-----------|--------|---------|
| 1 | Happy path: 3-node DAG assembly | assemble-and-prepare | task + gate | PASS | -- |
| 2 | Skill-based node (input-enrichment) | assemble-and-prepare | task (agent: null) | PASS | -- |
| 3 | No-agent gate (constitution-gate) | assemble-and-prepare | gate (agent: null) | PASS | -- |
| 4 | Status update with type validation | parse-report (CLI layer) | gate | PASS (after fix) | Finding 3 |
| 5 | Invariant violation (INV-002) | assemble-and-prepare | task | PASS | Finding 2 |
| 6 | Freeze pass + immutability | freeze-pass | -- | PASS | -- |
| 7a | Status update on non-existent node | parse-report (CLI layer) | -- | PASS (exit 1) | -- |
| 7b | Assemble non-existent catalog node | assemble-and-prepare | -- | PASS (exit 1) | -- |
| 7c | Validate with missing catalog file | assemble-and-prepare | -- | PASS (exit 2) | -- |
| 7d | Assemble duplicate node | assemble-and-prepare | gate | PASS (exit 1) | -- |
| 7e | Duplicate node idempotency | assemble-and-prepare | gate | PASS (exit 1) | -- |
| 7f | Cycle detection (invalid-cycle fixture) | validate | -- | PASS (exit 1) | -- |
| 7g | Unsatisfied contract (invalid-contract fixture) | validate | -- | PASS (exit 1) | -- |
| 7h | Invalid edge source (invalid-endpoint fixture) | validate | -- | PASS (exit 1) | -- |

### Run 2, Suite A: CLI Topology + Node Types

| # | Scenario | Result | Notes |
|---|----------|--------|-------|
| A1 | Full 7-node assembly | PASS | 6/7 nodes added; spec-complete correctly rejected by INV-001 |
| A2 | Decision node (human-clarification) | PASS | Assembled, status `decided` accepted |
| A3 | Milestone node (spec-complete) | PARTIAL | Blocked by INV-001; pivoted to status validation |
| A3b | Status type enforcement (all 4 types) | PASS | Invalid statuses rejected with type-specific errors |
| A4 | Multi-pass lifecycle | PASS | Freeze, multi-pass, order-dependent assembly all correct |
| A5 | Catalog validation | PASS | All 6 checks pass (unique IDs + 5 edge constraint types) |

### Run 2, Suite B: CLI Errors + Invariants

| # | Scenario | Result | Notes |
|---|----------|--------|-------|
| B1 | INV-001: task → gate → milestone | PASS | Rollback confirmed (2 nodes after rejected 3rd) |
| B2 | INV-002: constitution gate required | PASS | Rollback confirmed (0 nodes) |
| B3 | INV-003: validates edge source type | PASS | Exit 1, correct error |
| B4 | INV-005: cycle detection | PASS | Exit 1, correct error |
| B5 | Contract violation | PASS | Exit 1, unsatisfied artifact |
| B6 | Status type enforcement (8 valid + 5 invalid) | PASS | All type-specific validations correct |
| B7 | Frozen pass mutations (assemble, status, freeze) | PASS | All 3 mutation vectors blocked |
| B8 | Duplicate node assembly | PASS | Rejected, DAG integrity preserved |
| B9 | Non-existent node (assemble + status) | PASS | Distinct errors for catalog vs DAG lookup |
| B10 | Missing catalog file | PASS | Exit 2 (system error) |

### Run 2, Suite C: Spec-CLI Consistency Audit

| # | Item | Verdict | Finding |
|---|------|---------|---------|
| C1 | `cmd_assemble` output: `node_added` format | MISMATCH → Fixed | Finding 7 |
| C2 | `cmd_freeze` output: missing counts/path | MISMATCH → Fixed | Finding 8 |
| C3 | `parse-report` is agent-side, no CLI command | MISMATCH → Fixed | Finding 11 |
| C4 | CLI output lacks agent_prompt/agent_type | MISMATCH → Fixed | Finding 11 |
| C5 | CLI `validation` sub-object undocumented | MISMATCH → Fixed | Finding 11 |
| C6 | Error formats | MATCH | -- |
| C7 | Shell script delegation | MATCH | -- |
| C8 | Shell script argument patterns | MATCH | -- |
| C9 | Transactional rollback | MATCH | -- |

### Run 2, Suite D: Spec Internal Consistency Audit

| # | Item | Verdict | Finding |
|---|------|---------|---------|
| D1 | analyst-review NL prompt vs catalog consumes | INCONSISTENT → Fixed | Finding 5 |
| D2 | Gate status mapping incomplete | INCONSISTENT → Fixed | Finding 6 |
| D3 | Artifact path convention: missing entries | INCONSISTENT → Fixed | Finding 9 |
| D4 | Extension mismatch: catalog vs convention table | INCONSISTENT → Fixed | Finding 9 |
| D5 | "Never modify source artifacts" rule scope | INCONSISTENT → Fixed | Finding 10 |
| D6 | Special cases table: built-in vs plugin agents | INCONSISTENT → Fixed | Finding 12 |
| D7-D25 | Remaining 19 internal consistency checks | CONSISTENT | -- |

## Scenario Details

### Scenario 1: Happy Path — 3-Node DAG Assembly

**Purpose**: Verify the full assemble-and-prepare flow with edge inference and validation.

**Steps**:
1. `hil-dag create` — create empty DAG pass
2. `hil-dag assemble ... --node constitution-gate` — add prerequisite gate (0 edges inferred)
3. `hil-dag assemble ... --node analyst-review` — add task node (0 edges inferred, no producer match yet)
4. `hil-dag assemble ... --node advocate-review` — add gate node (3 edges inferred: depends-on, produces, validates)
5. `hil-dag validate` — confirms valid
6. `hil-dag sort` — returns topological order

**Expected output from advocate-review assembly**:
```json
{
  "status": "valid",
  "node_added": {"id": "advocate-review", "type": "gate", "status": "pending"},
  "edges_inferred": 3,
  "validation": {"status": "valid", ...}
}
```

**Inferred edges**:
- `analyst-review → advocate-review` (depends-on) — advocate consumes spec.md produced by analyst
- `analyst-review → advocate-review` (produces) — artifact flow
- `advocate-review → analyst-review` (validates) — gate validates task

**Topological order**: `analyst-review → advocate-review → constitution-gate`

### Scenario 2: Skill-Based Node (input-enrichment)

**Purpose**: Verify assembly of a node with `agent: null` and `skill: analysis-iterative`.

**Steps**:
1. Create fresh DAG pass
2. `hil-dag assemble ... --node input-enrichment`

**Verified**:
- Node added with `agent: null` in DAG JSON
- The agent spec's "Special cases" table says this should return `skill_to_invoke` + `skill_args` instead of `agent_prompt`
- CLI layer handles this correctly (no agent field)

### Scenario 3: No-Agent Gate (constitution-gate)

**Purpose**: Verify assembly of a gate node without an agent (Supervisor checks directly).

**Steps**:
1. Create fresh DAG pass
2. `hil-dag assemble ... --node constitution-gate`

**Verified**:
- `type: "gate"`, `agent: null`
- Consumes `constitution.md` (system artifact)
- The agent spec says this should return `gate_type: "file-check"` + `check_path`

### Scenario 4: Status Update with Type Validation

**Purpose**: Verify that node status updates respect type-specific valid statuses.

**Steps**:
1. Attempt `dag-status.sh <dag> advocate-review completed` — **REJECTED**
2. Use `dag-status.sh <dag> analyst-review completed` — accepted (task node)
3. Use `dag-status.sh <dag> advocate-review passed` — accepted (gate node)

**Valid statuses by type**:

| Node Type | Valid Statuses |
|-----------|---------------|
| task | pending, in-progress, completed, skipped, halted |
| gate | pending, in-progress, passed, failed, needs-revision |
| decision | pending, decided |
| milestone | pending, achieved |

### Scenario 5: Invariant Violation (INV-002)

**Purpose**: Verify that assembling `analyst-review` without `constitution-gate` triggers INV-002.

**Steps**:
1. Create fresh DAG
2. `hil-dag assemble ... --node analyst-review` (no constitution-gate present)

**Result**:
```json
{
  "status": "invalid",
  "node_added": {"id": "analyst-review", "type": "task", "status": "pending"},
  "validation": {
    "checks": [{
      "check": "INV-002",
      "passed": false,
      "issues": ["Task 'analyst-review' consumes constitution.md but no constitution gate exists in the DAG"]
    }]
  }
}
```

**Post-fix behavior**: The invalid node is NOT persisted to disk (transactional rollback).

### Scenario 6: Freeze Pass + Immutability

**Purpose**: Verify pass freezing and subsequent mutation rejection.

**Steps**:
1. `hil-dag freeze <dag> --outcome completed --detail "..." --rationale "..."`
2. Verify `outcome`, `outcome_detail`, `completed_at`, `assembly_rationale` are set
3. Attempt `hil-dag assemble` on frozen DAG

**Freeze output**:
```json
{
  "status": "success",
  "pass_frozen": true,
  "dag_path": "specs/001-feature/.workflow/dags/pass-001.json",
  "outcome": "completed",
  "outcome_detail": "advocate-verdict-needs-revision",
  "nodes_executed": 3,
  "edges_total": 4
}
```

**Post-freeze mutation attempt**:
```json
{"status": "error", "message": "Cannot add nodes to a frozen pass"}
```

### Scenario 7a–h: Error Paths

All error paths produce structured JSON with appropriate exit codes.

| Sub | Input | Error Message | Exit |
|-----|-------|---------------|------|
| 7a | Status update on non-existent node | `Node 'nonexistent-node' not found` | 1 |
| 7b | Assemble non-existent catalog node | `Node 'nonexistent-node' not found in catalog` | 1 |
| 7c | Validate with missing catalog file | `[Errno 2] No such file or directory` | 2 |
| 7d | Assemble duplicate node | `Node 'constitution-gate' already exists in the DAG` | 1 |
| 7e | Duplicate again (idempotent rejection) | Same as 7d | 1 |
| 7f | Cycle in depends-on edges | `Cycle in depends-on edges: analyst-review -> advocate-review` | 1 |
| 7g | Required artifact not produced | `Node 'analyst-review' requires artifact 'enriched-input' but no node produces it` | 1 |
| 7h | Invalid edge source type | `Edge 'edge-prod-gate-analyst' (produces): source 'constitution-gate' is type 'gate' but allowed sources are ['task']` | 1 |

## Findings and Fixes

### Finding 1: Agent Not Loadable (Known — not fixed)

`humaninloop:dag-assembler` and `humaninloop:state-briefer` are not available as Task subagent types despite being listed in `plugin.json`. Expected behavior for new agents not yet loaded in the current session.

### Finding 2: Non-Atomic Assembly (Fixed — Run 1)

**Problem**: `hil-dag assemble` added nodes to the DAG before validating invariants. When validation failed, the invalid node was persisted to disk.

**Fix**: `cmd_assemble` in `cli/main.py` now only calls `save_pass()` when `result.valid` is true (transactional). A new test `test_assemble_rollback_on_invariant_violation` verifies the DAG on disk has zero nodes after a failed assembly.

**Files**: `humaninloop_brain/src/humaninloop_brain/cli/main.py`, `humaninloop_brain/tests/test_cli/test_main_unit.py`

### Finding 3: Status Type Mismatch in parse-report Spec (Fixed — Run 1)

**Problem**: Line 106 of `dag-assembler.md` hardcoded `completed` as the status for all node types. Gate nodes use `passed`/`failed`/`needs-revision`, not `completed`.

**Fix**: Updated the parse-report process step to document type-aware status values. Updated the output example from `"status": "completed"` to `"status": "passed"` for the `advocate-review` gate node.

**Files**: `plugins/humaninloop/agents/dag-assembler.md`

### Finding 4: Agent Name Ambiguity (Fixed — Run 1)

**Problem**: The `targeted-research` catalog entry had `agent: "exploration"`, but the actual built-in Task agent type is `Explore`. No `humaninloop:exploration` agent exists.

**Fix**: Renamed `"exploration"` to `"Explore"` across all catalog files, test fixtures, and agent specs.

**Files**: `plugins/humaninloop/catalogs/specify-catalog.json`, `humaninloop_brain/catalogs/specify-catalog.json`, `humaninloop_brain/tests/fixtures/specify-catalog.json`, `humaninloop_brain/tests/fixtures/pass-with-research.json`, `plugins/humaninloop/agents/dag-assembler.md`, `plugins/humaninloop/agents/state-briefer.md`

### Finding 5: analyst-review NL Prompt vs Catalog Contract (Fixed — Run 2, D1)

**Problem**: The analyst-review NL prompt pattern referenced `advocate-report.md` (not in catalog `consumes`) and omitted `constitution.md`, `enriched-input`, and `raw-input` (all in catalog `consumes`). The prompt was revision-pass-only with no first-pass variant.

**Fix**:
- Added `{"artifact": "advocate-report.md", "required": false, "note": "present on revision passes"}` to the analyst-review catalog `consumes` list (all 3 catalog copies).
- Rewrote the NL prompt pattern with first-pass/revision-pass conditionals, including all catalog-contracted artifacts conditionally.

**Files**: `plugins/humaninloop/catalogs/specify-catalog.json`, `humaninloop_brain/catalogs/specify-catalog.json`, `humaninloop_brain/tests/fixtures/specify-catalog.json`, `plugins/humaninloop/agents/dag-assembler.md`

### Finding 6: Gate Status Mapping Incomplete (Fixed — Run 2, D2)

**Problem**: The parse-report step 5 listed `gate → passed or needs-revision` — omitting `failed`. The `critical-gaps` verdict had no status mapping. The `constitution-gate` (which only allows `passed`/`failed`) was incorrectly implied to support `needs-revision`.

**Fix**: Replaced the single-line generic mapping with two explicit tables:
- **By node type**: task→`completed`, decision→`decided`, milestone→`achieved`
- **Gate verdict-to-status mapping**: `ready`/`pass`→`passed`, `needs-revision`→`needs-revision` (advocate only), `critical-gaps`/`fail`→`failed` (both gates)

**Files**: `plugins/humaninloop/agents/dag-assembler.md`

### Finding 7: `cmd_assemble` Output Format (Fixed — Run 2, C1)

**Problem**: CLI returned `"node_added": "input-enrichment"` (bare string). The agent spec expected `"node_added": {"id": "...", "type": "...", "status": "..."}` (object).

**Fix**: `cmd_assemble` now returns `node_added` as an object with `id`, `type` (from enum value), and `status` fields, using the `GraphNode` data already available from `add_node()`.

**Files**: `humaninloop_brain/src/humaninloop_brain/cli/main.py`, `humaninloop_brain/tests/test_cli/test_main_unit.py`, `humaninloop_brain/tests/test_cli/test_main.py`, `humaninloop_brain/tests/test_cli/test_e2e_scenario.py`

### Finding 8: `cmd_freeze` Missing Output Fields (Fixed — Run 2, C2)

**Problem**: CLI freeze output lacked `dag_path`, `nodes_executed`, and `edges_total` — fields the agent spec promised in the freeze-pass output.

**Fix**: `cmd_freeze` now includes `dag_path` (from args), `nodes_executed` (`len(dag.nodes)`), and `edges_total` (`len(dag.edges)`) in the output JSON.

**Files**: `humaninloop_brain/src/humaninloop_brain/cli/main.py`, `humaninloop_brain/tests/test_cli/test_main_unit.py`

### Finding 9: Artifact Path Convention Gaps (Fixed — Run 2, D3+D4)

**Problem**: The artifact path convention table was missing `constitution.md` and `raw-input`. The table used `.md`-suffixed names (e.g., `enriched-input.md`) while the catalog used extensionless logical names (e.g., `enriched-input`), creating an undocumented naming mismatch.

**Fix**:
- Added `raw-input` (`{feature_dir}/.workflow/raw-input.md`) and `constitution.md` (`.humaninloop/memory/constitution.md`) to the table.
- Renamed column from "Artifact" to "Catalog Name" showing exact catalog logical names.
- Added header note explaining the convention: catalog uses logical names, physical paths append `.md`.

**Files**: `plugins/humaninloop/agents/dag-assembler.md`

### Finding 10: Ambiguous "Never Modify" Rule (Fixed — Run 2, D5)

**Problem**: The operational rule "Never modify source artifacts (spec.md, reports)" was ambiguous — domain agents DO write to `spec.md` via the NL prompt instructions the DAG Assembler constructs.

**Fix**: Clarified scope: "The DAG Assembler never directly modifies source artifacts (spec.md, reports) — it only writes DAG JSON files and context.md. Domain agents, operating under their own instructions, write to source artifacts."

**Files**: `plugins/humaninloop/agents/dag-assembler.md`

### Finding 11: CLI/Agent Boundary Not Documented (Fixed — Run 2, C3+C4)

**Problem**: The spec's action process steps and output formats mixed CLI operations with agent-side logic without distinction. Readers could not tell which fields come from the CLI vs which are constructed by the DAG Assembler agent. The `parse-report` action appeared to be a single CLI command when it is actually a composite agent action where only the status update (step 5) touches the CLI.

**Fix**:
- Added `_(CLI)_` and `_(agent)_` tags to each process step in both `assemble-and-prepare` and `parse-report`.
- Added process header annotations explaining the boundary.
- Added explanatory paragraph below the assemble-and-prepare output: CLI provides `status`, `node_added`, `edges_inferred`, `validation`; agent constructs `agent_prompt`, `agent_type`.
- Added `validation` field to the output example to match actual CLI output.

**Files**: `plugins/humaninloop/agents/dag-assembler.md`

### Finding 12: Built-in vs Plugin Agents Conflated (Fixed — Run 2, D6)

**Problem**: The "Special cases by node type" table had a single "task (with agent)" row covering both plugin agents (e.g., `requirements-analyst`) and built-in agents (e.g., `Explore`). No naming convention was documented for the `agent_type` field.

**Fix**:
- Split "task (with agent)" into "task (with plugin agent)" and "task (with built-in agent)".
- Renamed "gate (with agent)" to "gate (with plugin agent)" with concrete example.
- Added `agent_type` naming convention: plugin agents use `humaninloop:<agent-name>`, built-in Claude Code agents use bare name (e.g., `"Explore"`).

**Files**: `plugins/humaninloop/agents/dag-assembler.md`

## Exit Code Convention

| Code | Meaning |
|------|---------|
| 0 | Success / valid |
| 1 | Validation failure / logic error |
| 2 | System error (missing file, parse failure) |
