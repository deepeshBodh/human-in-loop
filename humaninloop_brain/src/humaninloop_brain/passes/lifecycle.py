"""Pass lifecycle manager — create, assemble, update, freeze, save/load."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.dag_pass import PassEntry
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import EdgeType, TYPE_STATUS_MAP
from humaninloop_brain.entities.nodes import (
    EvidenceAttachment,
    GraphNode,
    NodeHistoryEntry,
)
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.graph.inference import infer_edges


_V3 = "3.0.0"


class FrozenEntryError(Exception):
    """Raised on writes to frozen history entries."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _recompute_derived(node: GraphNode) -> GraphNode:
    """Return new GraphNode with status/verdict/last_active_pass derived from latest history entry."""
    if not node.history:
        return node
    latest = node.history[-1]
    return GraphNode(
        id=node.id,
        type=node.type,
        name=node.name,
        description=node.description,
        status=latest.status,
        contract=node.contract,
        agent=node.agent,
        history=node.history,
        verdict=latest.verdict,
        last_active_pass=latest.pass_number,
        schema_version=_V3,
    )


def create_strategy_graph(workflow_id: str) -> StrategyGraph:
    """Create a new StrategyGraph with an initial pass 1 entry."""
    now = _now_iso()
    return StrategyGraph(
        id=f"{workflow_id}-strategy",
        workflow_id=workflow_id,
        created_at=now,
        passes=[PassEntry(pass_number=1, created_at=now)],
    )


def add_or_reopen_node(
    graph: StrategyGraph, node_id: str, catalog: NodeCatalog, pass_number: int
) -> tuple[StrategyGraph, list[Edge]]:
    """Add a new node or reopen an existing one with a new history entry.

    New node: create GraphNode + initial history entry + infer edges.
    Existing node: append new history entry, skip edge inference.

    Returns the updated graph and list of newly inferred edges.
    """
    existing_idx = None
    for i, n in enumerate(graph.nodes):
        if n.id == node_id:
            existing_idx = i
            break

    if existing_idx is not None:
        # Reopen: add new history entry with initial status from catalog
        node = graph.nodes[existing_idx]
        # Check for frozen entry at target pass — immutability enforcement
        for entry in node.history:
            if entry.pass_number == pass_number and entry.frozen:
                raise FrozenEntryError(
                    f"Cannot reopen node '{node_id}' for pass {pass_number}: "
                    f"history entry is frozen"
                )
        cat_node = catalog.get_node(node_id)
        initial_status = (
            cat_node.valid_statuses[0] if cat_node and cat_node.valid_statuses
            else "pending"
        )
        new_entry = NodeHistoryEntry(
            pass_number=pass_number,
            status=initial_status,
        )
        new_history = list(node.history) + [new_entry]
        new_node = GraphNode(
            id=node.id,
            type=node.type,
            name=node.name,
            description=node.description,
            status=initial_status,
            contract=node.contract,
            agent=node.agent,
            history=new_history,
            verdict=None,
            last_active_pass=pass_number,
            schema_version=_V3,
        )
        new_nodes = list(graph.nodes)
        new_nodes[existing_idx] = new_node
        return graph.model_copy(update={"nodes": new_nodes}), []

    # New node
    cat_node = catalog.get_node(node_id)
    if cat_node is None:
        raise ValueError(f"Node '{node_id}' not found in catalog")

    initial_status = cat_node.valid_statuses[0] if cat_node.valid_statuses else "pending"
    history_entry = NodeHistoryEntry(
        pass_number=pass_number,
        status=initial_status,
    )

    graph_node = GraphNode(
        id=cat_node.id,
        type=cat_node.type,
        name=cat_node.name,
        description=cat_node.description,
        status=initial_status,
        contract=cat_node.contract,
        agent=cat_node.agent,
        history=[history_entry],
        verdict=None,
        last_active_pass=pass_number,
        schema_version=_V3,
    )
    new_nodes = list(graph.nodes) + [graph_node]
    graph = graph.model_copy(update={"nodes": new_nodes})

    # Infer edges for new node
    inferred = infer_edges(node_id, graph, catalog)
    new_edges = list(graph.edges) + inferred

    return graph.model_copy(update={"edges": new_edges}), inferred


