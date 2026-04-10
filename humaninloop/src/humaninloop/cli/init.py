"""Init command - scaffold humaninloop into a project or globally."""

import json
import shutil
from importlib import resources
from pathlib import Path


SCAFFOLD_DIRS = ["agents", "skills", "commands", "templates", "catalogs", "scripts"]

MCP_CONFIG = {
    "hil-dag": {
        "command": "uvx",
        "args": ["humaninloop", "server"],
    }
}


def run_init(*, global_install: bool = False, force: bool = False) -> int:
    target = _resolve_target(global_install)
    scaffolds_root = _scaffolds_path()

    if not scaffolds_root.exists():
        print("Error: scaffolds directory not found in package")
        return 1

    print(f"Installing humaninloop to {target}")

    installed = 0
    skipped = 0

    for dir_name in SCAFFOLD_DIRS:
        src_dir = scaffolds_root / dir_name
        if not src_dir.exists():
            continue

        dest_dir = target / dir_name
        count, skip = _copy_tree(src_dir, dest_dir, force=force)
        installed += count
        skipped += skip

    _write_mcp_config(target, global_install)

    print(f"Installed {installed} files ({skipped} skipped)")
    print("MCP server configured")
    print()
    print("Done! humaninloop is ready to use in Claude Code.")
    return 0


def _resolve_target(global_install: bool) -> Path:
    if global_install:
        return Path.home() / ".claude"
    return Path.cwd() / ".claude"


def _scaffolds_path() -> Path:
    pkg = resources.files("humaninloop")
    return Path(str(pkg)) / "scaffolds"


def _copy_tree(src: Path, dest: Path, *, force: bool) -> tuple[int, int]:
    installed = 0
    skipped = 0

    for src_file in src.rglob("*"):
        if src_file.is_dir():
            continue

        rel = src_file.relative_to(src)
        dest_file = dest / rel

        if dest_file.exists() and not force:
            skipped += 1
            continue

        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dest_file)
        installed += 1

    return installed, skipped


def _write_mcp_config(target: Path, global_install: bool) -> None:
    if global_install:
        _write_global_mcp_config()
    else:
        _write_local_mcp_config(target)


def _write_local_mcp_config(target: Path) -> None:
    mcp_path = target.parent / ".mcp.json"

    config: dict = {}
    if mcp_path.exists():
        try:
            config = json.loads(mcp_path.read_text())
        except (json.JSONDecodeError, OSError):
            config = {}

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    config["mcpServers"].update(MCP_CONFIG)
    mcp_path.write_text(json.dumps(config, indent=2) + "\n")


def _write_global_mcp_config() -> None:
    settings_path = Path.home() / ".claude" / "settings.json"

    config: dict = {}
    if settings_path.exists():
        try:
            config = json.loads(settings_path.read_text())
        except (json.JSONDecodeError, OSError):
            config = {}

    if "mcpServers" not in config:
        config["mcpServers"] = {}

    config["mcpServers"].update(MCP_CONFIG)
    settings_path.write_text(json.dumps(config, indent=2) + "\n")
