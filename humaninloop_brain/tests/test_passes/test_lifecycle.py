"""Tests for pass lifecycle manager."""

import pytest

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.dag_pass import DAGPass, ExecutionTraceEntry
from humaninloop_brain.entities.enums import PassOutcome
from humaninloop_brain.passes.lifecycle import (
    FrozenPassError,
    add_node,
    add_trace_entry,
    create_pass,
    freeze_pass,
    load_pass,
    save_pass,
    update_node_status,
)


@pytest.fixture
def catalog(load_fixture):
    return NodeCatalog.model_validate(load_fixture("specify-catalog.json"))


class TestCreatePass:
    def test_basic(self):
        dag = create_pass("specify-feature-auth", 1)
        assert dag.workflow_id == "specify-feature-auth"
        assert dag.pass_number == 1
        assert dag.created_at is not None
        assert dag.outcome is None
        assert dag.nodes == []

    def test_id_format(self):
        dag = create_pass("my-workflow", 3)
        assert dag.id == "my-workflow-pass-003"


class TestAddNode:
    def test_add_single_node(self, catalog):
        dag = create_pass("w", 1)
        dag, edges = add_node(dag, "input-enrichment", catalog)
        assert len(dag.nodes) == 1
        assert dag.nodes[0].id == "input-enrichment"
        assert dag.nodes[0].status == "pending"

    def test_add_with_edge_inference(self, catalog):
        dag = create_pass("w", 1)
        dag, _ = add_node(dag, "input-enrichment", catalog)
        dag, edges = add_node(dag, "analyst-review", catalog)
        assert len(dag.nodes) == 2
        assert len(edges) > 0  # Should infer depends-on and produces

    def test_reject_duplicate(self, catalog):
        dag = create_pass("w", 1)
        dag, _ = add_node(dag, "input-enrichment", catalog)
        with pytest.raises(ValueError, match="already exists"):
            add_node(dag, "input-enrichment", catalog)

    def test_reject_unknown_node(self, catalog):
        dag = create_pass("w", 1)
        with pytest.raises(ValueError, match="not found in catalog"):
            add_node(dag, "nonexistent", catalog)

    def test_reject_frozen_pass(self, catalog):
        dag = create_pass("w", 1)
        freeze_pass(dag, PassOutcome.completed, "done", "rationale")
        with pytest.raises(FrozenPassError):
            add_node(dag, "input-enrichment", catalog)


class TestUpdateNodeStatus:
    def test_update_status(self, catalog):
        dag = create_pass("w", 1)
        dag, _ = add_node(dag, "input-enrichment", catalog)
        update_node_status(dag, "input-enrichment", "completed")
        assert dag.nodes[0].status == "completed"

    def test_invalid_status(self, catalog):
        dag = create_pass("w", 1)
        dag, _ = add_node(dag, "input-enrichment", catalog)
        with pytest.raises(ValueError, match="not valid for node type"):
            update_node_status(dag, "input-enrichment", "passed")

    def test_unknown_node(self, catalog):
        dag = create_pass("w", 1)
        with pytest.raises(ValueError, match="not found"):
            update_node_status(dag, "nonexistent", "pending")

    def test_reject_frozen_pass(self, catalog):
        dag = create_pass("w", 1)
        dag, _ = add_node(dag, "input-enrichment", catalog)
        freeze_pass(dag, PassOutcome.completed, "d", "r")
        with pytest.raises(FrozenPassError):
            update_node_status(dag, "input-enrichment", "completed")


class TestAddTraceEntry:
    def test_add_entry(self, catalog):
        dag = create_pass("w", 1)
        entry = ExecutionTraceEntry(
            node_id="input-enrichment",
            started_at="2026-01-15T10:00:00Z",
            completed_at="2026-01-15T10:05:00Z",
        )
        add_trace_entry(dag, entry)
        assert len(dag.execution_trace) == 1

    def test_reject_frozen_pass(self):
        dag = create_pass("w", 1)
        freeze_pass(dag, PassOutcome.completed, "d", "r")
        entry = ExecutionTraceEntry(
            node_id="n", started_at="2026-01-15T10:00:00Z"
        )
        with pytest.raises(FrozenPassError):
            add_trace_entry(dag, entry)


class TestFreezePass:
    def test_freeze(self):
        dag = create_pass("w", 1)
        freeze_pass(dag, PassOutcome.completed, "advocate-verdict-ready", "All checks passed")
        assert dag.outcome == PassOutcome.completed
        assert dag.outcome_detail == "advocate-verdict-ready"
        assert dag.completed_at is not None

    def test_double_freeze_rejected(self):
        dag = create_pass("w", 1)
        freeze_pass(dag, PassOutcome.completed, "d", "r")
        with pytest.raises(FrozenPassError, match="already frozen"):
            freeze_pass(dag, PassOutcome.halted, "d2", "r2")


class TestSaveAndLoad:
    def test_roundtrip(self, tmp_path, catalog):
        dag = create_pass("specify-feature-auth", 1)
        dag, _ = add_node(dag, "input-enrichment", catalog)
        dag, _ = add_node(dag, "analyst-review", catalog)
        dag, _ = add_node(dag, "advocate-review", catalog)
        update_node_status(dag, "input-enrichment", "completed")
        freeze_pass(dag, PassOutcome.completed, "done", "rationale")

        path = tmp_path / "dag.json"
        save_pass(dag, path)
        loaded = load_pass(path)

        assert loaded.id == dag.id
        assert loaded.workflow_id == dag.workflow_id
        assert loaded.outcome == PassOutcome.completed
        assert len(loaded.nodes) == 3
        assert loaded.nodes[0].status == "completed"

    def test_full_lifecycle(self, tmp_path, catalog):
        """Full lifecycle: create -> add 3 nodes -> update -> freeze -> save -> load."""
        # Create
        dag = create_pass("specify-feature-auth", 1)
        assert dag.outcome is None

        # Add nodes
        dag, e1 = add_node(dag, "input-enrichment", catalog)
        dag, e2 = add_node(dag, "analyst-review", catalog)
        dag, e3 = add_node(dag, "advocate-review", catalog)
        assert len(dag.nodes) == 3
        total_edges = len(dag.edges)
        assert total_edges > 0

        # Update statuses
        update_node_status(dag, "input-enrichment", "completed")
        update_node_status(dag, "analyst-review", "completed")
        update_node_status(dag, "advocate-review", "passed")

        # Add trace
        add_trace_entry(
            dag,
            ExecutionTraceEntry(
                node_id="input-enrichment",
                started_at="2026-01-15T10:00:00Z",
                completed_at="2026-01-15T10:01:00Z",
            ),
        )

        # Freeze
        freeze_pass(dag, PassOutcome.completed, "advocate-verdict-ready", "All done")
        assert dag.outcome == PassOutcome.completed

        # Save + Load
        path = tmp_path / "pass.json"
        save_pass(dag, path)
        loaded = load_pass(path)

        assert loaded.id == dag.id
        assert loaded.outcome == PassOutcome.completed
        assert len(loaded.nodes) == 3
        assert len(loaded.edges) == total_edges
        assert len(loaded.execution_trace) == 1
        assert loaded.nodes[2].status == "passed"
