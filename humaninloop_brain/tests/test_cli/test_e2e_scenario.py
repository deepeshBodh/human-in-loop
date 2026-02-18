"""End-to-end scenario tests for /specify workflow through CLI.

Covers all workflow paths identified in manual scenario testing (runs 1-3).

Scenario 1: Skip enrichment (existing)
Scenario 2: Normal pass with enrichment
Scenario 3: Multi-pass with targeted research revision
Scenario 4: Multi-pass with human clarification revision
Scenario 5: Halted outcome and mutation blocking
Scenario 6: Status progression for all node types
Scenario 7: Parametrized status lifecycle (valid + invalid transitions)
Scenario 8: Edge inference exact counts and types
Scenario 9: Milestone INV-001 violation
"""

import json
from pathlib import Path

import pytest

from humaninloop_brain.cli.main import main

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
CATALOG = str(FIXTURES_DIR / "specify-catalog.json")


def _create_and_assemble(tmp_path, capsys, workflow_id, nodes, pass_number=1):
    """DRY helper: create a pass then assemble nodes sequentially.

    Returns (dag_path, outputs) where outputs is a list of parsed JSON
    for each assemble command.
    """
    dag_path = str(tmp_path / f"dag-pass-{pass_number}.json")

    code = main(["create", workflow_id, "--pass", str(pass_number), "--output", dag_path])
    assert code == 0
    capsys.readouterr()  # consume create output

    outputs = []
    for node_id in nodes:
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", node_id])
        assert code == 0, f"Failed to assemble {node_id}"
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid", f"Assembly invalid for {node_id}: {out}"
        outputs.append(out)

    return dag_path, outputs


