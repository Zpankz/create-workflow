---
name: generate-hooks
description: Generate Claude Code hooks (PreToolUse, PostToolUse, Stop) that serve as automatic reflexes in the workflow system. Hooks enforce rules, trigger formatting, validate state, and gate destructive actions. Invoked by scaffold or standalone via /generate-hooks.
---

# Generate Hooks

Produce hooks in `.claude/settings.json` (team-shared) or `.claude/settings.local.json` (personal).

## Role in the System

Hooks are **reflexes** — automatic responses to Claude Code events. They enforce rules without requiring Claude's cooperation. Unlike skills (on-demand), hooks fire every time their trigger condition is met.

## Input

Read `.claude/scaffold-decisions.md` if it exists — this is the primary source for resolved grill decisions. Map decisions to hooks using the table below.

## Hook Types

| Event | Fires When | Use For |
|-------|-----------|---------|
| `PreToolUse` | Before a tool runs | Validate, gate, modify parameters |
| `PostToolUse` | After a tool runs | Format, lint, verify output |
| `Stop` | End of every turn | Final checks, summaries, notifications |

## Matcher Patterns

Matchers filter which tool triggers the hook:

```json
{
  "event": "PostToolUse",
  "matcher": "Write|Edit",
  "command": "prettier --write $FILE_PATH"
}
```

Common matchers:
- `Write|Edit` — file modification events
- `Bash` — shell command execution (cannot filter by command content)
- `Read` — file reads
- Specific tool names

## Hook Design from Workflow Decisions

Map grill decisions to hooks:

| Decision Pattern | Hook |
|-----------------|------|
| "Format after every edit" | PostToolUse/Write\|Edit → formatter |
| "Lint changed files" | PostToolUse/Write\|Edit → linter on $FILE_PATH |
| "Type check before review" | Stop → typecheck command |
| "Notify when blocked" | Stop → notification script |
| "Validate imports" | PostToolUse/Write\|Edit → import validator |

## What Hooks CANNOT Do

- **Filter Bash by command content.** Matchers can't see what Bash command runs. "Before git commit" is NOT a hook — use a git pre-commit hook instead.
- **Access conversation context.** Hooks are shell commands, not Claude instructions.
- **Be skipped by Claude.** That's the point — they're deterministic.

## Target File Selection

- Team-shared hooks → `.claude/settings.json` (committed to repo)
- Personal hooks → `.claude/settings.local.json` (gitignored)

Default to team-shared unless the hook is personal preference (e.g., notification style).

## Generation Rules

- Test the command locally before writing the hook (pipe-test with sample input)
- Verify the formatter/linter/tool exists in the project
- Use `$FILE_PATH` for the affected file path
- Keep commands fast — hooks run on every trigger
- Validate resulting JSON with `jq -e`

## Upstream Dependencies

When invoked standalone, check for upstream primitives before generating:

- **Rules** (`.claude/rules/`): If empty or missing, warn: "No rules found. Hooks enforce rules — consider running `/generate-rules` first." Offer to continue anyway or run rules first.
- **CLAUDE.md**: If missing, warn similarly. Hooks implicitly enforce CLAUDE.md standards.

This check is informational, not blocking. Hooks can be generated without rules, but the user should know the enforcement target doesn't exist yet.

## Standalone Invocation

`/generate-hooks`

`$ARGUMENTS`:
- `--format-only` — Generate only formatter hooks
- `--personal` — Target settings.local.json
- `--quick-grill` — Abbreviated interrogation (3-5 questions)
