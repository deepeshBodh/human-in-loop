---
name: analyzing-project-context
description: Infer project characteristics from codebase to inform constitution content. Use when setting up a constitution, understanding project context, or when you need to determine tech stack, conventions, architecture patterns, or team signals from repository analysis.
---

# Analyzing Project Context

## Purpose

Infer project characteristics from codebase analysis to inform constitution authoring. Extract tech stack, conventions, architecture patterns, and team signals without requiring explicit user input for obvious context.

## Context Gathering Strategy

Analyze the repository systematically to build a project profile:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTEXT GATHERING FLOW                        │
├─────────────────────────────────────────────────────────────────┤
│  1. TECH STACK        → Language, framework, dependencies       │
│  2. CONVENTIONS       → Existing standards, style guides        │
│  3. ARCHITECTURE      → Folder structure, layer patterns        │
│  4. TEAM SIGNALS      → CI config, test patterns, tooling       │
│  5. EXISTING DOCS     → README, CLAUDE.md, prior governance     │
└─────────────────────────────────────────────────────────────────┘
```

## 1. Tech Stack Detection

### Primary Indicators

| File | Indicates | Extract |
|------|-----------|---------|
| `package.json` | Node.js/JavaScript | Dependencies, scripts, engine version |
| `pyproject.toml` | Python | Dependencies, Python version, tools |
| `requirements.txt` | Python (legacy) | Dependencies |
| `pubspec.yaml` | Flutter/Dart | Dependencies, SDK constraints |
| `Cargo.toml` | Rust | Dependencies, edition |
| `go.mod` | Go | Module path, Go version |
| `pom.xml` / `build.gradle` | Java | Dependencies, Java version |
| `Gemfile` | Ruby | Dependencies, Ruby version |

### Framework Detection

```markdown
## Tech Stack Analysis

**Language**: [Detected from package manager files]
**Version**: [Extracted from config or .tool-versions]
**Framework**: [Detected from dependencies]
**Package Manager**: [npm/yarn/pnpm, pip/uv/poetry, etc.]

**Key Dependencies**:
- [Framework]: [Version]
- [Testing]: [Library]
- [Linting]: [Tool]
```

### Detection Commands

```bash
# Node.js
cat package.json | jq '{name, engines, dependencies, devDependencies}'

# Python
cat pyproject.toml  # or requirements.txt

# Flutter
cat pubspec.yaml

# Check for version managers
cat .tool-versions .nvmrc .python-version 2>/dev/null
```

## 2. Convention Detection

### Linting & Formatting

| File | Tool | Extract Configuration |
|------|------|----------------------|
| `.eslintrc.*` | ESLint | Rules, extends, plugins |
| `ruff.toml` / `pyproject.toml [tool.ruff]` | Ruff | Line length, rules |
| `analysis_options.yaml` | Dart analyzer | Lint rules, includes |
| `.prettierrc` | Prettier | Formatting options |
| `.editorconfig` | EditorConfig | Indentation, line endings |

### Existing Standards

Check for existing governance or standards:

```bash
# Look for existing governance docs
ls -la CLAUDE.md CONTRIBUTING.md .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null

# Look for architecture docs
ls -la docs/architecture* docs/adr/* ADR/* 2>/dev/null

# Look for existing constitution
ls -la .humaninloop/memory/constitution.md 2>/dev/null
```

### Extract Convention Summary

```markdown
## Existing Conventions

**Linting**: [Tool] with [config file]
**Formatting**: [Tool] with [config file]
**Line Length**: [N characters] (from config)
**Indentation**: [tabs/spaces, size]

**Documented Standards**:
- [File]: [Summary of contents]
```

## 3. Architecture Detection

### Folder Structure Patterns

| Pattern | Indicates | Constitution Implications |
|---------|-----------|---------------------------|
| `src/domain/`, `src/application/`, `src/adapters/` | Clean/Hexagonal Architecture | Layer rules, dependency flow |
| `src/features/*` | Feature-based modules | Module isolation rules |
| `lib/screens/`, `lib/widgets/` | Flutter standard | Widget nesting rules |
| `app/`, `lib/`, `spec/` | Rails convention | MVC patterns |
| `cmd/`, `internal/`, `pkg/` | Go standard layout | Package visibility rules |

### Layer Detection

```bash
# Check for clean architecture layers
ls -d src/domain src/application src/adapters src/infrastructure 2>/dev/null

# Check for feature modules
ls -d src/features/* lib/features/* 2>/dev/null

# Check for standard structures
ls -d lib/screens lib/widgets lib/services lib/models 2>/dev/null
```

### Architecture Summary

```markdown
## Architecture Analysis

**Pattern**: [Detected pattern or "Flat/No clear pattern"]
**Layers Detected**:
- [Layer 1]: [Path]
- [Layer 2]: [Path]

**Module Structure**: [Feature-based / Layer-based / Mixed]

**Import Rules Suggested**:
- [Layer] MAY import [Layer]
- [Layer] MUST NOT import [Layer]
```

## 4. Team Signal Detection

### CI/CD Configuration

| File | Platform | Extract |
|------|----------|---------|
| `.github/workflows/*.yml` | GitHub Actions | Jobs, gates, required checks |
| `.gitlab-ci.yml` | GitLab CI | Stages, jobs, rules |
| `Jenkinsfile` | Jenkins | Stages, steps |
| `.circleci/config.yml` | CircleCI | Jobs, workflows |
| `bitbucket-pipelines.yml` | Bitbucket | Steps, conditions |

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

### Team Signals Summary

```markdown
## Team Signals

**CI Platform**: [Detected platform]
**Quality Gates in CI**:
- [ ] Static analysis
- [ ] Tests
- [ ] Coverage threshold: [N%]
- [ ] Security scan

**Test Structure**:
- Unit tests: [location]
- Integration tests: [location]
- Test count: [N files]

**Code Review**:
- Required approvals: [N] (from branch protection or PR template)
```

## 5. Documentation Analysis

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

```markdown
## Existing Documentation

**README.md**: [Summary of relevant sections]
**CLAUDE.md**: [Exists/Missing] - [Summary if exists]
**Prior Constitution**: [Exists/Missing] - [Version if exists]

**Key Extracted Information**:
- [Finding 1]
- [Finding 2]
```

## Output: Project Context Report

Compile findings into a structured report for constitution authoring:

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

## Inference Rules

When explicit configuration is missing, make reasonable inferences:

| Missing | Infer From | Default If Nothing |
|---------|------------|-------------------|
| Python version | `.python-version`, `pyproject.toml` | 3.11+ |
| Coverage threshold | CI config | 80% (industry standard) |
| Line length | Linter config | 100 characters |
| Required approvals | Branch protection | 1 approval |
| Test framework | Package dependencies | pytest (Python), jest (Node) |

## Quality Checklist

Before completing context analysis:

- [ ] Tech stack identified with versions
- [ ] Existing linting/formatting config extracted
- [ ] Architecture pattern identified (or noted as unstructured)
- [ ] CI configuration analyzed for quality gates
- [ ] Existing governance documents checked
- [ ] README scanned for relevant context
- [ ] Inferences documented with source or "default"
- [ ] Recommendations provided for constitution authoring

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Assuming without checking** | Guessing Python when it's Go | Check package manager files first |
| **Ignoring existing governance** | Overwriting prior decisions | Extract and evaluate existing docs |
| **Over-extraction** | Analyzing every file | Focus on config files and patterns |
| **Missing CI analysis** | Not leveraging existing gates | CI config reveals team standards |
| **Skipping README** | Missing project philosophy | README often has implicit governance |
