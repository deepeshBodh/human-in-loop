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

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """Lowercase, split on whitespace and hyphens, drop short tokens."""
        words: set[str] = set()
        for word in text.lower().replace("-", " ").split():
            stripped = word.strip(".,;:!?()[]{}\"'")
            if len(stripped) > 2:
                words.add(stripped)
        return words

    def resolve_by_description(
        self,
        intent: str,
        node_type: NodeType | None = None,
        candidates: list[CatalogNodeDefinition] | None = None,
    ) -> list[CatalogNodeDefinition]:
        """Score catalog nodes by word overlap between intent and description/name.

        Semantic fallback for when capability tag resolution fails.
        Returns nodes with the highest non-zero overlap score.
        If candidates provided, only scores those nodes.
        """
        pool = candidates if candidates is not None else self.nodes
        if node_type is not None:
            pool = [n for n in pool if n.type == node_type]
        intent_words = self._tokenize(intent)
        if not intent_words:
            return []
        scored: list[tuple[int, CatalogNodeDefinition]] = []
        for node in pool:
            node_words = self._tokenize(node.description) | self._tokenize(node.name)
            for cap in node.capabilities:
                node_words |= self._tokenize(cap)
            overlap = len(intent_words & node_words)
            if overlap > 0:
                scored.append((overlap, node))
        if not scored:
            return []
        scored.sort(key=lambda x: x[0], reverse=True)
        top_score = scored[0][0]
        return [n for score, n in scored if score == top_score]

    def get_edge_constraint(self, edge_type: EdgeType) -> EdgeConstraint | None:
        """Look up edge constraint by type."""
        return self.edge_constraints.get(edge_type)
