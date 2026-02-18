"""Load a StrategyGraph into a NetworkX MultiDiGraph."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

import networkx as nx

if TYPE_CHECKING:
    from humaninloop_brain.entities.edges import Edge
    from humaninloop_brain.entities.nodes import GraphNode


@runtime_checkable
class HasNodesAndEdges(Protocol):
    """Protocol for graph containers with .nodes and .edges."""

    nodes: list[GraphNode]
    edges: list[Edge]


def load_graph(dag: HasNodesAndEdges) -> nx.MultiDiGraph:
    """Convert a graph container into a NetworkX MultiDiGraph.

    Nodes carry attributes: type, status, contract, agent, verdict.
    Edges are keyed by type and carry edge_id attribute.
    """
    g = nx.MultiDiGraph()

    for node in dag.nodes:
        attrs = {
            "type": node.type.value,
            "status": node.status,
            "contract": node.contract,
            "agent": node.agent,
        }
        if node.verdict is not None:
            attrs["verdict"] = node.verdict
        g.add_node(node.id, **attrs)

    for edge in dag.edges:
        edge_attrs = {"edge_id": edge.id}
        if edge.source_pass is not None:
            edge_attrs["source_pass"] = edge.source_pass
        if edge.target_pass is not None:
            edge_attrs["target_pass"] = edge.target_pass
        g.add_edge(
            edge.source,
            edge.target,
            key=edge.type.value,
            **edge_attrs,
        )

    return g
