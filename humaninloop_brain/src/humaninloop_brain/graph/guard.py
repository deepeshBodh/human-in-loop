"""DAG acyclicity guard on depends-on edges."""

import networkx as nx

from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.entities.validation import ValidationResult, ValidationViolation
from humaninloop_brain.graph.loader import load_graph
from humaninloop_brain.graph.views import depends_on_view


def check_acyclicity(dag: DAGPass) -> ValidationResult:
    """Check that depends-on edges form a DAG (no cycles).

    Other edge types (validates, informed-by, etc.) may form cycles.
    Only depends-on edges must be acyclic.
    """
    g = load_graph(dag)
    dep_view = depends_on_view(g)

    try:
        cycle = nx.find_cycle(dep_view)
        cycle_path = " -> ".join(f"{u}" for u, v, *_ in cycle)
        return ValidationResult(
            valid=False,
            phase="acyclicity",
            violations=[
                ValidationViolation(
                    code="CYCLE",
                    severity="error",
                    message=f"Cycle in depends-on edges: {cycle_path}",
                )
            ],
        )
    except nx.NetworkXNoCycle:
        return ValidationResult(valid=True, phase="acyclicity")
