"""CLI integration tests — subprocess-based, verify JSON output and exit codes.

Tests the actual hil-dag binary via subprocess to verify end-to-end behavior
including argument parsing, JSON output format, and exit codes.
"""

import json
import subprocess
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
CATALOG = str(FIXTURES_DIR / "specify-catalog.json")


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


def _bootstrap(tmp_path, workflow="test-wf", nodes=None):
    """Bootstrap a v3 StrategyGraph via CLI and return dag_path."""
    nodes = nodes or ["constitution-gate"]
    dag_path = str(tmp_path / "strategy.json")
    for i, node_id in enumerate(nodes):
        args = ["assemble", dag_path, "--catalog", CATALOG, "--node", node_id]
        if i == 0:
            args.extend(["--workflow", workflow])
        code, _ = run_cli(*args)
        assert code == 0, f"Bootstrap failed at {node_id}"
    return dag_path


class TestValidateCommand:
    def test_valid_dag(self):
        code, out = run_cli(
            "validate",
            str(FIXTURES_DIR / "pass-normal.json"),
            "--catalog", CATALOG,
        )
        assert code == 0
        assert out["status"] == "valid"
        assert "checks" in out
        assert "summary" in out

    def test_invalid_cycle(self):
        code, out = run_cli(
            "validate",
            str(FIXTURES_DIR / "invalid-cycle.json"),
            "--catalog", CATALOG,
        )
        assert code == 1
        assert out["status"] == "invalid"
        assert out["summary"]["failed"] > 0


class TestSortCommand:
    def test_sort(self):
        code, out = run_cli(
            "sort", str(FIXTURES_DIR / "pass-normal.json"),
        )
        assert code == 0
        assert out["order"] == [
            "input-enrichment",
            "analyst-review",
            "advocate-review",
        ]


class TestAssembleCommand:
    def test_bootstrap_and_assemble(self, tmp_path):
        """First assemble bootstraps a v3 StrategyGraph."""
        dag_path = str(tmp_path / "strategy.json")
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "constitution-gate",
            "--workflow", "test-wf",
        )
        assert code == 0
        assert out["node_added"]["id"] == "constitution-gate"

        data = json.loads(Path(dag_path).read_text())
        assert data["schema_version"] == "3.0.0"

    def test_assemble_to_existing(self, tmp_path):
        dag_path = _bootstrap(tmp_path)
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "input-enrichment",
        )
        assert code == 0
        assert out["node_added"]["id"] == "input-enrichment"

    def test_assemble_unknown_node(self, tmp_path):
        dag_path = _bootstrap(tmp_path)
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "nonexistent",
        )
        assert code == 1
        assert out["status"] == "error"


class TestStatusCommand:
    def test_update_status(self, tmp_path):
        dag_path = _bootstrap(tmp_path, nodes=["constitution-gate", "input-enrichment"])
        code, out = run_cli(
            "status", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"

    def test_invalid_status(self, tmp_path):
        dag_path = _bootstrap(tmp_path, nodes=["constitution-gate", "input-enrichment"])
        code, out = run_cli(
            "status", dag_path,
            "--node", "input-enrichment",
            "--status", "passed",
        )
        assert code == 1
        assert out["status"] == "error"


class TestFreezeCommand:
    def test_freeze(self, tmp_path):
        dag_path = _bootstrap(tmp_path)
        code, out = run_cli(
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "advocate-verdict-ready",
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["pass_frozen"] is True

    def test_double_freeze(self, tmp_path):
        dag_path = _bootstrap(tmp_path)
        run_cli("freeze", dag_path, "--outcome", "completed", "--detail", "d")

        code, out = run_cli(
            "freeze", dag_path,
            "--outcome", "halted", "--detail", "d2",
        )
        assert code == 1
        assert out["status"] == "error"


class TestRecordCommand:
    def test_record_gate_verdict(self, tmp_path):
        """Subprocess test: record verdict on gate node via --verdict."""
        dag_path = _bootstrap(
            tmp_path, nodes=["constitution-gate", "analyst-review", "advocate-review"],
        )
        evidence = json.dumps([{
            "id": "EV-advocate-review-001",
            "type": "advocate-report",
            "description": "Found gaps",
            "reference": "specs/001/.workflow/advocate-report.md",
        }])
        trace = json.dumps({
            "node_id": "advocate-review",
            "started_at": "2026-01-15T10:00:00Z",
            "completed_at": "2026-01-15T10:10:00Z",
            "verdict": "needs-revision",
            "agent_report_summary": "Gaps found",
        })
        code, out = run_cli(
            "record", dag_path,
            "--node", "advocate-review",
            "--status", "completed",
            "--verdict", "needs-revision",
            "--evidence", evidence,
            "--trace", trace,
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["verdict_recorded"] == "needs-revision"

        data = json.loads(Path(dag_path).read_text())
        node = next(n for n in data["nodes"] if n["id"] == "advocate-review")
        assert node["verdict"] == "needs-revision"


class TestAssembleCapabilityTags:
    def test_assemble_via_capability_tags(self, tmp_path):
        """Subprocess integration test: resolve node by capability tags."""
        dag_path = str(tmp_path / "strategy.json")
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "input-enrichment",
            "--workflow", "test-wf",
        )
        assert code == 0
        assert out["status"] == "valid"
        assert out["node_added"]["id"] == "input-enrichment"

    def test_assemble_capability_tags_no_match(self, tmp_path):
        """Subprocess integration test: no matching capability tags."""
        dag_path = _bootstrap(tmp_path)
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "nonexistent",
        )
        assert code == 1
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "no_match"

    def test_assemble_capability_tags_ambiguous(self, tmp_path):
        """Subprocess integration test: ambiguous capability tags."""
        dag_path = _bootstrap(tmp_path)
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "gap-detection", "research",
        )
        assert code == 1
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "ambiguous"


class TestCatalogValidateCommand:
    def test_valid_catalog(self):
        code, out = run_cli("catalog-validate", CATALOG)
        assert code == 0
        assert out["status"] == "valid"
        assert out["summary"]["failed"] == 0

    def test_invalid_catalog(self, tmp_path):
        bad = tmp_path / "bad-catalog.json"
        bad.write_text('{"not": "a catalog"}')
        code, out = run_cli("catalog-validate", str(bad))
        assert code == 1
        assert out["status"] == "invalid"
