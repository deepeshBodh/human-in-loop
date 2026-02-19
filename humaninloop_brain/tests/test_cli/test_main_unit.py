"""Unit tests for CLI — in-process to capture coverage.

Tests cover StrategyGraph v3 schema operations through the CLI.
"""

import json
from pathlib import Path

import pytest

from humaninloop_brain.cli.main import main, validation_result_to_output
from humaninloop_brain.entities.validation import ValidationResult, ValidationViolation

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
CATALOG = str(FIXTURES_DIR / "specify-catalog.json")


def _bootstrap_graph(tmp_path, capsys, workflow="test-wf", nodes=None):
    """Bootstrap a v3 StrategyGraph and assemble nodes.

    Default: constitution-gate only.
    """
    nodes = nodes or ["constitution-gate"]
    dag_path = str(tmp_path / "strategy.json")
    for i, node_id in enumerate(nodes):
        args = ["assemble", dag_path, "--catalog", CATALOG, "--node", node_id]
        if i == 0:
            args.extend(["--workflow", workflow])
        code = main(args)
        assert code == 0, f"Bootstrap failed at {node_id}"
    capsys.readouterr()
    return dag_path


class TestValidationResultToOutput:
    def test_valid(self):
        result = ValidationResult(valid=True, phase="test")
        out = validation_result_to_output(result)
        assert out["status"] == "valid"
        assert out["summary"]["total"] == 1
        assert out["summary"]["passed"] == 1
        assert out["summary"]["failed"] == 0

    def test_with_errors(self):
        result = ValidationResult(
            valid=False,
            phase="test",
            violations=[
                ValidationViolation(code="A", severity="error", message="err"),
                ValidationViolation(code="B", severity="warning", message="warn"),
            ],
        )
        out = validation_result_to_output(result)
        assert out["status"] == "invalid"
        assert out["summary"]["failed"] == 1
        assert out["summary"]["warnings"] == 1


