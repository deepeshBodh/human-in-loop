"""Tests for validation entities."""

from humaninloop_brain.entities.validation import (
    ValidationResult,
    ValidationViolation,
)


class TestValidationViolation:
    def test_basic(self):
        v = ValidationViolation(
            code="CYCLE", severity="error", message="Cycle detected"
        )
        assert v.code == "CYCLE"
        assert v.severity == "error"
        assert v.node_id is None

    def test_with_node(self):
        v = ValidationViolation(
            code="STATUS",
            severity="error",
            message="Invalid status",
            node_id="analyst-review",
        )
        assert v.node_id == "analyst-review"

    def test_with_edge(self):
        v = ValidationViolation(
            code="ENDPOINT",
            severity="error",
            message="Invalid endpoint",
            edge_id="e1",
        )
        assert v.edge_id == "e1"


class TestValidationResult:
    def test_valid(self):
        vr = ValidationResult(valid=True, phase="structural")
        assert vr.valid is True
        assert vr.violations == []
        assert vr.has_errors is False
        assert vr.error_count == 0
        assert vr.warning_count == 0

    def test_with_errors(self):
        vr = ValidationResult(
            valid=False,
            phase="structural",
            violations=[
                ValidationViolation(
                    code="A", severity="error", message="error 1"
                ),
                ValidationViolation(
                    code="B", severity="warning", message="warning 1"
                ),
                ValidationViolation(
                    code="C", severity="error", message="error 2"
                ),
            ],
        )
        assert vr.valid is False
        assert vr.has_errors is True
        assert vr.error_count == 2
        assert vr.warning_count == 1

    def test_warnings_only(self):
        vr = ValidationResult(
            valid=True,
            phase="invariant",
            violations=[
                ValidationViolation(
                    code="W", severity="warning", message="warn"
                ),
            ],
        )
        assert vr.has_errors is False
        assert vr.error_count == 0
        assert vr.warning_count == 1

    def test_serialization_roundtrip(self):
        vr = ValidationResult(
            valid=False,
            phase="structural",
            violations=[
                ValidationViolation(
                    code="A", severity="error", message="msg", node_id="n1"
                ),
            ],
        )
        json_str = vr.model_dump_json()
        restored = ValidationResult.model_validate_json(json_str)
        assert restored.valid == vr.valid
        assert len(restored.violations) == 1
        assert restored.violations[0].node_id == "n1"
