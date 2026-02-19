"""Tests for invariant checker."""

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.nodes import (
    ArtifactConsumption,
    GraphNode,
    NodeContract,
)
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.validators.invariants import check_invariants


def _make_catalog(load_fixture):
    return NodeCatalog.model_validate(load_fixture("specify-catalog.json"))


class TestINV001:
    """Task output must pass through gate before milestone."""

    def test_valid_with_gate_before_milestone(self, load_fixture):
        """Task -> Gate -> Milestone is valid."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(
            id="sg", workflow_id="w",
            nodes=[
                GraphNode(
                    id="task-1", type=NodeType.task, name="t", description="d",
                    status="pending", contract=NodeContract(produces=["out"]),
                ),
                GraphNode(
                    id="gate-1", type=NodeType.gate, name="g", description="d",
                    status="pending",
                    contract=NodeContract(consumes=[ArtifactConsumption(artifact="out")]),
                ),
                GraphNode(
                    id="mile-1", type=NodeType.milestone, name="m", description="d",
                    status="pending",
                ),
            ],
            edges=[
                Edge(id="e1", source="task-1", target="gate-1", type=EdgeType.depends_on),
                Edge(id="e2", source="gate-1", target="mile-1", type=EdgeType.depends_on),
            ],
        )
        result = check_invariants(dag, catalog)
        inv001 = [v for v in result.violations if v.code == "INV-001"]
        assert len(inv001) == 0

    def test_invalid_task_to_milestone_no_gate(self, load_fixture):
        """Task -> Milestone without gate violates INV-001."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(
            id="sg", workflow_id="w",
            nodes=[
                GraphNode(
                    id="task-1", type=NodeType.task, name="t", description="d",
                    status="pending", contract=NodeContract(produces=["out"]),
                ),
                GraphNode(
                    id="mile-1", type=NodeType.milestone, name="m", description="d",
                    status="pending",
                ),
            ],
            edges=[
                Edge(id="e1", source="task-1", target="mile-1", type=EdgeType.depends_on),
            ],
        )
        result = check_invariants(dag, catalog)
        inv001 = [v for v in result.violations if v.code == "INV-001"]
        assert len(inv001) == 1

    def test_no_milestone_no_violation(self, load_fixture):
        """If no milestones exist, INV-001 does not apply."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        result = check_invariants(dag, catalog)
        inv001 = [v for v in result.violations if v.code == "INV-001"]
        assert len(inv001) == 0


class TestINV002:
    """Constitution gate must exist before spec task nodes."""

    def test_valid_with_constitution_gate(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-skip-enrichment.json"))
        catalog = _make_catalog(load_fixture)
        result = check_invariants(dag, catalog)
        inv002 = [v for v in result.violations if v.code == "INV-002"]
        assert len(inv002) == 0

    def test_invalid_no_constitution_gate(self, load_fixture):
        """Task consuming constitution.md without constitution gate."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(
            id="sg", workflow_id="w",
            nodes=[
                GraphNode(
                    id="analyst", type=NodeType.task, name="a", description="d",
                    status="pending",
                    contract=NodeContract(
                        consumes=[ArtifactConsumption(artifact="constitution.md")]
                    ),
                ),
            ],
        )
        result = check_invariants(dag, catalog)
        inv002 = [v for v in result.violations if v.code == "INV-002"]
        assert len(inv002) == 1

    def test_invalid_gate_exists_but_pending(self, load_fixture):
        """Gate exists but has not passed — INV-002 should fire."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(
            id="sg", workflow_id="w",
            nodes=[
                GraphNode(
                    id="constitution-gate", type=NodeType.gate,
                    name="Constitution Check", description="d",
                    status="pending",
                    contract=NodeContract(
                        consumes=[ArtifactConsumption(artifact="constitution.md")]
                    ),
                ),
                GraphNode(
                    id="analyst", type=NodeType.task, name="a", description="d",
                    status="pending",
                    contract=NodeContract(
                        consumes=[ArtifactConsumption(artifact="constitution.md")]
                    ),
                ),
            ],
        )
        result = check_invariants(dag, catalog)
        inv002 = [v for v in result.violations if v.code == "INV-002"]
        assert len(inv002) == 1
        assert "has not passed" in inv002[0].message


class TestINV003:
    """validates edges must originate from gate nodes."""

    def test_valid_validates_from_gate(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        catalog = _make_catalog(load_fixture)
        result = check_invariants(dag, catalog)
        inv003 = [v for v in result.violations if v.code == "INV-003"]
        assert len(inv003) == 0

    def test_invalid_validates_from_task(self, load_fixture):
        """validates edge from task node violates INV-003."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(
            id="sg", workflow_id="w",
            nodes=[
                GraphNode(
                    id="task-1", type=NodeType.task, name="t", description="d",
                    status="pending",
                ),
                GraphNode(
                    id="task-2", type=NodeType.task, name="t2", description="d",
                    status="pending",
                ),
            ],
            edges=[
                Edge(
                    id="bad-val", source="task-1", target="task-2",
                    type=EdgeType.validates,
                ),
            ],
        )
        result = check_invariants(dag, catalog)
        inv003 = [v for v in result.violations if v.code == "INV-003"]
        assert len(inv003) == 1


class TestINV004:
    """Maximum 5 passes per workflow invocation."""

    def test_under_limit_no_warning(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        sg = StrategyGraph(id="sg", workflow_id="w", current_pass=3)
        result = check_invariants(sg, catalog)
        inv004 = [v for v in result.violations if v.code == "INV-004"]
        assert len(inv004) == 0

    def test_over_limit_warning(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        sg = StrategyGraph(id="sg", workflow_id="w", current_pass=6)
        result = check_invariants(sg, catalog)
        inv004 = [v for v in result.violations if v.code == "INV-004"]
        assert len(inv004) == 1
        assert inv004[0].severity == "warning"


class TestINV005:
    """depends-on edges must be acyclic."""

    def test_cycle_detected(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("invalid-cycle.json"))
        catalog = _make_catalog(load_fixture)
        result = check_invariants(dag, catalog)
        inv005 = [v for v in result.violations if v.code == "INV-005"]
        assert len(inv005) == 1

    def test_no_cycle(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        catalog = _make_catalog(load_fixture)
        result = check_invariants(dag, catalog)
        inv005 = [v for v in result.violations if v.code == "INV-005"]
        assert len(inv005) == 0
