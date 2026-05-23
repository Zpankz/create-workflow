---
name: generate-tools
description: Generate tool configurations across all categories — MCP servers, CLI commands, internal code tools, and custom scripts. Maps the project's full tool surface for agents, skills, and workflows.
---

# Generate Tools

Map and configure the project's complete tool surface — everything agents, skills, and workflows can interact with.

## Role in the System

Tools are **instruments** — they extend the system's reach. Some are external (MCP servers, CLI commands), some are internal (project functions and classes that act as callable interfaces). The tool inventory tells agents what they can use and tells workflows what to orchestrate.

```
Tools (instruments)
├── MCP Servers     — external service connectors (APIs, databases, search)
├── CLI Commands    — system binaries and project scripts (ruff, pytest, opensrc)
├── Internal Tools  — project-native functions/classes (dispatch(), register_hook())
└── Custom Scripts  — project-specific automation (install.sh, deploy.sh)
```

## Input

Read `.claude/scaffold-decisions.md` if it exists. Scan the project for tool surfaces: function registries, schema definitions, CLI entry points, MCP configs, and scripts.

## Tool Categories

### 1. MCP Servers

Configure in `.mcp.json` or `.claude/settings.json`:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["-y", "@package/mcp-server"],
      "env": {
        "API_KEY": "env:SERVICE_API_KEY"
      }
    }
  }
}
```

Common patterns: database access, API integrations, search/knowledge, file processing.

### 2. CLI Commands

System and project-local commands that agents and skills invoke via Bash:

```markdown
## CLI Tool Inventory

| Command | Category | Purpose | Installed |
|---------|----------|---------|-----------|
| `ruff check --fix . && ruff format .` | Quality | Lint + format Python | Yes |
| `pyright` | Quality | Static type checking | Yes |
| `pytest --cov` | Testing | Run tests with coverage | Yes |
| `opensrc path pypi:<pkg>` | Research | Read dependency source | Yes |
| `./run.sh` | Runtime | Launch the application | — |
| `./install.sh` | Setup | Create venv, install deps | — |
```

Document each CLI tool in CLAUDE.md so agents know what's available without guessing.

### 3. Internal Code Tools

Project-native functions, classes, or registries that serve as callable interfaces. These are NOT MCP servers — they're the project's own tool surface that agents need to understand when working on the code.

Scan for:
- **Tool/function registries** — decorator-based registration, schema dictionaries, dispatch tables
- **Entry points** — `dispatch()`, `handle()`, `register()` functions
- **Schema definitions** — OpenAI function calling schemas, JSON Schema definitions, typed parameter specs
- **Plugin/extension interfaces** — hook registration, event handlers, middleware chains

Document as a tool map:

```markdown
## Internal Tool Map

### Tool Registry (`tools.py` or `tools/`)
| Tool Name | Handler | Side Effects | Dependencies |
|-----------|---------|-------------|--------------|
| `read_file` | `handle_read_file()` | No | — |
| `git_status` | `handle_git_status()` | No | — |
| `send_to_pane` | `handle_send_to_pane()` | Yes | tmux/cmux |
| `set_mode` | `handle_set_mode()` | Yes | state.py |
| `web_search` | `handle_web_search()` | No | OPENAI_API_KEY |

### Event Handlers (`client.py`)
| Event | Handler | Purpose |
|-------|---------|---------|
| `response.done` | `_on_response_done()` | Chain tool results → next response |
| `session.created` | `_on_session_created()` | Initialize persona + tools |

### State Interface (`state.py`)
| Field | Type | Mutators |
|-------|------|----------|
| `current_mode` | `str` | `set_mode()` |
| `response_active` | `bool` | event handlers |
```

This gives agents working ON the code a map of the internal tool surface — what functions exist, what they do, and what depends on what.

### 4. Custom Scripts

Project-specific automation:

| Script | Purpose | Idempotent |
|--------|---------|-----------|
| `install.sh` | Create venv, install deps | Yes |
| `run.sh` | Launch with env loading | No (long-running) |
| `scripts/migrate.py` | Data migration | Depends |

## Tool Configuration from Workflow Decisions

| Workflow Need | Tool Category | Configuration |
|--------------|---------------|---------------|
| "Query the database" | MCP Server | Database MCP config |
| "Deploy to production" | CLI + Script | kubectl + deploy.sh |
| "Track issues" | MCP Server | Linear/Jira MCP config |
| "Search documentation" | MCP Server | context7 or deepwiki |
| "Run E2E tests" | CLI | Playwright/Cypress config |
| "Add a new tool to the project" | Internal | Update tool registry + schema |
| "Understand tool dependencies" | Internal | Read tool map, trace dispatch |

## Configuration Rules

- **Never hardcode secrets.** Use `env:VAR_NAME` pattern in MCP configs.
- **Document all tool surfaces.** Add CLI tools to CLAUDE.md, internal tools to tool map.
- **Verify availability.** Check if CLI tools are installed before referencing.
- **Environment isolation.** Use project-local tools (npx, poetry run) over global installs.
- **Internal tools get architecture docs.** Don't just list them — document side effects, dependencies, and mutation patterns.

## Output

Generate a `.claude/tools.md` file (or section in CLAUDE.md) containing:
1. CLI tool inventory with install status
2. MCP server configurations (if any)
3. Internal tool map extracted from code analysis
4. Custom script inventory

## Standalone Invocation

`/generate-tools`

`$ARGUMENTS`:
- `--mcp-only` — Only configure MCP servers
- `--cli-only` — Only inventory CLI commands
- `--internal-only` — Only map internal code tools
- `--full` — All categories (default)
- `--quick-grill` — Abbreviated interrogation (3-5 questions)
