"""Update command - update an existing humaninloop installation."""

import filecmp
import shutil
from pathlib import Path

from humaninloop.cli.init import SCAFFOLD_DIRS, _resolve_target, _scaffolds_path, _write_mcp_config


def run_update(*, global_install: bool = False, force: bool = False) -> int:
    target = _resolve_target(global_install)
    scaffolds_root = _scaffolds_path()

    if not scaffolds_root.exists():
        print("Error: scaffolds directory not found in package")
        return 1

    if not target.exists():
        print(f"No existing installation found at {target}")
        print("Run 'humaninloop init' first.")
        return 1

    print(f"Updating humaninloop at {target}")

    updated = 0
    skipped = 0
    added = 0
    warned = 0

    for dir_name in SCAFFOLD_DIRS:
        src_dir = scaffolds_root / dir_name
        if not src_dir.exists():
            continue

        dest_dir = target / dir_name

        for src_file in src_dir.rglob("*"):
            if src_file.is_dir():
                continue

            rel = src_file.relative_to(src_dir)
            dest_file = dest_dir / rel

            if not dest_file.exists():
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
                added += 1
                continue

            if filecmp.cmp(src_file, dest_file, shallow=False):
                skipped += 1
                continue

            if force:
                shutil.copy2(src_file, dest_file)
                updated += 1
            else:
                print(f"  Modified: {dir_name}/{rel} (use --force to overwrite)")
                warned += 1

    _write_mcp_config(target, global_install)

    print(f"Added {added}, updated {updated}, unchanged {skipped}")
    if warned:
        print(f"Warning: {warned} locally modified files were skipped")
    print("MCP server config updated")
    return 0
