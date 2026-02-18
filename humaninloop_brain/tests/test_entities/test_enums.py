"""Tests for enumeration types."""

from humaninloop_brain.entities.enums import (
    DecisionStatus,
    EdgeType,
    GateStatus,
    InvariantEnforcement,
    InvariantSeverity,
    MilestoneStatus,
    NodeType,
    PassOutcome,
    TaskStatus,
    TYPE_STATUS_MAP,
)


class TestNodeType:
    def test_values(self):
        assert set(NodeType) == {
            NodeType.task,
            NodeType.gate,
            NodeType.decision,
            NodeType.milestone,
        }

    def test_string_serialization(self):
        assert NodeType.task.value == "task"
        assert NodeType.gate.value == "gate"
        assert NodeType.decision.value == "decision"
        assert NodeType.milestone.value == "milestone"

    def test_str_base(self):
        assert NodeType.task.value == "task"
        assert NodeType.task == "task"


class TestEdgeType:
    def test_values(self):
        assert set(EdgeType) == {
            EdgeType.depends_on,
            EdgeType.produces,
            EdgeType.validates,
            EdgeType.constrained_by,
            EdgeType.informed_by,
        }

    def test_kebab_case_values(self):
        assert EdgeType.depends_on.value == "depends-on"
        assert EdgeType.constrained_by.value == "constrained-by"
        assert EdgeType.informed_by.value == "informed-by"


class TestPassOutcome:
    def test_values(self):
        assert PassOutcome.completed.value == "completed"
        assert PassOutcome.halted.value == "halted"


class TestTaskStatus:
    def test_all_values(self):
        expected = {"pending", "in-progress", "completed", "skipped", "halted"}
        assert {s.value for s in TaskStatus} == expected


class TestGateStatus:
    def test_all_values(self):
        expected = {"pending", "in-progress", "passed", "failed", "needs-revision"}
        assert {s.value for s in GateStatus} == expected


class TestDecisionStatus:
    def test_all_values(self):
        expected = {"pending", "decided"}
        assert {s.value for s in DecisionStatus} == expected


class TestMilestoneStatus:
    def test_all_values(self):
        expected = {"pending", "achieved"}
        assert {s.value for s in MilestoneStatus} == expected


class TestInvariantEnums:
    def test_enforcement_values(self):
        assert InvariantEnforcement.assembly_time.value == "assembly-time"
        assert InvariantEnforcement.runtime.value == "runtime"

    def test_severity_values(self):
        assert InvariantSeverity.error.value == "error"
        assert InvariantSeverity.warning.value == "warning"


class TestTypeStatusMap:
    def test_all_node_types_mapped(self):
        for nt in NodeType:
            assert nt in TYPE_STATUS_MAP

    def test_correct_mapping(self):
        assert TYPE_STATUS_MAP[NodeType.task] is TaskStatus
        assert TYPE_STATUS_MAP[NodeType.gate] is GateStatus
        assert TYPE_STATUS_MAP[NodeType.decision] is DecisionStatus
        assert TYPE_STATUS_MAP[NodeType.milestone] is MilestoneStatus
