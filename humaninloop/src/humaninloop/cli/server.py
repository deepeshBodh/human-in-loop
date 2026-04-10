"""Server command - run the hil-dag MCP server."""

import sys


def run_server(extra_args: list[str] | None = None) -> int:
    try:
        from humaninloop_brain.mcp.server import main_sync
    except ImportError:
        print("Error: humaninloop-brain is not installed")
        print("Install it with: uv pip install humaninloop-brain")
        return 1

    sys.argv = ["hil-dag"] + (extra_args or [])
    main_sync()
    return 0
