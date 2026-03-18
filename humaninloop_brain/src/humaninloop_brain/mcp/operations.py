"""Transport-agnostic DAG operations — shared by CLI and MCP server.

Each op_*() function accepts typed parameters and returns (result_dict, exit_code).
No argparse, no stdout, no transport concerns.
"""

from __future__ import annotations

import json
from pathlib import Path

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.enums import PassOutcome
from humaninloop_brain.entities.nodes import EvidenceAttachment
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.entities.validation import ValidationResult
from humaninloop_brain.graph.sort import execution_order
from humaninloop_brain.passes.lifecycle import (
    FrozenEntryError,
    add_or_reopen_node,
    compute_triggered_nodes,
    create_strategy_graph,
    freeze_current_pass,
    load_graph_file,
    save_graph,
    update_node_history,
)
from humaninloop_brain.validators.structural import validate_structure

_VALID_OUTCOMES = frozenset(o.value for o in PassOutcome)


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


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def op_validate(dag_path: str, catalog_path: str) -> tuple[dict, int]:
    """Validate a DAG against a catalog."""
    dag = _load_graph(dag_path)
    catalog = _load_catalog(catalog_path)
    result = validate_structure(dag, catalog)
    output = validation_result_to_output(result)
    return output, 0 if result.valid else 1


def op_sort(dag_path: str) -> tuple[dict, int]:
    """Topological sort of DAG nodes."""
    dag = _load_graph(dag_path)
    order = execution_order(dag)
    return {"order": order}, 0


def op_assemble(
    dag_path: str,
    catalog_path: str,
    *,
    node: str | None = None,
    capability_tags: list[str] | None = None,
    node_type: str | None = None,
    intent: str | None = None,
    workflow: str | None = None,
    graph_id: str | None = None,
    pass_number: int | None = None,
) -> tuple[dict, int]:
    """Add a node from catalog to DAG.

    Either ``node`` (direct ID) or ``capability_tags`` (resolution) must be
    provided, but not both.
    """
    # Mutual exclusion validation (replaces argparse mutually_exclusive_group)
    if node and capability_tags:
        return {
            "status": "error",
            "message": "Cannot specify both 'node' and 'capability_tags'",
        }, 2
    if not node and not capability_tags:
        return {
            "status": "error",
            "message": "Either 'node' or 'capability_tags' is required",
        }, 2

    catalog = _load_catalog(catalog_path)
    path = Path(dag_path)

    # Resolve node ID: either direct or capability-tags resolution
    if capability_tags:
        from humaninloop_brain.entities.enums import NodeType as NT
        nt = NT(node_type) if node_type else None
        matches = catalog.resolve_by_capabilities(capability_tags, nt)
        if len(matches) == 1:
            node_id = matches[0].node_id
        elif len(matches) == 0:
            # Tier 2: semantic description fallback
            if intent:
                semantic = catalog.resolve_by_description(intent, nt)
                if len(semantic) == 1:
                    node_id = semantic[0].node_id
                else:
                    available = [
                        {"node_id": n.node_id, "name": n.name, "capabilities": n.capabilities}
                        for n in catalog.nodes
                    ]
                    return {
                        "status": "resolution_failed",
                        "reason": "no_match",
                        "resolution": "semantic_fallback_failed",
                        "tags": capability_tags,
                        "intent": intent,
                        "available_nodes": available,
                    }, 1
            else:
                available = [
                    {"node_id": n.node_id, "name": n.name, "capabilities": n.capabilities}
                    for n in catalog.nodes
                ]
                return {
                    "status": "resolution_failed",
                    "reason": "no_match",
                    "tags": capability_tags,
                    "available_nodes": available,
                }, 1
        else:
            # Tier 2: disambiguate among capability matches using intent
            if intent:
                semantic = catalog.resolve_by_description(
                    intent, nt, candidates=matches,
                )
                if len(semantic) == 1:
                    node_id = semantic[0].node_id
                else:
                    candidates = [
                        {
                            "node_id": n.node_id,
                            "name": n.name,
                            "capabilities": n.capabilities,
                            "description": n.description,
                        }
                        for n in matches
                    ]
                    return {
                        "status": "resolution_failed",
                        "reason": "ambiguous",
                        "resolution": "semantic_fallback_failed",
                        "candidates": candidates,
                    }, 1
            else:
                candidates = [
                    {
                        "node_id": n.node_id,
                        "name": n.name,
                        "capabilities": n.capabilities,
                        "description": n.description,
                    }
                    for n in matches
                ]
                return {
                    "status": "resolution_failed",
                    "reason": "ambiguous",
                    "candidates": candidates,
                }, 1
    else:
        node_id = node

    if not path.exists():
        # Bootstrap: create new StrategyGraph
        if not workflow:
            return {
                "status": "error",
                "message": "--workflow required when DAG file does not exist (bootstrap)",
            }, 1
        graph = create_strategy_graph(workflow, graph_id=graph_id)
    else:
        graph = _load_graph(str(path))

    if graph.status == "completed":
        return {
            "status": "error",
            "message": "Cannot add nodes to a completed graph",
        }, 1

    _pass_number = pass_number or graph.current_pass
    try:
        graph, inferred = add_or_reopen_node(graph, node_id, catalog, _pass_number)
    except (ValueError, FrozenEntryError) as e:
        return {"status": "error", "message": str(e)}, 1

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
                existing = next((n for n in graph.nodes if n.id == cat_node.node_id), None)
                gate_previously_passed = False
                prior_status = None
                if existing:
                    for entry in existing.history:
                        if entry.status in ("completed", "passed") and entry.frozen:
                            gate_previously_passed = True
                            prior_status = entry.status
                            break
                # Auto-resolve only if gate passed in a prior pass OR this is pass 1
                if gate_previously_passed or _pass_number == 1:
                    _POSITIVE_TERMINAL = {"completed", "passed"}
                    resolve_status = prior_status or next(
                        (s for s in cat_node.valid_statuses if s in _POSITIVE_TERMINAL),
                        "completed",
                    )
                    # Check if gate already has a history entry for this pass
                    has_current_entry = False
                    if existing:
                        has_current_entry = any(
                            e.pass_number == _pass_number for e in existing.history
                        )
                    if not has_current_entry:
                        graph, _ = add_or_reopen_node(
                            graph, cat_node.node_id, catalog, _pass_number,
                        )
                    graph = update_node_history(
                        graph, cat_node.node_id, _pass_number, resolve_status,
                    )
            result = validate_structure(graph, catalog)

    if result.valid:
        save_graph(graph, str(path))

    added_node = next(n for n in graph.nodes if n.id == node_id)
    return {
        "status": "valid" if result.valid else "invalid",
        "node_added": {
            "id": added_node.id,
            "type": added_node.type.value,
            "status": added_node.status,
        },
        "edges_inferred": len(inferred),
        "validation": validation_result_to_output(result),
    }, 0 if result.valid else 1


