"""Node entities for the DAG-first execution architecture."""

from __future__ import annotations

from pydantic import BaseModel, model_validator

from humaninloop_brain.entities.enums import NodeType, TYPE_STATUS_MAP, V3_TYPE_STATUS_MAP


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


class NodeHistoryEntry(BaseModel):
    """A single pass's history entry for a node in a StrategyGraph."""

    model_config = {"frozen": True}

    pass_number: int
    status: str
    verdict: str | None = None
    frozen: bool = False
    evidence: list[EvidenceAttachment] = []
    trace: dict | None = None


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
    history: list[NodeHistoryEntry] = []
    verdict: str | None = None
    last_active_pass: int | None = None
    schema_version: str | None = None

    @model_validator(mode="after")
    def validate_type_status(self) -> GraphNode:
        """Ensure status is valid for the node's type.

        Uses V3_TYPE_STATUS_MAP when schema_version is "3.0.0",
        otherwise uses the v2 TYPE_STATUS_MAP.
        """
        status_map = V3_TYPE_STATUS_MAP if self.schema_version == "3.0.0" else TYPE_STATUS_MAP
        status_enum = status_map[self.type]
        valid_values = {s.value for s in status_enum}
        if self.status not in valid_values:
            raise ValueError(
                f"Status '{self.status}' is not valid for node type "
                f"'{self.type.value}'. Valid statuses: {sorted(valid_values)}"
            )
        return self
