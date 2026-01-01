# Agent Skills: Complete technical reference

Agent Skills are organized folders of instructions, scripts, and resources that AI agents can discover and load dynamically to perform better at specific tasks. Originally developed by Anthropic and released as an open standard, Agent Skills provide a composable, portable, and efficient way to equip agents with domain-specific expertise. This comprehensive reference covers all 12 areas of the Agent Skills system based on official Anthropic documentation and the agentskills.io ecosystem.

---

## 1. Core concept

**Summary**: Agent Skills transform general-purpose agents into specialists by packaging domain knowledge, workflows, and executable code into self-contained directories. Unlike prompts (conversation-level instructions), Skills load on-demand and eliminate repetitive guidance across conversations. Skills are **model-invoked**—Claude autonomously decides when to use them based on task context.

### Technical details

**What Skills Are**:
- Folders containing a `SKILL.md` file with instructions, metadata, and optional supporting resources
- Self-contained packages of domain expertise that Claude loads dynamically
- Reusable capabilities that work across Claude.ai, Claude Code, Claude Agent SDK, and the Claude API

**Key Properties**:
| Property | Description |
|----------|-------------|
| **Composable** | Multiple skills work together automatically |
| **Portable** | Built once, usable across all Claude surfaces |
| **Efficient** | Load only necessary information when needed (progressive disclosure) |
| **Powerful** | Can include executable code for reliable, deterministic task execution |

**Skills vs Commands Comparison**:
| Aspect | Skills | Commands |
|--------|--------|----------|
| Invocation | Model-invoked automatically | User-invoked via `/command` |
| Trigger | Task context matching description | Manual typing |
| Format | Directory with SKILL.md + resources | Single Markdown file |
| Resources | Can bundle scripts, references, data | Standalone |
| Loading | Progressive (metadata → body → resources) | Full content at invocation |

**When to Use Skills**:
- Capturing domain-specific expertise (legal review, data analysis, brand guidelines)
- Creating repeatable workflows with consistent outputs
- Packaging organizational knowledge for team sharing
- Automating multi-step processes requiring specialized procedures

### Source URLs
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- https://agentskills.io/home

### Gaps
- No formal definition of "skill relevance" threshold for triggering
- Interaction between multiple overlapping skills not fully documented
- Maximum number of skills that can be installed not specified

### Claude usage tips
- When explaining skills, emphasize the **model-invoked** nature—users don't call skills directly
- Skills are like "onboarding guides for Claude"—structured knowledge packages
- Key distinction from commands: skills activate based on task context, not explicit user invocation
- Clarify that skills are NOT plugins—they're knowledge packages, not code extensions

---

## 2. SKILL.md schema

**Summary**: Every skill requires a `SKILL.md` file with YAML frontmatter containing required `name` and `description` fields. The markdown body contains instructions, examples, and guidelines that Claude follows when the skill is active. The description is critical—it determines when Claude chooses to use the skill from potentially hundreds of available options.

### Technical details

**Complete SKILL.md Format**:
```yaml
---
name: skill-name                           # REQUIRED: unique identifier
description: |                             # REQUIRED: what + when to use
  Clear description of what this skill does.
  Include keywords users would mention.
  Specify when Claude should use this skill.
license: MIT                               # Optional: license identifier
allowed-tools: Bash, Read, Write           # Optional: Claude Code only
model: claude-3-5-sonnet-20241022          # Optional: model override
metadata:                                  # Optional: custom key-value pairs
  version: "1.0.0"
  author: "developer-name"
  category: "development"
---

# Skill Name

## Purpose
Explain the skill's primary function.

## Instructions
1. Step-by-step guidance for Claude
2. Clear, actionable instructions
3. Include edge case handling

## Examples
- "User query example" → Expected behavior
- "Another example" → Expected behavior

## Guidelines
- Important consideration 1
- Important consideration 2
```

**YAML Frontmatter Field Requirements**:
| Field | Required | Constraints | Description |
|-------|----------|-------------|-------------|
| `name` | Yes | Max 64 chars, lowercase letters/numbers/hyphens only, no XML tags, no reserved words ("anthropic", "claude") | Unique identifier matching directory name |
| `description` | Yes | Max 1024 chars, non-empty, no XML tags | What skill does + when to use it |
| `license` | No | Any string | License identifier |
| `allowed-tools` | No | Comma-separated tool names | Tools Claude can use (Claude Code only) |
| `model` | No | Valid model ID | Override model when skill is active |
| `metadata` | No | Key-value pairs | Custom metadata |

