"""Tests for pass lifecycle manager."""

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from humaninloop_brain.entities.catalog import NodeCatalog
from humaninloop_brain.entities.enums import EdgeType, NodeType
from humaninloop_brain.entities.nodes import EvidenceAttachment, NodeHistoryEntry
from humaninloop_brain.passes.lifecycle import (
    FrozenEntryError,
    _recompute_derived,
    add_or_reopen_node,
    compute_triggered_nodes,
    create_strategy_graph,
    freeze_current_pass,
    load_graph_file,
    save_graph,
    update_node_history,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def catalog():
    data = json.loads((FIXTURES_DIR / "specify-catalog.json").read_text())
    return NodeCatalog.model_validate(data)


@pytest.fixture
def graph():
    return create_strategy_graph("specify-auth")


class TestCreateStrategyGraph:
    def test_basic(self):
        g = create_strategy_graph("specify-auth")
        assert g.id == "specify-auth-strategy"
        assert g.workflow_id == "specify-auth"
        assert g.schema_version == "3.0.0"
        assert g.current_pass == 1
        assert g.status == "in-progress"
        assert len(g.passes) == 1
        assert g.passes[0].pass_number == 1
        assert g.passes[0].created_at is not None

    def test_created_at_set(self):
        g = create_strategy_graph("w")
        assert g.created_at is not None


class TestAddOrReopenNode:
    def test_add_new_node(self, graph, catalog):
        graph, edges = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        assert len(graph.nodes) == 1
        node = graph.nodes[0]
        assert node.id == "analyst-review"
        assert node.type == NodeType.task
        assert node.status == "pending"
        assert len(node.history) == 1
        assert node.history[0].pass_number == 1
        assert node.last_active_pass == 1

    def test_add_multiple_nodes_infers_edges(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph, edges = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        assert len(graph.nodes) == 2
        # advocate-review consumes spec.md + analyst-report.md produced by analyst-review
        assert len(edges) > 0
        edge_types = {e.type for e in edges}
        assert EdgeType.depends_on in edge_types

    def test_reopen_existing_node(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        assert len(graph.nodes[0].history) == 1

        # Reopen for pass 2
        graph, edges = add_or_reopen_node(graph, "analyst-review", catalog, 2)
        assert len(graph.nodes) == 1  # Still one node
        assert len(graph.nodes[0].history) == 2  # Two history entries
        assert graph.nodes[0].history[1].pass_number == 2
        assert graph.nodes[0].last_active_pass == 2
        assert edges == []  # No new edges on reopen

    def test_reopen_resets_to_initial_status(self, graph, catalog):
        """Reopened node must reset to initial catalog status (pending), not copy stale status."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        assert graph.nodes[0].status == "completed"

        # Reopen for pass 2 — should be "pending", not "completed"
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 2)
        assert graph.nodes[0].status == "pending"
        assert graph.nodes[0].history[-1].status == "pending"

    def test_node_not_in_catalog(self, graph, catalog):
        with pytest.raises(ValueError, match="not found in catalog"):
            add_or_reopen_node(graph, "nonexistent", catalog, 1)

    def test_add_gate_node(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "constitution-gate", catalog, 1)
        node = graph.nodes[0]
        assert node.type == NodeType.gate
        assert node.status == "pending"

    def test_add_milestone_node(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "spec-complete", catalog, 1)
        node = graph.nodes[0]
        assert node.type == NodeType.milestone


    def test_reopen_frozen_pass_rejected(self, graph, catalog):
        """Reopening a node for a pass with a frozen entry raises FrozenEntryError."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        graph = freeze_current_pass(graph, "completed", "done")
        # Pass 1 entry is now frozen — reopening for pass 1 must fail
        with pytest.raises(FrozenEntryError, match="frozen"):
            add_or_reopen_node(graph, "analyst-review", catalog, 1)

    def test_reopen_unfrozen_pass_allowed(self, graph, catalog):
        """Reopening a node for a different (unfrozen) pass succeeds."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        graph = update_node_history(graph, "advocate-review", 1, "completed", verdict="needs-revision")
        graph = freeze_current_pass(
            graph, "completed", "needs-revision",
            triggered_nodes=["analyst-review"],
            trigger_source="advocate-review",
            reason="test",
        )
        # Pass 2 is unfrozen — reopening for pass 2 must succeed
        graph, edges = add_or_reopen_node(graph, "analyst-review", catalog, 2)
        node = next(n for n in graph.nodes if n.id == "analyst-review")
        assert len(node.history) == 2
        assert node.history[1].pass_number == 2
        assert edges == []


class TestUpdateNodeHistory:
    def test_update_status(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "in-progress")
        node = graph.nodes[0]
        assert node.status == "in-progress"
        assert node.history[0].status == "in-progress"
        assert node.last_active_pass == 1

    def test_update_with_verdict(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        graph = update_node_history(
            graph, "advocate-review", 1, "completed", verdict="ready"
        )
        node = next(n for n in graph.nodes if n.id == "advocate-review")
        assert node.status == "completed"
        assert node.verdict == "ready"
        assert node.history[0].verdict == "ready"

    def test_update_with_evidence(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        ev = EvidenceAttachment(
            id="ev-01", type="file", description="Spec", reference="spec.md"
        )
        graph = update_node_history(
            graph, "analyst-review", 1, "completed", evidence=[ev]
        )
        assert len(graph.nodes[0].history[0].evidence) == 1

    def test_update_with_trace(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        trace = {"node_id": "analyst-review", "started_at": "2026-01-15T10:00:00Z"}
        graph = update_node_history(
            graph, "analyst-review", 1, "completed", trace=trace
        )
        assert graph.nodes[0].history[0].trace is not None

    def test_frozen_entry_rejected(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        graph = freeze_current_pass(graph, "completed", "done")
        # Entry is now frozen
        with pytest.raises(FrozenEntryError):
            update_node_history(graph, "analyst-review", 1, "in-progress")

    def test_invalid_status_rejected(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        with pytest.raises(ValueError, match="not valid for node type"):
            update_node_history(graph, "analyst-review", 1, "passed")

    def test_node_not_found(self, graph):
        with pytest.raises(ValueError, match="not found"):
            update_node_history(graph, "nonexistent", 1, "pending")

    def test_creates_entry_for_new_pass(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 2, "in-progress")
        assert len(graph.nodes[0].history) == 2
        assert graph.nodes[0].history[1].pass_number == 2

    def test_derived_fields_recomputed(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        node = graph.nodes[0]
        # Derived from latest history entry
        assert node.status == "completed"
        assert node.last_active_pass == 1


class TestFreezeCurrentPass:
    def test_basic_freeze(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        graph = freeze_current_pass(graph, "completed", "done")

        assert graph.passes[0].frozen is True
        assert graph.passes[0].outcome == "completed"
        assert graph.passes[0].completed_at is not None
        # History entry also frozen
        assert graph.nodes[0].history[0].frozen is True

    def test_freeze_marks_graph_completed(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = freeze_current_pass(graph, "completed", "done")
        assert graph.status == "completed"
        assert graph.completed_at is not None

    def test_freeze_with_triggered_nodes(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        graph = update_node_history(graph, "advocate-review", 1, "completed")
        graph = freeze_current_pass(
            graph,
            "completed",
            "advocate-verdict-needs-revision",
            triggered_nodes=["analyst-review"],
            trigger_source="advocate-review",
            reason="advocate verdict needs-revision",
        )

        # Should have a triggered_by edge from gate to triggered node
        trig_edges = [e for e in graph.edges if e.type == EdgeType.triggered_by]
        assert len(trig_edges) == 1
        assert trig_edges[0].source == "advocate-review"
        assert trig_edges[0].target == "analyst-review"
        assert trig_edges[0].source_pass == 1
        assert trig_edges[0].target_pass == 2
        assert trig_edges[0].reason == "advocate verdict needs-revision"

        # Should have created pass 2
        assert len(graph.passes) == 2
        assert graph.passes[1].pass_number == 2
        assert graph.current_pass == 2

        # Graph NOT marked completed (has next pass)
        assert graph.status == "in-progress"

    def test_freeze_requires_trigger_source_with_triggered_nodes(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        with pytest.raises(ValueError, match="trigger_source is required"):
            freeze_current_pass(
                graph, "completed", "done",
                triggered_nodes=["analyst-review"],
            )

    def test_freeze_refuses_pass_beyond_max(self, graph, catalog):
        """INV-004: freeze must refuse to create pass 6."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)

        # Advance to pass 5 by freezing 4 times
        for _ in range(4):
            graph = update_node_history(graph, "analyst-review", graph.current_pass, "completed")
            graph = update_node_history(graph, "advocate-review", graph.current_pass, "completed")
            graph = freeze_current_pass(
                graph, "completed", "needs-revision",
                triggered_nodes=["analyst-review"],
                trigger_source="advocate-review",
                reason="test",
            )
            graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, graph.current_pass)
            graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, graph.current_pass)

        assert graph.current_pass == 5

        # Pass 5 freeze with triggered_nodes should refuse
        graph = update_node_history(graph, "analyst-review", 5, "completed")
        graph = update_node_history(graph, "advocate-review", 5, "completed")
        with pytest.raises(ValueError, match="INV-004"):
            freeze_current_pass(
                graph, "completed", "needs-revision",
                triggered_nodes=["analyst-review"],
                trigger_source="advocate-review",
                reason="test",
            )

    def test_freeze_halted(self, graph, catalog):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = freeze_current_pass(graph, "halted", "critical gaps")
        assert graph.passes[0].outcome == "halted"
        # Halted without triggered nodes => completed
        assert graph.status == "completed"


class TestMultiPassScenario:
    def test_two_pass_workflow(self, graph, catalog):
        # Pass 1: add analyst + advocate, advocate says needs-revision
        graph, _ = add_or_reopen_node(graph, "constitution-gate", catalog, 1)
        graph = update_node_history(graph, "constitution-gate", 1, "passed")
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        graph = update_node_history(
            graph, "advocate-review", 1, "completed", verdict="needs-revision"
        )

        # Freeze pass 1, trigger pass 2
        graph = freeze_current_pass(
            graph,
            "completed",
            "advocate-verdict-needs-revision",
            triggered_nodes=["analyst-review"],
            trigger_source="advocate-review",
            reason="needs-revision",
        )
        assert graph.current_pass == 2

        # Pass 2: reopen analyst, add advocate again
        graph, reopened_edges = add_or_reopen_node(graph, "analyst-review", catalog, 2)
        assert reopened_edges == []
        assert len(graph.nodes[1].history) == 2  # analyst has 2 entries

        graph = update_node_history(graph, "analyst-review", 2, "completed")
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 2)
        graph = update_node_history(
            graph, "advocate-review", 2, "completed", verdict="ready"
        )

        # Freeze pass 2 as completed (no triggered_nodes => graph completes)
        graph = freeze_current_pass(graph, "completed", "advocate-verdict-ready")
        assert graph.status == "completed"
        assert len(graph.passes) == 2

        # Verify final state
        analyst = next(n for n in graph.nodes if n.id == "analyst-review")
        assert len(analyst.history) == 2
        # Derived from latest history entry (pass 2)
        assert analyst.status == "completed"
        assert analyst.last_active_pass == 2

        advocate = next(n for n in graph.nodes if n.id == "advocate-review")
        # advocate has 2 history entries (pass 1 + pass 2), latest has verdict=ready
        assert advocate.verdict == "ready"


