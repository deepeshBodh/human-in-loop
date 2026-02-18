"""Node entities for the DAG-first execution architecture."""

from __future__ import annotations

from pydantic import BaseModel, model_validator

from humaninloop_brain.entities.enums import NodeType, TYPE_STATUS_MAP


class ArtifactConsumption(BaseModel):
    """An artifact consumed by a node."""

    model_config = {"frozen": True}

    artifact: str
    required: bool = True
    note: str | None = None


class NodeContract(BaseModel):
    """Input/output contract for a node."""

    model_config = {"frozen": True}

    consumes: list[ArtifactConsumption] = []
    produces: list[str] = []


class EvidenceAttachment(BaseModel):
    """An evidence reference attached to a node."""

    model_config = {"frozen": True}

    id: str
    type: str
    description: str
    reference: str


class GraphNode(BaseModel):
    """A node in a DAG pass graph."""

    model_config = {"frozen": True}

    id: str
    type: NodeType
    name: str
    description: str
    status: str
    contract: NodeContract = NodeContract()
    agent: str | None = None
    evidence: list[EvidenceAttachment] = []

    @model_validator(mode="after")
    def validate_type_status(self) -> GraphNode:
        """Ensure status is valid for the node's type."""
        status_enum = TYPE_STATUS_MAP[self.type]
        valid_values = {s.value for s in status_enum}
        if self.status not in valid_values:
            raise ValueError(
                f"Status '{self.status}' is not valid for node type "
                f"'{self.type.value}'. Valid statuses: {sorted(valid_values)}"
            )
        return self
