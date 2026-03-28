"""HTTP API for hil-dag — serves DAG data to web frontends.

Reads the same DAG JSON files that the MCP server writes.
Designed for read-only consumption (kanban boards, graph visualisers).
"""

from __future__ import annotations

import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from humaninloop_brain.entities.strategy_graph import StrategyGraph

app = FastAPI(
    title="hil-dag API",
    description="Read-only HTTP API for DAG workflow data",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Default root for DAG discovery — overridable via environment or query param.
_DEFAULT_SPECS_ROOT = "specs"


def _resolve_specs_root(specs_root: str | None = None) -> Path:
    """Resolve the specs root directory."""
    return Path(specs_root or _DEFAULT_SPECS_ROOT).resolve()


def _discover_dags(specs_root: Path) -> list[dict]:
    """Scan specs directory for DAG JSON files and return summary metadata."""
    dags: list[dict] = []
    if not specs_root.is_dir():
        return dags

    for feature_dir in sorted(specs_root.iterdir()):
        if not feature_dir.is_dir():
            continue
        dag_dir = feature_dir / ".workflow" / "dags"
        if not dag_dir.is_dir():
            continue
        for dag_file in sorted(dag_dir.glob("*.json")):
            try:
                data = json.loads(dag_file.read_text())
                graph = StrategyGraph.model_validate(data)
                dags.append({
                    "feature": feature_dir.name,
                    "dag_name": dag_file.stem,
                    "id": graph.id,
                    "workflow_id": graph.workflow_id,
                    "status": graph.status,
                    "current_pass": graph.current_pass,
                    "node_count": len(graph.nodes),
                    "edge_count": len(graph.edges),
                    "path": str(dag_file),
                })
            except (json.JSONDecodeError, Exception):
                # Skip malformed files — don't crash the listing
                dags.append({
                    "feature": feature_dir.name,
                    "dag_name": dag_file.stem,
                    "error": "failed to parse",
                    "path": str(dag_file),
                })
    return dags


@app.get("/dags")
def list_dags(specs_root: str | None = None) -> dict:
    """List all discovered DAGs with summary metadata.

    Scans ``specs/<feature>/.workflow/dags/*.json`` for DAG files.

    Query params:
        specs_root: Override the specs directory path (default: ``specs``).
    """
    root = _resolve_specs_root(specs_root)
    dags = _discover_dags(root)
    return {
        "specs_root": str(root),
        "count": len(dags),
        "dags": dags,
    }


@app.get("/dags/{feature}/{dag_name}")
def get_dag(feature: str, dag_name: str, specs_root: str | None = None) -> dict:
    """Return the full DAG data for a specific feature and DAG name.

    The response includes the raw graph data plus a ``kanban`` view that
    groups nodes by status — ready for direct rendering.

    Path params:
        feature: Feature directory name (e.g. ``003-memory-store-agentic``).
        dag_name: DAG filename without extension (e.g. ``strategy``).
    """
    root = _resolve_specs_root(specs_root)
    dag_file = root / feature / ".workflow" / "dags" / f"{dag_name}.json"

    if not dag_file.exists():
        raise HTTPException(status_code=404, detail=f"DAG not found: {feature}/{dag_name}")

    try:
        data = json.loads(dag_file.read_text())
        graph = StrategyGraph.model_validate(data)
    except (json.JSONDecodeError, Exception) as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse DAG: {e}")

    # Build kanban view: group nodes by status
    kanban: dict[str, list[dict]] = {}
    for node in graph.nodes:
        bucket = node.status
        if bucket not in kanban:
            kanban[bucket] = []
        kanban[bucket].append({
            "id": node.id,
            "type": node.type.value,
            "name": node.name,
            "description": node.description,
            "verdict": node.verdict,
            "last_active_pass": node.last_active_pass,
        })

    return {
        "feature": feature,
        "dag_name": dag_name,
        "graph": data,
        "summary": {
            "id": graph.id,
            "workflow_id": graph.workflow_id,
            "status": graph.status,
            "current_pass": graph.current_pass,
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "passes": [
                {
                    "pass": p.pass_number,
                    "outcome": p.outcome,
                    "frozen": p.frozen,
                }
                for p in graph.passes
            ],
        },
        "kanban": kanban,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Launch the API server with uvicorn."""
    uvicorn.run(app, host="127.0.0.1", port=8100)


if __name__ == "__main__":
    main()