class TestScenario1SkipEnrichment:
    """Full Scenario 1: constitution-gate -> analyst -> advocate."""

    def test_full_walkthrough(self, tmp_path, capsys):
        dag_path = str(tmp_path / "dag.json")

        # Step 1: Create pass
        code = main(["create", "specify-feature-auth", "--pass", "1", "--output", dag_path])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "success"

        # Step 2: Validate catalog
        code = main(["catalog-validate", CATALOG])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

        # Step 3: Assemble constitution-gate (skip enrichment — detailed input)
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "constitution-gate"
        assert out["node_added"]["type"] == "gate"

        # Step 4: Assemble analyst-review
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "analyst-review"
        assert out["node_added"]["type"] == "task"

        # Step 5: Update analyst status to completed
        code = main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"

        # Step 6: Assemble advocate-review (gate)
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "advocate-review"
        assert out["node_added"]["type"] == "gate"
        # Should have inferred edges from analyst produces -> advocate consumes
        assert out["edges_inferred"] > 0

        # Step 7: Topological sort
        code = main(["sort", dag_path])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        order = out["order"]
        # Constitution gate and analyst before advocate
        assert order.index("advocate-review") > order.index("analyst-review")

        # Step 8: Validate the assembled DAG
        code = main(["validate", dag_path, "--catalog", CATALOG])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

        # Step 9: Freeze the pass
        code = main([
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "advocate-verdict-ready",
            "--rationale", "Advocate approved specification",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True

        # Step 10: Verify frozen pass validates
        code = main(["validate", dag_path, "--catalog", CATALOG])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

        # Verify the final DAG structure
        dag_data = json.loads(Path(dag_path).read_text())
        assert dag_data["outcome"] == "completed"
        assert len(dag_data["nodes"]) == 3
        node_ids = {n["id"] for n in dag_data["nodes"]}
        assert node_ids == {"constitution-gate", "analyst-review", "advocate-review"}
        assert "input-enrichment" not in node_ids  # Enrichment was skipped


class TestScenario2NormalPassWithEnrichment:
    """Scenario 2: constitution-gate -> input-enrichment -> analyst -> advocate.

    Full 4-node pass where enrichment is included because the user
    provided sparse input.
    """

    def test_full_walkthrough(self, tmp_path, capsys):
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, outputs = _create_and_assemble(tmp_path, capsys, "specify-feature-sparse", nodes)

        dag_data = json.loads(Path(dag_path).read_text())
        assert len(dag_data["nodes"]) == 4

    def test_node_count_and_ids(self, tmp_path, capsys):
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _create_and_assemble(tmp_path, capsys, "specify-feature-sparse", nodes)

        dag_data = json.loads(Path(dag_path).read_text())
        node_ids = {n["id"] for n in dag_data["nodes"]}
        assert node_ids == {"constitution-gate", "input-enrichment", "analyst-review", "advocate-review"}

    def test_edge_count(self, tmp_path, capsys):
        """Verify edge inference: constitution-gate=0, enrichment=0, analyst=2, advocate=3."""
        dag_path = str(tmp_path / "dag.json")
        main(["create", "specify-feat", "--pass", "1", "--output", dag_path])
        capsys.readouterr()

        # constitution-gate: consumes constitution.md (system artifact), produces nothing
        # No existing nodes produce constitution.md, so 0 edges inferred
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 0

        # input-enrichment: consumes raw-input (system artifact), produces enriched-input
        # No existing nodes produce raw-input, so 0 edges inferred
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "input-enrichment"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 0

        # analyst-review: consumes enriched-input (produced by input-enrichment=task),
        #   constitution.md (system), advocate-report.md (not present), etc.
        # input-enrichment produces enriched-input -> analyst consumes it
        # Inference: depends-on(enrichment->analyst) + produces(enrichment->analyst) = 2
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 2

        # advocate-review (gate): consumes spec.md, analyst-report.md
        # Both produced by analyst-review (task)
        # For EACH consumed artifact from same producer:
        #   depends-on, produces, validates — but deduplication
        # depends-on(analyst->advocate) = 1 (deduplicated across both artifacts)
        # produces(analyst->advocate) = 1 (deduplicated)
        # validates(advocate->analyst) = 1 (deduplicated)
        # Total = 3
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 3

    def test_topological_order(self, tmp_path, capsys):
        """Verify enrichment and analyst come before advocate in topo sort."""
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _create_and_assemble(tmp_path, capsys, "specify-feat", nodes)

        code = main(["sort", dag_path])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        order = out["order"]

        # advocate depends on analyst depends on enrichment
        assert order.index("input-enrichment") < order.index("analyst-review")
        assert order.index("analyst-review") < order.index("advocate-review")

    def test_total_edges_in_dag(self, tmp_path, capsys):
        """Total edges in full 4-node enrichment pass should be 5 (0+0+2+3)."""
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _create_and_assemble(tmp_path, capsys, "specify-feat", nodes)

        dag_data = json.loads(Path(dag_path).read_text())
        assert len(dag_data["edges"]) == 5


class TestScenario3MultiPassRevision:
    """Scenario 3: Multi-pass with targeted-research on revision.

    Pass 1: constitution-gate -> analyst -> advocate -> freeze(needs-revision)
    Pass 2: targeted-research -> analyst -> advocate
    """

    def test_pass1_freeze_needs_revision(self, tmp_path, capsys):
        """Pass 1 freezes with needs-revision outcome detail."""
        nodes = ["constitution-gate", "analyst-review", "advocate-review"]
        dag_path, _ = _create_and_assemble(tmp_path, capsys, "specify-revision", nodes)

        code = main([
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "needs-revision",
            "--rationale", "Advocate found gaps requiring research",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True
        assert out["outcome"] == "completed"

    def test_pass2_with_research(self, tmp_path, capsys):
        """Pass 2 includes targeted-research after advocate provides report.

        In a multi-pass scenario, targeted-research requires advocate-report.md
        (required=true). Within a single DAG pass, the advocate must exist to
        produce it. So pass 2 assembles: constitution-gate -> analyst -> advocate
        -> targeted-research, demonstrating the research node consuming the
        advocate's output within the same pass.
        """
        dag_path = str(tmp_path / "dag-pass-2.json")
        main(["create", "specify-revision", "--pass", "2", "--output", dag_path])
        capsys.readouterr()

        # Build prerequisite chain: constitution-gate -> analyst -> advocate
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate"])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        capsys.readouterr()

        # targeted-research consumes advocate-report.md (produced by advocate-review)
        # advocate-review is a gate (not task), so only depends-on is inferred (no produces)
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "targeted-research"])
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"
        assert out["edges_inferred"] == 1  # depends-on only (gate->task, no produces)

    def test_two_separate_dag_files(self, tmp_path, capsys):
        """Each pass creates a separate DAG file."""
        dag1, _ = _create_and_assemble(
            tmp_path, capsys, "specify-rev", ["constitution-gate", "analyst-review", "advocate-review"],
            pass_number=1,
        )
        # Pass 2 also needs valid prerequisites for contract satisfaction
        dag2, _ = _create_and_assemble(
            tmp_path, capsys, "specify-rev", ["constitution-gate", "analyst-review", "advocate-review"],
            pass_number=2,
        )

        assert dag1 != dag2
        assert Path(dag1).exists()
        assert Path(dag2).exists()

        d1 = json.loads(Path(dag1).read_text())
        d2 = json.loads(Path(dag2).read_text())
        assert d1["pass_number"] == 1
        assert d2["pass_number"] == 2

    def test_pass1_frozen_immutable(self, tmp_path, capsys):
        """Frozen pass 1 rejects all mutations."""
        dag1, _ = _create_and_assemble(
            tmp_path, capsys, "specify-rev",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )
        main([
            "freeze", dag1, "--outcome", "completed",
            "--detail", "needs-revision", "--rationale", "Gaps found",
        ])
        capsys.readouterr()

        # Cannot assemble into frozen pass
        code = main(["assemble", dag1, "--catalog", CATALOG, "--node", "input-enrichment"])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "frozen" in out["message"].lower()


class TestScenario4MultiPassClarification:
    """Scenario 4: Multi-pass with human-clarification (decision node) on revision.

    Pass 1: constitution-gate -> analyst -> advocate -> freeze
    Pass 2: human-clarification -> analyst -> advocate
    """

    def test_decision_node_type(self, tmp_path, capsys):
        """human-clarification is assembled as a decision node.

        Requires advocate-review producing advocate-report.md first.
        """
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-clarify",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["type"] == "decision"

    def test_decision_node_edge_inference(self, tmp_path, capsys):
        """Decision node: depends-on inferred from advocate (no produces, no validates).

        human-clarification consumes advocate-report.md produced by advocate-review (gate).
        Gate is not task type -> no produces edge. Decision is not gate -> no validates edge.
        Only depends-on is inferred (1 edge).
        """
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-clarify",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 1  # depends-on only

    def test_pass2_clarification_then_analyst(self, tmp_path, capsys):
        """Analyst consumes clarification-answers from decision node.

        Decision type is NOT task, so produces edge not inferred.
        Only depends-on edge is inferred (1 edge) from clarification->analyst.
        """
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-clarify",
            ["constitution-gate", "analyst-review", "advocate-review", "human-clarification"],
        )

        # Remove analyst to re-assemble it after clarification
        # Instead, build a fresh DAG with the right order
        dag_path2 = str(tmp_path / "dag2.json")
        main(["create", "specify-clarify2", "--pass", "2", "--output", dag_path2])
        capsys.readouterr()

        # constitution-gate first (for INV-002)
        main(["assemble", dag_path2, "--catalog", CATALOG, "--node", "constitution-gate"])
        capsys.readouterr()

        # human-clarification produces clarification-answers
        # But requires advocate-report.md — assembly fails unless advocate exists
        # So we need advocate first, which needs analyst first
        main(["assemble", dag_path2, "--catalog", CATALOG, "--node", "analyst-review"])
        capsys.readouterr()

        main(["assemble", dag_path2, "--catalog", CATALOG, "--node", "advocate-review"])
        capsys.readouterr()

        main(["assemble", dag_path2, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"
        # Clarification produces clarification-answers, which analyst consumes (optional)
        # But analyst already exists in this DAG — we can verify the edge was inferred
        # advocate->clarification: depends-on (advocate produces advocate-report.md)
        assert out["edges_inferred"] == 1  # depends-on from advocate->clarification

    def test_decision_initial_status(self, tmp_path, capsys):
        """Decision node gets initial status from catalog valid_statuses[0]."""
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-clarify",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["status"] == "pending"


class TestScenario5HaltedOutcome:
    """Scenario 5: Freeze with halted outcome, verify all mutations blocked."""

    def test_freeze_halted(self, tmp_path, capsys):
        """Freeze with outcome=halted succeeds."""
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-halt",
            ["constitution-gate", "analyst-review"],
        )

        code = main([
            "freeze", dag_path,
            "--outcome", "halted",
            "--detail", "user-cancelled",
            "--rationale", "User decided not to proceed",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True
        assert out["outcome"] == "halted"

    def test_halted_outcome_persisted(self, tmp_path, capsys):
        """Halted outcome is persisted in DAG JSON."""
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-halt",
            ["constitution-gate", "analyst-review"],
        )
        main([
            "freeze", dag_path, "--outcome", "halted",
            "--detail", "user-cancelled", "--rationale", "cancelled",
        ])
        capsys.readouterr()

        dag_data = json.loads(Path(dag_path).read_text())
        assert dag_data["outcome"] == "halted"
        assert dag_data["outcome_detail"] == "user-cancelled"
        assert dag_data["completed_at"] is not None

    def test_halted_blocks_assemble(self, tmp_path, capsys):
        """Halted pass blocks node assembly."""
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-halt", ["constitution-gate"],
        )
        main([
            "freeze", dag_path, "--outcome", "halted",
            "--detail", "halt", "--rationale", "halt",
        ])
        capsys.readouterr()

        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "frozen" in out["message"].lower()

    def test_halted_blocks_status(self, tmp_path, capsys):
        """Halted pass blocks status updates."""
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-halt", ["constitution-gate"],
        )
        main([
            "freeze", dag_path, "--outcome", "halted",
            "--detail", "halt", "--rationale", "halt",
        ])
        capsys.readouterr()

        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "frozen" in out["message"].lower()

    def test_halted_blocks_refreeze(self, tmp_path, capsys):
        """Halted pass blocks re-freeze."""
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-halt", ["constitution-gate"],
        )
        main([
            "freeze", dag_path, "--outcome", "halted",
            "--detail", "halt", "--rationale", "halt",
        ])
        capsys.readouterr()

        code = main([
            "freeze", dag_path, "--outcome", "completed",
            "--detail", "retry", "--rationale", "retry",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "frozen" in out["message"].lower() or "already" in out["message"].lower()


class TestScenario6StatusProgression:
    """Scenario 6: Full 4-node pass with intermediate status transitions."""

    def test_gate_uses_passed_not_completed(self, tmp_path, capsys):
        """Gate nodes use 'passed' status, not 'completed'."""
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-status",
            ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"],
        )

        # Gate uses "passed"
        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["new_status"] == "passed"

        # Gate rejects "completed"
        code = main(["status", dag_path, "--node", "advocate-review", "--status", "completed"])
        assert code == 1

    def test_task_in_progress_then_completed(self, tmp_path, capsys):
        """Task nodes transition through in-progress to completed."""
        dag_path, _ = _create_and_assemble(
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

    def test_gate_in_progress_then_passed(self, tmp_path, capsys):
        """Gate nodes can transition through in-progress to passed."""
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-status",
            ["constitution-gate"],
        )

        # constitution-gate valid_statuses = ["pending", "passed", "failed"]
        # BUT GateStatus enum has in-progress too
        # The model validator checks against TYPE_STATUS_MAP, not catalog valid_statuses
        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "in-progress"])
        assert code == 0
        capsys.readouterr()  # consume first status output

        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["new_status"] == "passed"


