"""Pydantic entity models for DAG-first execution architecture."""

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
from humaninloop_brain.entities.nodes import (
    ArtifactConsumption,
    EvidenceAttachment,
    GraphNode,
    NodeContract,
)
from humaninloop_brain.entities.edges import Edge
from humaninloop_brain.entities.dag_pass import (
    DAGPass,
    ExecutionTraceEntry,
    HistoryContext,
    HistoryPass,
)
from humaninloop_brain.entities.catalog import (
    CatalogNodeDefinition,
    EdgeConstraint,
    NodeCatalog,
    SystemInvariant,
)
from humaninloop_brain.entities.validation import (
    ValidationResult,
    ValidationViolation,
)

__all__ = [
    # Enums
    "NodeType",
    "EdgeType",
    "PassOutcome",
    "TaskStatus",
    "GateStatus",
    "DecisionStatus",
    "MilestoneStatus",
    "InvariantEnforcement",
    "InvariantSeverity",
    "TYPE_STATUS_MAP",
    # Nodes
    "ArtifactConsumption",
    "NodeContract",
    "EvidenceAttachment",
    "GraphNode",
    # Edges
    "Edge",
    # DAG Pass
    "DAGPass",
    "ExecutionTraceEntry",
    "HistoryContext",
    "HistoryPass",
    # Catalog
    "CatalogNodeDefinition",
    "EdgeConstraint",
    "NodeCatalog",
    "SystemInvariant",
    # Validation
    "ValidationResult",
    "ValidationViolation",
]
