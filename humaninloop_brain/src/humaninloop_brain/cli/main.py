"""CLI entry point for hil-dag — machine-invoked DAG operations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.entities.enums import PassOutcome
from humaninloop_brain.entities.validation import ValidationResult
from humaninloop_brain.graph.sort import execution_order
from humaninloop_brain.entities.dag_pass import ExecutionTraceEntry
from humaninloop_brain.entities.nodes import EvidenceAttachment
from humaninloop_brain.passes.lifecycle import (
    FrozenPassError,
    add_node,
    create_pass,
    freeze_pass,
    load_pass,
    record_analysis,
    save_pass,
    update_node_status,
)
from humaninloop_brain.validators.structural import validate_structure


def validation_result_to_output(result: ValidationResult) -> dict:
    """Translate ValidationResult to constitution-compliant JSON output."""
    checks = []
    for v in result.violations:
        checks.append({
            "check": v.code,
            "passed": False,
            "issues": [v.message],
            "severity": v.severity,
        })
    if not result.violations:
        checks.append({
            "check": "all",
            "passed": True,
            "issues": [],
        })

    error_count = result.error_count
    warning_count = result.warning_count
    total = max(len(result.violations), 1)
    passed = total - error_count - warning_count

    return {
        "status": "valid" if result.valid else "invalid",
        "checks": checks,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": error_count,
            "warnings": warning_count,
        },
    }


def _load_catalog(path: str) -> NodeCatalog:
    data = json.loads(Path(path).read_text())
    return NodeCatalog.model_validate(data)


def _load_dag(path: str) -> DAGPass:
    return load_pass(path)


def _output(data: dict, exit_code: int = 0) -> int:
    print(json.dumps(data, indent=2))
    return exit_code


def cmd_validate(args: argparse.Namespace) -> int:
    dag = _load_dag(args.dag)
    catalog = _load_catalog(args.catalog)
    result = validate_structure(dag, catalog)
    output = validation_result_to_output(result)
    return _output(output, 0 if result.valid else 1)


def cmd_sort(args: argparse.Namespace) -> int:
    dag = _load_dag(args.dag)
    order = execution_order(dag)
    return _output({"order": order})


def cmd_create(args: argparse.Namespace) -> int:
    dag = create_pass(args.workflow, args.pass_number)
    save_pass(dag, args.output)
    return _output({
        "status": "success",
        "dag_path": str(args.output),
        "pass_number": args.pass_number,
    })


def cmd_assemble(args: argparse.Namespace) -> int:
    dag = _load_dag(args.dag)
    catalog = _load_catalog(args.catalog)
    try:
        dag, inferred = add_node(dag, args.node, catalog)
    except (ValueError, FrozenPassError) as e:
        return _output({"status": "error", "message": str(e)}, 1)

    # Validate after assembly — only persist if valid (transactional)
    result = validate_structure(dag, catalog)
    if result.valid:
        save_pass(dag, args.dag)
    added_node = next(n for n in dag.nodes if n.id == args.node)
    output = {
        "status": "valid" if result.valid else "invalid",
        "node_added": {
            "id": added_node.id,
            "type": added_node.type.value,
            "status": added_node.status,
        },
        "edges_inferred": len(inferred),
        "validation": validation_result_to_output(result),
    }
    return _output(output, 0 if result.valid else 1)


def cmd_status(args: argparse.Namespace) -> int:
    dag = _load_dag(args.dag)
    # Find current status
    old_status = None
    for node in dag.nodes:
        if node.id == args.node:
            old_status = node.status
            break
    if old_status is None:
        return _output({"status": "error", "message": f"Node '{args.node}' not found"}, 1)

    try:
        update_node_status(dag, args.node, args.status)
    except (ValueError, FrozenPassError) as e:
        return _output({"status": "error", "message": str(e)}, 1)

    save_pass(dag, args.dag)
    return _output({
        "status": "success",
        "node_id": args.node,
        "old_status": old_status,
        "new_status": args.status,
    })


def cmd_record(args: argparse.Namespace) -> int:
    dag = _load_dag(args.dag)

    # Find current status
    old_status = None
    for node in dag.nodes:
        if node.id == args.node:
            old_status = node.status
            break
    if old_status is None:
        return _output({"status": "error", "message": f"Node '{args.node}' not found"}, 1)

    # Parse evidence JSON
    try:
        evidence_raw = json.loads(args.evidence)
    except json.JSONDecodeError as e:
        return _output({"status": "error", "message": f"Invalid evidence JSON: {e}"}, 1)
    try:
        evidence = [EvidenceAttachment.model_validate(e) for e in evidence_raw]
    except Exception as e:
        return _output({"status": "error", "message": f"Invalid evidence schema: {e}"}, 1)

    # Parse trace JSON
    try:
        trace_raw = json.loads(args.trace)
    except json.JSONDecodeError as e:
        return _output({"status": "error", "message": f"Invalid trace JSON: {e}"}, 1)
    try:
        trace_entry = ExecutionTraceEntry.model_validate(trace_raw)
    except Exception as e:
        return _output({"status": "error", "message": f"Invalid trace schema: {e}"}, 1)

    try:
        record_analysis(dag, args.node, args.status, evidence, trace_entry)
    except (ValueError, FrozenPassError) as e:
        return _output({"status": "error", "message": str(e)}, 1)

    save_pass(dag, args.dag)
    return _output({
        "status": "success",
        "node_id": args.node,
        "old_status": old_status,
        "new_status": args.status,
        "evidence_added": len(evidence),
        "trace_recorded": True,
    })


def cmd_freeze(args: argparse.Namespace) -> int:
    dag = _load_dag(args.dag)
    try:
        outcome = PassOutcome(args.outcome)
    except ValueError:
        return _output({
            "status": "error",
            "message": f"Invalid outcome: '{args.outcome}'. Must be 'completed' or 'halted'",
        }, 1)

    try:
        freeze_pass(dag, outcome, args.detail, args.rationale)
    except FrozenPassError as e:
        return _output({"status": "error", "message": str(e)}, 1)

    save_pass(dag, args.dag)
    return _output({
        "status": "success",
        "pass_frozen": True,
        "dag_path": str(args.dag),
        "outcome": args.outcome,
        "outcome_detail": args.detail,
        "nodes_executed": len(dag.nodes),
        "edges_total": len(dag.edges),
    })


def cmd_catalog_validate(args: argparse.Namespace) -> int:
    try:
        catalog = _load_catalog(args.catalog)
    except Exception as e:
        return _output({
            "status": "invalid",
            "checks": [{"check": "schema", "passed": False, "issues": [str(e)]}],
            "summary": {"total": 1, "passed": 0, "failed": 1},
        }, 1)

    # Basic catalog validation
    checks = []
    issues_count = 0

    # Check node IDs unique
    ids = [n.id for n in catalog.nodes]
    if len(ids) != len(set(ids)):
        checks.append({"check": "unique_node_ids", "passed": False, "issues": ["Duplicate node IDs"]})
        issues_count += 1
    else:
        checks.append({"check": "unique_node_ids", "passed": True, "issues": []})

    # Check all edge types have constraints
    from humaninloop_brain.entities.enums import EdgeType
    for et in EdgeType:
        if catalog.get_edge_constraint(et) is None:
            checks.append({"check": f"edge_constraint_{et.value}", "passed": False, "issues": [f"Missing constraint for {et.value}"]})
            issues_count += 1
        else:
            checks.append({"check": f"edge_constraint_{et.value}", "passed": True, "issues": []})

    total = len(checks)
    return _output({
        "status": "valid" if issues_count == 0 else "invalid",
        "checks": checks,
        "summary": {"total": total, "passed": total - issues_count, "failed": issues_count},
    }, 0 if issues_count == 0 else 1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hil-dag",
        description="Deterministic DAG operations for humaninloop workflows",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate a DAG pass")
    p_val.add_argument("dag", help="Path to DAG pass JSON")
    p_val.add_argument("--catalog", required=True, help="Path to node catalog JSON")
    p_val.set_defaults(func=cmd_validate)

    # sort
    p_sort = subparsers.add_parser("sort", help="Topological sort of DAG nodes")
    p_sort.add_argument("dag", help="Path to DAG pass JSON")
    p_sort.set_defaults(func=cmd_sort)

    # create
    p_create = subparsers.add_parser("create", help="Create a new empty DAG pass")
    p_create.add_argument("workflow", help="Workflow ID")
    p_create.add_argument("--pass", dest="pass_number", type=int, required=True, help="Pass number")
    p_create.add_argument("--output", required=True, help="Output file path")
    p_create.set_defaults(func=cmd_create)

    # assemble
    p_asm = subparsers.add_parser("assemble", help="Add a node from catalog to DAG")
    p_asm.add_argument("dag", help="Path to DAG pass JSON")
    p_asm.add_argument("--catalog", required=True, help="Path to node catalog JSON")
    p_asm.add_argument("--node", required=True, help="Node ID from catalog")
    p_asm.set_defaults(func=cmd_assemble)

    # status
    p_stat = subparsers.add_parser("status", help="Update a node's status")
    p_stat.add_argument("dag", help="Path to DAG pass JSON")
    p_stat.add_argument("--node", required=True, help="Node ID")
    p_stat.add_argument("--status", required=True, help="New status")
    p_stat.set_defaults(func=cmd_status)

    # freeze
    p_frz = subparsers.add_parser("freeze", help="Freeze a completed pass")
    p_frz.add_argument("dag", help="Path to DAG pass JSON")
    p_frz.add_argument("--outcome", required=True, help="completed or halted")
    p_frz.add_argument("--detail", required=True, help="Outcome detail")
    p_frz.add_argument("--rationale", required=True, help="Assembly rationale")
    p_frz.set_defaults(func=cmd_freeze)

    # record
    p_rec = subparsers.add_parser("record", help="Record analysis results for a node")
    p_rec.add_argument("dag", help="Path to DAG pass JSON")
    p_rec.add_argument("--node", required=True, help="Node ID")
    p_rec.add_argument("--status", required=True, help="New status")
    p_rec.add_argument("--evidence", required=True, help="JSON array of evidence entries")
    p_rec.add_argument("--trace", required=True, help="JSON object for execution trace entry")
    p_rec.set_defaults(func=cmd_record)

    # catalog-validate
    p_cat = subparsers.add_parser("catalog-validate", help="Validate a node catalog")
    p_cat.add_argument("catalog", help="Path to catalog JSON")
    p_cat.set_defaults(func=cmd_catalog_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
