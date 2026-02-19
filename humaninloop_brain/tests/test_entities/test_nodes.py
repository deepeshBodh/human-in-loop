"""Tests for node entities."""

import pytest
from pydantic import ValidationError

from humaninloop_brain.entities.nodes import (
    ArtifactConsumption,
    EvidenceAttachment,
    GraphNode,
    NodeContract,
    NodeHistoryEntry,
)
from humaninloop_brain.entities.enums import NodeType


class TestArtifactConsumption:
    def test_basic(self):
        ac = ArtifactConsumption(artifact="spec.md", required=True)
        assert ac.artifact == "spec.md"
        assert ac.required is True
        assert ac.note is None

    def test_with_note(self):
        ac = ArtifactConsumption(
            artifact="enriched-input", required=False, note="optional"
        )
        assert ac.note == "optional"

    def test_default_required(self):
        ac = ArtifactConsumption(artifact="x")
        assert ac.required is True

    def test_frozen(self):
        ac = ArtifactConsumption(artifact="x")
        with pytest.raises(ValidationError):
            ac.artifact = "y"


class TestNodeContract:
    def test_empty(self):
        nc = NodeContract()
        assert nc.consumes == []
        assert nc.produces == []

    def test_with_data(self):
        nc = NodeContract(
            consumes=[ArtifactConsumption(artifact="raw-input")],
            produces=["enriched-input"],
        )
        assert len(nc.consumes) == 1
        assert nc.produces == ["enriched-input"]

    def test_frozen(self):
        nc = NodeContract()
        with pytest.raises(ValidationError):
            nc.produces = ["new"]


class TestEvidenceAttachment:
    def test_basic(self):
        ev = EvidenceAttachment(
            id="ev-01", type="file", description="Spec file", reference="spec.md"
        )
        assert ev.id == "ev-01"
        assert ev.type == "file"

    def test_frozen(self):
        ev = EvidenceAttachment(
            id="ev-01", type="file", description="d", reference="r"
        )
        with pytest.raises(ValidationError):
            ev.id = "ev-02"


class TestNodeHistoryEntry:
    def test_construct(self):
        entry = NodeHistoryEntry(pass_number=1, status="pending")
        assert entry.pass_number == 1
        assert entry.status == "pending"
        assert entry.verdict is None
        assert entry.frozen is False
        assert entry.evidence == []
        assert entry.trace is None

    def test_with_all_fields(self):
        ev = EvidenceAttachment(id="ev-01", type="file", description="d", reference="r")
        entry = NodeHistoryEntry(
            pass_number=2,
            status="completed",
            verdict="ready",
            frozen=True,
            evidence=[ev],
            trace={"node_id": "n", "started_at": "2026-01-15T10:00:00Z"},
        )
        assert entry.verdict == "ready"
        assert entry.frozen is True
        assert len(entry.evidence) == 1
        assert entry.trace["node_id"] == "n"

    def test_frozen(self):
        entry = NodeHistoryEntry(pass_number=1, status="pending")
        with pytest.raises(ValidationError):
            entry.status = "completed"

    def test_serialization_roundtrip(self):
        entry = NodeHistoryEntry(pass_number=1, status="in-progress", verdict="needs-revision")
        data = entry.model_dump()
        restored = NodeHistoryEntry.model_validate(data)
        assert restored == entry


class TestGraphNode:
    def test_valid_task_pending(self):
        node = GraphNode(
            id="analyst-review",
            type=NodeType.task,
            name="Analysis",
            description="desc",
            status="pending",
        )
        assert node.id == "analyst-review"
        assert node.type == NodeType.task
        assert node.status == "pending"

    def test_valid_task_all_statuses(self):
        for status in ["pending", "in-progress", "completed", "skipped", "halted"]:
            node = GraphNode(
                id="t", type=NodeType.task, name="n", description="d", status=status
            )
            assert node.status == status

    def test_valid_gate_all_statuses(self):
        for status in ["pending", "in-progress", "completed"]:
            node = GraphNode(
                id="g", type=NodeType.gate, name="n", description="d", status=status
            )
            assert node.status == status

    def test_valid_decision_all_statuses(self):
        for status in ["pending", "decided"]:
            node = GraphNode(
                id="d",
                type=NodeType.decision,
                name="n",
                description="d",
                status=status,
            )
            assert node.status == status

    def test_valid_milestone_all_statuses(self):
        for status in ["pending", "achieved"]:
            node = GraphNode(
                id="m",
                type=NodeType.milestone,
                name="n",
                description="d",
                status=status,
            )
            assert node.status == status

    def test_invalid_task_status(self):
        with pytest.raises(ValidationError, match="not valid for node type"):
            GraphNode(
                id="t",
                type=NodeType.task,
                name="n",
                description="d",
                status="passed",
            )

    def test_invalid_gate_status(self):
        with pytest.raises(ValidationError, match="not valid for node type"):
            GraphNode(
                id="g",
                type=NodeType.gate,
                name="n",
                description="d",
                status="decided",
            )

    def test_invalid_decision_status(self):
        with pytest.raises(ValidationError, match="not valid for node type"):
            GraphNode(
                id="d",
                type=NodeType.decision,
                name="n",
                description="d",
                status="completed",
            )

    def test_invalid_milestone_status(self):
        with pytest.raises(ValidationError, match="not valid for node type"):
            GraphNode(
                id="m",
                type=NodeType.milestone,
                name="n",
                description="d",
                status="completed",
            )

    def test_with_contract_and_agent(self):
        node = GraphNode(
            id="t",
            type=NodeType.task,
            name="n",
            description="d",
            status="pending",
            contract=NodeContract(produces=["spec.md"]),
            agent="requirements-analyst",
        )
        assert node.agent == "requirements-analyst"
        assert node.contract.produces == ["spec.md"]

    def test_frozen(self):
        node = GraphNode(
            id="t", type=NodeType.task, name="n", description="d", status="pending"
        )
        with pytest.raises(ValidationError):
            node.status = "completed"

    def test_serialization_roundtrip(self):
        node = GraphNode(
            id="t",
            type=NodeType.task,
            name="Test Node",
            description="desc",
            status="pending",
            contract=NodeContract(
                consumes=[ArtifactConsumption(artifact="raw-input")],
                produces=["output"],
            ),
            agent="test-agent",
            evidence=[
                EvidenceAttachment(
                    id="ev-01", type="file", description="d", reference="r"
                )
            ],
        )
        data = node.model_dump()
        restored = GraphNode.model_validate(data)
        assert restored == node

    def test_json_roundtrip(self):
        node = GraphNode(
            id="t",
            type=NodeType.task,
            name="n",
            description="d",
            status="pending",
        )
        json_str = node.model_dump_json()
        restored = GraphNode.model_validate_json(json_str)
        assert restored == node

    def test_with_history(self):
        entry = NodeHistoryEntry(pass_number=1, status="pending")
        node = GraphNode(
            id="t",
            type=NodeType.task,
            name="n",
            description="d",
            status="pending",
            history=[entry],
            verdict=None,
            last_active_pass=1,
        )
        assert len(node.history) == 1
        assert node.history[0].pass_number == 1
        assert node.last_active_pass == 1

    def test_backward_compatible(self):
        """V2 data (no history/verdict/last_active_pass) still deserializes."""
        data = {
            "id": "t",
            "type": "task",
            "name": "n",
            "description": "d",
            "status": "pending",
        }
        node = GraphNode.model_validate(data)
        assert node.history == []
        assert node.verdict is None
        assert node.last_active_pass is None