class TestValidateCommand:
    def test_valid(self, capsys):
        code = main([
            "validate",
            str(FIXTURES_DIR / "pass-normal.json"),
            "--catalog", CATALOG,
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

    def test_invalid(self, capsys):
        code = main([
            "validate",
            str(FIXTURES_DIR / "invalid-cycle.json"),
            "--catalog", CATALOG,
        ])
        assert code == 1


class TestSortCommand:
    def test_sort(self, capsys):
        code = main(["sort", str(FIXTURES_DIR / "pass-normal.json")])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["order"] == ["input-enrichment", "analyst-review", "advocate-review"]


class TestAssembleCommand:
    def test_bootstrap_and_assemble(self, tmp_path, capsys):
        """First assemble creates StrategyGraph (bootstrap)."""
        dag_path = str(tmp_path / "strategy.json")
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "constitution-gate",
            "--workflow", "test-wf",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"
        assert out["node_added"]["id"] == "constitution-gate"
        assert out["node_added"]["type"] == "gate"
        assert Path(dag_path).exists()

        # Verify it's a v3 StrategyGraph
        data = json.loads(Path(dag_path).read_text())
        assert data["schema_version"] == "3.0.0"

    def test_assemble_to_existing(self, tmp_path, capsys):
        """Second assemble adds to existing graph."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "input-enrichment",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "input-enrichment"
        assert out["node_added"]["type"] == "task"

    def test_bootstrap_requires_workflow(self, tmp_path, capsys):
        """Bootstrap without --workflow fails."""
        dag_path = str(tmp_path / "strategy.json")
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "constitution-gate",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "workflow" in out["message"].lower()

    def test_assemble_unknown_node(self, tmp_path, capsys):
        """Unknown node ID returns error."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "nonexistent",
        ])
        assert code == 1

    def test_assemble_auto_resolves_inv002(self, tmp_path, capsys):
        """INV-002 auto-resolved via carry_forward constitution-gate."""
        dag_path = str(tmp_path / "strategy.json")
        # Assemble analyst-review without constitution-gate → auto-resolution
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "analyst-review",
            "--workflow", "test-wf",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"
        # File should exist (auto-resolution succeeded)
        assert Path(dag_path).exists()

    def test_assemble_completed_graph_rejected(self, tmp_path, capsys):
        """Cannot assemble to a completed graph."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        main(["freeze", dag_path, "--outcome", "completed", "--detail", "done"])
        capsys.readouterr()

        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "input-enrichment",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "completed" in out["message"].lower()

    def test_assemble_auto_resolution(self, tmp_path, capsys):
        """INV-002 auto-resolved when carry_forward is set."""
        # Create a catalog with carry_forward on constitution-gate
        catalog_data = json.loads(Path(CATALOG).read_text())
        for node in catalog_data["nodes"]:
            if node["node_id"] == "constitution-gate":
                node["carry_forward"] = True
        custom_catalog = str(tmp_path / "catalog.json")
        Path(custom_catalog).write_text(json.dumps(catalog_data))

        dag_path = str(tmp_path / "strategy.json")
        code = main([
            "assemble", dag_path,
            "--catalog", custom_catalog,
            "--node", "analyst-review",
            "--workflow", "test-wf",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

    def test_carry_forward_gate_persists_across_passes(self, tmp_path, capsys):
        """carry_forward gate from pass 1 satisfies INV-002 in pass 2 (node persists in DAG)."""
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        # Complete all and freeze pass 1
        main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        main(["status", dag_path, "--node", "advocate-review", "--status", "completed"])
        capsys.readouterr()
        main([
            "freeze", dag_path, "--outcome", "completed", "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review",
            "--trigger-source", "advocate-review",
            "--reason", "test",
        ])
        capsys.readouterr()

        # Pass 2: assemble analyst-review — INV-002 satisfied because
        # constitution-gate node persists in the single DAG from pass 1
        code = main([
            "assemble", dag_path, "--catalog", CATALOG,
            "--node", "analyst-review",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

        # constitution-gate should have been auto-added
        graph_data = json.loads(Path(dag_path).read_text())
        node_ids = {n["id"] for n in graph_data["nodes"]}
        assert "constitution-gate" in node_ids
        assert "analyst-review" in node_ids


class TestStatusCommand:
    def test_update(self, tmp_path, capsys):
        dag_path = _bootstrap_graph(
            tmp_path, capsys, nodes=["constitution-gate", "input-enrichment"],
        )
        code = main(["status", dag_path, "--node", "input-enrichment", "--status", "completed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"

    def test_unknown_node(self, tmp_path, capsys):
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main(["status", dag_path, "--node", "nonexistent", "--status", "pending"])
        assert code == 1

    def test_invalid_status(self, tmp_path, capsys):
        dag_path = _bootstrap_graph(
            tmp_path, capsys, nodes=["constitution-gate", "input-enrichment"],
        )
        # "passed" is not valid for task nodes in v3
        code = main(["status", dag_path, "--node", "input-enrichment", "--status", "passed"])
        assert code == 1

    def test_gate_accepts_passed(self, tmp_path, capsys):
        """Deterministic gates accept 'passed' status."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["new_status"] == "passed"

    def test_gate_rejects_decided(self, tmp_path, capsys):
        """Gates reject 'decided' status (only valid for decision nodes)."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "decided"])
        assert code == 1

    def test_gate_verdict(self, tmp_path, capsys):
        """Status command supports --verdict for deterministic gates."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main([
            "status", dag_path,
            "--node", "constitution-gate",
            "--status", "passed",
            "--verdict", "ready",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["new_status"] == "passed"
        assert out["verdict_recorded"] == "ready"

        # Verify verdict persisted in graph
        graph_data = json.loads(Path(dag_path).read_text())
        gate = next(n for n in graph_data["nodes"] if n["id"] == "constitution-gate")
        assert gate["verdict"] == "ready"
        latest_entry = gate["history"][-1]
        assert latest_entry["verdict"] == "ready"

    def test_status_without_verdict_omits_field(self, tmp_path, capsys):
        """Status command without --verdict omits verdict_recorded from output."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert "verdict_recorded" not in out


class TestRecordCommand:
    EVIDENCE = json.dumps([{
        "id": "E1",
        "type": "report-summary",
        "description": "Analyst completed review",
        "reference": "specs/001/.workflow/analyst-report.md",
    }])
    TRACE = json.dumps({
        "node_id": "input-enrichment",
        "started_at": "2026-01-15T10:00:00Z",
        "completed_at": "2026-01-15T10:05:00Z",
        "verdict": "completed",
        "agent_report_summary": "Task finished",
    })

    def _setup_dag(self, tmp_path, capsys):
        return _bootstrap_graph(
            tmp_path, capsys, nodes=["constitution-gate", "input-enrichment"],
        )

    def test_record_success(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "success"
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"
        assert out["evidence_added"] == 1
        assert out["trace_recorded"] is True

    def test_record_unknown_node(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", dag_path,
            "--node", "nonexistent",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        assert code == 1

    def test_record_invalid_status(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "passed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        assert code == 1

    def test_record_invalid_evidence_json(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", "not-json",
            "--trace", self.TRACE,
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "Invalid evidence JSON" in out["message"]

    def test_record_invalid_trace_json(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", "not-json",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "Invalid trace JSON" in out["message"]

    def test_record_frozen_entry(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        main(["freeze", dag_path, "--outcome", "completed", "--detail", "done"])
        capsys.readouterr()

        code = main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        assert code == 1

    def test_record_persists_to_disk(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        capsys.readouterr()

        # Reload and verify
        data = json.loads(Path(dag_path).read_text())
        node = next(n for n in data["nodes"] if n["id"] == "input-enrichment")
        assert node["status"] == "completed"
        # Check history entry
        entry = next(e for e in node["history"] if e["pass"] == 1)
        assert entry["status"] == "completed"
        assert entry["trace"] is not None
        assert len(entry["evidence"]) == 1
        assert entry["evidence"][0]["id"] == "EV-input-enrichment-001-1"

    def test_record_evidence_schema(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        bad_evidence = json.dumps([{"id": "E1"}])  # Missing required fields
        code = main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", bad_evidence,
            "--trace", self.TRACE,
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "Invalid evidence schema" in out["message"]

    def test_record_gate_with_verdict(self, tmp_path, capsys):
        """Record a gate node with --verdict persists verdict in history and top-level."""
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        gate_evidence = json.dumps([{
            "id": "EV-advocate-review-001",
            "type": "advocate-report",
            "description": "Found 3 gaps",
            "reference": "specs/001/.workflow/advocate-report.md",
        }])
        gate_trace = json.dumps({
            "node_id": "advocate-review",
            "started_at": "2026-01-15T10:00:00Z",
            "completed_at": "2026-01-15T10:10:00Z",
            "verdict": "needs-revision",
            "agent_report_summary": "3 gaps found",
        })
        code = main([
            "record", dag_path,
            "--node", "advocate-review",
            "--status", "completed",
            "--verdict", "needs-revision",
            "--evidence", gate_evidence,
            "--trace", gate_trace,
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "success"
        assert out["verdict_recorded"] == "needs-revision"

        # Verify verdict persists in DAG file
        data = json.loads(Path(dag_path).read_text())
        node = next(n for n in data["nodes"] if n["id"] == "advocate-review")
        assert node["verdict"] == "needs-revision"
        entry = next(e for e in node["history"] if e["pass"] == 1)
        assert entry["verdict"] == "needs-revision"

    def test_record_without_verdict_omits_field(self, tmp_path, capsys):
        """Record without --verdict does not include verdict_recorded in output."""
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert "verdict_recorded" not in out

    def test_record_auto_generates_evidence_ids(self, tmp_path, capsys):
        """Evidence IDs are auto-generated as EV-{node}-{pass}-{seq}."""
        dag_path = self._setup_dag(tmp_path, capsys)
        evidence = json.dumps([
            {"id": "ignored", "type": "report", "description": "First", "reference": "a.md"},
            {"id": "also-ignored", "type": "report", "description": "Second", "reference": "b.md"},
        ])
        code = main([
            "record", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", evidence,
            "--trace", self.TRACE,
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["evidence_ids"] == ["EV-input-enrichment-001-1", "EV-input-enrichment-001-2"]

        # Verify on disk
        data = json.loads(Path(dag_path).read_text())
        node = next(n for n in data["nodes"] if n["id"] == "input-enrichment")
        entry = next(e for e in node["history"] if e["pass"] == 1)
        assert entry["evidence"][0]["id"] == "EV-input-enrichment-001-1"
        assert entry["evidence"][1]["id"] == "EV-input-enrichment-001-2"


class TestFreezeCommand:
    def test_freeze(self, tmp_path, capsys):
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main(["freeze", dag_path, "--outcome", "completed", "--detail", "done"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True
        assert out["dag_path"] == dag_path
        assert out["nodes_total"] == 1
        assert out["edges_total"] == 0

    def test_freeze_with_triggered_nodes(self, tmp_path, capsys):
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        code = main([
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review", "advocate-review",
            "--trigger-source", "advocate-review",
            "--reason", "Gaps found",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True

        # Verify triggered_by edges and next pass
        data = json.loads(Path(dag_path).read_text())
        assert data["current_pass"] == 2
        triggered_edges = [e for e in data["edges"] if e["type"] == "triggered_by"]
        assert len(triggered_edges) == 2
        # Verify edges go from gate to triggered nodes, not self-loops
        for edge in triggered_edges:
            assert edge["source"] == "advocate-review"
            assert edge["target"] in ("analyst-review", "advocate-review")

    def test_invalid_outcome(self, tmp_path, capsys):
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main(["freeze", dag_path, "--outcome", "invalid", "--detail", "d"])
        assert code == 1

    def test_double_freeze(self, tmp_path, capsys):
        dag_path = _bootstrap_graph(tmp_path, capsys)
        main(["freeze", dag_path, "--outcome", "completed", "--detail", "done"])
        capsys.readouterr()

        code = main(["freeze", dag_path, "--outcome", "halted", "--detail", "retry"])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "frozen" in out["message"].lower()


class TestAssembleCapabilityTags:
    def test_assemble_capability_tags_unique(self, tmp_path, capsys):
        """Capability tags that resolve to exactly one node succeed."""
        dag_path = str(tmp_path / "strategy.json")
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "input-enrichment",
            "--workflow", "test-wf",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"
        assert out["node_added"]["id"] == "input-enrichment"

    def test_assemble_capability_tags_ambiguous(self, tmp_path, capsys):
        """Capability tags matching multiple nodes return ambiguous error."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "gap-detection", "research",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "ambiguous"
        assert len(out["candidates"]) == 2
        candidate_ids = {c["node_id"] for c in out["candidates"]}
        assert candidate_ids == {"advocate-review", "targeted-research"}

    def test_assemble_capability_tags_no_match(self, tmp_path, capsys):
        """Capability tags matching nothing return no_match error."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "nonexistent-capability",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "no_match"
        assert "tags" in out
        assert "available_nodes" in out

    def test_assemble_node_and_tags_mutual_exclusion(self, capsys):
        """Cannot use both --node and --capability-tags."""
        with pytest.raises(SystemExit) as exc_info:
            main([
                "assemble", "/tmp/dummy.json",
                "--catalog", CATALOG,
                "--node", "input-enrichment",
                "--capability-tags", "input-enrichment",
            ])
        assert exc_info.value.code == 2

    def test_assemble_capability_tags_with_node_type_filter(self, tmp_path, capsys):
        """Node type filter narrows ambiguous resolution to unique match."""
        # targeted-research requires advocate-report.md, produced by advocate-review
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        # "gap-detection" + "research" matches advocate-review (gate) and
        # targeted-research (task). Filter to task only.
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "gap-detection", "research",
            "--node-type", "task",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"
        assert out["node_added"]["id"] == "targeted-research"


class TestAssembleSemanticFallback:
    """Tests for tier-2 semantic description fallback in capability resolution."""

    def test_no_match_with_intent_resolves_by_description(self, tmp_path, capsys):
        """When tags fail but intent matches one node, resolution succeeds."""
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "nonexistent-tag",
            "--intent", "Investigate specific knowledge gaps identified by validation",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"
        assert out["node_added"]["id"] == "targeted-research"

    def test_no_match_without_intent_still_fails(self, tmp_path, capsys):
        """When tags fail and no intent provided, returns no_match error."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "nonexistent-tag",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "no_match"
        assert "resolution" not in out  # no semantic fallback attempted

    def test_ambiguous_with_intent_disambiguates(self, tmp_path, capsys):
        """When tags match multiple nodes but intent disambiguates, resolution succeeds."""
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        # "gap-detection" + "research" matches advocate-review and targeted-research
        # Intent about "knowledge gaps through research" should favor targeted-research
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "gap-detection", "research",
            "--intent", "Investigate knowledge gaps through research",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"
        assert out["node_added"]["id"] == "targeted-research"

    def test_ambiguous_without_intent_still_fails(self, tmp_path, capsys):
        """When tags match multiple nodes and no intent, returns ambiguous error."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "gap-detection", "research",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "ambiguous"

    def test_no_match_intent_also_fails(self, tmp_path, capsys):
        """When tags fail and intent also fails, returns no_match with semantic note."""
        dag_path = _bootstrap_graph(tmp_path, capsys)
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "zzz-nonexistent",
            "--intent", "qqq xxx yyy zzz",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "no_match"
        assert out["resolution"] == "semantic_fallback_failed"


class TestCatalogValidateCommand:
    def test_valid(self, capsys):
        code = main(["catalog-validate", CATALOG])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

    def test_invalid(self, tmp_path, capsys):
        bad = tmp_path / "bad.json"
        bad.write_text('{"not": "a catalog"}')
        code = main(["catalog-validate", str(bad)])
        assert code == 1


class TestMilestonePrerequisiteVerification:
    """Milestone nodes reject 'achieved' when prerequisite nodes are incomplete.

    Covers main.py:292-310 — the milestone prerequisite verification block
    in cmd_status that checks depends_on/validates edges before allowing
    a milestone to be marked 'achieved'.
    """

    def _build_dag_with_milestone(self, tmp_path, capsys):
        """Build a DAG with constitution-gate, analyst, advocate, spec-complete."""
        return _bootstrap_graph(
            tmp_path, capsys,
            nodes=[
                "constitution-gate", "analyst-review",
                "advocate-review", "spec-complete",
            ],
        )

    def test_milestone_rejected_with_incomplete_prerequisites(self, tmp_path, capsys):
        """spec-complete depends on advocate-review; rejecting when advocate is pending."""
        dag_path = self._build_dag_with_milestone(tmp_path, capsys)

        # Try to achieve milestone without completing prerequisites
        code = main([
            "status", dag_path,
            "--node", "spec-complete",
            "--status", "achieved",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "invalid"
        assert out["reason"] == "prerequisite nodes incomplete"
        assert len(out["incomplete"]) > 0

    def test_milestone_succeeds_with_complete_prerequisites(self, tmp_path, capsys):
        """spec-complete succeeds when all prerequisite nodes have terminal status."""
        dag_path = self._build_dag_with_milestone(tmp_path, capsys)

        # Complete all prerequisites
        main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        main([
            "status", dag_path,
            "--node", "advocate-review",
            "--status", "completed",
            "--verdict", "ready",
        ])
        capsys.readouterr()

        # Now achieve milestone
        code = main([
            "status", dag_path,
            "--node", "spec-complete",
            "--status", "achieved",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["new_status"] == "achieved"

    def test_milestone_rejects_when_prereq_not_terminal(self, tmp_path, capsys):
        """Milestone fails when its depends_on prerequisite is still in-progress."""
        dag_path = self._build_dag_with_milestone(tmp_path, capsys)

        # Set advocate-review to in-progress (not terminal)
        main([
            "status", dag_path,
            "--node", "advocate-review",
            "--status", "in-progress",
        ])
        capsys.readouterr()

        # spec-complete depends_on advocate-review, which is in-progress → rejected
        code = main([
            "status", dag_path,
            "--node", "spec-complete",
            "--status", "achieved",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "invalid"
        assert "incomplete" in out

    def test_milestone_persists_achieved_in_graph(self, tmp_path, capsys):
        """Verify achieved status persists in the DAG file."""
        dag_path = self._build_dag_with_milestone(tmp_path, capsys)

        # Complete all prerequisites
        main(["status", dag_path, "--node", "constitution-gate", "--status", "passed"])
        main(["status", dag_path, "--node", "analyst-review", "--status", "completed"])
        main([
            "status", dag_path,
            "--node", "advocate-review",
            "--status", "completed",
            "--verdict", "ready",
        ])
        capsys.readouterr()

        main(["status", dag_path, "--node", "spec-complete", "--status", "achieved"])
        capsys.readouterr()

        data = json.loads(Path(dag_path).read_text())
        milestone = next(n for n in data["nodes"] if n["id"] == "spec-complete")
        assert milestone["status"] == "achieved"
        assert milestone["history"][0]["status"] == "achieved"


class TestSemanticFallbackAmbiguousFailure:
    """When ambiguous tags + intent also fails to disambiguate.

    Covers main.py:155-164 — the branch where multiple capability
    matches exist AND resolve_by_description with those candidates
    returns != 1 match (semantic_fallback_failed).
    """

    def test_ambiguous_tags_intent_fails_to_disambiguate(self, tmp_path, capsys):
        """Two capability matches + equally-matching intent → semantic_fallback_failed."""
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        # "gap-detection" + "research" matches advocate-review AND targeted-research.
        # "gap validation" has equal word overlap with both candidates:
        #   advocate-review tokens: {gap, validation, ...}  → overlap 2
        #   targeted-research tokens: {gap, validation, ...} → overlap 2
        # Equal scores → 2 results → ambiguous, semantic_fallback_failed.
        code = main([
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "gap-detection", "research",
            "--intent", "gap validation",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "ambiguous"
        assert out["resolution"] == "semantic_fallback_failed"
        assert len(out["candidates"]) == 2
        # Candidates include full details for debugging
        for candidate in out["candidates"]:
            assert "node_id" in candidate
            assert "capabilities" in candidate
            assert "description" in candidate


class TestFreezeValidationEdgeCases:
    """Freeze edge cases that flow through lifecycle exceptions.

    Covers main.py:440-441 (exception handler) and lifecycle.py:290,296,305
    (trigger_source validation, triggered_nodes validation).
    """

    def test_freeze_nonexistent_trigger_source(self, tmp_path, capsys):
        """trigger_source that doesn't exist in graph raises ValueError."""
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review"],
        )
        code = main([
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review",
            "--trigger-source", "nonexistent-gate",
            "--reason", "test",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "error"
        assert "nonexistent-gate" in out["message"]

    def test_freeze_non_gate_trigger_source(self, tmp_path, capsys):
        """trigger_source pointing to a task node (not gate) raises ValueError."""
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review"],
        )
        code = main([
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "analyst-review",
            "--trigger-source", "analyst-review",  # task, not gate
            "--reason", "test",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "error"
        assert "must be a gate node" in out["message"]

    def test_freeze_nonexistent_triggered_nodes(self, tmp_path, capsys):
        """triggered_nodes referencing nonexistent nodes raises ValueError."""
        dag_path = _bootstrap_graph(
            tmp_path, capsys,
            nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        code = main([
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "needs-revision",
            "--triggered-nodes", "nonexistent-node",
            "--trigger-source", "advocate-review",
            "--reason", "test",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "error"
        assert "nonexistent" in out["message"]
