---
name: generate-hooks
description: Generate hooks native to the target tool's runtime — Claude Code shell hooks, Antigravity/Gemini event hooks, Hermes Python register(ctx), Codex hooks.json, or Pi TypeScript pi.on(). Detects the active tool and emits the correct format. Invoked by scaffold or standalone via /generate-hooks.
---

# Generate Hooks

Produce hooks in the format native to the active AI coding tool. The workflow is the product — hooks enforce rules automatically as reflexes.

## Role in the System

Hooks are **reflexes** — automatic responses to tool events. They enforce rules without requiring the LLM's cooperation. Unlike skills (on-demand), hooks fire every time their trigger condition is met.

## Tool Detection

Detect which tool is running and emit native hook format:

| Signal | Tool | Hook Format |
|--------|------|-------------|
| `.claude-plugin/` exists or `CLAUDE_CODE` env | **Claude Code** | Shell commands in `.claude/settings.json` |
| `plugin.json` at root with gemini fields | **Antigravity/Gemini** | Shell commands in `.claude/settings.json` (shared format) |
| `plugin.yaml` + `__init__.py` exist | **Hermes** | Python callbacks via `register(ctx)` |
| `.codex-plugin/` exists or `CODEX` env | **Codex** | Shell commands in `hooks.json` |
| `package.json` with `"pi"` key | **Pi** | TypeScript `pi.on()` in extension file |

When the tool cannot be detected, default to Claude Code format and warn.

## Cross-Tool Event Mapping

Use this table to translate hook intent across tools:

| Intent | Claude Code | Antigravity/Gemini | Hermes | Codex | Pi |
|--------|------------|-------------------|--------|-------|-----|
| Before tool runs | `PreToolUse` | `BeforeTool` / `PreToolUse` | `pre_tool_call` | `PreToolUse` | `tool_execution_start` |
| After tool runs | `PostToolUse` | `PostToolUse` | `post_tool_call` | `PostToolUse` | `tool_result` |
| Session starts | _(none)_ | `SessionStart` | `on_session_start` | `SessionStart` | `session_start` |
| Session ends / turn done | `Stop` | `SessionEnd` | `on_session_end` | `Stop` | `session_shutdown` |
| Before LLM call | _(none)_ | `BeforeAgent` | `pre_llm_call` | _(none)_ | `before_provider_request` |
| After LLM call | _(none)_ | `AfterAgent` | `post_llm_call` | _(none)_ | `after_provider_response` |
| User submits prompt | _(none)_ | _(none)_ | _(none)_ | `UserPromptSubmit` | `input` |
| Transform output | _(none)_ | _(none)_ | `transform_llm_output` | _(none)_ | `message_update` |

## Native Output Formats

### Claude Code / Antigravity (shell commands)

Target: `.claude/settings.json` (team) or `.claude/settings.local.json` (personal)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "prettier --write $FILE_PATH"
      }
    ]
  }
}
```

Matcher patterns: `Write|Edit`, `Bash`, `Read`, specific tool names.

### Hermes (Python callbacks)

Target: project's `__init__.py` or standalone `hooks.py`

```python
def register(ctx):
    ctx.register_hook("post_tool_call", format_on_edit)
    ctx.register_hook("on_session_end", run_final_checks)

def format_on_edit(event):
    if event.tool_name in ("Write", "Edit"):
        import subprocess
        subprocess.run(["prettier", "--write", event.file_path])

def run_final_checks(event):
    import subprocess
    subprocess.run(["npm", "test"])
```

### Codex (hooks.json)

Target: project's `hooks.json`

```json
{
  "hooks": [
    {
      "event": "PostToolUse",
      "matcher": "Write|Edit",
      "command": "prettier --write $FILE_PATH"
    }
  ]
}
```

### Pi (TypeScript extension)

Target: project's `pi/extensions/hooks.ts`

```typescript
import type { ExtensionAPI } from "pi";

export default function projectHooks(pi: ExtensionAPI) {
  pi.on("tool_result", (event) => {
    if (["Write", "Edit"].includes(event.toolName)) {
      pi.exec(`prettier --write ${event.filePath}`);
    }
  });

  pi.on("session_shutdown", (_event) => {
    pi.exec("npm test");
  });
}
```

## Input

Read `.claude/scaffold-decisions.md` if it exists — primary source for resolved grill decisions. Map decisions to hooks using the intent table above.

## Hook Design from Workflow Decisions

Map grill decisions to hooks by **intent**, then translate to the target tool's native event:

| Decision Pattern | Intent | Example |
|-----------------|--------|---------|
| "Format after every edit" | After tool runs + file matcher | PostToolUse/Write\|Edit → formatter |
| "Lint changed files" | After tool runs + file matcher | PostToolUse/Write\|Edit → linter |
| "Type check before review" | Session ends | Stop → typecheck |
| "Notify when blocked" | Session ends | Stop → notification |
| "Validate before tool" | Before tool runs | PreToolUse → validator |

## What Hooks CANNOT Do (Any Tool)

- **Filter Bash by command content.** No tool's matcher can see what shell command runs. "Before git commit" requires a git pre-commit hook, not a tool hook.
- **Access conversation context.** Hooks are deterministic — shell commands (Claude Code/Antigravity/Codex) or event callbacks (Hermes/Pi).
- **Be skipped by the LLM.** That's the point.

## Target File Selection

| Tool | Team-shared | Personal |
|------|------------|----------|
| Claude Code | `.claude/settings.json` | `.claude/settings.local.json` |
| Antigravity | `.claude/settings.json` | `.claude/settings.local.json` |
| Hermes | `__init__.py` | _(not supported)_ |
| Codex | `hooks.json` | _(not supported)_ |
| Pi | `pi/extensions/hooks.ts` | _(not supported)_ |

## Generation Rules

- Detect the active tool first — never assume Claude Code
- Test the command locally before writing the hook (pipe-test with sample input)
- Verify the formatter/linter/tool exists in the project
- Use `$FILE_PATH` for shell-based hooks, `event.file_path`/`event.filePath` for callback-based
- Keep commands fast — hooks run on every trigger
- For shell hooks: validate resulting JSON with `jq -e`
- For Python hooks: validate syntax with `python -c "import ast; ast.parse(open('file').read())"`
- For TypeScript hooks: validate with `npx tsc --noEmit` if available

## Multi-Tool Generation

When `--all-tools` is passed, generate hooks for ALL detected tools simultaneously. Emit each format to its native target file. This enables projects that support multiple AI coding tools to share the same enforcement logic.

## Upstream Dependencies

When invoked standalone, check for upstream primitives:

- **Rules** (`.claude/rules/`): If empty, warn: "No rules found. Hooks enforce rules — consider running `/generate-rules` first."
- **CLAUDE.md**: If missing, warn similarly.

Informational, not blocking.

## Standalone Invocation

`/generate-hooks`

`$ARGUMENTS`:
- `--format-only` — Generate only formatter hooks
- `--personal` — Target personal/local config
- `--quick-grill` — Abbreviated interrogation (3-5 questions)
- `--tool=claude|antigravity|hermes|codex|pi` — Force specific tool output (overrides detection)
- `--all-tools` — Generate hooks for all detected tool manifests