**Description Best Practices**:
```yaml
# BAD - Too vague
description: Helps with documents

# BAD - Wrong point of view
description: I can help you process Excel files

# GOOD - Specific with keywords and trigger context
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Naming Conventions**:
- Use **gerund form** (verb + -ing): `processing-pdfs`, `analyzing-spreadsheets`
- Acceptable alternatives: noun phrases (`pdf-processing`) or action-oriented (`process-pdfs`)
- Avoid vague names: `helper`, `utils`, `tools`, `documents`

### Source URLs
- https://code.claude.com/docs/en/skills
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://github.com/anthropics/skills

### Gaps
- No formal JSON schema validator provided for SKILL.md
- `model` field behavior across different Claude surfaces undocumented
- Validation error messages not standardized

### Claude usage tips
- Always emphasize the **description field is critical**—it's how Claude selects skills
- Write descriptions in **third person** (not "I can" or "You can")
- Include specific trigger keywords users would naturally say
- The name must match the directory name exactly (case-sensitive)

---

## 3. Directory structure

**Summary**: Skills are self-contained directories with `SKILL.md` at the root. Additional files (reference docs, scripts, assets) can be bundled and referenced from the main file. The structure supports progressive disclosure—Claude loads files only as needed, keeping context efficient.

### Technical details

**Basic Structure** (single-file skill):
```
my-skill/
└── SKILL.md              # Required
```

**Complete Structure** (multi-file skill):
```
my-skill/
├── SKILL.md              # Required: main instructions
├── FORMS.md              # Optional: specialized guide (loaded as needed)
├── REFERENCE.md          # Optional: API reference (loaded as needed)
├── examples.md           # Optional: usage examples
├── LICENSE.txt           # Optional: license file
├── scripts/              # Optional: executable code
│   ├── analyzer.py       # Executed, not loaded into context
│   ├── validator.py
│   └── processor.sh
├── references/           # Optional: documentation
│   ├── api-guide.md
│   └── style-guide.md
└── assets/               # Optional: templates, data files
    ├── template.xlsx
    └── config.json
```

**File Organization Patterns**:

| Pattern | Use Case | Example |
|---------|----------|---------|
| High-level guide with references | General skills with optional deep-dives | Main SKILL.md links to FORMS.md, REFERENCE.md |
| Domain-specific organization | Skills with multiple distinct domains | `reference/finance.md`, `reference/sales.md` |
| Conditional details | Basic + advanced content | Show basic, link to REDLINING.md for advanced |

**Skill Locations by Platform**:
| Platform | Location | Scope |
|----------|----------|-------|
| Claude Code - Enterprise | Managed settings | All users in organization |
| Claude Code - Personal | `~/.claude/skills/` | You, across all projects |
| Claude Code - Project | `.claude/skills/` | Anyone in this repository |
| Claude Code - Plugin | Bundled with plugins | Anyone with plugin installed |
| Claude.ai | Uploaded via Settings | Individual user only |
| Claude API | Uploaded via `/v1/skills` | Workspace-wide |
| Agent SDK | `.claude/skills/` (requires settingSources) | Per configuration |

### Source URLs
- https://code.claude.com/docs/en/skills
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

### Gaps
- Maximum file count per skill not specified
- Maximum total skill size limit (only 8MB for API upload documented)
- Symlink behavior within skills undocumented

### Claude usage tips
- Emphasize that bundled files DON'T consume context until accessed
- Scripts are **executed**, not loaded—only output enters context
- Keep SKILL.md under 500 lines; split into separate files if larger
- Use forward slashes in all paths (Unix style), even on Windows

---

## 4. Progressive disclosure

**Summary**: Progressive disclosure is the core design principle that makes Agent Skills efficient and scalable. Like a well-organized manual, skills let Claude load information only as needed. This three-level system ensures only relevant content occupies the context window at any given time.

### Technical details

**Three Levels of Loading**:

| Level | When Loaded | Token Cost | Content |
|-------|-------------|------------|---------|
| **Level 1: Metadata** | Always (at startup) | ~100 tokens per skill | `name` and `description` from YAML frontmatter |
| **Level 2: Instructions** | When skill is triggered | Under 5k tokens recommended | SKILL.md body with instructions and guidance |
| **Level 3+: Resources** | As needed during execution | Effectively unlimited | Bundled files read via bash; scripts executed without loading |

**How It Works**:

1. **Startup**: Claude loads only name and description of every installed skill into system prompt
2. **User Request**: Claude evaluates request against skill descriptions using semantic matching
3. **Skill Triggered**: If request matches, Claude reads full SKILL.md from filesystem via bash
4. **Resource Access**: Claude reads additional files (FORMS.md, REFERENCE.md) only when referenced
5. **Script Execution**: Utility scripts run via bash; only output enters context, not code

**Token Efficiency**:
```
Context Window Usage:
┌─────────────────────────────────────────┐
│ System Prompt                           │
├─────────────────────────────────────────┤
│ Skill Metadata (~100 tokens each)       │  ← Always loaded
│ • pdf-processing: "Extract text..."     │
│ • code-review: "Analyze code..."        │
│ • data-analysis: "Process datasets..."  │
├─────────────────────────────────────────┤
│ Conversation History                    │
├─────────────────────────────────────────┤
│ Active Skill Content (when triggered)   │  ← Loaded on-demand
│ • SKILL.md body                         │
│ • Referenced files (as needed)          │
└─────────────────────────────────────────┘
```

**Why This Matters**:
- Install many skills without context penalty
- Large reference files don't consume tokens until accessed
- Scripts execute deterministically without loading code
- Effectively unbounded skill content capacity

### Source URLs
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

### Gaps
- Exact token budget for skill metadata in system prompt undocumented
- Behavior when total metadata exceeds system prompt capacity unclear
- Caching behavior for repeatedly-accessed skill files not specified

### Claude usage tips
- This is the **key innovation** of Agent Skills—explain it clearly
- Analogy: "Like a table of contents that loads chapters only when needed"
- Emphasize: bundled files are FREE until accessed
- Scripts are even more efficient—only OUTPUT enters context

---

## 5. Triggering mechanism

**Summary**: Claude uses semantic matching between user requests and skill descriptions to determine when to invoke skills. The description field is the primary trigger—it must contain both what the skill does AND when Claude should use it. Well-crafted descriptions with specific keywords dramatically improve trigger accuracy.

### Technical details

**Triggering Flow**:
```
User Request → Semantic Match Against Descriptions → Skill Selection → Permission Request → Load SKILL.md → Execute
```

**How Claude Decides**:
1. Claude receives user request
2. Compares request semantically against all skill descriptions
3. Selects most relevant skill(s) based on:
   - Keyword matching
   - Semantic similarity
   - Context alignment
4. Asks user permission to use the skill (in Claude Code)
5. Loads full SKILL.md into context
6. Follows skill instructions

**Description Optimization**:

| Element | Purpose | Example |
|---------|---------|---------|
| **What it does** | Core capability description | "Extract text and tables from PDF files" |
| **Specific actions** | Detailed capabilities | "fill forms, merge documents" |
| **Trigger context** | When to activate | "Use when working with PDF files" |
| **Keywords** | Natural user language | "PDFs, forms, document extraction" |

**Effective vs Ineffective Descriptions**:

```yaml
# INEFFECTIVE - Vague, no triggers
description: Helps with documents

