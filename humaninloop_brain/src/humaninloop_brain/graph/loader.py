"""Load a DAGPass into a NetworkX MultiDiGraph."""

import networkx as nx

from humaninloop_brain.entities.dag_pass import DAGPass


def load_graph(dag: DAGPass) -> nx.MultiDiGraph:
    """Convert a DAGPass entity into a NetworkX MultiDiGraph.

    Nodes carry attributes: type, status, contract, agent.
    Edges are keyed by type and carry edge_id attribute.
    """
    g = nx.MultiDiGraph()

    for node in dag.nodes:
        g.add_node(
            node.id,
            type=node.type.value,
            status=node.status,
            contract=node.contract,
            agent=node.agent,
        )

    for edge in dag.edges:
        g.add_edge(
            edge.source,
            edge.target,
            key=edge.type.value,
            edge_id=edge.id,
        )

    return g
