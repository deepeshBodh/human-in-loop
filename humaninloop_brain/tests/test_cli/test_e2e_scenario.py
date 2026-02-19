"""End-to-end scenario tests for /specify workflow through CLI (v3).

All scenarios use the v3 StrategyGraph single-DAG model.
Each scenario exercises a complete or partial workflow path.

Scenario 1: Skip enrichment (single pass)
Scenario 2: Normal pass with enrichment (single pass)
Scenario 3: Multi-pass revision with triggered-by edges
Scenario 4: Multi-pass with human clarification
Scenario 5: Halted outcome and mutation blocking
Scenario 6: V3 gate lifecycle status transitions
Scenario 7: Parametrized status lifecycle (valid + invalid)
Scenario 8: Edge inference exact counts and types
Scenario 9: Milestone INV-001 violation
Scenario 10: Node reopen in multi-pass
"""

import json
from pathlib import Path

import pytest

from humaninloop_brain.cli.main import main

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
CATALOG = str(FIXTURES_DIR / "specify-catalog.json")


def _bootstrap_and_assemble(tmp_path, capsys, workflow_id, nodes):
    """Bootstrap a v3 StrategyGraph and assemble nodes sequentially.

    Returns (dag_path, outputs) where outputs is a list of parsed JSON
    for each assemble command.
    """
    dag_path = str(tmp_path / "strategy.json")
    outputs = []
    for i, node_id in enumerate(nodes):
        args = ["assemble", dag_path, "--catalog", CATALOG, "--node", node_id]
        if i == 0:
            args.extend(["--workflow", workflow_id])
        code = main(args)
        assert code == 0, f"Failed to assemble {node_id}"
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid", f"Assembly invalid for {node_id}: {out}"
        outputs.append(out)
    return dag_path, outputs


