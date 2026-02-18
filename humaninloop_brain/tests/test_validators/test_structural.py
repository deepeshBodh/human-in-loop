"""Tests for structural validator."""

import json
from pathlib import Path

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.nodes import (
    ArtifactConsumption,
    GraphNode,
    NodeContract,
    NodeHistoryEntry,
)
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.validators.structural import validate_structure


def _make_catalog(load_fixture):
    return NodeCatalog.model_validate(load_fixture("specify-catalog.json"))


class TestStep1UniqueNodeIds:
    def test_duplicate_node_id(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes = [
            GraphNode(id="dup", type=NodeType.task, name="n", description="d", status="pending"),
            GraphNode(id="dup", type=NodeType.task, name="n2", description="d", status="pending"),
        ]
        result = validate_structure(dag, catalog)
        assert any(v.code == "DUPLICATE_NODE_ID" for v in result.violations)


class TestStep2EdgeReferences:
    def test_dangling_source(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes = [
            GraphNode(id="a", type=NodeType.task, name="n", description="d", status="pending"),
        ]
        dag.edges = [
            Edge(id="e", source="nonexistent", target="a", type=EdgeType.depends_on),
        ]
        result = validate_structure(dag, catalog)
        assert any(v.code == "DANGLING_EDGE_SOURCE" for v in result.violations)

    def test_dangling_target(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes = [
            GraphNode(id="a", type=NodeType.task, name="n", description="d", status="pending"),
        ]
        dag.edges = [
            Edge(id="e", source="a", target="nonexistent", type=EdgeType.depends_on),
        ]
        result = validate_structure(dag, catalog)
        assert any(v.code == "DANGLING_EDGE_TARGET" for v in result.violations)


class TestStep4SelfLoops:
    def test_self_loop(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes = [
            GraphNode(id="a", type=NodeType.task, name="n", description="d", status="pending"),
        ]
        dag.edges = [
            Edge(id="e", source="a", target="a", type=EdgeType.depends_on),
        ]
        result = validate_structure(dag, catalog)
        assert any(v.code == "SELF_LOOP" for v in result.violations)


class TestStep5DuplicateEdges:
    def test_duplicate_edge(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes = [
            GraphNode(id="a", type=NodeType.task, name="n", description="d", status="pending"),
            GraphNode(id="b", type=NodeType.task, name="n", description="d", status="pending"),
        ]
        dag.edges = [
            Edge(id="e1", source="a", target="b", type=EdgeType.depends_on),
            Edge(id="e2", source="a", target="b", type=EdgeType.depends_on),
        ]
        result = validate_structure(dag, catalog)
        assert any(v.code == "DUPLICATE_EDGE" for v in result.violations)


class TestStep6EndpointConstraints:
    def test_invalid_produces_source(self, load_fixture):
        """produces edge from gate (only task allowed)."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph.model_validate(load_fixture("invalid-endpoint.json"))
        result = validate_structure(dag, catalog)
        assert any(v.code == "INVALID_EDGE_SOURCE" for v in result.violations)


class TestStep7Acyclicity:
    def test_cycle(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph.model_validate(load_fixture("invalid-cycle.json"))
        result = validate_structure(dag, catalog)
        assert any(v.code == "CYCLE" for v in result.violations)


class TestStep8Contracts:
    def test_unsatisfied_contract(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph.model_validate(load_fixture("invalid-contract.json"))
        result = validate_structure(dag, catalog)
        assert any(v.code == "UNSATISFIED_CONTRACT" for v in result.violations)


class TestValidPasses:
    def test_normal_pass(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        result = validate_structure(dag, catalog)
        assert result.valid is True

    def test_skip_enrichment(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph.model_validate(load_fixture("pass-skip-enrichment.json"))
        result = validate_structure(dag, catalog)
        assert result.valid is True

    def test_with_research(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph.model_validate(load_fixture("pass-with-research.json"))
        result = validate_structure(dag, catalog)
        assert result.valid is True

    def test_with_clarification(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph.model_validate(load_fixture("pass-with-clarification.json"))
        result = validate_structure(dag, catalog)
        assert result.valid is True

    def test_empty_dag(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        result = validate_structure(dag, catalog)
        assert result.valid is True


class TestV3TriggeredByEdges:
    """V3-specific: triggered-by self-loops and duplicate detection."""

    def test_triggered_by_self_loop_allowed(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        sg = StrategyGraph(
            id="sg", workflow_id="w",
            nodes=[
                GraphNode(
                    id="a", type=NodeType.task, name="n",
                    description="d", status="pending",
                ),
            ],
            edges=[
                Edge(
                    id="e-trig", source="a", target="a",
                    type=EdgeType.triggered_by,
                    source_pass=1, target_pass=2,
                ),
            ],
        )
        result = validate_structure(sg, catalog)
        assert not any(v.code == "SELF_LOOP" for v in result.violations)

    def test_triggered_by_different_passes_not_duplicate(self, load_fixture):
        catalog = _make_catalog(load_fixture)
        sg = StrategyGraph(
            id="sg", workflow_id="w",
            nodes=[
                GraphNode(
                    id="a", type=NodeType.task, name="n",
                    description="d", status="pending",
                ),
            ],
            edges=[
                Edge(
                    id="e-trig-1", source="a", target="a",
                    type=EdgeType.triggered_by,
                    source_pass=1, target_pass=2,
                ),
                Edge(
                    id="e-trig-2", source="a", target="a",
                    type=EdgeType.triggered_by,
                    source_pass=2, target_pass=3,
                ),
            ],
        )
        result = validate_structure(sg, catalog)
        assert not any(v.code == "DUPLICATE_EDGE" for v in result.violations)

    def test_v3_gate_completed_status_valid(self, load_fixture):
        """In v3, gate with 'completed' status is valid."""
        catalog = _make_catalog(load_fixture)
        sg = StrategyGraph(
            id="sg", workflow_id="w",
            nodes=[
                GraphNode(
                    id="g", type=NodeType.gate, name="n",
                    description="d", status="completed",
                    schema_version="3.0.0",
                ),
            ],
        )
        result = validate_structure(sg, catalog)
        assert not any(v.code == "INVALID_STATUS" for v in result.violations)


class TestCollectsAllViolations:
    def test_multiple_violations(self, load_fixture):
        """Structural validator collects ALL violations, not just first."""
        catalog = _make_catalog(load_fixture)
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes = [
            GraphNode(id="a", type=NodeType.task, name="n", description="d", status="pending"),
            GraphNode(id="a", type=NodeType.task, name="n2", description="d", status="pending"),
        ]
        dag.edges = [
            Edge(id="e", source="a", target="a", type=EdgeType.depends_on),
            Edge(id="e2", source="x", target="a", type=EdgeType.depends_on),
        ]
        result = validate_structure(dag, catalog)
        codes = {v.code for v in result.violations}
        assert "DUPLICATE_NODE_ID" in codes
        assert "SELF_LOOP" in codes
        assert "DANGLING_EDGE_SOURCE" in codes
