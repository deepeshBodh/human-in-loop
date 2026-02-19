"""Enumeration types for the DAG-first execution architecture."""

from enum import Enum


class NodeType(str, Enum):
    """The four node types in the DAG catalog model."""

    task = "task"
    gate = "gate"
    decision = "decision"
    milestone = "milestone"


class EdgeType(str, Enum):
    """The six edge types with distinct cascade semantics."""

    depends_on = "depends_on"
    produces = "produces"
    validates = "validates"
    constrained_by = "constrained_by"
    informed_by = "informed_by"
    triggered_by = "triggered_by"


class PassOutcome(str, Enum):
    """Outcome of a completed DAG pass."""

    completed = "completed"
    halted = "halted"


class TaskStatus(str, Enum):
    """Valid statuses for task nodes."""

    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"
    skipped = "skipped"
    halted = "halted"


class GateLifecycleStatus(str, Enum):
    """Lifecycle statuses for gate nodes.

    Agent-backed gates use: pending → in-progress → completed (verdict separate).
    Deterministic gates may use: pending → passed / failed (status IS verdict).
    """

    pending = "pending"
    in_progress = "in-progress"
    completed = "completed"
    passed = "passed"
    failed = "failed"


class DecisionStatus(str, Enum):
    """Valid statuses for decision nodes."""

    pending = "pending"
    decided = "decided"


class MilestoneStatus(str, Enum):
    """Valid statuses for milestone nodes."""

    pending = "pending"
    achieved = "achieved"


class InvariantEnforcement(str, Enum):
    """When an invariant is checked."""

    assembly_time = "assembly-time"
    runtime = "runtime"


class InvariantSeverity(str, Enum):
    """Severity of an invariant violation."""

    error = "error"
    warning = "warning"


class GateVerdict(str, Enum):
    """Verdict outcomes for gate nodes."""

    ready = "ready"
    needs_revision = "needs-revision"
    critical_gaps = "critical-gaps"


TYPE_STATUS_MAP: dict[NodeType, type[Enum]] = {
    NodeType.task: TaskStatus,
    NodeType.gate: GateLifecycleStatus,
    NodeType.decision: DecisionStatus,
    NodeType.milestone: MilestoneStatus,
}
