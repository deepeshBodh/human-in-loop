"""Tests for StrategyGraph entity."""

import json

from humaninloop_brain.entities.dag_pass import PassEntry
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.nodes import GraphNode, NodeHistoryEntry
from humaninloop_brain.entities.strategy_graph import StrategyGraph


class TestStrategyGraph:
    def test_construct_empty(self):
        sg = StrategyGraph(id="sg-001", workflow_id="specify-auth")
        assert sg.id == "sg-001"
        assert sg.workflow_id == "specify-auth"
        assert sg.schema_version == "3.0.0"
        assert sg.current_pass == 1
        assert sg.status == "in-progress"
        assert sg.nodes == []
        assert sg.edges == []
        assert sg.passes == []

    def test_construct_with_pass(self):
        sg = StrategyGraph(
            id="sg-001",
            workflow_id="specify-auth",
            passes=[PassEntry(pass_number=1, created_at="2026-01-15T10:00:00Z")],
        )
        assert len(sg.passes) == 1
        assert sg.passes[0].pass_number == 1

    def test_construct_with_nodes_and_edges(self):
        node = GraphNode(
            id="t",
            type=NodeType.task,
            name="n",
            description="d",
            status="pending",
            history=[NodeHistoryEntry(pass_number=1, status="pending")],
            last_active_pass=1,
        )
        edge = Edge(id="e", source="t", target="g", type=EdgeType.depends_on)
        sg = StrategyGraph(
            id="sg-001",
            workflow_id="w",
            nodes=[node],
            edges=[edge],
        )
        assert len(sg.nodes) == 1
        assert len(sg.edges) == 1

    def test_serialization_roundtrip(self):
        sg = StrategyGraph(
            id="sg-001",
            workflow_id="specify-auth",
            created_at="2026-01-15T10:00:00Z",
            passes=[PassEntry(pass_number=1, created_at="2026-01-15T10:00:00Z")],
            nodes=[
                GraphNode(
                    id="t",
                    type=NodeType.task,
                    name="n",
                    description="d",
                    status="pending",
                    history=[NodeHistoryEntry(pass_number=1, status="pending")],
                    last_active_pass=1,
                )
            ],
            edges=[
                Edge(id="e", source="t", target="g", type=EdgeType.depends_on)
            ],
        )
        data = sg.model_dump()
        restored = StrategyGraph.model_validate(data)
        assert restored.id == sg.id
        assert len(restored.nodes) == 1
        assert len(restored.edges) == 1
        assert restored.passes[0].pass_number == 1

    def test_json_roundtrip(self):
        sg = StrategyGraph(
            id="sg-001",
            workflow_id="w",
            created_at="2026-01-15T10:00:00Z",
        )
        json_str = sg.model_dump_json()
        restored = StrategyGraph.model_validate_json(json_str)
        assert restored == sg

    def test_schema_version_default(self):
        sg = StrategyGraph(id="sg", workflow_id="w")
        dumped = json.loads(sg.model_dump_json())
        assert dumped["schema_version"] == "3.0.0"
