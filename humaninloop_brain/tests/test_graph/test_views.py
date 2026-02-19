"""Tests for subgraph views."""

from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.nodes import GraphNode
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.graph.loader import load_graph
from humaninloop_brain.graph.views import (
    constrained_by_view,
    depends_on_view,
    informed_by_view,
    produces_view,
    triggered_by_view,
    validates_view,
)


class TestDependsOnView:
    def test_normal_pass(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = depends_on_view(g)
        edges = list(view.edges(keys=True))
        assert all(k == "depends_on" for _, _, k in edges)
        assert len(edges) == 2

    def test_empty(self):
        dag = StrategyGraph(id="sg", workflow_id="w")
        g = load_graph(dag)
        view = depends_on_view(g)
        assert len(list(view.edges())) == 0


class TestProducesView:
    def test_normal_pass(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = produces_view(g)
        edges = list(view.edges(keys=True))
        assert all(k == "produces" for _, _, k in edges)
        assert len(edges) == 2


class TestValidatesView:
    def test_normal_pass(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = validates_view(g)
        edges = list(view.edges(keys=True))
        assert all(k == "validates" for _, _, k in edges)
        assert len(edges) == 1
        # advocate validates analyst
        u, v, _ = edges[0]
        assert u == "advocate-review"
        assert v == "analyst-review"


class TestConstrainedByView:
    def test_no_constrained_by_in_normal(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = constrained_by_view(g)
        assert len(list(view.edges())) == 0


class TestInformedByView:
    def test_no_informed_by_in_normal(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = informed_by_view(g)
        assert len(list(view.edges())) == 0


class TestTriggeredByView:
    def test_triggered_by_edges(self):
        sg = StrategyGraph(
            id="sg",
            workflow_id="w",
            nodes=[
                GraphNode(
                    id="a", type=NodeType.task, name="n",
                    description="d", status="pending",
                ),
            ],
            edges=[
                Edge(
                    id="e-dep", source="a", target="a",
                    type=EdgeType.depends_on,
                ),
                Edge(
                    id="e-trig", source="a", target="a",
                    type=EdgeType.triggered_by,
                    source_pass=1, target_pass=2,
                ),
            ],
        )
        g = load_graph(sg)
        view = triggered_by_view(g)
        edges = list(view.edges(keys=True))
        assert len(edges) == 1
        assert edges[0][2] == "triggered_by"

    def test_no_triggered_by_in_normal_graph(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = triggered_by_view(g)
        assert len(list(view.edges())) == 0