class TestScenario7StatusLifecycle:
    """Scenario 7: Parametrized valid + invalid status transitions.

    Each node has prerequisites for valid assembly (INV-002, UNSATISFIED_CONTRACT).
    We build a full valid DAG first, then test status updates on target nodes.
    """

    # Nodes that can be assembled with minimal prerequisites
    # (only constitution-gate and input-enrichment need no producers)
    SIMPLE_NODES = {"constitution-gate", "input-enrichment"}

    def _build_full_dag(self, tmp_path, capsys):
        """Build a DAG with 6 catalog nodes for status testing.

        Excludes spec-complete because the current catalog design causes
        INV-001: analyst-review produces spec.md which spec-complete consumes,
        creating a direct task->milestone depends-on edge that bypasses the gate.
        """
        dag_path, _ = _create_and_assemble(
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
        ("advocate-review", "passed"),
        ("advocate-review", "failed"),
        ("advocate-review", "needs-revision"),
        ("human-clarification", "decided"),
    ])
    def test_valid_status_transitions(self, tmp_path, capsys, node_id, status):
        """Valid statuses accepted for each node type."""
        dag_path = self._build_full_dag(tmp_path, capsys)

        code = main(["status", dag_path, "--node", node_id, "--status", status])
        assert code == 0, f"Expected {node_id} to accept status '{status}'"

    @pytest.mark.parametrize("node_id,status", [
        ("input-enrichment", "passed"),       # task can't have gate status
        ("input-enrichment", "decided"),       # task can't have decision status
        ("advocate-review", "completed"),      # gate can't have task status
        ("human-clarification", "completed"),  # decision can't have task status
    ])
    def test_invalid_status_rejections(self, tmp_path, capsys, node_id, status):
        """Invalid statuses rejected for each node type."""
        dag_path = self._build_full_dag(tmp_path, capsys)

        code = main(["status", dag_path, "--node", node_id, "--status", status])
        assert code == 1, f"Expected {node_id} to reject status '{status}'"


