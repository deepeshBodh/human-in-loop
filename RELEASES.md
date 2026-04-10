# Release Philosophy

This document defines the release strategy for HumanInLoop during active development.

## Versioning Strategy

HumanInLoop uses a **unified release tag** (e.g., `v0.2.0`) that covers both packages.

- **Major (X.0.0)**: Breaking changes to core APIs, fundamental workflow changes
- **Minor (0.X.0)**: New features, new commands, significant enhancements
- **Patch (0.0.X)**: Bug fixes, documentation updates, minor improvements

### Package Versions

| Package | Version source | Description |
|---------|---------------|-------------|
| `humaninloop` | `humaninloop/pyproject.toml` | CLI tool — user-facing |
| `humaninloop-brain` | `humaninloop_brain/pyproject.toml` | DAG engine — library |

Packages may version independently but release tags cover the whole repo.

## Release Frequency

**Frequent releases are expected** during active development (pre-1.0). The philosophy:

1. **Ship early, ship often** - Don't accumulate changes
2. **One coherent feature set per release** - Bundle related changes together
3. **Keep releases small and reviewable** - Easier to track what changed

Typical triggers for a new release:
- Completing a new command or workflow stage
- Adding new agents or skills
- Fixing bugs affecting usability
- Significant documentation improvements

## Creating a Release

1. **Update version** in `humaninloop/pyproject.toml` and `humaninloop/src/humaninloop/__init__.py`
2. **Update CHANGELOG.md** with release notes
3. **Commit with release message**:
   ```bash
   git commit -m "chore(humaninloop): prepare release X.Y.Z"
   ```
4. **Create the release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes "$(cat <<'EOF'
   ## humaninloop X.Y.Z

   ### Changes
   - ...

   ---

   ## Installation

   ```bash
   uvx --from "humaninloop @ git+https://github.com/deepeshBodh/human-in-loop.git#subdirectory=humaninloop" humaninloop init
   ```
   EOF
   )"
   ```

5. **Always include installation instructions** at the bottom of release notes

## Pre-1.0 Expectations

While HumanInLoop is pre-1.0:

- APIs and command interfaces may change between minor versions
- Frequent iteration is expected and encouraged
- Backwards compatibility is best-effort, not guaranteed
- Each release should document any breaking changes

## Post-1.0 Expectations

Once stable (1.0+):

- Breaking changes require major version bumps
- Deprecation warnings before removal
- Migration guides for breaking changes
- Slower, more deliberate release cadence
