#!/bin/bash
# ensure-marker.sh
# Creates the .humaninloop/core-installed marker file to signal that
# humaninloop-core is installed. Other humaninloop plugins check for this marker.

set -e

# Find repository root (look for .git directory)
find_repo_root() {
    local dir="$PWD"
    while [[ "$dir" != "/" ]]; do
        if [[ -d "$dir/.git" ]]; then
            echo "$dir"
            return 0
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

REPO_ROOT=$(find_repo_root) || {
    echo "Error: Not in a git repository" >&2
    exit 1
}

MARKER_DIR="$REPO_ROOT/.humaninloop"
MARKER_FILE="$MARKER_DIR/core-installed"

# Create .humaninloop directory if it doesn't exist
if [[ ! -d "$MARKER_DIR" ]]; then
    mkdir -p "$MARKER_DIR"
fi

# Create marker file with metadata
cat > "$MARKER_FILE" << EOF
# humaninloop-core installation marker
# This file signals that humaninloop-core is installed.
# Other humaninloop plugins check for this file.
#
# Do not delete this file while using humaninloop plugins.

installed_at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
version: 1.0.0
EOF

echo "humaninloop-core marker created at $MARKER_FILE"
