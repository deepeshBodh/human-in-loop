"""Subgraph views filtered by edge type."""

import networkx as nx

from humaninloop_brain.entities.enums import EdgeType


def _edge_type_view(g: nx.MultiDiGraph, edge_type: EdgeType) -> nx.MultiDiGraph:
    """Create a subgraph view showing only edges of the given type."""
    type_val = edge_type.value
    return nx.subgraph_view(
        g,
        filter_edge=lambda u, v, k: k == type_val,
    )


def depends_on_view(g: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """View with only depends-on edges."""
    return _edge_type_view(g, EdgeType.depends_on)


def produces_view(g: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """View with only produces edges."""
    return _edge_type_view(g, EdgeType.produces)


def validates_view(g: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """View with only validates edges."""
    return _edge_type_view(g, EdgeType.validates)


def constrained_by_view(g: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """View with only constrained-by edges."""
    return _edge_type_view(g, EdgeType.constrained_by)


def informed_by_view(g: nx.MultiDiGraph) -> nx.MultiDiGraph:
    """View with only informed-by edges."""
    return _edge_type_view(g, EdgeType.informed_by)
