# Release Philosophy

This document defines the release strategy for the HumanInLoop Marketplace during active development.

## Versioning Strategy

### Marketplace Releases

The marketplace uses a **unified release tag** (e.g., `v0.2.0`) that bundles all plugin changes since the last release.

- **Major (X.0.0)**: Breaking changes to core APIs, fundamental workflow changes
- **Minor (0.X.0)**: New features, new commands, new plugins, significant enhancements
- **Patch (0.0.X)**: Bug fixes, documentation updates, minor improvements

### Plugin Versioning

Each plugin maintains its **own version** in `plugin.json`. A marketplace release may include:

- Updates to multiple plugins at different versions
- One plugin at a major version while another is at a minor version
- This is intentional—plugins evolve independently

Example:
```
humaninloop: 0.7.0
```

## Release Frequency

**Frequent releases are expected** during active development (pre-1.0). The philosophy:

1. **Ship early, ship often** - Don't accumulate changes
2. **One coherent feature set per release** - Bundle related changes together
3. **Keep releases small and reviewable** - Easier to track what changed

Typical triggers for a new release:
- Completing a new command or workflow stage
- Adding a new plugin
- Fixing bugs affecting usability
- Significant documentation improvements

## Release Notes Structure

Follow this format for release notes:

```markdown
## plugin-name X.Y.Z

### New Features
- **Feature name** with brief description

### New Commands
- `/plugin:command` - What it does

### New Agents
- `agent-name` - What it handles

### New Check Modules
- `module-name` - What it validates

### New Templates
- `template-name.md`

### Fixes
- Description of what was fixed

### Breaking Changes
- Only if applicable; describe migration path
```

Group by plugin, then by change type within each plugin.

## Creating a Release

1. **Ensure versions are updated** in each modified plugin's `plugin.json`
2. **Commit with release message**:
   ```bash
   git commit -m "Release vX.Y.Z: Brief description of main changes"
   ```
3. **Create the release**:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes "$(cat <<'EOF'
   ## plugin-name X.Y.Z

   ### New Features
   - ...

   ---

   ## Installation

   \`\`\`bash
   /plugin marketplace add deepeshBodh/human-in-loop
   /plugin install humaninloop
   \`\`\`
   EOF
   )"
   ```

4. **Always include installation instructions** at the bottom of release notes

## Pre-1.0 Expectations

While the marketplace is pre-1.0:

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
