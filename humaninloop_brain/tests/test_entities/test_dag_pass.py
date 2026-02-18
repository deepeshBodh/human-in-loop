"""Tests for pass-level entities."""

import json

import pytest

from humaninloop_brain.entities.dag_pass import (
    ExecutionTraceEntry,
    PassEntry,
)


class TestExecutionTraceEntry:
    def test_basic(self):
        entry = ExecutionTraceEntry(
            node_id="analyst-review",
            started_at="2026-01-15T10:00:00Z",
            completed_at="2026-01-15T10:05:00Z",
            verdict=None,
            agent_report_summary="Produced spec.md",
            artifacts_produced=["spec.md"],
        )
        assert entry.node_id == "analyst-review"
        assert entry.artifacts_produced == ["spec.md"]

    def test_minimal(self):
        entry = ExecutionTraceEntry(
            node_id="n", started_at="2026-01-15T10:00:00Z"
        )
        assert entry.completed_at is None
        assert entry.verdict is None
        assert entry.artifacts_produced == []

    def test_frozen(self):
        entry = ExecutionTraceEntry(
            node_id="n", started_at="2026-01-15T10:00:00Z"
        )
        with pytest.raises(Exception):
            entry.node_id = "other"


class TestPassEntry:
    def test_construct(self):
        entry = PassEntry(pass_number=1)
        assert entry.pass_number == 1
        assert entry.outcome is None
        assert entry.detail is None
        assert entry.created_at is None
        assert entry.completed_at is None
        assert entry.frozen is False

    def test_with_all_fields(self):
        entry = PassEntry(
            pass_number=2,
            outcome="completed",
            detail="advocate-verdict-needs-revision",
            created_at="2026-01-15T10:00:00Z",
            completed_at="2026-01-15T10:30:00Z",
            frozen=True,
        )
        assert entry.outcome == "completed"
        assert entry.frozen is True

    def test_frozen(self):
        entry = PassEntry(pass_number=1)
        with pytest.raises(Exception):
            entry.outcome = "completed"

    def test_serialization_roundtrip(self):
        entry = PassEntry(pass_number=1, outcome="completed", detail="done")
        data = entry.model_dump()
        restored = PassEntry.model_validate(data)
        assert restored == entry
