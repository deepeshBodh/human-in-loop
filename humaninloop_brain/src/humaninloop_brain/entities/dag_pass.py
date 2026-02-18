"""DAG pass entity — the mutable container assembled per execution pass."""

from __future__ import annotations

from pydantic import BaseModel

from humaninloop_brain.entities.enums import PassOutcome
from humaninloop_brain.entities.nodes import GraphNode
from humaninloop_brain.entities.edges import Edge


class ExecutionTraceEntry(BaseModel):
    """Record of a single node's execution within a pass."""

    model_config = {"frozen": True}

    node_id: str
    started_at: str
    completed_at: str | None = None
    verdict: str | None = None
    agent_report_summary: str | None = None
    artifacts_produced: list[str] = []


class HistoryPass(BaseModel):
    """Summary of a previous pass for progressive context."""

    model_config = {"frozen": True}

    pass_number: int
    outcome: str
    outcome_detail: str | None = None
    summary: str


class HistoryContext(BaseModel):
    """Progressive summary of previous passes."""

    model_config = {"frozen": True}

    previous_passes: list[HistoryPass] = []


class DAGPass(BaseModel):
    """A single DAG pass — mutable during assembly, frozen after completion.

    Individual GraphNode and Edge values remain frozen (immutable Pydantic models).
    Status updates create new GraphNode instances and replace in the list.
    """

    id: str
    workflow_id: str
    schema_version: str = "1.0.0"
    pass_number: int
    outcome: PassOutcome | None = None
    outcome_detail: str | None = None
    assembly_rationale: str | None = None
    created_at: str | None = None
    completed_at: str | None = None
    nodes: list[GraphNode] = []
    edges: list[Edge] = []
    execution_trace: list[ExecutionTraceEntry] = []
    history_context: HistoryContext = HistoryContext()
