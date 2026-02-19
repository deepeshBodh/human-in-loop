"""Pass-level entities for the DAG execution architecture."""

from __future__ import annotations

from pydantic import BaseModel, Field


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
    """A pass entry in a StrategyGraph — tracks pass-level metadata.

    The ``pass_number`` field serializes as ``"pass"`` in JSON to match the
    V3 design doc schema.  Python code uses ``pass_number`` (since ``pass``
    is a keyword).  ``populate_by_name=True`` allows construction with either
    name, and ``alias="pass"`` allows deserialization from JSON ``"pass"`` keys.
    """

    model_config = {"frozen": True, "populate_by_name": True}

    pass_number: int = Field(alias="pass", serialization_alias="pass")
    outcome: str | None = None
    detail: str | None = None
    created_at: str | None = None
    completed_at: str | None = None
    frozen: bool = False