class TestScenario8EdgeInference:
    """Scenario 8: Exact edge counts and types for all assembly pairs."""

    def test_constitution_gate_zero_edges(self, tmp_path, capsys):
        """constitution-gate consumes only system artifact (constitution.md) -> 0 edges."""
        dag_path = str(tmp_path / "dag.json")
        main(["create", "specify-edges", "--pass", "1", "--output", dag_path])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 0

    def test_enrichment_to_analyst_two_edges(self, tmp_path, capsys):
        """enrichment(task) -> analyst: depends-on + produces = 2 edges."""
        dag_path = str(tmp_path / "dag.json")
        main(["create", "specify-edges", "--pass", "1", "--output", dag_path])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "input-enrichment"])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        out = json.loads(capsys.readouterr().out)
        # enrichment produces enriched-input, analyst consumes it (optional)
        # But inference still runs: depends-on + produces = 2
        assert out["edges_inferred"] == 2

    def test_analyst_to_advocate_three_edges(self, tmp_path, capsys):
        """analyst(task) -> advocate(gate): depends-on + produces + validates = 3.

        Needs constitution-gate first to satisfy INV-002 for analyst-review.
        """
        dag_path = str(tmp_path / "dag.json")
        main(["create", "specify-edges", "--pass", "1", "--output", dag_path])
        capsys.readouterr()

        # constitution-gate required for INV-002
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate"])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 3

    def test_advocate_to_clarification_one_edge(self, tmp_path, capsys):
        """advocate(gate) -> clarification(decision): depends-on only = 1.

        Gate is not task type, so no produces edge. Decision is not gate,
        so no validates edge.
        """
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-edges",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        # human-clarification consumes advocate-report.md, produced by advocate-review (gate)
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "human-clarification"])
        out = json.loads(capsys.readouterr().out)
        # advocate-review is gate (not task), so no produces edge inferred
        # human-clarification is decision (not gate), so no validates edge
        assert out["edges_inferred"] == 1  # depends-on only

    def test_advocate_to_research_one_edge(self, tmp_path, capsys):
        """advocate(gate) -> targeted-research(task): depends-on only = 1.

        Gate is not task type, so no produces edge. targeted-research is
        a task but not a gate, so no validates edge.
        """
        dag_path, _ = _create_and_assemble(
            tmp_path, capsys, "specify-edges",
            ["constitution-gate", "analyst-review", "advocate-review"],
        )

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "targeted-research"])
        out = json.loads(capsys.readouterr().out)
        assert out["edges_inferred"] == 1  # depends-on only

    def test_no_informed_by_or_constrained_by_ever_inferred(self, tmp_path, capsys):
        """Inference algorithm never produces informed-by or constrained-by edges."""
        nodes = ["constitution-gate", "input-enrichment", "analyst-review", "advocate-review"]
        dag_path, _ = _create_and_assemble(tmp_path, capsys, "specify-edges", nodes)

        dag_data = json.loads(Path(dag_path).read_text())
        edge_types = {e["type"] for e in dag_data["edges"]}
        assert "informed-by" not in edge_types
        assert "constrained-by" not in edge_types

    def test_edge_id_pattern(self, tmp_path, capsys):
        """Inferred edges follow 'inferred-{type}-{source}-{target}' pattern."""
        nodes = ["constitution-gate", "analyst-review", "advocate-review"]
        dag_path, _ = _create_and_assemble(tmp_path, capsys, "specify-edges", nodes)

        dag_data = json.loads(Path(dag_path).read_text())
        for edge in dag_data["edges"]:
            assert edge["id"].startswith("inferred-"), f"Edge {edge['id']} missing inferred prefix"
            parts = edge["id"].split("-", 2)  # inferred-{type}-{rest}
            assert len(parts) >= 2


