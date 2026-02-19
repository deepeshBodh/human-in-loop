"""CLI entry point for hil-dag — machine-invoked DAG operations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.nodes import EvidenceAttachment
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.entities.validation import ValidationResult
from humaninloop_brain.graph.sort import execution_order
from humaninloop_brain.passes.lifecycle import (
    FrozenEntryError,
    add_or_reopen_node,
    create_strategy_graph,
    freeze_current_pass,
    load_graph_file,
    save_graph,
    update_node_history,
)
from humaninloop_brain.validators.structural import validate_structure

_VALID_OUTCOMES = frozenset({"completed", "halted"})


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


def _load_graph(path: str) -> StrategyGraph:
    """Load a StrategyGraph from a JSON file."""
    data = json.loads(Path(path).read_text())
    return StrategyGraph.model_validate(data)


def _output(data: dict, exit_code: int = 0) -> int:
    print(json.dumps(data, indent=2))
    return exit_code


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_validate(args: argparse.Namespace) -> int:
    dag = _load_graph(args.dag)
    catalog = _load_catalog(args.catalog)
    result = validate_structure(dag, catalog)
    output = validation_result_to_output(result)
    return _output(output, 0 if result.valid else 1)


def cmd_sort(args: argparse.Namespace) -> int:
    dag = _load_graph(args.dag)
    order = execution_order(dag)
    return _output({"order": order})


def cmd_assemble(args: argparse.Namespace) -> int:
    catalog = _load_catalog(args.catalog)
    path = Path(args.dag)

    # Resolve node ID: either direct --node or --capability-tags resolution
    capability_tags = getattr(args, "capability_tags", None)
    node_type_filter = getattr(args, "node_type", None)

    if capability_tags:
        from humaninloop_brain.entities.enums import NodeType as NT
        nt = NT(node_type_filter) if node_type_filter else None
        matches = catalog.resolve_by_capabilities(capability_tags, nt)
        if len(matches) == 1:
            node_id = matches[0].id
        elif len(matches) == 0:
            # Tier 2: semantic description fallback
            intent = getattr(args, "intent", None)
            if intent:
                semantic = catalog.resolve_by_description(intent, nt)
                if len(semantic) == 1:
                    node_id = semantic[0].id
                else:
                    available = [
                        {"id": n.id, "name": n.name, "capabilities": n.capabilities}
                        for n in catalog.nodes
                    ]
                    return _output({
                        "status": "resolution_failed",
                        "reason": "no_match",
                        "resolution": "semantic_fallback_failed",
                        "tags": capability_tags,
                        "intent": intent,
                        "available_nodes": available,
                    }, 1)
            else:
                available = [
                    {"id": n.id, "name": n.name, "capabilities": n.capabilities}
                    for n in catalog.nodes
                ]
                return _output({
                    "status": "resolution_failed",
                    "reason": "no_match",
                    "tags": capability_tags,
                    "available_nodes": available,
                }, 1)
        else:
            # Tier 2: disambiguate among capability matches using intent
            intent = getattr(args, "intent", None)
            if intent:
                semantic = catalog.resolve_by_description(
                    intent, nt, candidates=matches,
                )
                if len(semantic) == 1:
                    node_id = semantic[0].id
                else:
                    candidates = [
                        {
                            "id": n.id,
                            "name": n.name,
                            "capabilities": n.capabilities,
                            "description": n.description,
                        }
                        for n in matches
                    ]
                    return _output({
                        "status": "resolution_failed",
                        "reason": "ambiguous",
                        "resolution": "semantic_fallback_failed",
                        "candidates": candidates,
                    }, 1)
            else:
                candidates = [
                    {
                        "id": n.id,
                        "name": n.name,
                        "capabilities": n.capabilities,
                        "description": n.description,
                    }
                    for n in matches
                ]
                return _output({
                    "status": "resolution_failed",
                    "reason": "ambiguous",
                    "candidates": candidates,
                }, 1)
    else:
        node_id = args.node

    if not path.exists():
        # Bootstrap: create new StrategyGraph
        if not args.workflow:
            return _output({
                "status": "error",
                "message": "--workflow required when DAG file does not exist (bootstrap)",
            }, 1)
        graph = create_strategy_graph(args.workflow)
    else:
        graph = _load_graph(str(path))

    if graph.status == "completed":
        return _output({
            "status": "error",
            "message": "Cannot add nodes to a completed graph",
        }, 1)

    pass_number = args.pass_number or graph.current_pass
    try:
        graph, inferred = add_or_reopen_node(graph, node_id, catalog, pass_number)
    except (ValueError, FrozenEntryError) as e:
        return _output({"status": "error", "message": str(e)}, 1)

    result = validate_structure(graph, catalog)

    # Invariant auto-resolution: carry_forward gates
    if not result.valid:
        inv002 = [v for v in result.violations if v.code == "INV-002"]
        if inv002:
            # Find all carry_forward gates in the catalog
            for cat_node in catalog.nodes:
                if not cat_node.carry_forward:
                    continue
                # Check if this gate completed in any prior pass
                existing = next((n for n in graph.nodes if n.id == cat_node.id), None)
                gate_previously_passed = False
                prior_status = None
                if existing:
                    for entry in existing.history:
                        if entry.status in ("completed", "passed") and entry.frozen:
                            gate_previously_passed = True
                            prior_status = entry.status
                            break
                # Auto-resolve only if gate passed in a prior pass OR this is pass 1
                # (on pass 1, the Supervisor has already verified the prerequisite)
                if gate_previously_passed or pass_number == 1:
                    # Use the prior pass's resolved status, or find a positive
                    # terminal status from the catalog's valid_statuses
                    _POSITIVE_TERMINAL = {"completed", "passed"}
                    resolve_status = prior_status or next(
                        (s for s in cat_node.valid_statuses if s in _POSITIVE_TERMINAL),
                        "completed",
                    )
                    graph, _ = add_or_reopen_node(
                        graph, cat_node.id, catalog, pass_number,
                    )
                    graph = update_node_history(
                        graph, cat_node.id, pass_number, resolve_status,
                    )
            result = validate_structure(graph, catalog)

    if result.valid:
        save_graph(graph, str(path))

    added_node = next(n for n in graph.nodes if n.id == node_id)
    return _output({
        "status": "valid" if result.valid else "invalid",
        "node_added": {
            "id": added_node.id,
            "type": added_node.type.value,
            "status": added_node.status,
        },
        "edges_inferred": len(inferred),
        "validation": validation_result_to_output(result),
    }, 0 if result.valid else 1)


def cmd_status(args: argparse.Namespace) -> int:
    graph = _load_graph(args.dag)

    # Find current status
    old_status = None
    for node in graph.nodes:
        if node.id == args.node:
            old_status = node.status
            break
    if old_status is None:
        return _output({"status": "error", "message": f"Node '{args.node}' not found"}, 1)

    pass_number = args.pass_number or graph.current_pass
    try:
        graph = update_node_history(
            graph, args.node, pass_number, args.status, verdict=args.verdict,
        )
    except (ValueError, FrozenEntryError) as e:
        return _output({"status": "error", "message": str(e)}, 1)
    save_graph(graph, args.dag)

    result = {
        "status": "success",
        "node_id": args.node,
        "old_status": old_status,
        "new_status": args.status,
    }
    if args.verdict is not None:
        result["verdict_recorded"] = args.verdict
    return _output(result)


def cmd_record(args: argparse.Namespace) -> int:
    graph = _load_graph(args.dag)

    # Find current status
    old_status = None
    for node in graph.nodes:
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
        evidence_parsed = [EvidenceAttachment.model_validate(e) for e in evidence_raw]
    except Exception as e:
        return _output({"status": "error", "message": f"Invalid evidence schema: {e}"}, 1)

    # Parse trace JSON
    try:
        trace_raw = json.loads(args.trace)
    except json.JSONDecodeError as e:
        return _output({"status": "error", "message": f"Invalid trace JSON: {e}"}, 1)

    pass_number = args.pass_number or graph.current_pass

    # Auto-generate evidence IDs: EV-{node_id}-{pass}-{sequence}
    # Count existing evidence for this node+pass to determine starting sequence
    existing_count = 0
    target_node = next((n for n in graph.nodes if n.id == args.node), None)
    if target_node:
        for entry in target_node.history:
            if entry.pass_number == pass_number:
                existing_count = len(entry.evidence)
                break
    evidence = []
    for i, ev in enumerate(evidence_parsed, start=existing_count + 1):
        evidence.append(
            EvidenceAttachment(
                id=f"EV-{args.node}-{pass_number:03d}-{i}",
                type=ev.type,
                description=ev.description,
                reference=ev.reference,
            )
        )

    try:
        graph = update_node_history(
            graph, args.node, pass_number, args.status,
            verdict=args.verdict,
            evidence=evidence, trace=trace_raw,
        )
    except (ValueError, FrozenEntryError) as e:
        return _output({"status": "error", "message": str(e)}, 1)
    save_graph(graph, args.dag)

    result = {
        "status": "success",
        "node_id": args.node,
        "old_status": old_status,
        "new_status": args.status,
        "evidence_added": len(evidence),
        "evidence_ids": [ev.id for ev in evidence],
        "trace_recorded": True,
    }
    if args.verdict is not None:
        result["verdict_recorded"] = args.verdict
    return _output(result)


def cmd_freeze(args: argparse.Namespace) -> int:
    # Validate outcome
    if args.outcome not in _VALID_OUTCOMES:
        return _output({
            "status": "error",
            "message": (
                f"Invalid outcome: '{args.outcome}'. "
                f"Must be 'completed' or 'halted'"
            ),
        }, 1)

    graph = _load_graph(args.dag)

    # Check double-freeze
    current_entry = next(
        (p for p in graph.passes if p.pass_number == graph.current_pass), None,
    )
    if current_entry and current_entry.frozen:
        return _output({
            "status": "error",
            "message": "Current pass is already frozen",
        }, 1)

    triggered = args.triggered_nodes or None
    try:
        graph = freeze_current_pass(
            graph, args.outcome, args.detail,
            triggered_nodes=triggered,
            trigger_source=args.trigger_source,
            reason=args.reason,
        )
    except (FrozenEntryError, ValueError) as e:
        return _output({"status": "error", "message": str(e)}, 1)

    save_graph(graph, args.dag)
    return _output({
        "status": "success",
        "pass_frozen": True,
        "dag_path": str(args.dag),
        "outcome": args.outcome,
        "outcome_detail": args.detail,
        "nodes_total": len(graph.nodes),
        "edges_total": len(graph.edges),
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

    checks = []
    issues_count = 0

    ids = [n.id for n in catalog.nodes]
    if len(ids) != len(set(ids)):
        checks.append({"check": "unique_node_ids", "passed": False, "issues": ["Duplicate node IDs"]})
        issues_count += 1
    else:
        checks.append({"check": "unique_node_ids", "passed": True, "issues": []})

    from humaninloop_brain.entities.enums import EdgeType
    for et in EdgeType:
        if catalog.get_edge_constraint(et) is None:
            checks.append({
                "check": f"edge_constraint_{et.value}",
                "passed": False,
                "issues": [f"Missing constraint for {et.value}"],
            })
            issues_count += 1
        else:
            checks.append({
                "check": f"edge_constraint_{et.value}",
                "passed": True,
                "issues": [],
            })

    total = len(checks)
    return _output({
        "status": "valid" if issues_count == 0 else "invalid",
        "checks": checks,
        "summary": {"total": total, "passed": total - issues_count, "failed": issues_count},
    }, 0 if issues_count == 0 else 1)


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
