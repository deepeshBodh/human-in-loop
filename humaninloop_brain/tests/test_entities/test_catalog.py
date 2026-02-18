"""Tests for catalog entities."""

import pytest
from pydantic import ValidationError

from humaninloop_brain.entities.catalog import (
    CatalogNodeDefinition,
    EdgeConstraint,
    NodeCatalog,
    SystemInvariant,
)
from humaninloop_brain.entities.enums import (
    EdgeType,
    InvariantEnforcement,
    InvariantSeverity,
    NodeType,
)
from humaninloop_brain.entities.nodes import NodeContract, ArtifactConsumption


class TestCatalogNodeDefinition:
    def test_valid_task(self):
        node = CatalogNodeDefinition(
            id="input-enrichment",
            type=NodeType.task,
            name="Input Enrichment",
            description="desc",
            valid_statuses=["pending", "in-progress", "completed", "skipped"],
        )
        assert node.id == "input-enrichment"
        assert node.type == NodeType.task

    def test_valid_gate(self):
        node = CatalogNodeDefinition(
            id="advocate-review",
            type=NodeType.gate,
            name="Advocate",
            description="desc",
            valid_statuses=["pending", "passed", "failed"],
            verdict_field="verdict",
            verdict_values=["ready", "needs-revision"],
        )
        assert node.verdict_field == "verdict"

    def test_invalid_status_for_type(self):
        with pytest.raises(ValidationError, match="not valid for node type"):
            CatalogNodeDefinition(
                id="bad",
                type=NodeType.decision,
                name="n",
                description="d",
                valid_statuses=["pending", "completed"],
            )

    def test_task_with_gate_status_rejected(self):
        with pytest.raises(ValidationError, match="not valid for node type"):
            CatalogNodeDefinition(
                id="bad",
                type=NodeType.task,
                name="n",
                description="d",
                valid_statuses=["pending", "passed"],
            )

    def test_with_contract(self):
        node = CatalogNodeDefinition(
            id="n",
            type=NodeType.task,
            name="n",
            description="d",
            contract=NodeContract(
                consumes=[ArtifactConsumption(artifact="raw-input")],
                produces=["enriched-input"],
            ),
            valid_statuses=["pending", "completed"],
        )
        assert len(node.contract.consumes) == 1

    def test_frozen(self):
        node = CatalogNodeDefinition(
            id="n",
            type=NodeType.task,
            name="n",
            description="d",
            valid_statuses=["pending"],
        )
        with pytest.raises(ValidationError):
            node.id = "other"


class TestEdgeConstraint:
    def test_basic(self):
        ec = EdgeConstraint(
            valid_sources=[NodeType.task],
            valid_targets=[NodeType.task, NodeType.gate],
            note="Artifact flow",
        )
        assert NodeType.task in ec.valid_sources
        assert len(ec.valid_targets) == 2

    def test_frozen(self):
        ec = EdgeConstraint(
            valid_sources=[NodeType.gate], valid_targets=[NodeType.task]
        )
        with pytest.raises(ValidationError):
            ec.note = "changed"


class TestSystemInvariant:
    def test_basic(self):
        inv = SystemInvariant(
            id="INV-001",
            rule="Test rule",
            enforcement=InvariantEnforcement.assembly_time,
            severity=InvariantSeverity.error,
        )
        assert inv.id == "INV-001"
        assert inv.enforcement == InvariantEnforcement.assembly_time

    def test_frozen(self):
        inv = SystemInvariant(
            id="INV-001",
            rule="r",
            enforcement=InvariantEnforcement.runtime,
            severity=InvariantSeverity.warning,
        )
        with pytest.raises(ValidationError):
            inv.rule = "changed"


class TestNodeCatalog:
    def test_load_fixture(self, load_fixture):
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        assert catalog.catalog_version == "1.0.0"
        assert catalog.workflow == "specify"
        assert len(catalog.nodes) == 7
        assert len(catalog.edge_constraints) == 5
        assert len(catalog.invariants) == 5

    def test_get_node(self, load_fixture):
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        node = catalog.get_node("analyst-review")
        assert node is not None
        assert node.name == "Requirements Analysis"
        assert catalog.get_node("nonexistent") is None

    def test_get_edge_constraint(self, load_fixture):
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        ec = catalog.get_edge_constraint(EdgeType.validates)
        assert ec is not None
        assert NodeType.gate in ec.valid_sources
        assert catalog.get_edge_constraint(EdgeType.informed_by) is not None

    def test_all_node_ids_unique(self, load_fixture):
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        ids = [n.id for n in catalog.nodes]
        assert len(ids) == len(set(ids))

    def test_serialization_roundtrip(self, load_fixture):
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        json_str = catalog.model_dump_json()
        restored = NodeCatalog.model_validate_json(json_str)
        assert len(restored.nodes) == len(catalog.nodes)
        assert len(restored.invariants) == len(catalog.invariants)
