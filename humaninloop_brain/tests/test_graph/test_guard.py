"""Tests for DAG guard (acyclicity check)."""

from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.graph.guard import check_acyclicity


class TestCheckAcyclicity:
    def test_valid_normal_pass(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        result = check_acyclicity(dag)
        assert result.valid is True
        assert result.violations == []

    def test_valid_skip_enrichment(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-skip-enrichment.json"))
        result = check_acyclicity(dag)
        assert result.valid is True

    def test_cycle_detected(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("invalid-cycle.json"))
        result = check_acyclicity(dag)
        assert result.valid is False
        assert len(result.violations) == 1
        assert result.violations[0].code == "CYCLE"
        assert "depends-on" in result.violations[0].message

    def test_empty_dag(self):
        dag = StrategyGraph(id="sg", workflow_id="w")
        result = check_acyclicity(dag)
        assert result.valid is True

    def test_validates_edges_not_checked(self, load_fixture):
        """validates edges can form cycles — only depends-on checked."""
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        # normal pass has advocate-review -> analyst-review validates edge
        # and analyst-review -> advocate-review depends-on edge
        # This is NOT a depends-on cycle
        result = check_acyclicity(dag)
        assert result.valid is True
