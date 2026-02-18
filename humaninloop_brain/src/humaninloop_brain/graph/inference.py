"""Edge inference when adding a new node to a DAG pass."""

from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.catalog import NodeCatalog


def infer_edges(
    node_id: str, dag: DAGPass, catalog: NodeCatalog
) -> list[Edge]:
    """Infer edges when adding a node to a DAG.

    Algorithm:
    1. Look up the new node's contract from the catalog.
    2. For each consumed artifact, find existing nodes that produce it.
       - Infer a 'produces' edge (producer -> new node).
       - Infer a 'depends-on' edge (producer -> new node).
    3. If the new node is a gate and consumes output of a task, infer
       a 'validates' edge (new gate -> task).

    Edge IDs follow the pattern: "inferred-{type}-{source}-{target}"
    """
    cat_node = catalog.get_node(node_id)
    if cat_node is None:
        return []

    # Build lookup: artifact -> list of node IDs that produce it
    producers: dict[str, list[str]] = {}
    for existing_node in dag.nodes:
        if existing_node.id == node_id:
            continue
        for artifact in existing_node.contract.produces:
            producers.setdefault(artifact, []).append(existing_node.id)

    # Build lookup for node types
    node_types: dict[str, NodeType] = {}
    for n in dag.nodes:
        node_types[n.id] = n.type

    inferred: list[Edge] = []
    seen_edges: set[tuple[str, str, str]] = set()

    # Collect existing edges to avoid duplicates
    for e in dag.edges:
        seen_edges.add((e.source, e.target, e.type.value))

    for consumed in cat_node.contract.consumes:
        artifact = consumed.artifact
        if artifact not in producers:
            continue

        for producer_id in producers[artifact]:
            # Infer depends-on edge
            dep_key = (producer_id, node_id, EdgeType.depends_on.value)
            if dep_key not in seen_edges:
                inferred.append(
                    Edge(
                        id=f"inferred-depends-on-{producer_id}-{node_id}",
                        source=producer_id,
                        target=node_id,
                        type=EdgeType.depends_on,
                    )
                )
                seen_edges.add(dep_key)

            # Infer produces edge (only if source is a task)
            source_type = node_types.get(producer_id)
            target_type = cat_node.type
            if source_type == NodeType.task and target_type in (
                NodeType.task,
                NodeType.gate,
            ):
                prod_key = (producer_id, node_id, EdgeType.produces.value)
                if prod_key not in seen_edges:
                    inferred.append(
                        Edge(
                            id=f"inferred-produces-{producer_id}-{node_id}",
                            source=producer_id,
                            target=node_id,
                            type=EdgeType.produces,
                        )
                    )
                    seen_edges.add(prod_key)

            # Infer validates edge (gate -> task it consumes from)
            if (
                cat_node.type == NodeType.gate
                and source_type == NodeType.task
            ):
                val_key = (node_id, producer_id, EdgeType.validates.value)
                if val_key not in seen_edges:
                    inferred.append(
                        Edge(
                            id=f"inferred-validates-{node_id}-{producer_id}",
                            source=node_id,
                            target=producer_id,
                            type=EdgeType.validates,
                        )
                    )
                    seen_edges.add(val_key)

    return inferred
