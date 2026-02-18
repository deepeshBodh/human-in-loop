"""Validation result entities for structured error reporting."""

from __future__ import annotations

from pydantic import BaseModel


class ValidationViolation(BaseModel):
    """A single validation violation."""

    model_config = {"frozen": True}

    code: str
    severity: str
    message: str
    node_id: str | None = None
    edge_id: str | None = None


class ValidationResult(BaseModel):
    """Result of a validation pass."""

    model_config = {"frozen": True}

    valid: bool
    phase: str
    violations: list[ValidationViolation] = []

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)

    @property
    def error_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for v in self.violations if v.severity == "warning")