# INEFFECTIVE - Generic
description: Processes data

# EFFECTIVE - Specific with triggers
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# EFFECTIVE - Domain-specific with keywords
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

**Multiple Skills Disambiguation**:
- Make descriptions distinct with specific trigger terms
- Avoid two skills both mentioning generic terms like "data analysis"
- Use domain-specific language: "sales data in Excel/CRM" vs "log files and metrics"

### Source URLs
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://code.claude.com/docs/en/skills

### Gaps
- Exact semantic matching algorithm not disclosed
- Priority when multiple skills match equally not documented
- Threshold for "sufficient match" to trigger not specified

### Claude usage tips
- The description is the **most important field**—emphasize this repeatedly
- Include keywords users would naturally say in their requests
- Think from user's perspective: "What would someone type when they need this?"
- Avoid jargon in descriptions—use natural language users would use

---

## 6. Description optimization

**Summary**: Writing effective descriptions is the most critical skill authoring task. The description must be specific, include trigger keywords, and clearly state both what the skill does and when to use it. Poor descriptions lead to skills never being triggered; excellent descriptions enable reliable, contextual activation.

### Technical details

**Description Formula**:
```
[What it does] + [Specific capabilities] + [When to use] + [Trigger keywords]
```

**Character Constraints**:
- Maximum: 1024 characters
- Recommended: 100-300 characters for optimal balance
- Must be non-empty
- Cannot contain XML tags

**Writing Guidelines**:

| Guideline | Why | Example |
|-----------|-----|---------|
| Third person | Injected into system prompt; consistent POV | "Processes Excel files" not "I can help you" |
| Active verbs | Clear, actionable | "Extract", "Analyze", "Generate" |
| Specific capabilities | Helps matching | "fill forms, merge documents" |
| Trigger phrases | Natural language activation | "Use when working with..." |
| Domain keywords | User vocabulary | "PDF, spreadsheet, .xlsx" |

**Description Templates by Skill Type**:

