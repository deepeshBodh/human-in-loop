"""MCP server tests — tool discovery, invocation, and error handling."""

import json
from pathlib import Path

import pytest

from humaninloop_brain.mcp.server import mcp, _ToolError

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
CATALOG = str(FIXTURES_DIR / "specify-catalog.json")


class TestToolDiscovery:
    """Server exposes 7 tools with correct names."""

    def test_seven_tools_registered(self):
        tools = mcp._tool_manager._tools
        assert len(tools) == 7

    def test_tool_names(self):
        tools = mcp._tool_manager._tools
        expected = {
            "assemble", "catalog_validate", "freeze",
            "record", "sort", "status", "validate",
        }
        assert set(tools.keys()) == expected


class TestValidateTool:
    def test_valid_dag(self):
        from humaninloop_brain.mcp.operations import op_validate
        result, code = op_validate(
            str(FIXTURES_DIR / "pass-normal.json"), CATALOG,
        )
        assert code == 0
        assert result["status"] == "valid"

    def test_invalid_dag(self):
        from humaninloop_brain.mcp.operations import op_validate
        result, code = op_validate(
            str(FIXTURES_DIR / "invalid-cycle.json"), CATALOG,
        )
        assert code == 1
        assert result["status"] == "invalid"


class TestSortTool:
    def test_sort_order(self):
        from humaninloop_brain.mcp.operations import op_sort
        result, code = op_sort(str(FIXTURES_DIR / "pass-normal.json"))
        assert code == 0
        assert result["order"] == [
            "input-enrichment", "analyst-review", "advocate-review",
        ]


class TestAssembleTool:
    def test_bootstrap(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_assemble
        dag_path = str(tmp_path / "strategy.json")
        result, code = op_assemble(
            dag_path, CATALOG,
            node="constitution-gate", workflow="test-wf",
        )
        assert code == 0
        assert result["node_added"]["id"] == "constitution-gate"

    def test_mutual_exclusion_both(self, tmp_path):
        """Cannot specify both node and capability_tags."""
        from humaninloop_brain.mcp.operations import op_assemble
        result, code = op_assemble(
            str(tmp_path / "strategy.json"), CATALOG,
            node="constitution-gate",
            capability_tags=["input-enrichment"],
        )
        assert code == 2
        assert "Cannot specify both" in result["message"]

    def test_mutual_exclusion_neither(self, tmp_path):
        """Must specify either node or capability_tags."""
        from humaninloop_brain.mcp.operations import op_assemble
        result, code = op_assemble(
            str(tmp_path / "strategy.json"), CATALOG,
        )
        assert code == 2
        assert "required" in result["message"]

    def test_capability_tags_resolution(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_assemble
        dag_path = str(tmp_path / "strategy.json")
        result, code = op_assemble(
            dag_path, CATALOG,
            capability_tags=["input-enrichment"], workflow="test-wf",
        )
        assert code == 0
        assert result["node_added"]["id"] == "input-enrichment"


class TestStatusTool:
    def test_update_status(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_assemble, op_status
        dag_path = str(tmp_path / "strategy.json")
        op_assemble(dag_path, CATALOG, node="constitution-gate", workflow="test-wf")
        op_assemble(dag_path, CATALOG, node="input-enrichment")

        result, code = op_status(dag_path, "input-enrichment", "completed")
        assert code == 0
        assert result["old_status"] == "pending"
        assert result["new_status"] == "completed"

    def test_node_not_found(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_assemble, op_status
        dag_path = str(tmp_path / "strategy.json")
        op_assemble(dag_path, CATALOG, node="constitution-gate", workflow="test-wf")

        result, code = op_status(dag_path, "nonexistent", "completed")
        assert code == 1
        assert "not found" in result["message"]


class TestRecordTool:
    EVIDENCE = json.dumps([{
        "id": "E1",
        "type": "report-summary",
        "description": "Review done",
        "reference": "specs/001/.workflow/report.md",
    }])
    TRACE = json.dumps({
        "node_id": "input-enrichment",
        "started_at": "2026-01-15T10:00:00Z",
        "completed_at": "2026-01-15T10:05:00Z",
    })

    def test_record_success(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_assemble, op_record
        dag_path = str(tmp_path / "strategy.json")
        op_assemble(dag_path, CATALOG, node="constitution-gate", workflow="test-wf")
        op_assemble(dag_path, CATALOG, node="input-enrichment")

        result, code = op_record(
            dag_path, "input-enrichment", "completed",
            self.EVIDENCE, self.TRACE,
        )
        assert code == 0
        assert result["evidence_added"] == 1
        assert result["trace_recorded"] is True

    def test_invalid_evidence_json(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_assemble, op_record
        dag_path = str(tmp_path / "strategy.json")
        op_assemble(dag_path, CATALOG, node="constitution-gate", workflow="test-wf")
        op_assemble(dag_path, CATALOG, node="input-enrichment")

        result, code = op_record(
            dag_path, "input-enrichment", "completed",
            "not-json", self.TRACE,
        )
        assert code == 1
        assert "Invalid evidence JSON" in result["message"]


class TestFreezeTool:
    def test_freeze(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_assemble, op_freeze
        dag_path = str(tmp_path / "strategy.json")
        op_assemble(dag_path, CATALOG, node="constitution-gate", workflow="test-wf")

        result, code = op_freeze(dag_path, "completed", "done")
        assert code == 0
        assert result["pass_frozen"] is True

    def test_invalid_outcome(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_assemble, op_freeze
        dag_path = str(tmp_path / "strategy.json")
        op_assemble(dag_path, CATALOG, node="constitution-gate", workflow="test-wf")

        result, code = op_freeze(dag_path, "invalid", "d")
        assert code == 1
        assert "Invalid outcome" in result["message"]


class TestCatalogValidateTool:
    def test_valid_catalog(self):
        from humaninloop_brain.mcp.operations import op_catalog_validate
        result, code = op_catalog_validate(CATALOG)
        assert code == 0
        assert result["status"] == "valid"

    def test_invalid_catalog(self, tmp_path):
        from humaninloop_brain.mcp.operations import op_catalog_validate
        bad = tmp_path / "bad.json"
        bad.write_text('{"not": "a catalog"}')
        result, code = op_catalog_validate(str(bad))
        assert code == 1
        assert result["status"] == "invalid"


class TestToolErrorHandling:
    """MCP server wraps errors with _ToolError for is_error responses."""

    def test_tool_error_wraps_dict(self):
        err = _ToolError({"status": "error", "message": "test"})
        assert "test" in str(err)
        parsed = json.loads(str(err))
        assert parsed["status"] == "error"
