"""Contract checker — verifies artifact chains are satisfiable."""

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.entities.validation import ValidationResult, ValidationViolation

# System-level artifacts that are always available (not produced by any node)
SYSTEM_ARTIFACTS = frozenset({"raw-input", "constitution.md"})


def check_contracts(dag: DAGPass, catalog: NodeCatalog) -> ValidationResult:
    """Check that required consumed artifacts are produced by upstream nodes.

    - Required artifacts must be produced by some node in the DAG or be
      a system artifact.
    - Optional artifacts generate no violations.
    """
    violations: list[ValidationViolation] = []

    # Collect all artifacts produced by nodes in this DAG
    produced: set[str] = set(SYSTEM_ARTIFACTS)
    for node in dag.nodes:
        for artifact in node.contract.produces:
            produced.add(artifact)

    # Check each node's consumed artifacts
    for node in dag.nodes:
        for consumed in node.contract.consumes:
            if not consumed.required:
                continue
            if consumed.artifact not in produced:
                violations.append(
                    ValidationViolation(
                        code="UNSATISFIED_CONTRACT",
                        severity="error",
                        message=(
                            f"Node '{node.id}' requires artifact "
                            f"'{consumed.artifact}' but no node produces it"
                        ),
                        node_id=node.id,
                    )
                )

    return ValidationResult(
        valid=len(violations) == 0,
        phase="contracts",
        violations=violations,
    )