**Document Processing**:
```yaml
description: Extract text and tables from [format] files, [specific actions]. Use when working with [format] files or when the user mentions [keywords].
```

**Data Analysis**:
```yaml
description: Analyze [data type], create [outputs], generate [visualizations]. Use when analyzing [data sources] or working with [file types].
```

**Code/Development**:
```yaml
description: Generate [output type] by analyzing [input]. Use when the user asks for help [specific task] or reviewing [code type].
```

**Workflow Automation**:
```yaml
description: Execute [workflow name] following [methodology]. Use when [trigger conditions] or when processing [input types].
```

**Real Examples from Anthropic**:

```yaml
# PDF Skill
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# Excel Skill
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.

# Git Commit Helper
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

### Source URLs
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://code.claude.com/docs/en/skills

### Gaps
- No A/B testing framework for description optimization
- Semantic similarity scoring not exposed to authors
- No feedback mechanism on why a skill wasn't triggered

### Claude usage tips
- This is where most skill authoring failures occur—emphasize importance
- Test descriptions by asking: "Would I know to use this skill from this description?"
- Include file extensions when relevant (.pdf, .xlsx, .docx)
- Avoid overly technical jargon—match user vocabulary

---

## 7. Tool restrictions

**Summary**: Skills can restrict which tools Claude uses via the `allowed-tools` YAML field in Claude Code, or through the main configuration in the Agent SDK. Tool restrictions enable read-only skills, security-sensitive workflows, and scoped automation. Note: `allowed-tools` in SKILL.md only works in Claude Code CLI, not in the SDK.

### Technical details

**Claude Code `allowed-tools` Field**:
```yaml
---
name: safe-file-reader
description: Read files without making changes
allowed-tools: Read, Grep, Glob
---

# Safe File Reader

Use Read, Grep, and Glob for read-only access.
Do not modify any files.
```

**Available Tools for Restriction**:
| Tool | Description |
|------|-------------|
| `Read` | Read file contents |
| `Write` | Create/overwrite files |
| `Edit` | Modify existing files |
| `Bash` | Execute shell commands |
| `Bash(command:*)` | Specific command patterns |
| `Glob` | Find files by pattern |
| `Grep` | Search file contents |
| `WebFetch` | Fetch web content |
| `WebSearch` | Search the web |

**Use Cases for Tool Restrictions**:
| Use Case | Allowed Tools | Rationale |
|----------|---------------|-----------|
| Read-only analysis | `Read, Grep, Glob` | Prevent file modifications |
| Data analysis only | `Read, Bash(python:*)` | Limited to Python execution |
| Documentation | `Read, Write` | No shell access |
| Security review | `Read, Grep, Glob` | No execution capabilities |

**Agent SDK Tool Configuration**:
```python
# SDK: allowed-tools in SKILL.md is IGNORED
# Use allowedTools in query options instead
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],
    allowed_tools=["Skill", "Read", "Grep", "Glob"]  # Restricts all tools
)
```

**Platform Differences**:
| Platform | Tool Restriction Method |
|----------|------------------------|
| Claude Code CLI | `allowed-tools` in SKILL.md frontmatter |
| Claude Agent SDK | `allowedTools` in query options (SKILL.md field ignored) |
| Claude API | No skill-level tool restrictions |
| Claude.ai | No skill-level tool restrictions |

### Source URLs
- https://code.claude.com/docs/en/skills
- https://platform.claude.com/docs/en/agent-sdk/skills

### Gaps
- Behavior when skill restrictions conflict with session restrictions unclear
- MCP tool restriction patterns not documented
- Error handling when restricted tool is requested not specified

### Claude usage tips
- **Important caveat**: `allowed-tools` only works in Claude Code CLI
- For SDK, emphasize using the main `allowedTools` configuration
- Read-only skills are a common pattern—explain the security benefits
- Bash patterns like `Bash(python:*)` allow fine-grained control

---

## 8. Bundled resources

**Summary**: Skills can bundle additional files—instructions, scripts, and resources—that Claude accesses only when needed. This enables comprehensive skill packages without context penalties. Scripts execute deterministically without loading code into context, providing reliable, repeatable operations.

### Technical details

**Three Types of Bundled Content**:

| Type | Purpose | Context Impact | Example |
|------|---------|----------------|---------|
| **Instructions** | Specialized guides, workflows | Loaded when referenced | `FORMS.md`, `REFERENCE.md` |
| **Code** | Executable scripts | Only OUTPUT enters context | `scripts/analyze.py` |
| **Resources** | Reference materials, templates | Loaded when referenced | `schemas/`, `templates/` |

**Instructions Files**:
```
skill/
├── SKILL.md              # Main instructions
├── FORMS.md              # Form-filling guide
├── REFERENCE.md          # API reference
└── examples.md           # Usage examples
```

Referenced in SKILL.md:
```markdown
For form filling, see [FORMS.md](FORMS.md).
For API reference, see [REFERENCE.md](REFERENCE.md).
```

**Executable Scripts**:
```
skill/
├── SKILL.md
└── scripts/
    ├── analyze_form.py   # Analyze PDF form fields
    ├── fill_form.py      # Fill form with values
    └── validate.py       # Validate output
