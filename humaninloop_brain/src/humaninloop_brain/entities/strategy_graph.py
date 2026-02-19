"""StrategyGraph entity — the single-DAG container for v3 architecture."""

from pydantic import BaseModel

from humaninloop_brain.entities.dag_pass import PassEntry
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.nodes import GraphNode


class StrategyGraph(BaseModel):
    """A single DAG containing the full workflow history across passes.

    Accumulates nodes and edges across multiple passes, with node-level
    history entries tracking per-pass status evolution.
    """

    model_config = {"frozen": True}

    id: str
    workflow_id: str
    schema_version: str = "3.0.0"
    current_pass: int = 1
    status: str = "in-progress"
    created_at: str | None = None
    completed_at: str | None = None
    passes: list[PassEntry] = []
    nodes: list[GraphNode] = []
    edges: list[Edge] = []