def update_node_history(
    graph: StrategyGraph,
    node_id: str,
    pass_number: int,
    status: str,
    verdict: str | None = None,
    evidence: list[EvidenceAttachment] | None = None,
    trace: dict | None = None,
) -> StrategyGraph:
    """Update a node's history entry for the given pass.

    Writes to the pass's history entry, then recomputes derived fields.
    Raises FrozenEntryError if the target entry is frozen.
    """
    for i, node in enumerate(graph.nodes):
        if node.id != node_id:
            continue

        # Validate status against type-status map
        status_enum = TYPE_STATUS_MAP[node.type]
        valid_values = {s.value for s in status_enum}
        if status not in valid_values:
            raise ValueError(
                f"Status '{status}' is not valid for node type "
                f"'{node.type.value}'. Valid: {sorted(valid_values)}"
            )

        # Find or create history entry for this pass
        new_history = list(node.history)
        entry_idx = None
        for j, entry in enumerate(new_history):
            if entry.pass_number == pass_number:
                entry_idx = j
                break

        if entry_idx is not None:
            existing = new_history[entry_idx]
            if existing.frozen:
                raise FrozenEntryError(
                    f"History entry for node '{node_id}' pass {pass_number} is frozen"
                )
            # Replace with updated entry
            merged_evidence = list(existing.evidence) + (evidence or [])
            new_history[entry_idx] = NodeHistoryEntry(
                pass_number=pass_number,
                status=status,
                verdict=verdict if verdict is not None else existing.verdict,
                frozen=existing.frozen,
                evidence=merged_evidence,
                trace=trace if trace is not None else existing.trace,
            )
        else:
            # Create new entry
            new_history.append(
                NodeHistoryEntry(
                    pass_number=pass_number,
                    status=status,
                    verdict=verdict,
                    evidence=evidence or [],
                    trace=trace,
                )
            )

        # Build updated node with derived fields from latest history entry
        latest = new_history[-1]
        updated = GraphNode(
            id=node.id,
            type=node.type,
            name=node.name,
            description=node.description,
            status=latest.status,
            contract=node.contract,
            agent=node.agent,
            history=new_history,
            verdict=latest.verdict,
            last_active_pass=latest.pass_number,
            schema_version=_V3,
        )
        new_nodes = list(graph.nodes)
        new_nodes[i] = updated
        return graph.model_copy(update={"nodes": new_nodes})

    raise ValueError(f"Node '{node_id}' not found in graph")


def freeze_current_pass(
    graph: StrategyGraph,
    outcome: str,
    detail: str | None = None,
    triggered_nodes: list[str] | None = None,
    trigger_source: str | None = None,
    reason: str | None = None,
) -> StrategyGraph:
    """Freeze all current-pass history entries and update pass metadata.

    Optionally creates triggered_by edges and a next pass entry.

    Args:
        trigger_source: The gate node whose verdict triggered the new pass.
            Required when triggered_nodes is provided. Each triggered_by edge
            runs from this source to each triggered node.
    """
    if triggered_nodes and not trigger_source:
        raise ValueError(
            "trigger_source is required when triggered_nodes is provided"
        )

    # INV-004: Refuse to create pass beyond maximum (structural invariant)
    _MAX_PASSES = 5
    current = graph.current_pass
    if triggered_nodes and current >= _MAX_PASSES:
        raise ValueError(
            f"INV-004: Cannot create pass {current + 1}. "
            f"Maximum {_MAX_PASSES} passes reached — mandatory human checkpoint required."
        )

    # Freeze all history entries for the current pass
    new_nodes = list(graph.nodes)
    for i, node in enumerate(new_nodes):
        new_history = list(node.history)
        changed = False
        for j, entry in enumerate(new_history):
            if entry.pass_number == current and not entry.frozen:
                new_history[j] = NodeHistoryEntry(
                    pass_number=entry.pass_number,
                    status=entry.status,
                    verdict=entry.verdict,
                    frozen=True,
                    evidence=entry.evidence,
                    trace=entry.trace,
                )
                changed = True
        if changed:
            latest = new_history[-1]
            new_nodes[i] = GraphNode(
                id=node.id,
                type=node.type,
                name=node.name,
                description=node.description,
                status=latest.status,
                contract=node.contract,
                agent=node.agent,
                history=new_history,
                verdict=latest.verdict,
                last_active_pass=latest.pass_number,
                schema_version=_V3,
            )

    # Update pass metadata
    now = _now_iso()
    new_passes = list(graph.passes)
    for j, p in enumerate(new_passes):
        if p.pass_number == current:
            new_passes[j] = PassEntry(
                pass_number=p.pass_number,
                outcome=outcome,
                detail=detail,
                created_at=p.created_at,
                completed_at=now,
                frozen=True,
            )
            break

    # Create triggered_by edges (source=gate that triggered, target=node to re-execute)
    new_edges = list(graph.edges)
    updates: dict = {
        "nodes": new_nodes,
        "passes": new_passes,
        "edges": new_edges,
    }

    if triggered_nodes:
        next_pass = current + 1
        for target_node_id in triggered_nodes:
            edge_id = f"triggered-by-{trigger_source}-{target_node_id}-pass{current}-to-pass{next_pass}"
            new_edges.append(
                Edge(
                    id=edge_id,
                    source=trigger_source,
                    target=target_node_id,
                    type=EdgeType.triggered_by,
                    source_pass=current,
                    target_pass=next_pass,
                    reason=reason,
                )
            )

        # Create next pass entry
        new_passes.append(PassEntry(pass_number=next_pass, created_at=now))
        updates["current_pass"] = next_pass

    # If no next pass created, mark graph as done
    if not triggered_nodes:
        updates["status"] = "completed"
        updates["completed_at"] = now

    return graph.model_copy(update=updates)


def save_graph(graph: StrategyGraph, path: str | Path) -> None:
    """Save StrategyGraph to a JSON file.

    Uses ``by_alias=True`` so ``pass_number`` serializes as ``"pass"`` in
    JSON, matching the V3 design doc schema.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(graph.model_dump_json(indent=2, by_alias=True))


def load_graph_file(path: str | Path) -> StrategyGraph:
    """Load StrategyGraph from a JSON file."""
    path = Path(path)
    data = json.loads(path.read_text())
    return StrategyGraph.model_validate(data)
