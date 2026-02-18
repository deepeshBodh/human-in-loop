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
        assert out["node_added"] == "input-enrichment"

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


class TestFreezeCommand:
    def test_freeze(self, tmp_path, capsys):
        dag_path = tmp_path / "dag.json"
        main(["create", "w", "--pass", "1", "--output", str(dag_path)])
        capsys.readouterr()

        code = main(["freeze", str(dag_path), "--outcome", "completed", "--detail", "d", "--rationale", "r"])
        assert code == 0
        out = json.loads(capsys.readouterr().out)
        assert out["pass_frozen"] is True

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
