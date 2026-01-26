# Context Gathering Mode

Detailed guidance for gathering project context to inform constitution authoring.

## Context Gathering Flow

```
1. TECH STACK      → Language, framework, dependencies
2. CONVENTIONS     → Existing standards, style guides
3. ARCHITECTURE    → Folder structure, layer patterns
4. TEAM SIGNALS    → CI config, test patterns, tooling
5. EXISTING DOCS   → README, CLAUDE.md, prior governance
```

## Convention Detection

### Linting & Formatting

| File | Tool | Extract Configuration |
|------|------|----------------------|
| `.eslintrc.*` | ESLint | Rules, extends, plugins |
| `ruff.toml` / `pyproject.toml [tool.ruff]` | Ruff | Line length, rules |
| `analysis_options.yaml` | Dart analyzer | Lint rules, includes |
| `.prettierrc` | Prettier | Formatting options |
| `.editorconfig` | EditorConfig | Indentation, line endings |

### Existing Standards

```bash
# Look for existing governance docs
ls -la CLAUDE.md CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null

# Look for architecture docs
ls -la docs/architecture* docs/adr/* ADR/* 2>/dev/null

# Look for existing constitution
ls -la .humaninloop/memory/constitution.md 2>/dev/null
```

## Team Signal Detection

### CI/CD Configuration

| File | Platform | Extract |
|------|----------|---------|
| `.github/workflows/*.yml` | GitHub Actions | Jobs, gates, required checks |
| `.gitlab-ci.yml` | GitLab CI | Stages, jobs, rules |
| `Jenkinsfile` | Jenkins | Stages, steps |
| `.circleci/config.yml` | CircleCI | Jobs, workflows |

### Quality Gates from CI

```bash
# Extract test commands
grep -r "pytest\|jest\|flutter test\|go test" .github/workflows/ 2>/dev/null

# Extract coverage requirements
grep -r "cov-fail-under\|coverage-minimum\|--coverage" .github/workflows/ 2>/dev/null

# Extract lint commands
grep -r "ruff\|eslint\|flutter analyze" .github/workflows/ 2>/dev/null
```

### Test Patterns

```bash
# Check test directory structure
ls -d test/ tests/ spec/ __tests__/ 2>/dev/null

# Check test file count
find . -name "*_test.*" -o -name "*.test.*" -o -name "test_*.*" 2>/dev/null | wc -l

# Check for integration tests
ls -d integration_test/ e2e/ cypress/ 2>/dev/null
```

## Documentation Analysis

### README Extraction

```bash
# Check README for tech stack mentions
head -100 README.md | grep -i "built with\|stack\|technologies\|requirements"

# Check for setup instructions
grep -A 10 "Getting Started\|Installation\|Setup" README.md
```

### Existing Governance

If prior constitution or CLAUDE.md exists, extract:
- Existing principles (to preserve or migrate)
- Version history (for continuity)
- Tech stack declarations (to validate)

## Inference Rules

When explicit configuration is missing, make reasonable inferences:

| Missing | Infer From | Default If Nothing |
|---------|------------|-------------------|
| Python version | `.python-version`, `pyproject.toml` | 3.11+ |
| Coverage threshold | CI config | 80% (industry standard) |
| Line length | Linter config | 100 characters |
| Required approvals | Branch protection | 1 approval |
| Test framework | Package dependencies | pytest (Python), jest (Node) |

## Output Format: Project Context Report

```markdown
# Project Context Report

Generated: [ISO timestamp]

## Tech Stack

| Category | Detected | Source |
|----------|----------|--------|
| Language | [Language] [Version] | [Config file] |
| Framework | [Framework] [Version] | [package.json/etc] |
| Testing | [Library] | [Config file] |
| Linting | [Tool] | [Config file] |
| CI | [Platform] | [Config location] |

## Existing Conventions

- **Line length**: [N] characters
- **Indent**: [tabs/spaces] [size]
- **Coverage threshold**: [N%] (from CI)
- **Required approvals**: [N] (from branch protection)

## Architecture

- **Pattern**: [Detected or "Unstructured"]
- **Layers**: [List if detected]
- **Module strategy**: [Feature/Layer/Mixed]

## Team Signals

- **Test coverage enforced**: [Yes/No]
- **Lint checks in CI**: [Yes/No]
- **Type checking**: [Yes/No]
- **Security scanning**: [Yes/No]

## Existing Governance

- **CLAUDE.md**: [Present/Absent]
- **Prior constitution**: [Present v.X.Y.Z / Absent]
- **ADRs**: [Count] found in [location]

## Recommendations

Based on this analysis, the constitution should:
1. [Recommendation based on findings]
2. [Recommendation based on findings]
3. [Recommendation based on findings]
```
