"""Invariant checker — assembly-time system invariant verification."""

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.validation import ValidationResult, ValidationViolation
from humaninloop_brain.graph.guard import check_acyclicity
from humaninloop_brain.graph.loader import load_graph
from humaninloop_brain.graph.views import depends_on_view


def check_invariants(dag: DAGPass, catalog: NodeCatalog) -> ValidationResult:
    """Check assembly-time invariants.

    INV-001: Task output must pass through gate before milestone.
    INV-002: Constitution gate exists before spec task nodes.
    INV-003: validates edges originate from gate nodes.
    INV-005: depends-on acyclicity (delegates to guard).

    Runtime invariant INV-004 is NOT checked here.
    """
    violations: list[ValidationViolation] = []

    g = load_graph(dag)
    node_types = {n.id: n.type for n in dag.nodes}

    # INV-001: Every task output must pass through a gate before milestone
    milestones = [n for n in dag.nodes if n.type == NodeType.milestone]
    gates = {n.id for n in dag.nodes if n.type == NodeType.gate}
    tasks = {n.id for n in dag.nodes if n.type == NodeType.task}

    if milestones and tasks:
        dep_view = depends_on_view(g)
        for milestone in milestones:
            # Check if there's a gate between every task and this milestone
            # by verifying that all paths from tasks to milestone pass through a gate
            import networkx as nx

            for task_id in tasks:
                if not nx.has_path(dep_view, task_id, milestone.id):
                    continue
                # Check all simple paths from task to milestone
                paths = nx.all_simple_paths(dep_view, task_id, milestone.id)
                for path in paths:
                    # Check if any gate exists on this path (excluding endpoints)
                    intermediate = path[1:-1]
                    if not any(n in gates for n in intermediate):
                        violations.append(
                            ValidationViolation(
                                code="INV-001",
                                severity="error",
                                message=(
                                    f"Task '{task_id}' has path to milestone "
                                    f"'{milestone.id}' without passing through a gate"
                                ),
                                node_id=milestone.id,
                            )
                        )
                        break  # One violation per task-milestone pair

    # INV-002: Constitution gate must exist before spec task nodes
    constitution_gates = [
        n.id for n in dag.nodes
        if n.type == NodeType.gate
        and any(
            c.artifact == "constitution.md" for c in n.contract.consumes
        )
    ]
    spec_tasks = [
        n.id for n in dag.nodes
        if n.type == NodeType.task
        and any(
            c.artifact == "constitution.md" for c in n.contract.consumes
        )
    ]

    if spec_tasks and not constitution_gates:
        for task_id in spec_tasks:
            violations.append(
                ValidationViolation(
                    code="INV-002",
                    severity="error",
                    message=(
                        f"Task '{task_id}' consumes constitution.md but "
                        f"no constitution gate exists in the DAG"
                    ),
                    node_id=task_id,
                )
            )

    # INV-003: validates edges must originate from gate nodes
    for edge in dag.edges:
        if edge.type == EdgeType.validates:
            source_type = node_types.get(edge.source)
            if source_type != NodeType.gate:
                violations.append(
                    ValidationViolation(
                        code="INV-003",
                        severity="error",
                        message=(
                            f"validates edge '{edge.id}' originates from "
                            f"'{edge.source}' (type: {source_type}) "
                            f"but must originate from a gate node"
                        ),
                        edge_id=edge.id,
                    )
                )

    # INV-005: depends-on acyclicity
    acyclicity = check_acyclicity(dag)
    violations.extend(
        ValidationViolation(
            code="INV-005",
            severity=v.severity,
            message=v.message,
        )
        for v in acyclicity.violations
    )

    return ValidationResult(
        valid=len(violations) == 0,
        phase="invariants",
        violations=violations,
    )
