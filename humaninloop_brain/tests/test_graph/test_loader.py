"""Tests for graph loader."""

from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.graph.loader import load_graph


class TestLoadGraph:
    def test_empty_dag(self):
        dag = DAGPass(id="p", workflow_id="w", pass_number=1)
        g = load_graph(dag)
        assert len(g.nodes) == 0
        assert len(g.edges) == 0

    def test_normal_pass(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        assert len(g.nodes) == 3
        assert len(g.edges) == 5

    def test_node_attributes(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        attrs = g.nodes["analyst-review"]
        assert attrs["type"] == "task"
        assert attrs["status"] == "pending"
        assert attrs["agent"] == "requirements-analyst"

    def test_edge_attributes(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        # depends-on edge from enrichment to analyst
        edge_data = g.get_edge_data("input-enrichment", "analyst-review")
        assert "depends-on" in edge_data
        assert edge_data["depends-on"]["edge_id"] == "edge-dep-enrich-analyst"

    def test_skip_enrichment_pass(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-skip-enrichment.json"))
        g = load_graph(dag)
        assert "input-enrichment" not in g.nodes
        assert "constitution-gate" in g.nodes

    def test_multi_edge_types(self, load_fixture):
        """Same node pair can have multiple edge types."""
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        edge_data = g.get_edge_data("analyst-review", "advocate-review")
        assert "depends-on" in edge_data
        assert "produces" in edge_data
