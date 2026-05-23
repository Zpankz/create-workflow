---
name: generate-hooks
description: Generate hooks native to the target tool's runtime — shell hooks, Python register(ctx), TypeScript pi.on(), hookify rules, or quality tool integrations (ruff, pyright, eslint, pytest). Detects the active tool and emits the correct format. Invoked by scaffold or standalone via /generate-hooks.
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

## Quality Tool Hooks

### Common Quality Patterns

Map quality tools to hook events. These are the most frequently generated hooks:

| Quality Tool | Event | Matcher | Command | When |
|-------------|-------|---------|---------|------|
| **ruff** (Python lint+format) | `PostToolUse` | `Write\|Edit` | `ruff check --fix "$CLAUDE_FILE_PATH" && ruff format "$CLAUDE_FILE_PATH"` | After every Python file edit |
| **pyright** (Python types) | `Stop` | _(none)_ | `pyright --pythonpath .venv/bin/python .` | End of every turn |
| **pytest** | `Stop` | _(none)_ | `python -m pytest tests/ --tb=short -q` | End of every turn |
| **eslint** | `PostToolUse` | `Write\|Edit` | `npx eslint --fix "$CLAUDE_FILE_PATH"` | After every JS/TS file edit |
| **prettier** | `PostToolUse` | `Write\|Edit` | `npx prettier --write "$CLAUDE_FILE_PATH"` | After every file edit |
| **biome** | `PostToolUse` | `Write\|Edit` | `npx biome check --write "$CLAUDE_FILE_PATH"` | After every file edit |
| **black** (Python format) | `PostToolUse` | `Write\|Edit` | `black "$CLAUDE_FILE_PATH"` | After every Python file edit |
| **mypy** (Python types) | `Stop` | _(none)_ | `mypy .` | End of every turn |
| **tsc** (TypeScript) | `Stop` | _(none)_ | `npx tsc --noEmit` | End of every turn |
| **cargo clippy** (Rust) | `PostToolUse` | `Write\|Edit` | `cargo clippy --fix --allow-dirty` | After every Rust file edit |
| **go vet** | `Stop` | _(none)_ | `go vet ./...` | End of every turn |
| **secret scan** | `Stop` | _(none)_ | `grep -rn "sk-\|AKIA\|password=" --include="*.py" . \|\| true` | End of every turn |

### Detection and Auto-Configuration

When generating hooks, scan the project for installed quality tools:

```bash
# Python
which ruff && echo "ruff"
which pyright && echo "pyright"
which black && echo "black"
which mypy && echo "mypy"
python -m pytest --version 2>/dev/null && echo "pytest"

# JavaScript/TypeScript
[ -f node_modules/.bin/eslint ] && echo "eslint"
[ -f node_modules/.bin/prettier ] && echo "prettier"
[ -f node_modules/.bin/biome ] && echo "biome"
[ -f node_modules/.bin/tsc ] && echo "tsc"

# Rust
which cargo && echo "cargo"

# Go
which go && echo "go"
```

For each detected tool, generate the corresponding hook entry. Group by event type: all `PostToolUse/Write|Edit` hooks together, all `Stop` hooks together.

### Hook Ordering

When multiple quality tools run on the same event:

1. **PostToolUse**: formatter first, then linter (format → lint, not lint → format)
2. **Stop**: type checker first, then tests (types catch errors faster than test runs)

## Hookify Integration

When the `hookify` plugin is installed (check for `.claude/plugins/cache/hookify/` or `/hookify` skill availability), generate **hookify rules** alongside or instead of raw hooks for pattern-based enforcement.

### When to Use Hookify vs Raw Hooks

| Use Case | Format | Reason |
|----------|--------|--------|
| Run a CLI tool (ruff, pytest, pyright) | **Raw hook** | Deterministic shell command, no pattern matching needed |
| Warn about code patterns (console.log, hardcoded secrets) | **Hookify rule** | Pattern matching on file content |
| Block behaviors (rm -rf, force push) | **Hookify rule** | Transcript/command pattern matching |
| Enforce test coverage before stop | **Hookify rule** | Transcript analysis (did tests run?) |
| Format on every edit | **Raw hook** | Fast shell command, no analysis |

### Hookify Rule Format

Write to `.claude/hookify.<rule-name>.local.md`:

```markdown
---
name: <rule-name>
enabled: true
event: file|stop|tool
pattern: <regex>  # for file/tool events
action: warn|block
conditions:        # for stop events
  - field: transcript
    operator: contains|not_contains
    pattern: <regex>
---

**Message Title**

Explanation of why this rule exists and what to do about it.
```

### Common Hookify Rules to Generate

| Rule | Event | Action | Pattern |
|------|-------|--------|---------|
| Warn on console.log | `file` | `warn` | `console\.log\(` |
| Warn on hardcoded secrets | `file` | `warn` | `sk-[a-zA-Z0-9]{20,}\|AKIA[A-Z0-9]{16}` |
| Block rm -rf | `tool` | `block` | `rm\s+-rf\s+/` |
| Block force push | `tool` | `block` | `git\s+push\s+.*--force` |
| Require tests before stop | `stop` | `block` | condition: transcript not_contains `pytest\|npm test\|cargo test` |
| Warn on TODO in code | `file` | `warn` | `TODO\|FIXME\|HACK` |
| Warn on Any type (Python) | `file` | `warn` | `:\s*Any[^a-zA-Z]` |
| Warn on sync I/O in async | `file` | `warn` | `def\s+(?!async\s).*(?:open\|read\|write)\(` |

### Hybrid Generation