```

Executed from SKILL.md:
```markdown
## Utility Scripts

**analyze_form.py**: Extract form fields from PDF
```bash
python scripts/analyze_form.py input.pdf > fields.json
```

**fill_form.py**: Apply values to PDF form
```bash
python scripts/fill_form.py input.pdf fields.json output.pdf
```
```

**Resource Files**:
```
skill/
├── SKILL.md
└── reference/
    ├── finance.md        # Revenue, billing metrics
    ├── sales.md          # Pipeline, opportunities
    ├── product.md        # Usage analytics
    └── schemas/
        └── database.sql  # Database schema
```

**Best Practices for Scripts**:

1. **Solve, don't punt**: Handle errors explicitly rather than failing and letting Claude figure it out
2. **Document parameters**: Explain all configuration values
3. **Provide validation**: Include scripts that verify outputs
4. **Use feedback loops**: `validate → fix → repeat` patterns improve quality

```python
# GOOD: Handle errors explicitly
def process_file(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File {path} not found, creating default")
        with open(path, 'w') as f:
            f.write('')
        return ''

# BAD: Punt to Claude
def process_file(path):
    return open(path).read()  # Just fails
```

### Source URLs
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

### Gaps
- Maximum file size for individual bundled files not specified
- Binary file handling (images, compiled assets) not documented
- Script execution timeout limits not specified

### Claude usage tips
- Emphasize scripts provide **deterministic execution**—more reliable than generated code
- Scripts save tokens: no code generation, only output enters context
- Keep reference depth to ONE level—don't chain references through multiple files
- For long reference files (100+ lines), include a table of contents

---

## 9. Plugin integration

**Summary**: In Claude Code, skills can be bundled with plugins for distribution through marketplaces. Plugin-bundled skills follow the same SKILL.md format but are stored in the plugin's `skills/` directory. Skills inherit the plugin namespace and are discovered automatically when the plugin is installed.

### Technical details

**Plugin Directory Structure with Skills**:
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── commands/                  # Slash commands
│   └── my-command.md
├── skills/                    # Skills directory
│   ├── pdf-processing/
│   │   ├── SKILL.md
│   │   ├── FORMS.md
│   │   └── scripts/
│   │       └── analyzer.py
│   └── data-analysis/
│       ├── SKILL.md
│       └── reference/
│           └── metrics.md
└── README.md
```

**plugin.json Configuration**:
```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "Plugin with bundled skills",
  "skills": "./skills/"           // Path to skills directory
}
```

**Skill Discovery Priority** (highest to lowest):
1. Enterprise managed settings
2. Personal skills (`~/.claude/skills/`)
3. Project skills (`.claude/skills/`)
4. Plugin skills (from installed plugins)

**Distributing Skills via Plugins**:
1. Create skills in plugin's `skills/` directory
2. Each skill is a subdirectory with SKILL.md
3. Specify skills path in plugin.json
4. Users install plugin; skills are automatically available

**Skills vs Plugin Commands**:
| Aspect | Skills | Commands |
|--------|--------|----------|
| Invocation | Model-invoked | User-invoked (`/plugin:command`) |
| Location | `skills/` directory | `commands/` directory |
| Format | Directory with SKILL.md | Single .md file |
| Namespace | None (global) | Plugin-prefixed |

**Important Notes**:
- Built-in agents (Explore, Plan, Verify) and the Task tool cannot use Skills
- Custom subagents can access skills by specifying them in AGENT.md:
```yaml
# .claude/agents/code-reviewer/AGENT.md
---
name: code-reviewer
description: Review code for quality
skills: pr-review, security-check
---
```

### Source URLs
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/plugins-reference

### Gaps
- Skill naming conflicts between plugins not documented
- Plugin skill update behavior during plugin updates unclear
- Enterprise override of plugin skills not specified

### Claude usage tips
- Plugin skills are discovered automatically—no explicit registration needed
- Skills don't have plugin namespace prefix (unlike commands)
- For team distribution, plugins are the recommended approach
- Individual skills can be shared via git in `.claude/skills/`

---

## 10. Best practices & examples

**Summary**: Effective skills are concise, well-structured, and tested with real usage. Anthropic provides official example skills and extensive authoring guidance. Key patterns include progressive disclosure, feedback loops, template patterns, and evaluation-driven development.

### Technical details

**Core Principles**:

1. **Concise is key**: Claude is already smart—only add context Claude doesn't have
2. **Set appropriate degrees of freedom**: Match specificity to task fragility
3. **Test with all models**: What works for Opus might need more detail for Haiku

**Degrees of Freedom**:
| Level | When to Use | Example |
|-------|-------------|---------|
| High (text instructions) | Multiple valid approaches | "Analyze code structure, check for bugs" |
| Medium (pseudocode/params) | Preferred pattern exists | "Use this template, customize as needed" |
| Low (specific scripts) | Fragile operations | "Run exactly: `python scripts/migrate.py`" |

**Workflow Pattern**:
```markdown
## PDF Form Filling Workflow

Copy this checklist and track progress:

```
- [ ] Step 1: Analyze form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate.py)
- [ ] Step 4: Fill form (run fill_form.py)
- [ ] Step 5: Verify output (run verify.py)
```

**Step 1: Analyze the form**
Run: `python scripts/analyze_form.py input.pdf`
...
```

