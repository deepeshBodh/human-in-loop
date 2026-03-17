"""MCP server for hil-dag — exposes DAG operations as MCP tools over stdio."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from humaninloop_brain.mcp.operations import (
    op_assemble,
    op_catalog_validate,
    op_freeze,
    op_record,
    op_sort,
    op_status,
    op_validate,
)

mcp = FastMCP("hil-dag")


@mcp.tool()
def validate(dag_path: str, catalog_path: str) -> dict:
    """Validate a DAG against a node catalog.

    Runs structural validation checks (acyclicity, invariants, edge constraints)
    and returns a constitution-compliant result with checks and summary.

    Args:
        dag_path: Path to the StrategyGraph JSON file.
        catalog_path: Path to the node catalog JSON file.
    """
    result, code = op_validate(dag_path, catalog_path)
    if code > 0:
        raise _ToolError(result)
    return result


@mcp.tool()
def sort(dag_path: str) -> dict:
    """Topological sort of DAG nodes.

    Returns the execution order of nodes based on dependency edges.

    Args:
        dag_path: Path to the StrategyGraph JSON file.
    """
    result, code = op_sort(dag_path)
    if code > 0:
        raise _ToolError(result)
    return result


@mcp.tool()
def assemble(
    dag_path: str,
    catalog_path: str,
    node: str | None = None,
    capability_tags: list[str] | None = None,
    node_type: str | None = None,
    intent: str | None = None,
    workflow: str | None = None,
    graph_id: str | None = None,
    pass_number: int | None = None,
) -> dict:
    """Add a node from catalog to the DAG.

    Resolves the node by direct ID or capability tag matching (with semantic
    fallback via intent). Auto-creates the StrategyGraph on first call when
    workflow is provided. Infers edges from catalog contracts.

    Either ``node`` or ``capability_tags`` must be provided, but not both.

    Args:
        dag_path: Path to the StrategyGraph JSON file (created if missing).
        catalog_path: Path to the node catalog JSON file.
        node: Direct node ID from the catalog.
        capability_tags: Capability tags for resolution (alternative to node).
        node_type: Node type filter for capability resolution.
        intent: Intent description for semantic fallback when capability tags fail.
        workflow: Workflow ID (required when DAG file does not exist).
        graph_id: Custom graph ID for bootstrap.
        pass_number: Target pass number (defaults to current pass).
    """
    result, code = op_assemble(
        dag_path,
        catalog_path,
        node=node,
        capability_tags=capability_tags,
        node_type=node_type,
        intent=intent,
        workflow=workflow,
        graph_id=graph_id,
        pass_number=pass_number,
    )
    if code > 0:
        raise _ToolError(result)
    return result


@mcp.tool()
def status(
    dag_path: str,
    node: str,
    status: str,
    verdict: str | None = None,
    pass_number: int | None = None,
) -> dict:
    """Update a node's status in the DAG.

    For milestone nodes being marked 'achieved', verifies all prerequisite
    nodes are complete first.

    Args:
        dag_path: Path to the StrategyGraph JSON file.
        node: Node ID to update.
        status: New status value.
        verdict: Gate verdict (for gate nodes only).
        pass_number: Target pass number (defaults to current pass).
    """
    result, code = op_status(
        dag_path,
        node,
        status,
        verdict=verdict,
        pass_number=pass_number,
    )
    if code > 0:
        raise _ToolError(result)
    return result


@mcp.tool()
def record(
    dag_path: str,
    node: str,
    status: str,
    evidence: str,
    trace: str,
    verdict: str | None = None,
    pass_number: int | None = None,
) -> dict:
    """Record analysis results for a node (status + evidence + trace).

    Updates the node's status and atomically attaches evidence entries and
    an execution trace. Evidence IDs are auto-generated.

    Args:
        dag_path: Path to the StrategyGraph JSON file.
        node: Node ID to record results for.
        status: New status value.
        evidence: JSON string — array of evidence entries.
        trace: JSON string — execution trace object.
        verdict: Gate verdict (for gate nodes only).
        pass_number: Target pass number (defaults to current pass).
    """
    result, code = op_record(
        dag_path,
        node,
        status,
        evidence,
        trace,
        verdict=verdict,
        pass_number=pass_number,
    )
    if code > 0:
        raise _ToolError(result)
    return result


@mcp.tool()
def freeze(
    dag_path: str,
    outcome: str,
    detail: str,
    triggered_nodes: list[str] | None = None,
    trigger_source: str | None = None,
    reason: str | None = None,
    auto_trigger: bool = False,
) -> dict:
    """Freeze a completed pass.

    Atomically freezes all current-pass history entries, updates pass metadata.
    Optionally creates triggered_by edges and a next pass.

    Args:
        dag_path: Path to the StrategyGraph JSON file.
        outcome: Pass outcome — 'completed' or 'halted'.
        detail: Outcome detail description.
        triggered_nodes: Node IDs to trigger in the next pass.
        trigger_source: Gate node whose verdict triggered the new pass.
        reason: Reason for triggered_by edges.
        auto_trigger: Deterministically compute triggered nodes from graph topology.
    """
    result, code = op_freeze(
        dag_path,
        outcome,
        detail,
        triggered_nodes=triggered_nodes,
        trigger_source=trigger_source,
        reason=reason,
        auto_trigger=auto_trigger,
    )
    if code > 0:
        raise _ToolError(result)
    return result


@mcp.tool()
def catalog_validate(catalog_path: str) -> dict:
    """Validate a node catalog.

    Checks for unique node IDs and presence of all required edge constraints.

    Args:
        catalog_path: Path to the catalog JSON file.
    """
    result, code = op_catalog_validate(catalog_path)
    if code > 0:
        raise _ToolError(result)
    return result


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

import json


class _ToolError(Exception):
    """Wraps a structured error dict for MCP error responses."""

    def __init__(self, result: dict):
        super().__init__(json.dumps(result))


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------


async def main():
    """Run the MCP server over stdio."""
    await mcp.run_async(transport="stdio")


def main_sync():
    """Synchronous entry point for the hil-dag binary."""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()