When hookify is available, generate BOTH:
1. **Raw hooks** in settings.json for CLI tool execution (ruff, pyright, pytest)
2. **Hookify rules** for pattern-based warnings and blocks

This gives the best of both worlds: deterministic CLI enforcement via hooks + intelligent pattern matching via hookify.

## Native Output Formats

### Claude Code / Antigravity (shell commands)

Target: `.claude/settings.json` (team) or `.claude/settings.local.json` (personal)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "ruff check --fix \"$CLAUDE_FILE_PATH\" 2>/dev/null && ruff format \"$CLAUDE_FILE_PATH\" 2>/dev/null || true"
          },
          {
            "type": "command",
            "command": "pyright \"$CLAUDE_FILE_PATH\" 2>&1 | tail -3"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "pyright --pythonpath .venv/bin/python . 2>&1 | tail -5"
          },
          {
            "type": "command",
            "command": "python -m pytest tests/ --tb=short -q 2>&1 | tail -5"
          }
        ]
      }
    ]
  }
}
```

### Hermes (Python callbacks)

Target: project's `__init__.py` or standalone `hooks.py`

```python
def register(ctx):
    ctx.register_hook("post_tool_call", format_on_edit)
    ctx.register_hook("on_session_end", run_quality_gates)

def format_on_edit(event):
    if event.tool_name in ("Write", "Edit"):
        import subprocess
        subprocess.run(["ruff", "check", "--fix", event.file_path], capture_output=True)
        subprocess.run(["ruff", "format", event.file_path], capture_output=True)

def run_quality_gates(event):
    import subprocess
    subprocess.run(["pyright", "."], capture_output=True)
    subprocess.run(["python", "-m", "pytest", "tests/", "--tb=short", "-q"])
```

### Codex (hooks.json)

Target: project's `hooks.json`

```json
{
  "hooks": [
    {
      "event": "PostToolUse",
      "matcher": "Write|Edit",
      "command": "ruff check --fix \"$CLAUDE_FILE_PATH\" && ruff format \"$CLAUDE_FILE_PATH\""
    },
    {
      "event": "Stop",
      "command": "pyright . 2>&1 | tail -5 && python -m pytest tests/ --tb=short -q 2>&1 | tail -5"
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
      pi.exec(`ruff check --fix "${event.filePath}" && ruff format "${event.filePath}"`);
    }
  });

  pi.on("session_shutdown", (_event) => {
    pi.exec("pyright .");
    pi.exec("python -m pytest tests/ --tb=short -q");
  });
}
```

## Input

Read `.claude/scaffold-decisions.md` if it exists — primary source for resolved grill decisions. Map decisions to hooks using the intent table above.

## Hook Design from Workflow Decisions

Map grill decisions to hooks by **intent**, then translate to the target tool's native event:

| Decision Pattern | Intent | Hook Type |
|-----------------|--------|-----------|
| "Format after every edit" | After tool + file matcher | **Raw hook** → formatter CLI |
| "Lint changed files" | After tool + file matcher | **Raw hook** → linter CLI |
| "Type check on stop" | Session ends | **Raw hook** → type checker CLI |
| "Run tests on stop" | Session ends | **Raw hook** → test runner CLI |
| "Warn on console.log" | File content pattern | **Hookify rule** → warn |
| "Block force push" | Command pattern | **Hookify rule** → block |
| "Enforce tests ran" | Transcript analysis | **Hookify rule** → block on stop |

## What Hooks CANNOT Do (Any Tool)

- **Filter Bash by command content.** No tool's matcher can see what shell command runs. "Before git commit" requires a git pre-commit hook, not a tool hook.
- **Access conversation context.** Hooks are deterministic — shell commands (Claude Code/Antigravity/Codex) or event callbacks (Hermes/Pi). Hookify rules CAN match transcripts.
- **Be skipped by the LLM.** That's the point.

## Target File Selection

| Tool | Team-shared | Personal |
|------|------------|----------|
| Claude Code | `.claude/settings.json` | `.claude/settings.local.json` |
| Antigravity | `.claude/settings.json` | `.claude/settings.local.json` |
| Hermes | `__init__.py` | _(not supported)_ |
| Codex | `hooks.json` | _(not supported)_ |
| Pi | `pi/extensions/hooks.ts` | _(not supported)_ |
| Hookify | `.claude/hookify.<name>.local.md` | Same (always local) |

## Generation Rules

- Detect installed quality tools first — only generate hooks for tools that exist
- Test the command locally before writing the hook (pipe-test with sample input)
- Use `$CLAUDE_FILE_PATH` (Claude Code) or `$FILE_PATH` for shell-based hooks
- Keep commands fast — hooks run on every trigger
- Pipe output through `tail -N` for Stop hooks to keep feedback concise
- Add `|| true` to PostToolUse formatters so non-matching files don't block
- For shell hooks: validate resulting JSON with `jq -e`
- For Python hooks: validate syntax with `python -c "import ast; ast.parse(open('file').read())"`
- For TypeScript hooks: validate with `npx tsc --noEmit` if available

## Multi-Tool Generation

When `--all-tools` is passed, generate hooks for ALL detected tools simultaneously.

## Standalone Invocation

`/generate-hooks`

`$ARGUMENTS`:
- `--format-only` — Generate only formatter hooks
- `--quality` — Auto-detect and generate all quality tool hooks (ruff, pyright, pytest, eslint, etc.)
- `--hookify` — Generate hookify rules instead of/alongside raw hooks
- `--personal` — Target personal/local config
- `--quick-grill` — Abbreviated interrogation (3-5 questions)
- `--tool=claude|antigravity|hermes|codex|pi` — Force specific tool output
- `--all-tools` — Generate hooks for all detected tool manifests