**Feedback Loop Pattern**:
```markdown
## Document Editing Process

1. Make edits to document
2. **Validate immediately**: `python scripts/validate.py`
3. If validation fails:
   - Review error message
   - Fix issues
   - Run validation again
4. **Only proceed when validation passes**
5. Finalize output
```

**Template Pattern**:
```markdown
## Report Structure

ALWAYS use this exact template:

```markdown
# [Analysis Title]

## Executive Summary
[One-paragraph overview]

## Key Findings
- Finding 1 with data
- Finding 2 with data

## Recommendations
1. Specific recommendation
2. Specific recommendation
```
```

**Examples Pattern**:
```markdown
## Commit Message Format

**Example 1:**
Input: Added user authentication
Output:
```
feat(auth): implement JWT authentication

Add login endpoint and token validation
```

**Example 2:**
Input: Fixed date display bug
Output:
```
fix(reports): correct date formatting

Use UTC timestamps consistently
```
```

**Official Example Skills** (github.com/anthropics/skills):
| Skill | Purpose |
|-------|---------|
| `docx` | Word document creation/editing |
| `pdf` | PDF creation/editing |
| `pptx` | PowerPoint creation/editing |
| `xlsx` | Excel spreadsheet creation/editing |

**Evaluation-Driven Development**:
1. Identify gaps: Run Claude on tasks without skill, document failures
2. Create evaluations: Build 3 scenarios testing those gaps
3. Establish baseline: Measure performance without skill
4. Write minimal instructions: Just enough to pass evaluations
5. Iterate: Execute, compare, refine

### Source URLs
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- https://github.com/anthropics/skills
- https://github.com/anthropics/claude-cookbooks/tree/main/skills

### Gaps
- No hot-reload for skill development
- Unit testing framework for skills not provided
- Performance benchmarking guidance missing

### Claude usage tips
- Start with evaluations BEFORE writing documentation
- Collaborate with Claude to develop skills iteratively
- "Work with Claude A to create skills for Claude B"
- Keep SKILL.md under 500 lines—split if larger

---

## 11. Limitations & constraints

**Summary**: Skills have specific constraints around file sizes, network access, and cross-surface availability. Understanding these limitations helps plan skill deployments effectively. Key constraints include 8MB upload limit for API, no network access in API container, and skills not syncing across surfaces.

### Technical details

**Request Limits**:
| Constraint | Limit |
|------------|-------|
| Maximum skills per request | 8 |
| Maximum skill upload size | 8MB (all files combined) |
| Name field | 64 characters max |
| Description field | 1024 characters max |
| SKILL.md body | 500 lines recommended |

**Environment Constraints by Platform**:

| Platform | Network Access | Package Installation | Notes |
|----------|---------------|---------------------|-------|
| Claude.ai | Varies by settings | Yes (npm, PyPI) | Admin-controlled |
| Claude API | None | None at runtime | Pre-installed packages only |
| Claude Code | Full | Discouraged globally | Same as local machine |
| Agent SDK | Inherited | Inherited | Depends on configuration |

**Cross-Surface Limitations**:
- Skills uploaded to Claude.ai must be separately uploaded to API
- Skills uploaded via API are not available on Claude.ai
- Claude Code skills are filesystem-based, separate from both
- Custom skills do not sync across surfaces

**Sharing Scope**:
| Platform | Sharing Model |
|----------|---------------|
| Claude.ai | Individual user only (no org distribution) |
| Claude API | Workspace-wide |
| Claude Code | Personal (~/.claude/skills/) or project (.claude/skills/) |

