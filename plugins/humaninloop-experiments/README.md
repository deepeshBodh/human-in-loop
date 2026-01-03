# HumanInLoop Experiments Plugin

Experimental plugins following the ADR-005 decoupled agents architecture. This plugin serves as a sandbox for testing new agent patterns, artifact chains, and workflow designs before promoting them to production plugins.

## Architecture (ADR-005)

This plugin implements the **Decoupled Agents Architecture**:

1. **Agents are pure domain experts** - They have domain knowledge, not workflow knowledge
2. **Supervisors communicate via natural language** - No rigid schemas or protocols
3. **Artifacts are self-describing** - Agents read their input from artifacts, not supervisor prompts
4. **Artifact chain** - Each agent's output becomes the next agent's input

```
ARTIFACT CHAIN

scaffold.md --> result.md --> analysis.md
     |              |             |
     v              v             v
experiment-   experiment-   experiment-
  runner       analyzer      reporter
```

## Installation

```bash
claude-code plugins add humaninloop-experiments
```

## Usage

### Run an Experiment

```
/humaninloop-experiments:run <experiment description>
```

The command will:
1. Create a scaffold artifact in `.humaninloop/experiments/`
2. Invoke the experiment-runner agent
3. Iterate on clarifications if needed
4. Generate experiment results

### Example

```
/humaninloop-experiments:run Test the new artifact chain pattern for spec writing
```

## Plugin Structure

```
humaninloop-experiments/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── experiment-runner.md      # Domain expert for running experiments
├── commands/
│   └── run.md                    # Supervisor command (owns the loop)
├── skills/
│   └── experiment-design/        # Skill for designing experiments
│       └── SKILL.md
├── templates/
│   └── experiment-scaffold.md    # Template for experiment scaffolds
└── README.md
```

## Decoupled Agent Pattern

### Supervisor (commands/run.md)

The supervisor:
- Creates the scaffold artifact
- Spawns the agent with a simple prompt
- Parses structured prose output
- Updates workflow state
- Owns the iteration loop

### Agent (agents/experiment-runner.md)

The agent:
- Reads context from the scaffold artifact
- Applies domain expertise (experiment design)
- Writes results to output artifact
- Reports back with structured prose
- Has NO workflow knowledge

### Communication Flow

```
Supervisor --> Agent:
  "Work on the experiment at .humaninloop/experiments/exp-001/
   Read scaffold.md for context."

Agent --> Supervisor:
  ## What I Created
  [Summary of experiment results]

  ## Clarifications Needed
  [Questions requiring user input]

  ## Assumptions Made
  [Decisions made when ambiguous]
```

## Creating New Experiments

Use this plugin to prototype:

- New agent patterns
- Novel artifact chain designs
- Alternative supervisor strategies
- Skill combinations
- Cross-plugin workflows

When an experiment proves successful, promote it to a production plugin.

## Output Location

```
.humaninloop/
└── experiments/
    └── exp-<timestamp>/
        ├── scaffold.md    # Initial experiment setup
        └── result.md      # Experiment outcomes
```

## License

MIT License - Copyright (c) HumanInLoop (humaninloop.dev)