def op_status(
    dag_path: str,
    node: str,
    status: str,
    *,
    verdict: str | None = None,
    pass_number: int | None = None,
) -> tuple[dict, int]:
    """Update a node's status."""
    graph = _load_graph(dag_path)

    # Find target node
    target_node = None
    for n in graph.nodes:
        if n.id == node:
            target_node = n
            break
    if target_node is None:
        return {"status": "error", "message": f"Node '{node}' not found"}, 1

    old_status = target_node.status
    _pass_number = pass_number or graph.current_pass

    # Node-type routing: milestone prerequisite verification
    from humaninloop_brain.entities.enums import NodeType
    if target_node.type == NodeType.milestone and status == "achieved":
        prereq_node_ids = set()
        for edge in graph.edges:
            if edge.target == node and edge.type.value == "depends_on":
                prereq_node_ids.add(edge.source)
        incomplete = []
        _TERMINAL = {"completed", "passed", "achieved", "decided"}
        for prereq_id in prereq_node_ids:
            prereq = next((n for n in graph.nodes if n.id == prereq_id), None)
            if prereq is None:
                incomplete.append(prereq_id)
                continue
            current_entry = next(
                (e for e in prereq.history if e.pass_number == _pass_number), None,
            )
            if current_entry is None or current_entry.status not in _TERMINAL:
                incomplete.append(prereq_id)
        if incomplete:
            return {
                "status": "invalid",
                "reason": "prerequisite nodes incomplete",
                "incomplete": incomplete,
            }, 1

    try:
        graph = update_node_history(
            graph, node, _pass_number, status, verdict=verdict,
        )
    except (ValueError, FrozenEntryError) as e:
        return {"status": "error", "message": str(e)}, 1
    save_graph(graph, dag_path)

    result = {
        "status": "success",
        "node_id": node,
        "old_status": old_status,
        "new_status": status,
    }
    if verdict is not None:
        result["verdict_recorded"] = verdict
    return result, 0


