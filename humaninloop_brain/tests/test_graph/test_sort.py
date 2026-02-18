"""Tests for topological sort."""

from humaninloop_brain.entities.dag_pass import DAGPass
from humaninloop_brain.graph.sort import execution_order


class TestExecutionOrder:
    def test_normal_pass(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        order = execution_order(dag)
        assert order == ["input-enrichment", "analyst-review", "advocate-review"]

    def test_skip_enrichment(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-skip-enrichment.json"))
        order = execution_order(dag)
        assert order == ["constitution-gate", "analyst-review", "advocate-review"]

    def test_with_research(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-with-research.json"))
        order = execution_order(dag)
        assert order == ["targeted-research", "analyst-review", "advocate-review"]

    def test_with_clarification(self, load_fixture):
        dag = DAGPass.model_validate(load_fixture("pass-with-clarification.json"))
        order = execution_order(dag)
        assert order == ["human-clarification", "analyst-review", "advocate-review"]

    def test_deterministic(self, load_fixture):
        """Same input always produces same output."""
        dag = DAGPass.model_validate(load_fixture("pass-normal.json"))
        order1 = execution_order(dag)
        order2 = execution_order(dag)
        assert order1 == order2

    def test_empty_dag(self):
        dag = DAGPass(id="p", workflow_id="w", pass_number=1)
        assert execution_order(dag) == []
