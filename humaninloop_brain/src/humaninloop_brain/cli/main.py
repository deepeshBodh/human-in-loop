"""CLI entry point for hil-dag — machine-invoked DAG operations.

Thin adapter: argparse → op_*() → print JSON to stdout.
Business logic lives in humaninloop_brain.mcp.operations.
"""

from __future__ import annotations

import argparse
import json
import sys

from humaninloop_brain.mcp.operations import (
    op_assemble,
    op_catalog_validate,
    op_freeze,
    op_record,
    op_sort,
    op_status,
    op_validate,
    validation_result_to_output,
)


def _output(data: dict, exit_code: int = 0) -> int:
    print(json.dumps(data, indent=2))
    return exit_code


# ---------------------------------------------------------------------------
# Commands — thin adapters delegating to op_*()
# ---------------------------------------------------------------------------


def cmd_validate(args: argparse.Namespace) -> int:
    result, code = op_validate(args.dag, args.catalog)
    return _output(result, code)


def cmd_sort(args: argparse.Namespace) -> int:
    result, code = op_sort(args.dag)
    return _output(result, code)


def cmd_assemble(args: argparse.Namespace) -> int:
    result, code = op_assemble(
        args.dag,
        args.catalog,
        node=getattr(args, "node", None),
        capability_tags=getattr(args, "capability_tags", None),
        node_type=getattr(args, "node_type", None),
        intent=getattr(args, "intent", None),
        workflow=getattr(args, "workflow", None),
        graph_id=getattr(args, "graph_id", None),
        pass_number=getattr(args, "pass_number", None),
    )
    return _output(result, code)


def cmd_status(args: argparse.Namespace) -> int:
    result, code = op_status(
        args.dag,
        args.node,
        args.status,
        verdict=args.verdict,
        pass_number=args.pass_number,
    )
    return _output(result, code)


def cmd_record(args: argparse.Namespace) -> int:
    result, code = op_record(
        args.dag,
        args.node,
        args.status,
        args.evidence,
        args.trace,
        verdict=args.verdict,
        pass_number=args.pass_number,
    )
    return _output(result, code)


def cmd_freeze(args: argparse.Namespace) -> int:
    result, code = op_freeze(
        args.dag,
        args.outcome,
        args.detail,
        triggered_nodes=args.triggered_nodes,
        trigger_source=args.trigger_source,
        reason=args.reason,
        auto_trigger=getattr(args, "auto_trigger", False),
    )
    return _output(result, code)


def cmd_catalog_validate(args: argparse.Namespace) -> int:
    result, code = op_catalog_validate(args.catalog)
    return _output(result, code)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hil-dag",
        description="Deterministic DAG operations for humaninloop workflows",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # validate
    p_val = subparsers.add_parser("validate", help="Validate a DAG")
    p_val.add_argument("dag", help="Path to DAG JSON")
    p_val.add_argument("--catalog", required=True, help="Path to node catalog JSON")
    p_val.set_defaults(func=cmd_validate)

    # sort
    p_sort = subparsers.add_parser("sort", help="Topological sort of DAG nodes")
    p_sort.add_argument("dag", help="Path to DAG JSON")
    p_sort.set_defaults(func=cmd_sort)

    # assemble
    p_asm = subparsers.add_parser("assemble", help="Add a node from catalog to DAG")
    p_asm.add_argument("dag", help="Path to DAG JSON (created if missing)")
    p_asm.add_argument("--catalog", required=True, help="Path to node catalog JSON")
    asm_node_group = p_asm.add_mutually_exclusive_group(required=True)
    asm_node_group.add_argument("--node", help="Node ID from catalog")
    asm_node_group.add_argument(
        "--capability-tags", nargs="+", dest="capability_tags",
        help="Capability tags for resolution (alternative to --node)",
    )
    p_asm.add_argument(
        "--node-type", dest="node_type", default=None,
        help="Node type filter for capability resolution",
    )
    p_asm.add_argument(
        "--intent", default=None,
        help="Intent description for semantic fallback when capability tags fail",
    )
    p_asm.add_argument("--workflow", help="Workflow ID (required for bootstrap)")
    p_asm.add_argument(
        "--id", dest="graph_id", default=None,
        help="Custom graph ID for bootstrap (default: {workflow}-strategy)",
    )
    p_asm.add_argument(
        "--pass", dest="pass_number", type=int, default=None,
        help="Target pass number",
    )
    p_asm.set_defaults(func=cmd_assemble)

    # status
    p_stat = subparsers.add_parser("status", help="Update a node's status")
    p_stat.add_argument("dag", help="Path to DAG JSON")
    p_stat.add_argument("--node", required=True, help="Node ID")
    p_stat.add_argument("--status", required=True, help="New status")
    p_stat.add_argument("--verdict", default=None, help="Gate verdict (for gate nodes only)")
    p_stat.add_argument(
        "--pass", dest="pass_number", type=int, default=None,
        help="Target pass number",
    )
    p_stat.set_defaults(func=cmd_status)

    # record
    p_rec = subparsers.add_parser("record", help="Record analysis results for a node")
    p_rec.add_argument("dag", help="Path to DAG JSON")
    p_rec.add_argument("--node", required=True, help="Node ID")
    p_rec.add_argument("--status", required=True, help="New status")
    p_rec.add_argument("--evidence", required=True, help="JSON array of evidence entries")
    p_rec.add_argument("--trace", required=True, help="JSON object for execution trace entry")
    p_rec.add_argument("--verdict", default=None, help="Gate verdict (for gate nodes only)")
    p_rec.add_argument(
        "--pass", dest="pass_number", type=int, default=None,
        help="Target pass number",
    )
    p_rec.set_defaults(func=cmd_record)

    # freeze
    p_frz = subparsers.add_parser("freeze", help="Freeze a completed pass")
    p_frz.add_argument("dag", help="Path to DAG JSON")
    p_frz.add_argument("--outcome", required=True, help="completed or halted")
    p_frz.add_argument("--detail", required=True, help="Outcome detail")
    p_frz.add_argument(
        "--triggered-nodes", nargs="*", default=None,
        help="Node IDs to trigger in next pass",
    )
    p_frz.add_argument(
        "--trigger-source", default=None,
        help="Gate node whose verdict triggered the new pass (required with --triggered-nodes)",
    )
    p_frz.add_argument("--reason", default=None, help="Reason for triggered-by edges")
    p_frz.add_argument(
        "--auto-trigger", action="store_true", default=False,
        dest="auto_trigger",
        help="Deterministically compute triggered nodes from graph topology "
             "(mutually exclusive with --triggered-nodes)",
    )
    p_frz.set_defaults(func=cmd_freeze)

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