**What Skills CANNOT Do**:
- Access network (API container)
- Install packages at runtime (API container)
- Sync automatically across surfaces
- Be managed centrally in Claude.ai (no admin controls)
- Override allowed-tools in SDK (SKILL.md field ignored)

**Security Model**:
- Skills execute in code execution container (VM environment)
- Scripts run with filesystem access and bash commands
- Malicious skills can direct Claude to execute harmful code
- Only install skills from trusted sources
- Audit all bundled files before using untrusted skills

### Source URLs
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- https://platform.claude.com/docs/en/build-with-claude/skills-guide

### Gaps
- Memory limits for skill execution not specified
- Concurrent skill execution limits not documented
- Behavior when skill exceeds size limits not specified

### Claude usage tips
- Emphasize: **skills don't sync across surfaces**—must upload separately
- API container has NO network access—plan accordingly
- Claude.ai doesn't support org-wide skill distribution (yet)
- For sensitive environments, audit skills like you'd audit installed software

---

## 12. agentskills.io ecosystem

**Summary**: agentskills.io is the central hub for the Agent Skills open standard, originally developed by Anthropic and now adopted across the AI ecosystem. The platform provides skill discovery, a partner directory, community contributions, and specification documentation. Major adopters include GitHub, VS Code, OpenAI Codex, Cursor, and many others.

### Technical details

**Platform Components**:
| Component | Description |
|-----------|-------------|
| Skills Directory | Featured skills from partners (Notion, Figma, Atlassian, etc.) |
| Specification | Complete format specification for SKILL.md |
| Reference Library | Validation tools and prompt XML generation |
| Example Skills | Browsable examples on GitHub |

**Ecosystem Adoption**:
- **Claude Products**: Claude.ai, Claude Code, Claude Agent SDK, Claude API
- **IDE Tools**: VS Code, Cursor, Amp
- **Development Platforms**: GitHub, OpenCode, Goose, Letta
- **Other AI**: OpenAI Codex

**Skill Categories**:
| Category | Examples |
|----------|----------|
| Creative & Design | Art generation, brand styling, p5.js |
| Development & Technical | Web app testing, MCP server generation |
| Enterprise & Communication | Brand guidelines, document processing |
| Document Skills | Word, Excel, PowerPoint, PDF |

**Partner Skills Directory**:
Featured professionally-built skills from commercial partners:
- Atlassian, Canva, Cloudflare
- Figma, Notion, Ramp, Sentry

**Community Skills**:
Community-developed skills for:
- Test-driven development
- Socratic design exploration
- Fixing flaky tests
- Multi-layer validation

**Cross-Platform Portability**:
Skills created for one platform work across all compatible agents:
- GitHub Copilot in VS Code
- GitHub Copilot CLI
- GitHub Copilot coding agent
- Claude Code, Claude.ai
- And others in the ecosystem

**Installing Skills in Claude Code**:
```bash
# Register marketplace
/plugin marketplace add anthropics/skills

# Install skill collections
/plugin install document-skills@anthropic-agent-skills
/plugin install example-skills@anthropic-agent-skills
```

### Source URLs
- https://agentskills.io/home
- https://github.com/anthropics/skills
- https://github.com/agentskills/agentskills

### Gaps
- No centralized submission process documented
- Skill verification/certification process unclear
- Community skill quality standards not specified

### Claude usage tips
- agentskills.io is the **ecosystem hub**—not just Anthropic's platform
- Skills are portable across all compatible agents
- The spec is intentionally minimal—"read in a few minutes"
- Partner skills often integrate with corresponding MCP connectors

---

## Consolidated reference

### Complete SKILL.md template

```yaml
---
name: skill-name                              # REQUIRED: max 64 chars, lowercase/numbers/hyphens
description: |                                # REQUIRED: max 1024 chars
  Clear description of what this skill does.
  Include specific capabilities and actions.
  State when Claude should use this skill.
  Add keywords users would naturally mention.
license: MIT                                  # Optional
allowed-tools: Read, Bash(python:*)           # Optional: Claude Code only
model: claude-sonnet-4-5-20250929               # Optional: model override
metadata:                                     # Optional: custom key-value pairs
  version: "1.0.0"
  author: "author-name"
  category: "category"
---

# Skill Name

## Purpose
One-paragraph explanation of what this skill does and why it exists.

## Quick Start
Minimal example to get started quickly.

```python
# Example code
import library
result = library.process("input")
```

## Instructions

### Step 1: [First Step]
Clear, actionable instructions.

### Step 2: [Second Step]
Continue with detailed guidance.

## Advanced Features

**Feature 1**: See [FEATURE1.md](FEATURE1.md) for details
**Feature 2**: See [FEATURE2.md](FEATURE2.md) for details

## Utility Scripts

**analyze.py**: Extract data from input
```bash
python scripts/analyze.py input.file > output.json
```

**validate.py**: Verify output quality
```bash
python scripts/validate.py output.json
```

## Examples

**Example 1:**
Input: "User request example"
Expected: How Claude should respond

**Example 2:**
Input: "Another request"
Expected: Another expected response

## Guidelines
- Important consideration 1
- Important consideration 2
- Common pitfall to avoid

## Requirements
- Required package: `pip install package-name`
- System requirement: Description
```

