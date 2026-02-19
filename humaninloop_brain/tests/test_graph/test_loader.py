"""Tests for graph loader."""

import json
from pathlib import Path

from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.nodes import GraphNode, NodeHistoryEntry
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.graph.loader import load_graph


class TestLoadGraph:
    def test_empty_dag(self):
        dag = StrategyGraph(id="sg", workflow_id="w")
        g = load_graph(dag)
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_normal_pass(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        assert len(g.nodes) == 3
        assert len(g.edges) == 5

    def test_node_attributes(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        attrs = g.nodes["analyst-review"]
        assert attrs["type"] == "task"
        assert attrs["status"] == "pending"
        assert attrs["agent"] == "requirements-analyst"

    def test_edge_attributes(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        # depends-on edge from enrichment to analyst
        edge_data = g.get_edge_data("input-enrichment", "analyst-review")
        assert "depends_on" in edge_data
        assert edge_data["depends_on"]["edge_id"] == "edge-dep-enrich-analyst"

    def test_skip_enrichment_pass(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-skip-enrichment.json"))
        g = load_graph(dag)
        assert "input-enrichment" not in g.nodes
        assert "constitution-gate" in g.nodes

    def test_multi_edge_types(self, load_fixture):
        """Same node pair can have multiple edge types."""
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        edge_data = g.get_edge_data("analyst-review", "advocate-review")
        assert "depends_on" in edge_data
        assert "produces" in edge_data


class TestLoadStrategyGraph:
    def test_basic_strategy_graph(self):
        sg = StrategyGraph(
            id="sg-001",
            workflow_id="w",
            nodes=[
                GraphNode(
                    id="t",
                    type=NodeType.task,
                    name="n",
                    description="d",
                    status="pending",
                    history=[NodeHistoryEntry(pass_number=1, status="pending")],
                    last_active_pass=1,
                ),
            ],
            edges=[
                Edge(id="e", source="t", target="t", type=EdgeType.depends_on),
            ],
        )
        g = load_graph(sg)
        assert len(g.nodes) == 1
        assert len(g.edges) == 1
        assert g.nodes["t"]["type"] == "task"

    def test_verdict_attribute(self):
        sg = StrategyGraph(
            id="sg",
            workflow_id="w",
            nodes=[
                GraphNode(
                    id="g",
                    type=NodeType.gate,
                    name="n",
                    description="d",
                    status="completed",
                    verdict="ready",
                ),
            ],
        )
        g = load_graph(sg)
        assert g.nodes["g"]["verdict"] == "ready"

    def test_no_verdict_when_none(self):
        sg = StrategyGraph(
            id="sg",
            workflow_id="w",
            nodes=[
                GraphNode(
                    id="t",
                    type=NodeType.task,
                    name="n",
                    description="d",
                    status="pending",
                ),
            ],
        )
        g = load_graph(sg)
        assert "verdict" not in g.nodes["t"]

    def test_triggered_by_edge_attributes(self):
        sg = StrategyGraph(
            id="sg",
            workflow_id="w",
            edges=[
                Edge(
                    id="e-trig",
                    source="a",
                    target="a",
                    type=EdgeType.triggered_by,
                    source_pass=1,
                    target_pass=2,
                ),
            ],
            nodes=[
                GraphNode(
                    id="a",
                    type=NodeType.task,
                    name="n",
                    description="d",
                    status="pending",
                ),
            ],
        )
        g = load_graph(sg)
        edge_data = g.get_edge_data("a", "a")
        assert "triggered_by" in edge_data
        assert edge_data["triggered_by"]["source_pass"] == 1
        assert edge_data["triggered_by"]["target_pass"] == 2
