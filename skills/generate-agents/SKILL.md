---
name: generate-agents
description: Generate .claude/agents/ definitions that serve as specialist team members in the workflow system. Each agent has a focused role, constrained tools, and clear responsibilities. Invoked by scaffold or standalone via /generate-agents.
---

# Generate Agents

Produce `.claude/agents/<name>.md` files — specialist definitions for the workflow system.

## Role in the System

Agents are **specialists** — team members with focused expertise. Each agent has:
- A clear role in the workflow
- Constrained tool access (only what it needs)
- Specific instructions for its domain
- A model selection matched to its task complexity

## Input

Read `.claude/scaffold-decisions.md` if it exists — this is the primary source for resolved grill decisions. Map workflow roles from decisions to agent definitions.

## Agent Definition Format

```yaml
---
name: <agent-name>
description: <what this agent does — when the system should invoke it>
model: <haiku|sonnet|opus — match to task complexity>
tools:
  - Read
  - Grep
  - Glob
  # Only tools this agent needs
---

# <Agent Name>

[Instructions for this agent's specific domain]

## When to Invoke

[Conditions that trigger this agent]

## Constraints

[What this agent must NOT do]
```

## Agent Design from Workflow Decisions

Map workflow roles to agents:

| Workflow Role | Agent | Model | Tools |
|--------------|-------|-------|-------|
| Code review before merge | `code-reviewer` | sonnet | Read, Grep, Glob |
| Security audit | `security-reviewer` | opus | Read, Grep, Glob, Bash |
| Test writing | `test-writer` | sonnet | Read, Write, Edit, Bash |
| Documentation | `doc-updater` | haiku | Read, Write, Edit, Glob |
| Build error triage | `build-fixer` | sonnet | Read, Edit, Bash, Grep |
| Deployment verification | `deploy-verifier` | sonnet | Read, Bash, Grep |

## Agent Design Rules

- **Minimal tools.** Only grant tools the agent needs. Read-only agents don't get Write/Edit.
- **Clear boundaries.** Each agent has one job. Don't make Swiss-army agents.
- **Model matching.** Haiku for simple lookups, Sonnet for implementation, Opus for deep reasoning.
- **Composable.** Agents should work alone OR as part of a workflow/team.
- **Instruction density.** Agent instructions should be specific to their domain — don't repeat CLAUDE.md content.

## Agent Interaction Patterns

Agents participate in workflows through:

1. **Direct invocation** — User or orchestrator spawns the agent for a task
2. **Team coordination** — TeamCreate for 3+ related agents with cross-pollination
3. **Pipeline stages** — Workflow scripts invoke agents sequentially
4. **Parallel analysis** — Multiple agents analyze the same change from different angles

## Upstream Dependencies

When invoked standalone, check for upstream primitives:

- **Skills** (`.claude/skills/`): If empty, warn: "No skills found. Agents execute skills — consider running `/generate-skills` first."
- **Rules** (`.claude/rules/`): If empty, warn: "No rules found. Agents follow rules — consider running `/generate-rules` first."

Informational, not blocking. Agents can reference skills/rules that will be created later.

## Don't Create Agents For

- Tasks that are a single command (use a hook or alias)
- Tasks that need no specialization (use general Claude)
- Tasks already covered by built-in agents (explore, plan, etc.)

## Standalone Invocation

`/generate-agents`

`$ARGUMENTS`:
- `--list` — List candidate agents without generating
- `--name=reviewer,tester` — Generate only specified agents
- `--quick-grill` — Abbreviated interrogation (3-5 questions)