class TestSaveLoadGraph:
    def test_save_and_load(self, graph, catalog, tmp_path):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")

        path = tmp_path / "test-graph.json"
        save_graph(graph, path)

        loaded = load_graph_file(path)
        assert loaded.id == graph.id
        assert len(loaded.nodes) == 1
        assert loaded.nodes[0].status == "completed"
        assert loaded.nodes[0].history[0].status == "completed"

    def test_roundtrip_preserves_structure(self, graph, catalog, tmp_path):
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        graph = update_node_history(graph, "advocate-review", 1, "completed")
        graph = freeze_current_pass(
            graph, "completed", "done",
            triggered_nodes=["analyst-review"],
            trigger_source="advocate-review",
            reason="test",
        )
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 2)

        path = tmp_path / "graph.json"
        save_graph(graph, path)
        loaded = load_graph_file(path)

        assert loaded.current_pass == 2
        assert len(loaded.passes) == 2
        node = loaded.nodes[0]
        assert len(node.history) == 2
        assert node.history[0].frozen is True


class TestVerdictValidation:
    """Verdict is only valid on gate nodes and must be a valid GateVerdict value.

    Covers lifecycle.py:194 (verdict on non-gate) and lifecycle.py:200 (invalid verdict).
    """

    def test_verdict_on_non_gate_raises(self, graph, catalog):
        """Setting verdict on a task node raises ValueError."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        with pytest.raises(ValueError, match="only valid for gate nodes"):
            update_node_history(graph, "analyst-review", 1, "completed", verdict="ready")

    def test_invalid_verdict_value_raises(self, graph, catalog):
        """Setting invalid verdict string on a gate raises ValueError."""
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        with pytest.raises(ValueError, match="not valid"):
            update_node_history(
                graph, "advocate-review", 1, "completed", verdict="invalid-verdict"
            )

    def test_valid_verdicts_accepted(self, graph, catalog):
        """All three GateVerdict values are accepted on gate nodes."""
        for verdict in ("ready", "needs-revision", "critical-gaps"):
            g, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
            g = update_node_history(g, "advocate-review", 1, "completed", verdict=verdict)
            node = next(n for n in g.nodes if n.id == "advocate-review")
            assert node.verdict == verdict


class TestFreezeValidation:
    """Freeze validation for trigger_source and triggered_nodes.

    Covers lifecycle.py:290 (trigger_source not in graph),
    lifecycle.py:296 (trigger_source not a gate),
    lifecycle.py:305 (triggered_nodes reference nonexistent nodes).
    """

    def test_trigger_source_not_in_graph(self, graph, catalog):
        """trigger_source referencing a nonexistent node raises ValueError."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        with pytest.raises(ValueError, match="does not exist in graph"):
            freeze_current_pass(
                graph, "completed", "done",
                triggered_nodes=["analyst-review"],
                trigger_source="nonexistent",
                reason="test",
            )

    def test_trigger_source_not_gate(self, graph, catalog):
        """trigger_source pointing to a task node raises ValueError."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        with pytest.raises(ValueError, match="must be a gate node"):
            freeze_current_pass(
                graph, "completed", "done",
                triggered_nodes=["analyst-review"],
                trigger_source="analyst-review",
                reason="test",
            )

    def test_triggered_nodes_nonexistent(self, graph, catalog):
        """triggered_nodes referencing nonexistent nodes raises ValueError."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        with pytest.raises(ValueError, match="nonexistent nodes"):
            freeze_current_pass(
                graph, "completed", "done",
                triggered_nodes=["nonexistent-node"],
                trigger_source="advocate-review",
                reason="test",
            )


