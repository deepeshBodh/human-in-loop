"""Tests for DAG pass entities."""

import json

import pytest

from humaninloop_brain.entities.dag_pass import (
    DAGPass,
    ExecutionTraceEntry,
    HistoryContext,
    HistoryPass,
    PassEntry,
)
from humaninloop_brain.entities.nodes import GraphNode
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import EdgeType, NodeType, PassOutcome


class TestExecutionTraceEntry:
    def test_basic(self):
        entry = ExecutionTraceEntry(
            node_id="analyst-review",
            started_at="2026-01-15T10:00:00Z",
            completed_at="2026-01-15T10:05:00Z",
            verdict=None,
            agent_report_summary="Produced spec.md",
            artifacts_produced=["spec.md"],
        )
        assert entry.node_id == "analyst-review"
        assert entry.artifacts_produced == ["spec.md"]

    def test_minimal(self):
        entry = ExecutionTraceEntry(
            node_id="n", started_at="2026-01-15T10:00:00Z"
        )
        assert entry.completed_at is None
        assert entry.verdict is None
        assert entry.artifacts_produced == []

    def test_frozen(self):
        entry = ExecutionTraceEntry(
            node_id="n", started_at="2026-01-15T10:00:00Z"
        )
        with pytest.raises(Exception):
            entry.node_id = "other"


class TestHistoryPass:
    def test_basic(self):
        hp = HistoryPass(
            pass_number=1,
            outcome="completed",
            outcome_detail="advocate-verdict-needs-revision",
            summary="Advocate found 3 gaps",
        )
        assert hp.pass_number == 1
        assert hp.outcome == "completed"

    def test_frozen(self):
        hp = HistoryPass(pass_number=1, outcome="completed", summary="s")
        with pytest.raises(Exception):
            hp.pass_number = 2


class TestHistoryContext:
    def test_empty(self):
        hc = HistoryContext()
        assert hc.previous_passes == []

    def test_with_passes(self):
        hc = HistoryContext(
            previous_passes=[
                HistoryPass(pass_number=1, outcome="completed", summary="pass 1")
            ]
        )
        assert len(hc.previous_passes) == 1


class TestPassEntry:
    def test_construct(self):
        entry = PassEntry(pass_number=1)
        assert entry.pass_number == 1
        assert entry.outcome is None
        assert entry.detail is None
        assert entry.created_at is None
        assert entry.completed_at is None
        assert entry.frozen is False

    def test_with_all_fields(self):
        entry = PassEntry(
            pass_number=2,
            outcome="completed",
            detail="advocate-verdict-needs-revision",
            created_at="2026-01-15T10:00:00Z",
            completed_at="2026-01-15T10:30:00Z",
            frozen=True,
        )
        assert entry.outcome == "completed"
        assert entry.frozen is True

    def test_frozen(self):
        entry = PassEntry(pass_number=1)
        with pytest.raises(Exception):
            entry.outcome = "completed"

    def test_serialization_roundtrip(self):
        entry = PassEntry(pass_number=1, outcome="completed", detail="done")
        data = entry.model_dump()
        restored = PassEntry.model_validate(data)
        assert restored == entry


class TestDAGPass:
    def test_create_empty(self):
        dag = DAGPass(
            id="pass-001",
            workflow_id="specify-feature-auth",
            pass_number=1,
        )
        assert dag.id == "pass-001"
        assert dag.schema_version == "1.0.0"
        assert dag.outcome is None
        assert dag.nodes == []
        assert dag.edges == []

    def test_mutable_nodes_list(self):
        """DAGPass is mutable — nodes list can be modified."""
        dag = DAGPass(id="p", workflow_id="w", pass_number=1)
        node = GraphNode(
            id="t", type=NodeType.task, name="n", description="d", status="pending"
        )
        dag.nodes.append(node)
        assert len(dag.nodes) == 1

    def test_mutable_edges_list(self):
        dag = DAGPass(id="p", workflow_id="w", pass_number=1)
        edge = Edge(id="e", source="a", target="b", type=EdgeType.depends_on)
        dag.edges.append(edge)
        assert len(dag.edges) == 1

    def test_set_outcome(self):
        dag = DAGPass(id="p", workflow_id="w", pass_number=1)
        dag.outcome = PassOutcome.completed
        assert dag.outcome == PassOutcome.completed

    def test_fixture_loading(self, load_fixture):
        data = load_fixture("pass-normal.json")
        dag = DAGPass.model_validate(data)
        assert dag.id == "specify-pass-001"
        assert len(dag.nodes) == 3
        assert len(dag.edges) == 5
        assert dag.pass_number == 1

    def test_fixture_skip_enrichment(self, load_fixture):
        data = load_fixture("pass-skip-enrichment.json")
        dag = DAGPass.model_validate(data)
        assert len(dag.nodes) == 3
        node_ids = {n.id for n in dag.nodes}
        assert "input-enrichment" not in node_ids
        assert "constitution-gate" in node_ids

    def test_fixture_with_research(self, load_fixture):
        data = load_fixture("pass-with-research.json")
        dag = DAGPass.model_validate(data)
        assert dag.pass_number == 2
        assert len(dag.history_context.previous_passes) == 1
        node_ids = {n.id for n in dag.nodes}
        assert "targeted-research" in node_ids

    def test_fixture_with_clarification(self, load_fixture):
        data = load_fixture("pass-with-clarification.json")
        dag = DAGPass.model_validate(data)
        node_ids = {n.id for n in dag.nodes}
        assert "human-clarification" in node_ids

    def test_serialization_roundtrip(self, load_fixture):
        data = load_fixture("pass-normal.json")
        dag = DAGPass.model_validate(data)
        json_str = dag.model_dump_json()
        restored = DAGPass.model_validate_json(json_str)
        assert restored.id == dag.id
        assert len(restored.nodes) == len(dag.nodes)
        assert len(restored.edges) == len(dag.edges)

    def test_json_roundtrip_preserves_structure(self, load_fixture):
        """Round-trip through JSON preserves all data."""
        data = load_fixture("pass-with-research.json")
        dag = DAGPass.model_validate(data)
        dumped = json.loads(dag.model_dump_json())
        dag2 = DAGPass.model_validate(dumped)
        assert dag2.history_context.previous_passes[0].pass_number == 1
