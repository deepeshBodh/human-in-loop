"""Edge entity for the DAG-first execution architecture."""

from pydantic import BaseModel

from humaninloop_brain.entities.enums import EdgeType


class Edge(BaseModel):
    """A typed edge between two nodes in a DAG pass."""

    model_config = {"frozen": True}

    id: str
    source: str
    target: str
    type: EdgeType
    source_pass: int | None = None
    target_pass: int | None = None
    reason: str | None = None
