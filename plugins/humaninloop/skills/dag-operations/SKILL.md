---
name: dag-operations
description: Deterministic DAG infrastructure operations for workflow execution via the hil-dag CLI. Use when assembling DAG passes, validating graph structure, updating node status, or freezing completed passes.
---

# DAG Operations

Deterministic DAG infrastructure operations for workflow execution.

## Overview

This skill wraps the `hil-dag` CLI from the `humaninloop_brain` package, providing the DAG Assembler and State Analyst agents with deterministic graph operations: creation, assembly, validation, sorting, status updates, analysis recording, and pass freezing.

## Available Operations

| Operation | Script | Purpose |
|-----------|--------|---------|
| `create` | `dag-create.sh` | Create a new empty DAG pass |
| `assemble` | `dag-assemble.sh` | Add a catalog node with edge inference |
| `validate` | `dag-validate.sh` | Run 9-step structural validation |
| `sort` | `dag-sort.sh` | Topological execution order |
| `status` | `dag-status.sh` | Update node status |
| `record` | `dag-record.sh` | Record analysis results (status + evidence + trace) |
| `freeze` | `dag-freeze.sh` | Freeze a completed pass |
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

Scripts are invoked by the DAG Assembler agent during workflow execution. The agent passes file paths to DAG pass JSON and catalog JSON files.

```bash
# Create a new pass
./scripts/dag-create.sh <workflow-id> <pass-number> <output-path>

# Add a node
./scripts/dag-assemble.sh <dag-path> <catalog-path> <node-id>

# Validate
./scripts/dag-validate.sh <dag-path> <catalog-path>

# Sort
./scripts/dag-sort.sh <dag-path>

# Update status
./scripts/dag-status.sh <dag-path> <node-id> <new-status>

# Record analysis results (status + evidence + trace atomically)
./scripts/dag-record.sh <dag-path> <node-id> <status> '<evidence-json-array>' '<trace-json-object>'

# Freeze
./scripts/dag-freeze.sh <dag-path> <outcome> <detail> <rationale>

# Validate catalog
./scripts/dag-catalog-validate.sh <catalog-path>
```

## Dependencies

Requires the `humaninloop_brain` package (>= 0.1.0) to be installed. Run from the `humaninloop_brain/` directory or ensure `hil-dag` is on PATH:

```bash
cd humaninloop_brain && uv sync
```
