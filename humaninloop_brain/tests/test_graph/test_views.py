"""Tests for subgraph views."""

from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.graph.loader import load_graph
from humaninloop_brain.graph.views import (
    constrained_by_view,
    depends_on_view,
    informed_by_view,
    produces_view,
    validates_view,
)


class TestDependsOnView:
    def test_normal_pass(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = depends_on_view(g)
        edges = list(view.edges(keys=True))
        assert all(k == "depends-on" for _, _, k in edges)
        assert len(edges) == 2

    def test_empty(self):
        dag = DAGPass(id="p", workflow_id="w", pass_number=1)
        g = load_graph(dag)
        view = depends_on_view(g)
        assert len(list(view.edges())) == 0


class TestProducesView:
    def test_normal_pass(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = produces_view(g)
        edges = list(view.edges(keys=True))
        assert all(k == "produces" for _, _, k in edges)
        assert len(edges) == 2


class TestValidatesView:
    def test_normal_pass(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
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
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = constrained_by_view(g)
        assert len(list(view.edges())) == 0


class TestInformedByView:
    def test_no_informed_by_in_normal(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        g = load_graph(dag)
        view = informed_by_view(g)
        assert len(list(view.edges())) == 0
