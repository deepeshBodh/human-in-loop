"""CLI integration tests — subprocess-based, verify JSON output and exit codes."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def run_cli(*args: str, cwd: str | None = None) -> tuple[int, dict]:
    """Run hil-dag CLI and return (exit_code, parsed_json_output)."""
    result = subprocess.run(
        ["uv", "run", "hil-dag", *args],
        capture_output=True,
        text=True,
        cwd=cwd or str(Path(__file__).parent.parent.parent),
    )
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = {"raw_stdout": result.stdout, "raw_stderr": result.stderr}
    return result.returncode, output


class TestValidateCommand:
    def test_valid_dag(self):
        code, out = run_cli(
            "validate",
            str(FIXTURES_DIR / "pass-normal.json"),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
        )
        assert code == 0
        assert out["status"] == "valid"
        assert "checks" in out
        assert "summary" in out

    def test_invalid_cycle(self):
        code, out = run_cli(
            "validate",
            str(FIXTURES_DIR / "invalid-cycle.json"),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
        )
        assert code == 1
        assert out["status"] == "invalid"
        assert out["summary"]["failed"] > 0


class TestSortCommand:
    def test_sort(self):
        code, out = run_cli(
            "sort", str(FIXTURES_DIR / "pass-normal.json")
        )
        assert code == 0
        assert out["order"] == [
            "input-enrichment",
            "analyst-review",
            "advocate-review",
        ]


class TestCreateCommand:
    def test_create(self, tmp_path):
        output_path = tmp_path / "new-dag.json"
        code, out = run_cli(
            "create", "specify-feature-auth",
            "--pass", "1",
            "--output", str(output_path),
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["pass_number"] == 1
        assert output_path.exists()

        # Verify the created file
        data = json.loads(output_path.read_text())
        assert data["workflow_id"] == "specify-feature-auth"
        assert data["pass_number"] == 1


class TestAssembleCommand:
    def test_assemble_node(self, tmp_path):
        # Create a new DAG
        dag_path = tmp_path / "dag.json"
        run_cli(
            "create", "test-workflow",
            "--pass", "1",
            "--output", str(dag_path),
        )

        # Assemble a node
        code, out = run_cli(
            "assemble", str(dag_path),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
            "--node", "input-enrichment",
        )
        assert code == 0
        assert out["node_added"] == "input-enrichment"

    def test_assemble_unknown_node(self, tmp_path):
        dag_path = tmp_path / "dag.json"
        run_cli("create", "test", "--pass", "1", "--output", str(dag_path))

        code, out = run_cli(
            "assemble", str(dag_path),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
            "--node", "nonexistent",
        )
        assert code == 1
        assert out["status"] == "error"


class TestStatusCommand:
    def test_update_status(self, tmp_path):
        dag_path = tmp_path / "dag.json"
        run_cli("create", "test", "--pass", "1", "--output", str(dag_path))
        run_cli(
            "assemble", str(dag_path),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
            "--node", "input-enrichment",
        )

        code, out = run_cli(
            "status", str(dag_path),
            "--node", "input-enrichment",
            "--status", "completed",
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"

    def test_invalid_status(self, tmp_path):
        dag_path = tmp_path / "dag.json"
        run_cli("create", "test", "--pass", "1", "--output", str(dag_path))
        run_cli(
            "assemble", str(dag_path),
            "--catalog", str(FIXTURES_DIR / "specify-catalog.json"),
            "--node", "input-enrichment",
        )

        code, out = run_cli(
            "status", str(dag_path),
            "--node", "input-enrichment",
            "--status", "passed",
        )
        assert code == 1
        assert out["status"] == "error"


class TestFreezeCommand:
    def test_freeze(self, tmp_path):
        dag_path = tmp_path / "dag.json"
        run_cli("create", "test", "--pass", "1", "--output", str(dag_path))

        code, out = run_cli(
            "freeze", str(dag_path),
            "--outcome", "completed",
            "--detail", "advocate-verdict-ready",
            "--rationale", "All checks passed",
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["pass_frozen"] is True

    def test_double_freeze(self, tmp_path):
        dag_path = tmp_path / "dag.json"
        run_cli("create", "test", "--pass", "1", "--output", str(dag_path))
        run_cli(
            "freeze", str(dag_path),
            "--outcome", "completed", "--detail", "d", "--rationale", "r",
        )

        code, out = run_cli(
            "freeze", str(dag_path),
            "--outcome", "halted", "--detail", "d2", "--rationale", "r2",
        )
        assert code == 1
        assert out["status"] == "error"


class TestCatalogValidateCommand:
    def test_valid_catalog(self):
        code, out = run_cli(
            "catalog-validate",
            str(FIXTURES_DIR / "specify-catalog.json"),
        )
        assert code == 0
        assert out["status"] == "valid"
        assert out["summary"]["failed"] == 0

    def test_invalid_catalog(self, tmp_path):
        # Write invalid catalog
        bad = tmp_path / "bad-catalog.json"
        bad.write_text('{"not": "a catalog"}')
        code, out = run_cli("catalog-validate", str(bad))
        assert code == 1
        assert out["status"] == "invalid"
