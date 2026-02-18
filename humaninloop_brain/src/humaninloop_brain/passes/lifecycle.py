"""Pass lifecycle manager — create, assemble, update, freeze, save/load."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.dag_pass import DAGPass, ExecutionTraceEntry
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import NodeType, PassOutcome, TYPE_STATUS_MAP
from humaninloop_brain.entities.nodes import EvidenceAttachment, GraphNode
from humaninloop_brain.graph.inference import infer_edges


class FrozenPassError(Exception):
    """Raised when attempting to mutate a frozen (completed) pass."""


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_pass(workflow_id: str, pass_number: int) -> DAGPass:
    """Create a new empty DAG pass."""
    return DAGPass(
        id=f"{workflow_id}-pass-{pass_number:03d}",
        workflow_id=workflow_id,
        pass_number=pass_number,
        created_at=_now_iso(),
    )


def add_node(
    dag: DAGPass, node_id: str, catalog: NodeCatalog
) -> tuple[DAGPass, list[Edge]]:
    """Add a catalog node to the DAG and infer edges.

    Returns the updated DAG and the list of inferred edges.
    """
    if dag.outcome is not None:
        raise FrozenPassError("Cannot add nodes to a frozen pass")

    cat_node = catalog.get_node(node_id)
    if cat_node is None:
        raise ValueError(f"Node '{node_id}' not found in catalog")

    # Check for duplicate
    if any(n.id == node_id for n in dag.nodes):
        raise ValueError(f"Node '{node_id}' already exists in the DAG")

    # Create GraphNode from catalog definition
    graph_node = GraphNode(
        id=cat_node.id,
        type=cat_node.type,
        name=cat_node.name,
        description=cat_node.description,
        status=cat_node.valid_statuses[0] if cat_node.valid_statuses else "pending",
        contract=cat_node.contract,
        agent=cat_node.agent,
    )
    dag.nodes.append(graph_node)

    # Infer and add edges
    inferred = infer_edges(node_id, dag, catalog)
    dag.edges.extend(inferred)

    return dag, inferred


def update_node_status(dag: DAGPass, node_id: str, status: str) -> DAGPass:
    """Replace a frozen GraphNode with a new one at the updated status.

    Validates the new status against the node's type.
    """
    if dag.outcome is not None:
        raise FrozenPassError("Cannot update nodes in a frozen pass")

    for i, node in enumerate(dag.nodes):
        if node.id == node_id:
            # Validate status
            status_enum = TYPE_STATUS_MAP[node.type]
            valid_values = {s.value for s in status_enum}
            if status not in valid_values:
                raise ValueError(
                    f"Status '{status}' is not valid for node type "
                    f"'{node.type.value}'. Valid: {sorted(valid_values)}"
                )
            # Create new node with updated status
            new_node = GraphNode(
                id=node.id,
                type=node.type,
                name=node.name,
                description=node.description,
                status=status,
                contract=node.contract,
                agent=node.agent,
                evidence=node.evidence,
            )
            dag.nodes[i] = new_node
            return dag

    raise ValueError(f"Node '{node_id}' not found in DAG")


def add_trace_entry(dag: DAGPass, entry: ExecutionTraceEntry) -> DAGPass:
    """Append an execution trace entry."""
    if dag.outcome is not None:
        raise FrozenPassError("Cannot add trace entries to a frozen pass")
    dag.execution_trace.append(entry)
    return dag


def add_evidence(
    dag: DAGPass, node_id: str, evidence: list[EvidenceAttachment]
) -> DAGPass:
    """Append evidence attachments to a node.

    Creates a new GraphNode with combined evidence (frozen model requires replacement).
    """
    if dag.outcome is not None:
        raise FrozenPassError("Cannot add evidence to a frozen pass")

    for i, node in enumerate(dag.nodes):
        if node.id == node_id:
            new_node = GraphNode(
                id=node.id,
                type=node.type,
                name=node.name,
                description=node.description,
                status=node.status,
                contract=node.contract,
                agent=node.agent,
                evidence=list(node.evidence) + list(evidence),
            )
            dag.nodes[i] = new_node
            return dag

    raise ValueError(f"Node '{node_id}' not found in DAG")


def record_analysis(
    dag: DAGPass,
    node_id: str,
    status: str,
    evidence: list[EvidenceAttachment],
    trace_entry: ExecutionTraceEntry,
) -> DAGPass:
    """Record analysis results: update status, append evidence, add trace entry.

    Compound operation — if any step raises, nothing is persisted
    (the CLI only saves on full success).
    """
    dag = update_node_status(dag, node_id, status)
    dag = add_evidence(dag, node_id, evidence)
    dag = add_trace_entry(dag, trace_entry)
    return dag


def freeze_pass(
    dag: DAGPass,
    outcome: PassOutcome,
    detail: str,
    rationale: str,
) -> DAGPass:
    """Freeze the pass — set outcome, completed_at. Rejects further mutations."""
    if dag.outcome is not None:
        raise FrozenPassError("Pass is already frozen")
    dag.outcome = outcome
    dag.outcome_detail = detail
    dag.assembly_rationale = rationale
    dag.completed_at = _now_iso()
    return dag


def save_pass(dag: DAGPass, path: str | Path) -> None:
    """Save DAG pass to a JSON file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dag.model_dump_json(indent=2))


def load_pass(path: str | Path) -> DAGPass:
    """Load DAG pass from a JSON file."""
    path = Path(path)
    data = json.loads(path.read_text())
    return DAGPass.model_validate(data)