class TestScenario1SkipEnrichment:
    """Full Scenario 1: constitution-gate -> analyst -> advocate."""

    def test_full_walkthrough(self, tmp_path, capsys):
        dag_path = str(tmp_path / "strategy.json")

        # Step 1: Bootstrap with constitution-gate
        code = main([
            "assemble", dag_path, "--catalog", CATALOG,
            "--node", "constitution-gate", "--workflow", "specify-feature-auth",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "constitution-gate"
        assert out["node_added"]["type"] == "gate"

        # Step 2: Validate catalog
        code = main(["catalog-validate", CATALOG])
        assert code == 0
        capsys.readouterr()

        # Step 3: Assemble analyst-review
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "analyst-review"

        # Step 4: Update analyst status
        code = main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"

        # Step 5: Assemble advocate-review
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "advocate-review"
        assert out["edges_inferred"] > 0

        # Step 6: Topological sort
        code = main(["sort", dag_path])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        order = out["order"]
        assert order.index("advocate-review") > order.index("analyst-review")

        # Step 7: Validate
        code = main(["validate", dag_path, "--catalog", CATALOG])
        assert code == 0
        capsys.readouterr()

        # Step 8: Freeze
        code = main(["freeze", dag_path, "--outcome", "completed", "--detail", "advocate-verdict-ready"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True

        # Step 9: Verify structure
        data = json.loads(Path(dag_path).read_text())
        assert data["schema_version"] == "3.0.0"
        assert data["status"] == "completed"
        node_ids = {n["id"] for n in data["nodes"]}
        assert node_ids == {"constitution-gate", "analyst-review", "advocate-review"}
        assert "input-enrichment" not in node_ids


class TestScenario2NormalPassWithEnrichment:
    """Scenario 2: constitution-gate -> input-enrichment -> analyst -> advocate."""

    def test_full_walkthrough(self, tmp_path, capsys):
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-feature-sparse", nodes)

        data = json.loads(Path(dag_path).read_text())
        assert len(data["nodes"]) == 4

    def test_node_count_and_ids(self, tmp_path, capsys):
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-feature-sparse", nodes)

        data = json.loads(Path(dag_path).read_text())
        node_ids = {n["id"] for n in data["nodes"]}
        assert node_ids == {"constitution-gate", "input-enrichment", "analyst-review", "advocate-review"}

    def test_edge_count(self, tmp_path, capsys):
        """Verify edge inference: constitution-gate=0, enrichment=0, analyst=2, advocate=3."""
        dag_path = str(tmp_path / "strategy.json")

        # constitution-gate: 0 edges
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate", "--workflow", "w"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 0

        # input-enrichment: 0 edges
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "input-enrichment"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 0

        # analyst-review: 3 edges (informed-by + produces from enrichment, constrained-by to gate)
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 3

        # advocate-review: 3 edges (depends-on + produces + validates)
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 3

    def test_topological_order(self, tmp_path, capsys):
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-feat", nodes)

        code = main(["sort", dag_path])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        order = out["order"]
        # enriched-input is optional (informed_by), so no topological constraint
        # between enrichment and analyst. Only hard dependency: analyst < advocate.
        assert order.index("analyst-review") < order.index("advocate-review")

    def test_total_edges_in_dag(self, tmp_path, capsys):
        """Total edges in full 4-node enrichment pass should be 6 (0+0+3+3)."""
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-feat", nodes)

        data = json.loads(Path(dag_path).read_text())
        assert len(data["edges"]) == 6


class TestScenario3MultiPassRevision:
    """Scenario 3: Multi-pass with triggered-by edges in single file.

    Pass 1: constitution-gate -> analyst -> advocate -> freeze(needs-revision)
    Pass 2: analyst (reopen) -> advocate (reopen) -> freeze
    """

    def test_single_file_multi_pass(self, tmp_path, capsys):
        """Everything stays in one StrategyGraph file across passes."""
        nodes = ["constitution-gate", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-revision", nodes)

        # Freeze pass 1 with triggered nodes
        code = main([
            "freeze", dag_path, "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review", "advocate-review",
            "--trigger-source", "advocate-review",
            "--reason", "Advocate found gaps requiring research",
        ])
        assert code == 0
        capsys.readouterr()

        # Verify pass 1 frozen, pass 2 created
        data = json.loads(Path(dag_path).read_text())
        assert data["current_pass"] == 2
        assert data["status"] == "in-progress"
        assert len(data["passes"]) == 2
        assert data["passes"][0]["frozen"] is True
        assert data["passes"][1]["frozen"] is False

        # Verify triggered-by edges: source is the gate, target is the triggered node
        triggered_edges = [e for e in data["edges"] if e["type"] == "triggered-by"]
        assert len(triggered_edges) == 2
        for edge in triggered_edges:
            assert edge["source"] == "advocate-review", "trigger source should be the gate node"
            assert edge["target"] in ("analyst-review", "advocate-review")
            assert edge["source_pass"] == 1
            assert edge["target_pass"] == 2
            assert edge["reason"] == "Advocate found gaps requiring research"

    def test_pass2_reopen_and_assemble(self, tmp_path, capsys):
        """Pass 2: reopen existing nodes in same file."""
        nodes = ["constitution-gate", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-revision", nodes)

        # Freeze pass 1
        main([
            "freeze", dag_path, "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review",
            "--trigger-source", "advocate-review",
            "--reason", "Gaps found",
        ])
        capsys.readouterr()

        # Reopen analyst-review in pass 2
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "analyst-review"
        assert out["edges_inferred"] == 0  # No new edges for reopened node

        # Verify node history has entries for both passes
        data = json.loads(Path(dag_path).read_text())
        analyst = next(n for n in data["nodes"] if n["id"] == "analyst-review")
        assert len(analyst["history"]) == 2
        assert analyst["history"][0]["pass"] == 1
        assert analyst["history"][1]["pass"] == 2

    def test_pass1_entries_frozen(self, tmp_path, capsys):
        """Frozen pass 1 history entries reject modifications."""
        nodes = ["constitution-gate", "analyst-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-revision", nodes)

        main([
            "freeze", dag_path, "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review",
            "--trigger-source", "constitution-gate",
            "--reason", "Gaps",
        ])
        capsys.readouterr()

        # Try to update pass 1 entry (frozen) — should fail
        code = main([
            "status", dag_path, "--node", "analyst-review",
            "--status", "completed", "--pass", "1",
        ])
        assert code == 1

    def test_pass2_entries_modifiable(self, tmp_path, capsys):
        """Pass 2 entries are modifiable after pass 1 freeze."""
        nodes = ["constitution-gate", "analyst-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-revision", nodes)

        main([
            "freeze", dag_path, "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review",
            "--trigger-source", "constitution-gate",
            "--reason", "Gaps",
        ])
        capsys.readouterr()

        # Reopen in pass 2
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        capsys.readouterr()

        # Update pass 2 entry — should succeed
        code = main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        assert code == 0


class TestScenario4MultiPassClarification:
    """Scenario 4: Multi-pass with human-clarification decision node."""

    def test_decision_node_type(self, tmp_path, capsys):
        """human-clarification is assembled as a decision node."""
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-clarify",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["type"] == "decision"

    def test_decision_node_edge_inference(self, tmp_path, capsys):
        """Decision node: depends-on inferred from advocate (1 edge)."""
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-clarify",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 1

    def test_decision_initial_status(self, tmp_path, capsys):
        """Decision node gets initial status 'pending'."""
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-clarify",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["status"] == "pending"


class TestScenario5HaltedOutcome:
    """Scenario 5: Freeze with halted outcome, verify all mutations blocked."""

    def test_freeze_halted(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-halt",
            ["constitution-gate", "analyst-review"],
        )

        code = main([
            "freeze", dag_path, "--outcome", "halted",
            "--detail", "user-cancelled",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True
        assert out["outcome"] == "halted"

    def test_halted_outcome_persisted(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-halt",
            ["constitution-gate", "analyst-review"],
        )
        main(["freeze", dag_path, "--outcome", "halted", "--detail", "user-cancelled"])
        capsys.readouterr()

        data = json.loads(Path(dag_path).read_text())
        assert data["status"] == "completed"
        assert data["completed_at"] is not None
        pass_entry = data["passes"][0]
        assert pass_entry["outcome"] == "halted"
        assert pass_entry["detail"] == "user-cancelled"

    def test_halted_blocks_assemble(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-halt", ["constitution-gate"],
        )
        main(["freeze", dag_path, "--outcome", "halted", "--detail", "halt"])
        capsys.readouterr()

        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "completed" in out["message"].lower()

    def test_halted_blocks_status(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-halt", ["constitution-gate"],
        )
        main(["freeze", dag_path, "--outcome", "halted", "--detail", "halt"])
        capsys.readouterr()

        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        assert code == 1

    def test_halted_blocks_refreeze(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-halt", ["constitution-gate"],
        )
        main(["freeze", dag_path, "--outcome", "halted", "--detail", "halt"])
        capsys.readouterr()

        code = main(["freeze", dag_path, "--outcome", "completed", "--detail", "retry"])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "frozen" in out["message"].lower()


class TestScenario6V3GateLifecycle:
    """Scenario 6: V3 gate lifecycle with completed status and separate verdict."""

    def test_gate_lifecycle_statuses(self, tmp_path, capsys):
        """V3 gates support both 'completed' (agent-backed) and 'passed' (deterministic)."""
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-status",
            ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"],
        )

        # Deterministic gate uses "passed"
        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["new_status"] == "passed"

        # Agent-backed gate uses "completed"
        code = main(["status", dag_path, "--node", "advocate-review", "--status", "completed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["new_status"] == "completed"

    def test_task_in_progress_then_completed(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-status",
            ["constitution-gate", "input-enrichment"],
        )

        code = main(["status", dag_path, "--node", "input-enrichment", "--status", "in-progress"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["old_status"] == "pending"
        assert out["new_status"] == "in-progress"

        code = main(["status", dag_path, "--node", "input-enrichment", "--status", "completed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["old_status"] == "in-progress"
        assert out["new_status"] == "completed"

    def test_gate_in_progress_then_completed(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-status", ["constitution-gate"],
        )

        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "in-progress"])
        assert code == 0
        capsys.readouterr()

        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "completed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["new_status"] == "completed"


class TestScenario7StatusLifecycle:
    """Scenario 7: Parametrized valid + invalid status transitions (v3)."""

    def _build_full_dag(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-lifecycle",
            [
                "constitution-gate",
                "input-enrichment",
                "analyst-review",
                "advocate-review",
                "human-clarification",
                "targeted-research",
            ],
        )
        return dag_path

    @pytest.mark.parametrize("node_id,status", [
        ("input-enrichment", "completed"),
        ("input-enrichment", "halted"),
        ("input-enrichment", "skipped"),
        # V3 gates use GateLifecycleStatus
        ("advocate-review", "in-progress"),
        ("advocate-review", "completed"),
        # Decision status
        ("human-clarification", "decided"),
    ])
    def test_valid_status_transitions(self, tmp_path, capsys, node_id, status):
        dag_path = self._build_full_dag(tmp_path, capsys)
        code = main(["status", dag_path, "--node", node_id, "--status", status])
        assert code == 0, f"Expected {node_id} to accept status '{status}'"

    @pytest.mark.parametrize("node_id,status", [
        ("input-enrichment", "passed"),       # task can't have gate status
        ("input-enrichment", "decided"),       # task can't have decision status
        ("advocate-review", "decided"),        # gate can't have decision status
        ("advocate-review", "needs-revision"), # gate can't have verdict as status
        ("human-clarification", "completed"),  # decision can't have task status
    ])
    def test_invalid_status_rejections(self, tmp_path, capsys, node_id, status):
        dag_path = self._build_full_dag(tmp_path, capsys)
        code = main(["status", dag_path, "--node", node_id, "--status", status])
        assert code == 1, f"Expected {node_id} to reject status '{status}'"


class TestScenario8EdgeInference:
    """Scenario 8: Exact edge counts and types for all assembly pairs."""

    def test_constitution_gate_zero_edges(self, tmp_path, capsys):
        dag_path = str(tmp_path / "strategy.json")
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate", "--workflow", "w"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 0

    def test_enrichment_to_analyst_two_edges(self, tmp_path, capsys):
        dag_path = str(tmp_path / "strategy.json")
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "input-enrichment", "--workflow", "w"])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 2

    def test_analyst_to_advocate_three_edges(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "w", ["constitution-gate", "analyst-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 3

    def test_advocate_to_clarification_one_edge(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "w",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 1

    def test_advocate_to_research_one_edge(self, tmp_path, capsys):
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "w",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "targeted-research"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 1

    def test_informed_by_and_constrained_by_inferred(self, tmp_path, capsys):
        """Optional artifacts get informed-by edges; shared gate artifacts get constrained-by."""
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "w", nodes)

        data = json.loads(Path(dag_path).read_text())
        edge_types = {e["type"] for e in data["edges"]}
        assert "informed-by" in edge_types  # enriched-input is optional for analyst
        assert "constrained-by" in edge_types  # analyst constrained by constitution-gate

    def test_edge_id_pattern(self, tmp_path, capsys):
        nodes = ["constitution-gate", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "w", nodes)

        data = json.loads(Path(dag_path).read_text())
        for edge in data["edges"]:
            assert edge["id"].startswith("inferred-"), f"Edge {edge['id']} missing inferred prefix"


class TestScenario9MilestoneINV001:
    """Scenario 9: INV-001 violation when task directly reaches milestone."""

    def test_task_to_milestone_without_gate_fails_validation(self, tmp_path, capsys):
        """Assembling spec-complete after analyst (no advocate gate) triggers INV-001.

        analyst-review(task) -> spec-complete(milestone) with inferred depends-on
        bypasses gate requirement. Need constitution-gate for INV-002 to pass.
        """
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "specify-inv001",
            ["constitution-gate", "analyst-review"],
        )

        # spec-complete: consumes spec.md (produced by analyst) + advocate-report.md (not produced)
        # Direct task->milestone path without advocate gate -> INV-001 or UNSATISFIED_CONTRACT
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "spec-complete"])
        out = json.loads(capsys.readouterr().out)
        assert code == 1
        assert out["status"] == "invalid"

    def test_spec_complete_succeeds_with_gate_path(self, tmp_path, capsys):
        """spec-complete succeeds when advocate gate creates the path."""
        dag_path, _ = _bootstrap_and_assemble(
            tmp_path, capsys, "w",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "spec-complete"])
        out = json.loads(capsys.readouterr().out)
        assert code == 0
        assert out["status"] == "valid"


class TestScenario10NodeReopen:
    """Scenario 10: Node reopen across passes — single file, history tracking."""

    def test_reopen_adds_history_entry(self, tmp_path, capsys):
        """Reopening adds a new history entry without new edges."""
        nodes = ["constitution-gate", "analyst-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-reopen", nodes)

        # Complete pass 1
        main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        capsys.readouterr()
        main([
            "freeze", dag_path, "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review",
            "--trigger-source", "constitution-gate",
            "--reason", "Needs rework",
        ])
        capsys.readouterr()

        # Reopen in pass 2
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 0  # No new edges

        # Verify history
        data = json.loads(Path(dag_path).read_text())
        analyst = next(n for n in data["nodes"] if n["id"] == "analyst-review")
        assert len(analyst["history"]) == 2
        assert analyst["history"][0]["pass"] == 1
        assert analyst["history"][0]["frozen"] is True
        assert analyst["history"][1]["pass"] == 2
        assert analyst["history"][1]["frozen"] is False

    def test_reopen_preserves_original_edges(self, tmp_path, capsys):
        """Original edges from pass 1 remain after reopen."""
        nodes = ["constitution-gate", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-reopen", nodes)

        data_before = json.loads(Path(dag_path).read_text())
        edge_count_before = len(data_before["edges"])

        # Freeze and reopen
        main([
            "freeze", dag_path, "--outcome", "completed",
            "--detail", "revision",
            "--triggered-nodes", "analyst-review",
            "--trigger-source", "advocate-review",
            "--reason", "Gaps",
        ])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        capsys.readouterr()

        data_after = json.loads(Path(dag_path).read_text())
        # Original edges + 1 triggered-by edge
        assert len(data_after["edges"]) == edge_count_before + 1

    def test_full_two_pass_workflow(self, tmp_path, capsys):
        """Complete two-pass workflow in a single file."""
        # Pass 1
        nodes = ["constitution-gate", "analyst-review", "advocate-review"]
        dag_path, _ = _bootstrap_and_assemble(tmp_path, capsys, "specify-2pass", nodes)

        main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        main(["status", dag_path, "--node", "advocate-review", "--status", "completed"])
        capsys.readouterr()

        main([
            "freeze", dag_path, "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review", "advocate-review",
            "--trigger-source", "advocate-review",
            "--reason", "Gaps found",
        ])
        capsys.readouterr()

        # Pass 2
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        capsys.readouterr()

        main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        main(["status", dag_path, "--node", "advocate-review", "--status", "completed"])
        capsys.readouterr()

        main(["freeze", dag_path, "--outcome", "completed", "--detail", "advocate-verdict-ready"])
        capsys.readouterr()

        # Verify final state
        data = json.loads(Path(dag_path).read_text())
        assert data["status"] == "completed"
        assert data["current_pass"] == 2
        assert len(data["passes"]) == 2
        assert data["passes"][0]["frozen"] is True
        assert data["passes"][1]["frozen"] is True

        # Each reopened node has 2 history entries
        analyst = next(n for n in data["nodes"] if n["id"] == "analyst-review")
        assert len(analyst["history"]) == 2

        # Triggered-by edges exist
        triggered = [e for e in data["edges"] if e["type"] == "triggered-by"]
        assert len(triggered) == 2