def op_record(
    dag_path: str,
    node: str,
    status: str,
    evidence: str,
    trace: str,
    *,
    verdict: str | None = None,
    pass_number: int | None = None,
) -> tuple[dict, int]:
    """Record analysis results for a node (status + evidence + trace)."""
    graph = _load_graph(dag_path)

    # Find current status
    old_status = None
    for n in graph.nodes:
        if n.id == node:
            old_status = n.status
            break
    if old_status is None:
        return {"status": "error", "message": f"Node '{node}' not found"}, 1

    # Parse evidence JSON
    try:
        evidence_raw = json.loads(evidence)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid evidence JSON: {e}"}, 1
    try:
        evidence_parsed = [EvidenceAttachment.model_validate(e) for e in evidence_raw]
    except Exception as e:
        return {"status": "error", "message": f"Invalid evidence schema: {e}"}, 1

    # Parse trace JSON
    try:
        trace_raw = json.loads(trace)
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Invalid trace JSON: {e}"}, 1

    # Derive duration_ms from started_at/completed_at if both present
    if (
        isinstance(trace_raw, dict)
        and "started_at" in trace_raw
        and "completed_at" in trace_raw
        and "duration_ms" not in trace_raw
    ):
        try:
            from datetime import datetime, timezone

            started = datetime.fromisoformat(trace_raw["started_at"])
            completed = datetime.fromisoformat(trace_raw["completed_at"])
            trace_raw["duration_ms"] = int(
                (completed - started).total_seconds() * 1000
            )
        except (ValueError, TypeError):
            pass  # Best-effort — skip if timestamps are unparseable

    _pass_number = pass_number or graph.current_pass

    # Auto-generate evidence IDs: EV-{node_id}-{pass}-{sequence}
    existing_count = 0
    target_node = next((n for n in graph.nodes if n.id == node), None)
    if target_node:
        for entry in target_node.history:
            if entry.pass_number == _pass_number:
                existing_count = len(entry.evidence)
                break
    evidence_list = []
    for i, ev in enumerate(evidence_parsed, start=existing_count + 1):
        evidence_list.append(
            EvidenceAttachment(
                id=f"EV-{node}-{_pass_number:03d}-{i}",
                type=ev.type,
                description=ev.description,
                reference=ev.reference,
            )
        )

    try:
        graph = update_node_history(
            graph, node, _pass_number, status,
            verdict=verdict,
            evidence=evidence_list, trace=trace_raw,
        )
    except (ValueError, FrozenEntryError) as e:
        return {"status": "error", "message": str(e)}, 1
    save_graph(graph, dag_path)

    result = {
        "status": "success",
        "node_id": node,
        "old_status": old_status,
        "new_status": status,
        "evidence_added": len(evidence_list),
        "evidence_ids": [ev.id for ev in evidence_list],
        "trace_recorded": True,
    }
    if verdict is not None:
        result["verdict_recorded"] = verdict
    return result, 0


def op_freeze(
    dag_path: str,
    outcome: str,
    detail: str,
    *,
    triggered_nodes: list[str] | None = None,
    trigger_source: str | None = None,
    reason: str | None = None,
    auto_trigger: bool = False,
) -> tuple[dict, int]:
    """Freeze a completed pass."""
    # Validate outcome
    if outcome not in _VALID_OUTCOMES:
        return {
            "status": "error",
            "message": (
                f"Invalid outcome: '{outcome}'. "
                f"Must be 'completed' or 'halted'"
            ),
        }, 1

    graph = _load_graph(dag_path)

    # Check double-freeze
    current_entry = next(
        (p for p in graph.passes if p.pass_number == graph.current_pass), None,
    )
    if current_entry and current_entry.frozen:
        return {
            "status": "error",
            "message": "Current pass is already frozen",
        }, 1

    triggered = triggered_nodes

    # --auto-trigger: deterministically compute triggered nodes from graph topology
    if auto_trigger:
        if not trigger_source:
            return {
                "status": "error",
                "message": "--trigger-source is required with --auto-trigger",
            }, 1
        if triggered is not None:
            return {
                "status": "error",
                "message": "--auto-trigger and --triggered-nodes are mutually exclusive",
            }, 1
        triggered = compute_triggered_nodes(graph, trigger_source)

    try:
        graph = freeze_current_pass(
            graph, outcome, detail,
            triggered_nodes=triggered,
            trigger_source=trigger_source,
            reason=reason,
        )
    except (FrozenEntryError, ValueError) as e:
        return {"status": "error", "message": str(e)}, 1

    save_graph(graph, dag_path)
    return {
        "status": "success",
        "pass_frozen": True,
        "dag_path": str(dag_path),
        "outcome": outcome,
        "outcome_detail": detail,
        "nodes_total": len(graph.nodes),
        "edges_total": len(graph.edges),
    }, 0


def op_catalog_validate(catalog_path: str) -> tuple[dict, int]:
    """Validate a node catalog."""
    try:
        catalog = _load_catalog(catalog_path)
    except Exception as e:
        return {
            "status": "invalid",
            "checks": [{"check": "schema", "passed": False, "issues": [str(e)]}],
            "summary": {"total": 1, "passed": 0, "failed": 1},
        }, 1

    checks = []
    issues_count = 0

    ids = [n.node_id for n in catalog.nodes]
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
    return {
        "status": "valid" if issues_count == 0 else "invalid",
        "checks": checks,
        "summary": {"total": total, "passed": total - issues_count, "failed": issues_count},
    }, 0 if issues_count == 0 else 1
