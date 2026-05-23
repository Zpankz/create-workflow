---
name: generate-tools
description: Generate tool configurations (MCP servers, CLI integrations, external service connectors) that serve as instruments in the workflow system. Tools extend what agents and skills can interact with. Invoked by scaffold or standalone via /generate-tools.
---

# Generate Tools

Configure tool integrations — MCP servers, CLI tools, and external service connectors.

## Role in the System

Tools are **instruments** — they extend the system's reach beyond the local codebase. Agents use tools, skills reference tools, workflows orchestrate tools.

## Tool Categories

### MCP Servers

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

Common MCP server patterns:
- Database access (postgres, sqlite, redis)
- API integrations (GitHub, Jira, Linear, Slack)
- Search/knowledge (context7, deepwiki, perplexity)
- File processing (pageindex for PDFs, image tools)

### CLI Tools

Tools available via Bash that agents and skills use:
- Linters and formatters (eslint, prettier, ruff, black)
- Build tools (webpack, vite, cargo, go build)
- Testing frameworks (jest, pytest, go test)
- Infrastructure (docker, terraform, kubectl)

### Custom Scripts

Project-specific tools in `scripts/` or `tools/`:
- Data migration scripts
- Environment setup scripts
- Deployment scripts
- Code generation scripts

## Tool Configuration from Workflow Decisions

| Workflow Need | Tool Configuration |
|--------------|-------------------|
| "Need to query the database" | MCP server for the database |
| "Deploy to Kubernetes" | kubectl CLI + deploy scripts |
| "Track issues in Linear" | Linear MCP server |
| "Search documentation" | context7 or deepwiki MCP |
| "Run E2E tests in browser" | Playwright/Cypress CLI config |

## Configuration Rules

- **Never hardcode secrets.** Use `env:VAR_NAME` pattern in MCP configs.
- **Document required tools.** Add to CLAUDE.md's setup section.
- **Verify availability.** Check if CLI tools are installed before referencing.
- **Environment isolation.** Use project-local tools (npx, poetry run) over global installs.

## Standalone Invocation

`/generate-tools`

`$ARGUMENTS`:
- `--mcp-only` — Only configure MCP servers
- `--skip-grill` — Use scan defaults
