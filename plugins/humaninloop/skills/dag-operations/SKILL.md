---
name: dag-operations
description: Deterministic DAG infrastructure operations for workflow execution via the hil-dag CLI. Use when assembling DAG passes, validating graph structure, updating node status, or freezing completed passes.
---

# DAG Operations

Deterministic DAG infrastructure operations for workflow execution.

## Overview

This skill wraps the `hil-dag` CLI from the `humaninloop_brain` package, providing the DAG Assembler and State Analyst agents with deterministic graph operations: assembly (with auto-bootstrap), validation, sorting, status updates, analysis recording, and pass freezing.

## Available Operations

| Operation | Script | Purpose |
|-----------|--------|---------|
| `assemble` | `dag-assemble.sh` | Add a catalog node with edge inference (auto-creates StrategyGraph if missing) |
| `validate` | `dag-validate.sh` | Run structural validation |
| `sort` | `dag-sort.sh` | Topological execution order |
| `status` | `dag-status.sh` | Update node status |
| `record` | `dag-record.sh` | Record analysis results (status + evidence + trace) |
| `freeze` | `dag-freeze.sh` | Freeze a completed pass (with triggered_by edges and next pass creation) |
| `catalog-validate` | `dag-catalog-validate.sh` | Validate a node catalog |

## Output Format

All operations produce JSON to stdout following the constitution pattern:

```json
{
  "status": "valid|invalid|success|error",
  "checks": [...],
  "summary": {"total": N, "passed": M, "failed": K}
}
```

Exit codes: 0=success, 1=validation failure, 2=unexpected error.

## Usage

Scripts are invoked by the DAG Assembler agent during workflow execution. The agent passes file paths to the single StrategyGraph JSON file and catalog JSON files.

```bash
# Add a node by ID (auto-creates StrategyGraph if file missing; --workflow required for first call)
./scripts/dag-assemble.sh <dag-path> <catalog-path> --node <node-id> [--workflow <workflow-id>]

# Add a node by capability tags (primary resolution — resolves to catalog node via tag matching)
./scripts/dag-assemble.sh <dag-path> <catalog-path> --capability-tags <tag1> [<tag2>...] [--node-type <type>] [--intent "<description>"] [--workflow <workflow-id>]

# Validate
./scripts/dag-validate.sh <dag-path> <catalog-path>

# Sort
./scripts/dag-sort.sh <dag-path>

# Update status (optional --pass to target specific pass)
./scripts/dag-status.sh <dag-path> <node-id> <new-status> [<pass-number>]

# Record analysis results (optional --pass and --verdict for gate nodes)
./scripts/dag-record.sh <dag-path> <node-id> <status> '<evidence-json-array>' '<trace-json-object>' [--pass <pass-number>] [--verdict <verdict>]

# Freeze (optional triggered nodes, trigger source gate, and reason for triggered_by edges)
./scripts/dag-freeze.sh <dag-path> <outcome> <detail> [--triggered-nodes <node>...] [--trigger-source <gate-node>] [--reason <reason>]

# Validate catalog
./scripts/dag-catalog-validate.sh <catalog-path>
```

## Dependencies

Requires the `humaninloop_brain` package (>= 0.1.0) to be installed. Run from the `humaninloop_brain/` directory or ensure `hil-dag` is on PATH:

```bash
cd humaninloop_brain && uv sync
```
