"""Topological sort on depends-on edges for deterministic execution order."""

from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.graph.loader import load_graph
from humaninloop_brain.graph.views import depends_on_view

import networkx as nx


def execution_order(dag: DAGPass) -> list[str]:
    """Return lexicographic topological sort on depends-on edges.

    Only depends-on edges are considered for ordering.
    Uses lexicographic sort for determinism across runs.
    """
    g = load_graph(dag)
    dep_view = depends_on_view(g)
    return list(nx.lexicographical_topological_sort(dep_view))
