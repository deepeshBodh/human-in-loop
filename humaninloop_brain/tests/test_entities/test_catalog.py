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
            valid_statuses=["pending", "in-progress", "completed"],
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

    def test_with_capabilities(self):
        node = CatalogNodeDefinition(
            id="n",
            type=NodeType.task,
            name="n",
            description="d",
            valid_statuses=["pending"],
            capabilities=["specification-writing", "requirements-analysis"],
        )
        assert len(node.capabilities) == 2
        assert "specification-writing" in node.capabilities

    def test_with_carry_forward(self):
        node = CatalogNodeDefinition(
            id="g",
            type=NodeType.gate,
            name="g",
            description="d",
            valid_statuses=["pending", "completed"],
            carry_forward=True,
            gate_type="deterministic",
        )
        assert node.carry_forward is True
        assert node.gate_type == "deterministic"

    def test_backward_compatible(self):
        """V2 data (no capabilities/carry_forward/gate_type) still deserializes."""
        data = {
            "id": "n",
            "type": "task",
            "name": "n",
            "description": "d",
            "valid_statuses": ["pending"],
        }
        node = CatalogNodeDefinition.model_validate(data)
        assert node.capabilities == []
        assert node.carry_forward is False
        assert node.gate_type is None


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
        assert catalog.catalog_version == "2.0.0"
        assert catalog.workflow == "specify"
        assert len(catalog.nodes) == 7
        assert len(catalog.edge_constraints) == 6
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

    def test_resolve_single_match(self, load_fixture):
        """Tags that uniquely match one node return exactly that node."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        matches = catalog.resolve_by_capabilities(["input-enrichment"])
        assert len(matches) == 1
        assert matches[0].id == "input-enrichment"

    def test_resolve_no_match(self, load_fixture):
        """Tags that match nothing return empty list."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        matches = catalog.resolve_by_capabilities(["nonexistent-capability"])
        assert matches == []

    def test_resolve_ambiguous(self, load_fixture):
        """Tags shared by multiple nodes return all matches."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        # "specification-writing" is on analyst-review,
        # "specification-validation" is on advocate-review.
        # Use a tag that appears on only one, then a broader query.
        # Both analyst-review and advocate-review have spec-related capabilities.
        # Let's use a tag intersection approach:
        # analyst-review has: requirements-analysis, specification-writing
        # advocate-review has: specification-validation, gap-detection
        # targeted-research has: research, knowledge-gap-resolution
        # So "gap-detection" + "research" should match both advocate + targeted-research
        matches = catalog.resolve_by_capabilities(["gap-detection", "research"])
        ids = {m.id for m in matches}
        assert len(matches) == 2
        assert ids == {"advocate-review", "targeted-research"}

    def test_resolve_with_node_type_filter(self, load_fixture):
        """Type filter narrows results to matching node type."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        # "gap-detection" + "research" matches advocate-review (gate) and
        # targeted-research (task). Filter to task only.
        matches = catalog.resolve_by_capabilities(
            ["gap-detection", "research"], NodeType.task,
        )
        assert len(matches) == 1
        assert matches[0].id == "targeted-research"

    def test_resolve_empty_tags(self, load_fixture):
        """Empty tags list matches nothing."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        matches = catalog.resolve_by_capabilities([])
        assert matches == []


class TestResolveByDescription:
    """Tests for semantic description fallback (V3 tier-2 intent resolution)."""

    def test_unique_match_by_description(self, load_fixture):
        """Intent matching a single node's description returns that node."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        matches = catalog.resolve_by_description(
            "Investigate specific knowledge gaps identified by validation"
        )
        assert len(matches) == 1
        assert matches[0].id == "targeted-research"

    def test_no_match_returns_empty(self, load_fixture):
        """Intent with no word overlap returns empty list."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        matches = catalog.resolve_by_description("zzz qqq xxx")
        assert matches == []

    def test_empty_intent_returns_empty(self, load_fixture):
        """Empty intent string returns empty list."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        matches = catalog.resolve_by_description("")
        assert matches == []

    def test_node_type_filter(self, load_fixture):
        """Node type filter narrows semantic results."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        # "specification" appears in both analyst-review (task) and
        # advocate-review (gate) descriptions
        matches = catalog.resolve_by_description(
            "specification", node_type=NodeType.task,
        )
        task_ids = {m.id for m in matches}
        assert all(m.type == NodeType.task for m in matches)
        # Should not include advocate-review (gate type)
        assert "advocate-review" not in task_ids

    def test_candidates_parameter_narrows_pool(self, load_fixture):
        """Providing candidates restricts search to those nodes only."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        # Get two candidates via capability match
        candidates = catalog.resolve_by_capabilities(
            ["gap-detection", "research"],
        )
        assert len(candidates) == 2
        # Disambiguate using intent that matches targeted-research better
        matches = catalog.resolve_by_description(
            "Investigate knowledge gaps through research",
            candidates=candidates,
        )
        assert len(matches) == 1
        assert matches[0].id == "targeted-research"

    def test_capabilities_included_in_scoring(self, load_fixture):
        """Capability tag words contribute to description matching score."""
        data = load_fixture("specify-catalog.json")
        catalog = NodeCatalog.model_validate(data)
        # "enrichment" appears in input-enrichment's capabilities
        matches = catalog.resolve_by_description("input enrichment")
        assert any(m.id == "input-enrichment" for m in matches)
