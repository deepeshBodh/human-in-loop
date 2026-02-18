"""Structural validator — 9-step validation collecting all violations."""

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.entities.enums import TYPE_STATUS_MAP
from humaninloop_brain.entities.validation import ValidationResult, ValidationViolation
from humaninloop_brain.graph.guard import check_acyclicity
from humaninloop_brain.validators.contracts import check_contracts
from humaninloop_brain.validators.invariants import check_invariants


def validate_structure(dag: DAGPass, catalog: NodeCatalog) -> ValidationResult:
    """Run 9-step structural validation, collecting all violations.

    Steps:
    1. Unique node IDs
    2. Edge references exist
    3. Type-status validity (defense in depth)
    4. No self-loops
    5. No duplicate edges (same source+target+type)
    6. Edge endpoint constraints match catalog
    7. Acyclicity (delegates to guard)
    8. Contract satisfiability (delegates to contracts.py)
    9. Invariant compliance (delegates to invariants.py)
    """
    violations: list[ValidationViolation] = []

    # Step 1: Unique node IDs
    seen_ids: set[str] = set()
    for node in dag.nodes:
        if node.id in seen_ids:
            violations.append(
                ValidationViolation(
                    code="DUPLICATE_NODE_ID",
                    severity="error",
                    message=f"Duplicate node ID: '{node.id}'",
                    node_id=node.id,
                )
            )
        seen_ids.add(node.id)

    # Step 2: Edge references exist
    node_ids = {n.id for n in dag.nodes}
    for edge in dag.edges:
        if edge.source not in node_ids:
            violations.append(
                ValidationViolation(
                    code="DANGLING_EDGE_SOURCE",
                    severity="error",
                    message=(
                        f"Edge '{edge.id}' references nonexistent "
                        f"source node '{edge.source}'"
                    ),
                    edge_id=edge.id,
                )
            )
        if edge.target not in node_ids:
            violations.append(
                ValidationViolation(
                    code="DANGLING_EDGE_TARGET",
                    severity="error",
                    message=(
                        f"Edge '{edge.id}' references nonexistent "
                        f"target node '{edge.target}'"
                    ),
                    edge_id=edge.id,
                )
            )

    # Step 3: Type-status validity (defense in depth)
    node_types = {n.id: n.type for n in dag.nodes}
    for node in dag.nodes:
        status_enum = TYPE_STATUS_MAP[node.type]
        valid_values = {s.value for s in status_enum}
        if node.status not in valid_values:
            violations.append(
                ValidationViolation(
                    code="INVALID_STATUS",
                    severity="error",
                    message=(
                        f"Node '{node.id}' has status '{node.status}' "
                        f"which is invalid for type '{node.type.value}'"
                    ),
                    node_id=node.id,
                )
            )

    # Step 4: No self-loops
    for edge in dag.edges:
        if edge.source == edge.target:
            violations.append(
                ValidationViolation(
                    code="SELF_LOOP",
                    severity="error",
                    message=f"Edge '{edge.id}' is a self-loop on '{edge.source}'",
                    edge_id=edge.id,
                )
            )

    # Step 5: No duplicate edges (same source+target+type)
    seen_edges: set[tuple[str, str, str]] = set()
    for edge in dag.edges:
        key = (edge.source, edge.target, edge.type.value)
        if key in seen_edges:
            violations.append(
                ValidationViolation(
                    code="DUPLICATE_EDGE",
                    severity="error",
                    message=(
                        f"Duplicate edge: {edge.source} -> {edge.target} "
                        f"({edge.type.value})"
                    ),
                    edge_id=edge.id,
                )
            )
        seen_edges.add(key)

    # Step 6: Edge endpoint constraints
    for edge in dag.edges:
        constraint = catalog.get_edge_constraint(edge.type)
        if constraint is None:
            continue
        source_type = node_types.get(edge.source)
        target_type = node_types.get(edge.target)
        if source_type is not None and source_type not in constraint.valid_sources:
            violations.append(
                ValidationViolation(
                    code="INVALID_EDGE_SOURCE",
                    severity="error",
                    message=(
                        f"Edge '{edge.id}' ({edge.type.value}): source "
                        f"'{edge.source}' is type '{source_type.value}' "
                        f"but allowed sources are "
                        f"{[t.value for t in constraint.valid_sources]}"
                    ),
                    edge_id=edge.id,
                )
            )
        if target_type is not None and target_type not in constraint.valid_targets:
            violations.append(
                ValidationViolation(
                    code="INVALID_EDGE_TARGET",
                    severity="error",
                    message=(
                        f"Edge '{edge.id}' ({edge.type.value}): target "
                        f"'{edge.target}' is type '{target_type.value}' "
                        f"but allowed targets are "
                        f"{[t.value for t in constraint.valid_targets]}"
                    ),
                    edge_id=edge.id,
                )
            )

    # Step 7: Acyclicity
    acyclicity = check_acyclicity(dag)
    violations.extend(acyclicity.violations)

    # Step 8: Contract satisfiability
    contracts = check_contracts(dag, catalog)
    violations.extend(contracts.violations)

    # Step 9: Invariant compliance
    invariants = check_invariants(dag, catalog)
    # Filter out INV-005 since acyclicity already checked in step 7
    for v in invariants.violations:
        if v.code != "INV-005":
            violations.append(v)

    return ValidationResult(
        valid=len([v for v in violations if v.severity == "error"]) == 0,
        phase="structural",
        violations=violations,
    )
