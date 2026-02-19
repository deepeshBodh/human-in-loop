"""Node entities for the DAG-first execution architecture."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

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


class NodeHistoryEntry(BaseModel):
    """A single pass's history entry for a node in a StrategyGraph.

    The ``pass_number`` field serializes as ``"pass"`` in JSON to match the
    V3 design doc schema.
    """

    model_config = {"frozen": True, "populate_by_name": True}

    pass_number: int = Field(alias="pass", serialization_alias="pass")
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
    history: list[NodeHistoryEntry] = []
    verdict: str | None = None
    last_active_pass: int | None = None

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

    @model_validator(mode="after")
    def validate_derived_fields(self) -> GraphNode:
        """Enforce that status, verdict, and last_active_pass are derived from latest history entry.

        Per V3 design doc (lines 326-334): these fields always equal the
        corresponding values from the most recent history entry.  Only
        enforced when history is non-empty — nodes without history (e.g.
        in test fixtures or during initial construction) are allowed.
        """
        if not self.history:
            return self
        latest = self.history[-1]
        if self.status != latest.status:
            raise ValueError(
                f"Derived field 'status' ({self.status!r}) must equal "
                f"latest history entry status ({latest.status!r})"
            )
        if self.verdict != latest.verdict:
            raise ValueError(
                f"Derived field 'verdict' ({self.verdict!r}) must equal "
                f"latest history entry verdict ({latest.verdict!r})"
            )
        if self.last_active_pass != latest.pass_number:
            raise ValueError(
                f"Derived field 'last_active_pass' ({self.last_active_pass!r}) must equal "
                f"latest history entry pass ({latest.pass_number!r})"
            )
        return self