### Multi-file skill structure

```
complete-skill/
├── SKILL.md                    # Required: main instructions
├── FORMS.md                    # Optional: specialized guide
├── REFERENCE.md                # Optional: API reference
├── examples.md                 # Optional: usage examples
├── LICENSE.txt                 # Optional: license
├── scripts/                    # Optional: executable code
│   ├── analyze.py              # Utility script
│   ├── validate.py             # Validation script
│   └── process.sh              # Shell script
├── reference/                  # Optional: domain-specific docs
│   ├── finance.md
│   ├── sales.md
│   └── schemas/
│       └── database.sql
└── assets/                     # Optional: templates, data
    ├── template.xlsx
    └── config.json
```

### Platform comparison

| Feature | Claude.ai | Claude API | Claude Code | Agent SDK |
|---------|-----------|------------|-------------|-----------|
| Pre-built Skills | Yes | Yes | No | No |
| Custom Skills | Yes (upload) | Yes (API) | Yes (filesystem) | Yes (filesystem) |
| Network Access | Varies | None | Full | Inherited |
| Package Install | Yes | None | Discouraged | Inherited |
| `allowed-tools` | No | No | Yes | No (use config) |
| Sharing | Individual | Workspace | Project/Personal | Per config |
| Skill Limit | Unknown | 8 per request | Unknown | Unknown |

### Troubleshooting checklist

**Skill Not Triggering**:
- [ ] Description is specific with keywords
- [ ] Description includes "Use when..." trigger phrase
- [ ] Keywords match user vocabulary
- [ ] No conflicting skills with similar descriptions

**Skill Won't Load**:
- [ ] File named exactly `SKILL.md` (case-sensitive)
- [ ] Valid YAML frontmatter (no blank lines before `---`)
- [ ] Spaces, not tabs, for indentation
- [ ] `name` field matches directory name
- [ ] Description is non-empty

**SDK Skills Not Found**:
- [ ] `settingSources` includes `"user"` or `"project"`
- [ ] `allowedTools` includes `"Skill"`
- [ ] `cwd` points to directory with `.claude/skills/`
- [ ] SKILL.md exists at expected path

**Dependencies Not Working**:
- [ ] Packages listed in skill description
- [ ] Packages pre-installed (API) or installable (Claude.ai)
- [ ] Scripts have correct shebangs
- [ ] File paths use forward slashes

---

## Conclusion

Agent Skills represent a paradigm shift in how AI agents acquire specialized capabilities. By packaging domain expertise into composable, portable, and efficiently-loaded directories, skills enable Claude to transform from a general-purpose assistant into a domain specialist on-demand.

**Key Takeaways**:

1. **Progressive disclosure** is the core innovation—skills load only what's needed, when it's needed
2. **The description field is critical**—it determines when Claude uses your skill
3. **Scripts provide determinism**—executable code runs reliably without consuming context
4. **Skills are portable**—write once, use across Claude.ai, Claude Code, API, and SDK
5. **The ecosystem is open**—adopted by GitHub, VS Code, OpenAI Codex, and many others

The Agent Skills standard continues to evolve as Anthropic and the broader AI community refine best practices for equipping agents with real-world capabilities.

---

## Sources

### Official Anthropic Documentation
- [Agent Skills Overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Agent Skills Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Skills in Claude Code](https://code.claude.com/docs/en/skills)
- [Skills API Guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide)
- [Skills in Agent SDK](https://platform.claude.com/docs/en/agent-sdk/skills)
- [Engineering Blog: Equipping Agents](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Skills Announcement](https://claude.com/blog/skills)

### GitHub Repositories
- [anthropics/skills](https://github.com/anthropics/skills) - Official skills repository
- [Skills Cookbook](https://github.com/anthropics/claude-cookbooks/tree/main/skills) - Example skills

### Ecosystem
- [agentskills.io](https://agentskills.io) - Open standard hub
- [VS Code Agent Skills](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
- [OpenAI Codex Skills](https://developers.openai.com/codex/skills/)
