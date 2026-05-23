---
name: generate-agents
description: Generate agent definitions native to the target tool's runtime — Claude Code .claude/agents/*.md, Antigravity/Gemini agents with kind field, Hermes plugin-provided agents via register(ctx), Codex agent definitions, or Pi agent configs. Detects the active tool and emits the correct format. Invoked by scaffold or standalone via /generate-agents.
---

# Generate Agents

Produce agent definitions in the format native to the active AI coding tool.

## Role in the System

Agents are **specialists** — team members with focused expertise. Each agent has:
- A clear role in the workflow
- Constrained tool access (only what it needs)
- Specific instructions for its domain
- A model selection matched to its task complexity

## Tool Detection

Detect which tool is running and emit native agent format:

| Signal | Tool | Agent Format |
|--------|------|-------------|
| `.claude-plugin/` exists or `CLAUDE_CODE` env | **Claude Code** | `.claude/agents/<name>.md` with YAML frontmatter |
| `plugin.json` at root with gemini fields | **Antigravity/Gemini** | `agents/<name>.md` with `kind` field in frontmatter |
| `plugin.yaml` + `__init__.py` exist | **Hermes** | Python `ctx.register_agent()` in `__init__.py` |
| `.codex-plugin/` exists or `CODEX` env | **Codex** | `.agents/<name>.md` with YAML frontmatter |
| `package.json` with `"pi"` key | **Pi** | `pi/agents/<name>.md` or TypeScript agent config |

When the tool cannot be detected, default to Claude Code format and warn.

## Native Output Formats

### Claude Code (canonical)

Path: `.claude/agents/<name>.md`

```yaml
---
name: <agent-name>
description: <what this agent does — when the system should invoke it>
model: <haiku|sonnet|opus>
tools:
  - Read
  - Grep
  - Glob
---

# <Agent Name>

[Instructions for this agent's specific domain]

## When to Invoke

[Conditions that trigger this agent]

## Constraints

[What this agent must NOT do]
```

### Antigravity / Gemini

Path: `agents/<name>.md`

```yaml
---
name: <agent-name>
description: <what this agent does>
kind: <reviewer|builder|researcher|analyst>
model: <gemini-2.5-flash|gemini-2.5-pro>
tools:
  - Read
  - Grep
  - Glob
---

# <Agent Name>

[Instructions]
```

Key difference: Antigravity uses `kind` field for agent categorization and Gemini model names.

### Hermes (Python)

Agents registered via `ctx.register_agent()` in `__init__.py`:

```python
def register(ctx):
    ctx.register_agent(
        name="code-reviewer",
        description="Reviews code for quality and security",
        instructions="You are a code reviewer. Focus on...",
        model="sonnet",
        tools=["Read", "Grep", "Glob"],
    )
```

### Codex

Path: `.agents/<name>.md`

```yaml
---
name: <agent-name>
description: <what this agent does>
model: <gpt-4.1|o3|o4-mini>
tools:
  - Read
  - Grep
  - Glob
---

# <Agent Name>

[Instructions]
```

Key difference: Codex uses OpenAI model names.

### Pi

Path: `pi/agents/<name>.md`

```yaml
---
name: <agent-name>
description: <what this agent does>
model: <haiku|sonnet|opus>
tools:
  - Read
  - Grep
  - Glob
---

# <Agent Name>

[Instructions]
```

Pi shares Claude Code's model names (Anthropic provider).

## Cross-Tool Model Mapping

When translating agents between tools, map models by capability tier:

| Tier | Claude Code | Antigravity/Gemini | Hermes | Codex | Pi |
|------|-----------|-------------------|--------|-------|-----|
| Fast/cheap | haiku | gemini-2.5-flash | haiku | o4-mini | haiku |
| Balanced | sonnet | gemini-2.5-flash | sonnet | gpt-4.1 | sonnet |
| Deep reasoning | opus | gemini-2.5-pro | opus | o3 | opus |

## Input

Read `.claude/scaffold-decisions.md` if it exists — primary source for resolved grill decisions. Map workflow roles from decisions to agent definitions.

## Agent Design from Workflow Decisions

Map workflow roles to agents:

| Workflow Role | Agent | Tier | Tools |
|--------------|-------|------|-------|
| Code review | `code-reviewer` | Balanced | Read, Grep, Glob |
| Security audit | `security-reviewer` | Deep | Read, Grep, Glob, Bash |
| Test writing | `test-writer` | Balanced | Read, Write, Edit, Bash |
| Documentation | `doc-updater` | Fast | Read, Write, Edit, Glob |
| Build triage | `build-fixer` | Balanced | Read, Edit, Bash, Grep |
| Deploy verify | `deploy-verifier` | Balanced | Read, Bash, Grep |

## Agent Design Rules

- **Minimal tools.** Only grant tools the agent needs. Read-only agents don't get Write/Edit.
- **Clear boundaries.** Each agent has one job.
- **Model matching.** Map to the correct tier, then translate to the target tool's model names.
- **Composable.** Agents should work alone OR as part of a workflow/team.
- **Instruction density.** Specific to domain — don't repeat CLAUDE.md content.

## Multi-Tool Generation

When `--all-tools` is passed, generate agents for ALL detected tools simultaneously. Emit each format to its native path. Model names are auto-translated using the cross-tool mapping table.

## Upstream Dependencies

When invoked standalone, check for upstream primitives:

- **Skills** (`.claude/skills/`): If empty, warn: "No skills found. Agents execute skills — consider running `/generate-skills` first."
- **Rules** (`.claude/rules/`): If empty, warn: "No rules found. Agents follow rules — consider running `/generate-rules` first."

Informational, not blocking.

## Don't Create Agents For

- Tasks that are a single command (use a hook)
- Tasks that need no specialization (use general LLM)
- Tasks already covered by built-in agents

## Standalone Invocation

`/generate-agents`

`$ARGUMENTS`:
- `--list` — List candidate agents without generating
- `--name=reviewer,tester` — Generate only specified agents
- `--quick-grill` — Abbreviated interrogation (3-5 questions)
- `--tool=claude|antigravity|hermes|codex|pi` — Force specific tool output (overrides detection)
- `--all-tools` — Generate agents for all detected tool manifests
