"""CLI entry point for humaninloop."""

import argparse
import sys

from humaninloop.cli.init import run_init
from humaninloop.cli.update import run_update
from humaninloop.cli.server import run_server


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="humaninloop",
        description="Install and manage humaninloop workflows for Claude Code",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_get_version()}",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    init_parser = subparsers.add_parser(
        "init",
        help="Scaffold humaninloop agents, skills, commands, and templates",
    )
    init_parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Install globally to ~/.claude/ instead of project .claude/",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without prompting",
    )

    # update
    update_parser = subparsers.add_parser(
        "update",
        help="Update an existing humaninloop installation",
    )
    update_parser.add_argument(
        "--global",
        dest="global_install",
        action="store_true",
        help="Update global installation at ~/.claude/",
    )
    update_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite modified files without prompting",
    )

    # server
    server_parser = subparsers.add_parser(
        "server",
        help="Run the hil-dag MCP server",
    )
    server_parser.add_argument(
        "server_args",
        nargs="*",
        help="Additional arguments passed to hil-dag server",
    )

    args = parser.parse_args()

    if args.command == "init":
        sys.exit(run_init(global_install=args.global_install, force=args.force))
    elif args.command == "update":
        sys.exit(run_update(global_install=args.global_install, force=args.force))
    elif args.command == "server":
        sys.exit(run_server(args.server_args))


def _get_version() -> str:
    from humaninloop import __version__

    return __version__


if __name__ == "__main__":
    main()
