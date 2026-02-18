"""Tests for contract checker."""

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.strategy_graph import StrategyGraph
from humaninloop_brain.entities.enums import NodeType
from humaninloop_brain.entities.nodes import (
    ArtifactConsumption,
    GraphNode,
    NodeContract,
)
from humaninloop_brain.validators.contracts import SYSTEM_ARTIFACTS, check_contracts


class TestCheckContracts:
    def test_valid_normal_pass(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-normal.json"))
        catalog = NodeCatalog.model_validate(load_fixture("specify-catalog.json"))
        result = check_contracts(dag, catalog)
        assert result.valid is True

    def test_valid_skip_enrichment(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("pass-skip-enrichment.json"))
        catalog = NodeCatalog.model_validate(load_fixture("specify-catalog.json"))
        result = check_contracts(dag, catalog)
        assert result.valid is True

    def test_invalid_contract(self, load_fixture):
        dag = StrategyGraph.model_validate(load_fixture("invalid-contract.json"))
        catalog = NodeCatalog.model_validate(load_fixture("specify-catalog.json"))
        result = check_contracts(dag, catalog)
        assert result.valid is False
        assert any(v.code == "UNSATISFIED_CONTRACT" for v in result.violations)
        assert any("enriched-input" in v.message for v in result.violations)

    def test_system_artifacts_always_available(self):
        """raw-input and constitution.md are always available."""
        assert "raw-input" in SYSTEM_ARTIFACTS
        assert "constitution.md" in SYSTEM_ARTIFACTS

    def test_system_artifacts_satisfy_contracts(self, load_fixture):
        """Nodes consuming system artifacts don't need producers."""
        catalog = NodeCatalog.model_validate(load_fixture("specify-catalog.json"))
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes.append(
            GraphNode(
                id="test",
                type=NodeType.task,
                name="t",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[
                        ArtifactConsumption(artifact="raw-input", required=True),
                        ArtifactConsumption(artifact="constitution.md", required=True),
                    ],
                ),
            )
        )
        result = check_contracts(dag, catalog)
        assert result.valid is True

    def test_optional_artifacts_no_violation(self, load_fixture):
        catalog = NodeCatalog.model_validate(load_fixture("specify-catalog.json"))
        dag = StrategyGraph(id="sg", workflow_id="w")
        dag.nodes.append(
            GraphNode(
                id="test",
                type=NodeType.task,
                name="t",
                description="d",
                status="pending",
                contract=NodeContract(
                    consumes=[
                        ArtifactConsumption(
                            artifact="nonexistent", required=False
                        ),
                    ],
                ),
            )
        )
        result = check_contracts(dag, catalog)
        assert result.valid is True

    def test_empty_dag(self, load_fixture):
        catalog = NodeCatalog.model_validate(load_fixture("specify-catalog.json"))
        dag = StrategyGraph(id="sg", workflow_id="w")
        result = check_contracts(dag, catalog)
        assert result.valid is True
