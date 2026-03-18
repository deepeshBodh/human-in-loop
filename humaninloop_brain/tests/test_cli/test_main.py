"""CLI integration tests — in-process, verify JSON output and exit codes.

Originally subprocess-based tests calling `uv run hil-dag`. Converted to
in-process calls via main(argv) since the hil-dag entry point is now an
MCP server. The logic coverage is identical since both paths go through op_*().
"""

import json
from pathlib import Path

import pytest

from humaninloop_brain.cli.main import main

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
CATALOG = str(FIXTURES_DIR / "specify-catalog.json")


def run_cli(*args: str, capsys=None) -> tuple[int, dict]:
    """Run hil-dag CLI in-process and return (exit_code, parsed_json_output)."""
    code = main(list(args))
    captured = capsys.readouterr()
    try:
        output = json.loads(captured.out)
    except json.JSONDecodeError:
        output = {"raw_stdout": captured.out, "raw_stderr": captured.err}
    return code, output


def _bootstrap(tmp_path, capsys, workflow="test-wf", nodes=None):
    """Bootstrap a v3 StrategyGraph via CLI and return dag_path."""
    nodes = nodes or ["constitution-gate"]
    dag_path = str(tmp_path / "strategy.json")
    for i, node_id in enumerate(nodes):
        args = ["assemble", dag_path, "--catalog", CATALOG, "--node", node_id]
        if i == 0:
            args.extend(["--workflow", workflow])
        code, _ = run_cli(*args, capsys=capsys)
        assert code == 0, f"Bootstrap failed at {node_id}"
    return dag_path


class TestValidateCommand:
    def test_valid_dag(self, capsys):
        code, out = run_cli(
            "validate",
            str(FIXTURES_DIR / "pass-normal.json"),
            "--catalog", CATALOG,
            capsys=capsys,
        )
        assert code == 0
        assert out["status"] == "valid"
        assert "checks" in out
        assert "summary" in out

    def test_invalid_cycle(self, capsys):
        code, out = run_cli(
            "validate",
            str(FIXTURES_DIR / "invalid-cycle.json"),
            "--catalog", CATALOG,
            capsys=capsys,
        )
        assert code == 1
        assert out["status"] == "invalid"
        assert out["summary"]["failed"] > 0


class TestSortCommand:
    def test_sort(self, capsys):
        code, out = run_cli(
            "sort", str(FIXTURES_DIR / "pass-normal.json"),
            capsys=capsys,
        )
        assert code == 0
        assert out["order"] == [
            "input-enrichment",
            "analyst-review",
            "advocate-review",
        ]


class TestAssembleCommand:
    def test_bootstrap_and_assemble(self, tmp_path, capsys):
        """First assemble bootstraps a v3 StrategyGraph."""
        dag_path = str(tmp_path / "strategy.json")
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "constitution-gate",
            "--workflow", "test-wf",
            capsys=capsys,
        )
        assert code == 0
        assert out["node_added"]["id"] == "constitution-gate"

        data = json.loads(Path(dag_path).read_text())
        assert data["schema_version"] == "3.0.0"

    def test_assemble_to_existing(self, tmp_path, capsys):
        dag_path = _bootstrap(tmp_path, capsys)
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "input-enrichment",
            capsys=capsys,
        )
        assert code == 0
        assert out["node_added"]["id"] == "input-enrichment"

    def test_assemble_unknown_node(self, tmp_path, capsys):
        dag_path = _bootstrap(tmp_path, capsys)
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--node", "nonexistent",
            capsys=capsys,
        )
        assert code == 1
        assert out["status"] == "error"


class TestStatusCommand:
    def test_update_status(self, tmp_path, capsys):
        dag_path = _bootstrap(tmp_path, capsys, nodes=["constitution-gate", "input-enrichment"])
        code, out = run_cli(
            "status", dag_path,
            "--node", "input-enrichment",
            "--status", "completed",
            capsys=capsys,
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["old_status"] == "pending"
        assert out["new_status"] == "completed"

    def test_invalid_status(self, tmp_path, capsys):
        dag_path = _bootstrap(tmp_path, capsys, nodes=["constitution-gate", "input-enrichment"])
        code, out = run_cli(
            "status", dag_path,
            "--node", "input-enrichment",
            "--status", "passed",
            capsys=capsys,
        )
        assert code == 1
        assert out["status"] == "error"


class TestFreezeCommand:
    def test_freeze(self, tmp_path, capsys):
        dag_path = _bootstrap(tmp_path, capsys)
        code, out = run_cli(
            "freeze", dag_path,
            "--outcome", "completed",
            "--detail", "advocate-verdict-ready",
            capsys=capsys,
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["pass_frozen"] is True

    def test_double_freeze(self, tmp_path, capsys):
        dag_path = _bootstrap(tmp_path, capsys)
        run_cli("freeze", dag_path, "--outcome", "completed", "--detail", "d", capsys=capsys)

        code, out = run_cli(
            "freeze", dag_path,
            "--outcome", "halted", "--detail", "d2",
            capsys=capsys,
        )
        assert code == 1
        assert out["status"] == "error"


class TestRecordCommand:
    def test_record_gate_verdict(self, tmp_path, capsys):
        """In-process test: record verdict on gate node via --verdict."""
        dag_path = _bootstrap(
            tmp_path, capsys, nodes=["constitution-gate", "analyst-review", "advocate-review"],
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
            capsys=capsys,
        )
        assert code == 0
        assert out["status"] == "success"
        assert out["verdict_recorded"] == "needs-revision"

        data = json.loads(Path(dag_path).read_text())
        node = next(n for n in data["nodes"] if n["id"] == "advocate-review")
        assert node["verdict"] == "needs-revision"


class TestAssembleCapabilityTags:
    def test_assemble_via_capability_tags(self, tmp_path, capsys):
        """In-process integration test: resolve node by capability tags."""
        dag_path = str(tmp_path / "strategy.json")
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "input-enrichment",
            "--workflow", "test-wf",
            capsys=capsys,
        )
        assert code == 0
        assert out["status"] == "valid"
        assert out["node_added"]["id"] == "input-enrichment"

    def test_assemble_capability_tags_no_match(self, tmp_path, capsys):
        """In-process integration test: no matching capability tags."""
        dag_path = _bootstrap(tmp_path, capsys)
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "nonexistent",
            capsys=capsys,
        )
        assert code == 1
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "no_match"

    def test_assemble_capability_tags_ambiguous(self, tmp_path, capsys):
        """In-process integration test: ambiguous capability tags."""
        dag_path = _bootstrap(tmp_path, capsys)
        code, out = run_cli(
            "assemble", dag_path,
            "--catalog", CATALOG,
            "--capability-tags", "gap-detection", "research",
            capsys=capsys,
        )
        assert code == 1
        assert out["status"] == "resolution_failed"
        assert out["reason"] == "ambiguous"


class TestCatalogValidateCommand:
    def test_valid_catalog(self, capsys):
        code, out = run_cli("catalog-validate", CATALOG, capsys=capsys)
        assert code == 0
        assert out["status"] == "valid"
        assert out["summary"]["failed"] == 0

    def test_invalid_catalog(self, tmp_path, capsys):
        bad = tmp_path / "bad-catalog.json"
        bad.write_text('{"not": "a catalog"}')
        code, out = run_cli("catalog-validate", str(bad), capsys=capsys)
        assert code == 1
        assert out["status"] == "invalid"
