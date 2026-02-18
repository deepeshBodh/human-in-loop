"""Pass-level entities for the DAG execution architecture."""

from __future__ import annotations

from pydantic import BaseModel


class ExecutionTraceEntry(BaseModel):
    """Record of a single node's execution within a pass."""

    model_config = {"frozen": True}

    node_id: str
    started_at: str
    completed_at: str | None = None
    verdict: str | None = None
    agent_report_summary: str | None = None
    artifacts_produced: list[str] = []


class PassEntry(BaseModel):
    """A pass entry in a StrategyGraph — tracks pass-level metadata."""

    model_config = {"frozen": True}

    pass_number: int
    outcome: str | None = None
    detail: str | None = None
    created_at: str | None = None
    completed_at: str | None = None
    frozen: bool = False
