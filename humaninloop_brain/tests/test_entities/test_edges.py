"""Tests for edge entity."""

import pytest
from pydantic import ValidationError

from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import EdgeType


class TestEdge:
    def test_basic(self):
        edge = Edge(
            id="e1", source="a", target="b", type=EdgeType.depends_on
        )
        assert edge.id == "e1"
        assert edge.source == "a"
        assert edge.target == "b"
        assert edge.type == EdgeType.depends_on

    def test_all_edge_types(self):
        for et in EdgeType:
            edge = Edge(id="e", source="a", target="b", type=et)
            assert edge.type == et

    def test_frozen(self):
        edge = Edge(id="e", source="a", target="b", type=EdgeType.produces)
        with pytest.raises(ValidationError):
            edge.source = "c"

    def test_serialization_roundtrip(self):
        edge = Edge(id="e1", source="a", target="b", type=EdgeType.validates)
        data = edge.model_dump()
        restored = Edge.model_validate(data)
        assert restored == edge

    def test_json_roundtrip(self):
        edge = Edge(id="e1", source="a", target="b", type=EdgeType.constrained_by)
        json_str = edge.model_dump_json()
        restored = Edge.model_validate_json(json_str)
        assert restored == edge

    def test_from_json_string_type(self):
        """Edge type can be constructed from JSON string value."""
        edge = Edge(id="e", source="a", target="b", type="depends_on")
        assert edge.type == EdgeType.depends_on

    def test_triggered_by_fields(self):
        edge = Edge(
            id="e-trig",
            source="analyst-review",
            target="analyst-review",
            type=EdgeType.triggered_by,
            source_pass=1,
            target_pass=2,
            reason="advocate-verdict-needs-revision",
        )
        assert edge.type == EdgeType.triggered_by
        assert edge.source_pass == 1
        assert edge.target_pass == 2
        assert edge.reason == "advocate-verdict-needs-revision"

    def test_backward_compatible(self):
        """V2 data (no source_pass/target_pass/reason) still deserializes."""
        data = {"id": "e", "source": "a", "target": "b", "type": "depends_on"}
        edge = Edge.model_validate(data)
        assert edge.source_pass is None
        assert edge.target_pass is None
        assert edge.reason is None
