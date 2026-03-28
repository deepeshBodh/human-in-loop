"""HTTP API tests — endpoint discovery, DAG listing, and detail retrieval."""

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from humaninloop_brain.mcp.api import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

client = TestClient(app)


class TestListDags:
    """GET /dags — discover DAGs from specs directory."""

    def test_empty_specs_dir(self, tmp_path):
        resp = client.get("/dags", params={"specs_root": str(tmp_path)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["dags"] == []

    def test_nonexistent_specs_dir(self, tmp_path):
        resp = client.get("/dags", params={"specs_root": str(tmp_path / "nope")})
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0

    def test_discovers_dag_file(self, tmp_path):
        # Set up specs/<feature>/.workflow/dags/<dag>.json
        dag_dir = tmp_path / "feat-auth" / ".workflow" / "dags"
        dag_dir.mkdir(parents=True)
        shutil.copy(FIXTURES_DIR / "pass-normal.json", dag_dir / "strategy.json")

        resp = client.get("/dags", params={"specs_root": str(tmp_path)})
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1

        dag = data["dags"][0]
        assert dag["feature"] == "feat-auth"
        assert dag["dag_name"] == "strategy"
        assert dag["workflow_id"] == "specify-feature-auth"
        assert dag["status"] == "in-progress"
        assert dag["node_count"] == 3
        assert dag["edge_count"] == 5

    def test_discovers_multiple_features(self, tmp_path):
        for name in ("feat-a", "feat-b"):
            dag_dir = tmp_path / name / ".workflow" / "dags"
            dag_dir.mkdir(parents=True)
            shutil.copy(FIXTURES_DIR / "pass-normal.json", dag_dir / "strategy.json")

        resp = client.get("/dags", params={"specs_root": str(tmp_path)})
        data = resp.json()
        assert data["count"] == 2
        features = [d["feature"] for d in data["dags"]]
        assert features == ["feat-a", "feat-b"]

    def test_skips_malformed_json(self, tmp_path):
        dag_dir = tmp_path / "feat-bad" / ".workflow" / "dags"
        dag_dir.mkdir(parents=True)
        (dag_dir / "broken.json").write_text("not valid json {{{")

        resp = client.get("/dags", params={"specs_root": str(tmp_path)})
        data = resp.json()
        assert data["count"] == 1
        assert data["dags"][0]["error"] == "failed to parse"

    def test_ignores_non_json_files(self, tmp_path):
        dag_dir = tmp_path / "feat-x" / ".workflow" / "dags"
        dag_dir.mkdir(parents=True)
        (dag_dir / "notes.txt").write_text("not a dag")
        shutil.copy(FIXTURES_DIR / "pass-normal.json", dag_dir / "strategy.json")

        resp = client.get("/dags", params={"specs_root": str(tmp_path)})
        data = resp.json()
        assert data["count"] == 1
        assert data["dags"][0]["dag_name"] == "strategy"


class TestGetDag:
    """GET /dags/{feature}/{dag_name} — full DAG detail with kanban view."""

    def _setup_dag(self, tmp_path, feature="feat-auth", dag_name="strategy"):
        dag_dir = tmp_path / feature / ".workflow" / "dags"
        dag_dir.mkdir(parents=True)
        shutil.copy(FIXTURES_DIR / "pass-normal.json", dag_dir / f"{dag_name}.json")
        return tmp_path

    def test_returns_full_dag(self, tmp_path):
        self._setup_dag(tmp_path)
        resp = client.get(
            "/dags/feat-auth/strategy",
            params={"specs_root": str(tmp_path)},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["feature"] == "feat-auth"
        assert data["dag_name"] == "strategy"

    def test_includes_summary(self, tmp_path):
        self._setup_dag(tmp_path)
        resp = client.get(
            "/dags/feat-auth/strategy",
            params={"specs_root": str(tmp_path)},
        )
        summary = resp.json()["summary"]
        assert summary["id"] == "specify-pass-001"
        assert summary["workflow_id"] == "specify-feature-auth"
        assert summary["node_count"] == 3
        assert summary["edge_count"] == 5
        assert summary["current_pass"] == 1

    def test_includes_raw_graph(self, tmp_path):
        self._setup_dag(tmp_path)
        resp = client.get(
            "/dags/feat-auth/strategy",
            params={"specs_root": str(tmp_path)},
        )
        graph = resp.json()["graph"]
        assert "nodes" in graph
        assert "edges" in graph
        assert len(graph["nodes"]) == 3

    def test_kanban_groups_by_status(self, tmp_path):
        self._setup_dag(tmp_path)
        resp = client.get(
            "/dags/feat-auth/strategy",
            params={"specs_root": str(tmp_path)},
        )
        kanban = resp.json()["kanban"]
        # All 3 nodes in pass-normal.json are "pending"
        assert "pending" in kanban
        assert len(kanban["pending"]) == 3

    def test_kanban_node_fields(self, tmp_path):
        self._setup_dag(tmp_path)
        resp = client.get(
            "/dags/feat-auth/strategy",
            params={"specs_root": str(tmp_path)},
        )
        node = resp.json()["kanban"]["pending"][0]
        assert "id" in node
        assert "type" in node
        assert "name" in node
        assert "description" in node

    def test_404_missing_feature(self, tmp_path):
        resp = client.get(
            "/dags/nonexistent/strategy",
            params={"specs_root": str(tmp_path)},
        )
        assert resp.status_code == 404

    def test_404_missing_dag(self, tmp_path):
        self._setup_dag(tmp_path)
        resp = client.get(
            "/dags/feat-auth/missing",
            params={"specs_root": str(tmp_path)},
        )
        assert resp.status_code == 404

    def test_422_malformed_dag(self, tmp_path):
        dag_dir = tmp_path / "feat-bad" / ".workflow" / "dags"
        dag_dir.mkdir(parents=True)
        (dag_dir / "broken.json").write_text("not json")

        resp = client.get(
            "/dags/feat-bad/broken",
            params={"specs_root": str(tmp_path)},
        )
        assert resp.status_code == 422


class TestPassesSummary:
    """Verify passes are included in the detail response."""

    def test_passes_in_summary(self, tmp_path):
        dag_dir = tmp_path / "feat-auth" / ".workflow" / "dags"
        dag_dir.mkdir(parents=True)
        shutil.copy(FIXTURES_DIR / "pass-normal.json", dag_dir / "strategy.json")

        resp = client.get(
            "/dags/feat-auth/strategy",
            params={"specs_root": str(tmp_path)},
        )
        passes = resp.json()["summary"]["passes"]
        assert len(passes) == 1
        assert passes[0]["pass"] == 1