class TestRecomputeDerived:
    """_recompute_derived handles edge cases.

    Covers lifecycle.py:40-43 (empty history returns node unchanged).
    """

    def test_empty_history_returns_node_unchanged(self):
        """Node with no history entries is returned unchanged."""
        from humaninloop_brain.entities.nodes import GraphNode

        node = GraphNode(
            id="test",
            type=NodeType.task,
            name="Test",
            description="Test node",
            status="pending",
            history=[],
            last_active_pass=None,
        )
        result = _recompute_derived(node)
        assert result.id == "test"
        assert result.status == "pending"
        assert result.history == []


class TestSaveGraphEdgeCases:
    """save_graph atomic write error paths.

    Covers lifecycle.py:425-426 (backup OSError) and
    lifecycle.py:442-448 (temp file cleanup on validation failure).
    """

    def test_save_creates_backup_file(self, graph, catalog, tmp_path):
        """save_graph creates a .bak file when overwriting existing file."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        path = tmp_path / "test-graph.json"

        # First save — no backup
        save_graph(graph, path)
        assert not path.with_suffix(".json.bak").exists()

        # Second save — backup should be created
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        save_graph(graph, path)
        assert path.with_suffix(".json.bak").exists()

    def test_save_validation_failure_cleans_temp(self, graph, catalog, tmp_path):
        """When re-validation of written file fails, temp file is cleaned up."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        path = tmp_path / "test-graph.json"

        # Patch model_validate_json to raise on the re-validation step
        with patch.object(
            type(graph), "model_validate_json",
            side_effect=ValueError("Corrupted JSON"),
        ):
            with pytest.raises(ValueError, match="Corrupted JSON"):
                save_graph(graph, path)

        # Original file should NOT exist (first write, no prior file)
        # Temp file should be cleaned up
        tmp_files = list(tmp_path.glob("*.tmp"))
        assert len(tmp_files) == 0, f"Temp file not cleaned up: {tmp_files}"

    def test_save_backup_oserror_ignored(self, graph, catalog, tmp_path):
        """OSError during backup is silently ignored (best-effort)."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        path = tmp_path / "test-graph.json"

        # First save to create the file
        save_graph(graph, path)

        # Make the backup path a directory so write_text fails with OSError
        backup_path = path.with_suffix(".json.bak")
        backup_path.mkdir()

        # Second save should succeed despite backup failure
        graph = update_node_history(graph, "analyst-review", 1, "completed")
        save_graph(graph, path)

        # Graph was saved successfully
        loaded = load_graph_file(path)
        assert loaded.nodes[0].status == "completed"


class TestComputeTriggeredNodes:
    """compute_triggered_nodes deterministically finds re-execution targets."""

    def test_gate_with_validates_edges(self, graph, catalog):
        """Gate + validated tasks are returned."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        triggered = compute_triggered_nodes(graph, "advocate-review")
        assert "advocate-review" in triggered
        assert "analyst-review" in triggered

    def test_returns_sorted(self, graph, catalog):
        """Output is deterministically sorted."""
        graph, _ = add_or_reopen_node(graph, "analyst-review", catalog, 1)
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        triggered = compute_triggered_nodes(graph, "advocate-review")
        assert triggered == sorted(triggered)

    def test_gate_without_validates_edges(self, graph, catalog):
        """Gate with no validates edges returns only itself."""
        graph, _ = add_or_reopen_node(graph, "constitution-gate", catalog, 1)
        triggered = compute_triggered_nodes(graph, "constitution-gate")
        assert triggered == ["constitution-gate"]

    def test_always_includes_source(self, graph, catalog):
        """Trigger source is always included even with no validates edges."""
        graph, _ = add_or_reopen_node(graph, "advocate-review", catalog, 1)
        triggered = compute_triggered_nodes(graph, "advocate-review")
        assert "advocate-review" in triggered
