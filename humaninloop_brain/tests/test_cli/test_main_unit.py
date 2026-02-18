"""Unit tests for CLI — in-process to capture coverage."""

import json
from pathlib import Path

import pytest

from humaninloop_brain.cli.main import main, validation_result_to_output
from humaninloop_brain.entities.validation import ValidationResult, ValidationViolation

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


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
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

    def test_invalid(self, capsys):
        code = main([
            "validate",
            str(FIXTURES_DIR / "invalid-cycle.json"),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
        ])
        assert code == 1


class TestSortCommand:
    def test_sort(self, capsys):
        code = main(["sort", str(FIXTURES_DIR / "pass-normal.json")])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["order"] == ["input-enrichment", "analyst-review", "advocate-review"]


class TestCreateCommand:
    def test_create(self, tmp_path, capsys):
        output_path = tmp_path / "dag.json"
        code = main([
            "create", "my-workflow",
            "--pass", "1",
            "--output", str(output_path),
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "success"
        assert output_path.exists()


class TestAssembleCommand:
    def test_assemble(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        capsys.readouterr()  # Clear

        code = main([
            "assemble", str(dag_path),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
            "--node", "input-enrichment",
        ])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["node_added"]["id"] == "input-enrichment"
        assert out["node_added"]["type"] == "task"
        assert out["node_added"]["status"] == "pending"

    def test_assemble_unknown(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        capsys.readouterr()

        code = main([
            "assemble", str(dag_path),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
            "--node", "nonexistent",
        ])
        assert code == 1

    def test_assemble_rollback_on_invariant_violation(self, tmp_path, capsys):
        """Assemble must not persist the DAG when validation fails (transactional)."""
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        capsys.readouterr()

        # Add analyst-review WITHOUT constitution-gate → INV-002 violation
        code = main([
            "assemble", str(dag_path),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
            "--node", "analyst-review",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "invalid"

        # DAG on disk should NOT contain the invalid node
        from humaninloop_brain.passes.lifecycle import load_pass
        dag = load_pass(str(dag_path))
        assert len(dag.nodes) == 0, "Invalid node should not be persisted"

    def test_assemble_frozen(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        main(["freeze", str(dag_path), "--outcome", "completed", "--detail", "d", "--rationale", "r"])
        capsys.readouterr()

        code = main([
            "assemble", str(dag_path),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
            "--node", "input-enrichment",
        ])
        assert code == 1


class TestStatusCommand:
    def test_update(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        main(["assemble", str(dag_path), "--catalog", str(FIXTURES_DIR / "specify-catalog.json"), "--node", "input-enrichment"])
        capsys.readouterr()

        code = main(["status", str(dag_path), "--node", "input-enrichment", "--status", "completed"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"

    def test_unknown_node(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        capsys.readouterr()

        code = main(["status", str(dag_path), "--node", "nonexistent", "--status", "pending"])
        assert code == 1

    def test_invalid_status(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        main(["assemble", str(dag_path), "--catalog", str(FIXTURES_DIR / "specify-catalog.json"), "--node", "input-enrichment"])
        capsys.readouterr()

        code = main(["status", str(dag_path), "--node", "input-enrichment", "--status", "passed"])
        assert code == 1


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
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        main(["assemble", str(dag_path), "--catalog", str(FIXTURES_DIR / "specify-catalog.json"), "--node", "input-enrichment"])
        capsys.readouterr()
        return dag_path

    def test_record_success(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", str(dag_path),
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
            "record", str(dag_path),
            "--node", "nonexistent",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        assert code == 1

    def test_record_invalid_status(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", str(dag_path),
            "--node", "input-enrichment",
            "--status", "passed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        assert code == 1

    def test_record_invalid_evidence_json(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        code = main([
            "record", str(dag_path),
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
            "record", str(dag_path),
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", "not-json",
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "Invalid trace JSON" in out["message"]

    def test_record_frozen_pass(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        main(["freeze", str(dag_path), "--outcome", "completed", "--detail", "d", "--rationale", "r"])
        capsys.readouterr()
        code = main([
            "record", str(dag_path),
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        assert code == 1

    def test_record_persists_to_disk(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        main([
            "record", str(dag_path),
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", self.EVIDENCE,
            "--trace", self.TRACE,
        ])
        capsys.readouterr()
        # Reload and verify
        from humaninloop_brain.passes.lifecycle import load_pass
        dag = load_pass(str(dag_path))
        assert dag.nodes[0].status == "completed"
        assert len(dag.nodes[0].evidence) == 1
        assert dag.nodes[0].evidence[0].id == "E1"
        assert len(dag.execution_trace) == 1
        assert dag.execution_trace[0].verdict == "completed"

    def test_record_evidence_schema(self, tmp_path, capsys):
        dag_path = self._setup_dag(tmp_path, capsys)
        bad_evidence = json.dumps([{"id": "E1"}])  # Missing required fields
        code = main([
            "record", str(dag_path),
            "--node", "input-enrichment",
            "--status", "completed",
            "--evidence", bad_evidence,
            "--trace", self.TRACE,
        ])
        assert code == 1
        out = json.loads(capsys.readouterr().out)
        assert "Invalid evidence schema" in out["message"]


class TestFreezeCommand:
    def test_freeze(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        capsys.readouterr()

        code = main(["freeze", str(dag_path), "--outcome", "completed", "--detail", "d", "--rationale", "r"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True
        assert out["dag_path"] == str(dag_path)
        assert out["nodes_executed"] == 0
        assert out["edges_total"] == 0

    def test_invalid_outcome(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        capsys.readouterr()

        code = main(["freeze", str(dag_path), "--outcome", "invalid", "--detail", "d", "--rationale", "r"])
        assert code == 1

    def test_double_freeze(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        main(["freeze", str(dag_path), "--outcome", "completed", "--detail", "d", "--rationale", "r"])
        capsys.readouterr()

        code = main(["freeze", str(dag_path), "--outcome", "halted", "--detail", "d", "--rationale", "r"])
        assert code == 1


class TestCatalogValidateCommand:
    def test_valid(self, capsys):
        code = main(["catalog-validate", str(FIXTURES_DIR / "specify-catalog.json")])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["status"] == "valid"

    def test_invalid(self, tmp_path, capsys):
        bad = tmp_path / "bad.json"
        bad.write_text('{"not": "a catalog"}')
        code = main(["catalog-validate", str(bad)])
        assert code == 1
