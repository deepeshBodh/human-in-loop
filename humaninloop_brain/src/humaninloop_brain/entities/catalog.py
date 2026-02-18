"""Node catalog entities — the library of available nodes and constraints."""

from __future__ import annotations

from pydantic import BaseModel, model_validator

from humaninloop_brain.entities.enums import (
    EdgeType,
    InvariantEnforcement,
    InvariantSeverity,
    NodeType,
    TYPE_STATUS_MAP,
)
from humaninloop_brain.entities.nodes import NodeContract


class CatalogNodeDefinition(BaseModel):
    """A node definition in the catalog."""

    model_config = {"frozen": True}

    id: str
    type: NodeType
    name: str
    description: str
    agent: str | None = None
    skill: str | None = None
    contract: NodeContract = NodeContract()
    valid_statuses: list[str] = []
    verdict_field: str | None = None
    verdict_values: list[str] | None = None
    capabilities: list[str] = []
    carry_forward: bool = False
    gate_type: str | None = None

    @model_validator(mode="after")
    def validate_statuses_match_type(self) -> CatalogNodeDefinition:
        """Ensure valid_statuses are all valid for this node type."""
        status_enum = TYPE_STATUS_MAP[self.type]
        valid_values = {s.value for s in status_enum}
        for status in self.valid_statuses:
            if status not in valid_values:
                raise ValueError(
                    f"Status '{status}' is not valid for node type "
                    f"'{self.type.value}'. Valid statuses: {sorted(valid_values)}"
                )
        return self


class EdgeConstraint(BaseModel):
    """Constraint on which node types can be source/target for an edge type."""

    model_config = {"frozen": True}

    valid_sources: list[NodeType]
    valid_targets: list[NodeType]
    note: str | None = None


class SystemInvariant(BaseModel):
    """A system-level invariant that must hold regardless of DAG shape."""

    model_config = {"frozen": True}

    id: str
    rule: str
    enforcement: InvariantEnforcement
    severity: InvariantSeverity


class NodeCatalog(BaseModel):
    """The complete node catalog for a workflow."""

    model_config = {"frozen": True}

    catalog_version: str
    workflow: str
    nodes: list[CatalogNodeDefinition]
    edge_constraints: dict[EdgeType, EdgeConstraint] = {}
    invariants: list[SystemInvariant] = []

    def get_node(self, node_id: str) -> CatalogNodeDefinition | None:
        """Look up a node definition by ID."""
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def resolve_by_capabilities(
        self, tags: list[str], node_type: NodeType | None = None,
    ) -> list[CatalogNodeDefinition]:
        """Find catalog nodes whose capabilities intersect with given tags.

        Returns all matching nodes. Caller decides on ambiguity.
        If node_type provided, filters by type first.
        """
        candidates = self.nodes
        if node_type is not None:
            candidates = [n for n in candidates if n.type == node_type]
        tag_set = set(tags)
        return [n for n in candidates if set(n.capabilities) & tag_set]

    def get_edge_constraint(self, edge_type: EdgeType) -> EdgeConstraint | None:
        """Look up edge constraint by type."""
        return self.edge_constraints.get(edge_type)