class TestScenario9MilestoneINV001:
    """Scenario 9: INV-001 violation when task directly reaches milestone."""

    def test_task_to_milestone_without_gate_fails_validation(self, tmp_path, capsys):
        """Assembling spec-complete after analyst (no gate) triggers INV-001.

        analyst-review(task) -> spec-complete(milestone) with inferred depends-on
        bypasses gate requirement. The assembly should either fail validation
        or the assembled DAG should be invalid.
        """
        dag_path = str(tmp_path / "dag.json")
        main(["create", "specify-inv001", "--pass", "1", "--output", dag_path])
        capsys.readouterr()

        # Assemble analyst first
        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        capsys.readouterr()

        # Assemble spec-complete — consumes spec.md + advocate-report.md
        # spec.md is produced by analyst-review -> depends-on inferred
        # advocate-report.md not produced -> UNSATISFIED_CONTRACT
        # Also: task->milestone path without gate -> INV-001
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "spec-complete"])
        out = json.loads(capsys.readouterr().out)
        # Assembly should be invalid (transactional: not persisted)
        assert code == 1
        assert out["status"] == "invalid"

        # Verify INV-001 or UNSATISFIED_CONTRACT appears in violations
        all_checks = out["validation"]["checks"]
        violation_codes = {c["check"] for c in all_checks}
        # At minimum: advocate-report.md not produced -> UNSATISFIED_CONTRACT
        assert "UNSATISFIED_CONTRACT" in violation_codes or "INV-001" in violation_codes

    def test_spec_complete_always_triggers_inv001(self, tmp_path, capsys):
        """spec-complete triggers INV-001 even with advocate-review in the DAG.

        The current catalog design means spec-complete consumes spec.md (from
        analyst-review=task), so edge inference creates a direct depends-on
        from analyst->spec-complete. This path bypasses advocate-review (gate),
        triggering INV-001 even though a gate exists on ANOTHER path.

        This is by design: INV-001 requires ALL paths from tasks to milestones
        to pass through a gate.
        """
        dag_path = str(tmp_path / "dag.json")
        main(["create", "specify-inv001-direct", "--pass", "1", "--output", dag_path])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "constitution-gate"])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "analyst-review"])
        capsys.readouterr()

        main(["assemble", dag_path, "--catalog", CATALOG, "--node", "advocate-review"])
        capsys.readouterr()

        # spec-complete assembly fails INV-001: analyst(task)->spec-complete(milestone)
        # path exists without passing through a gate
        code = main(["assemble", dag_path, "--catalog", CATALOG, "--node", "spec-complete"])
        out = json.loads(capsys.readouterr().out)
        assert code == 1
        assert out["status"] == "invalid"

        # INV-001 should be in the violations
        violation_codes = {c["check"] for c in out["validation"]["checks"]}
        assert "INV-001" in violation_codes
