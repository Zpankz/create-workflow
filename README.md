# create-workflow

Claude Code plugin that designs and builds complete workflow systems from the ground up. Uses grill-with-docs interrogation to understand your project, then composes CLAUDE.md, rules, skills, hooks, agents, tools, and workflows as primitives within a systems-thinking architecture.

**The workflow is the product.** Everything else is a building block.

## Install

### Claude Code (native)

```bash
claude plugin install https://github.com/Zpankz/create-workflow
```

### Pi (native)

```bash
pi install https://github.com/Zpankz/create-workflow
```

### Antigravity / Gemini (native)

```bash
gemini extensions install https://github.com/Zpankz/create-workflow
```

### Hermes (native)

```bash
hermes plugins install https://github.com/Zpankz/create-workflow
```

### Codex (marketplace)

Add the repo as a self-hosted marketplace, then install:

```bash
codex plugin marketplace add https://github.com/Zpankz/create-workflow
codex plugin add create-workflow@create-workflow-marketplace
```

## Compatibility Matrix

| Tool | Method | Manifest | Skills | Hooks | Agents |
|------|--------|----------|--------|-------|--------|
| Claude Code | `claude plugin install` | `.claude-plugin/plugin.json` | Yes | Generator | Generator |
| Pi | `pi install` | `package.json` (`"pi"` key) | Yes | Generator | Generator |
| Antigravity | `gemini extensions install` | `plugin.json` (root) | Yes | Generator | Generator |
| Hermes | `hermes plugins install` | `plugin.yaml` + `__init__.py` | Yes | Generator | Generator |
| Codex | `codex plugin marketplace add` | `.codex-plugin/plugin.json` | Yes | Generator | Generator |

Skills are bundled and work natively. Hooks and agents are **generated** by the `generate-hooks` and `generate-agents` skills — they emit native output for whichever tool is running.

### Generator Output

The `generate-hooks` and `generate-agents` skills detect which tool is running and emit **native** output:

| Generator | Claude Code | Antigravity | Hermes | Codex | Pi |
|-----------|-----------|-------------|--------|-------|-----|
| generate-hooks | settings.json | settings.json | Python ctx.register_hook() | hooks.json | TypeScript pi.on() |
| generate-agents | .claude/agents/*.md | agents/*.md (with kind) | Python ctx.register_agent() | .agents/*.md | pi/agents/*.md |

## Primitive Taxonomy

```
Semantic (natural language, interpreted by LLM)
  ./CLAUDE.md              — generalised context
  .claude/agents/*.md      — specialised context
  .claude/skills/*/SKILL.md — conditionals (invoked on match or command)
  .claude/rules/*.md       — constraints

Programmatic (deterministic, executed by runtime)
  .claude/settings.json    — constraints (hooks: PreToolUse, PostToolUse, Stop)
  .mcp.json                — functions (MCP server configurations)
  .claude/workflows/*.js   — orchestration (sandboxed JS VM, gated)
```

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| **scaffold** | `/scaffold` | Full pipeline: scan, grill, generate, verify |
| **grill** | `/grill` | Standalone interrogation with domain docs |
| **generate-claudemd** | `/generate-claudemd` | Generate CLAUDE.md (shared context) |
| **generate-rules** | `/generate-rules` | Generate .claude/rules/ (constraints) |
| **generate-skills** | `/generate-skills` | Generate .claude/skills/ (capabilities) |
| **generate-hooks** | `/generate-hooks` | Generate hooks — native to active tool's runtime |
| **generate-agents** | `/generate-agents` | Generate agents — native to active tool's format |
| **generate-tools** | `/generate-tools` | Configure MCP servers and tool integrations |
| **generate-workflows** | `/generate-workflows` | Generate workflow skills (orchestration, --dual-track for .js) |

## How It Works

```
/scaffold
  |- Phase 1: Scan — explore the repo, build a system map
  |- Phase 2: Grill — structured interrogation, one question at a time
  |   |- Recommend answers based on scan findings
  |   |- Explore code before asking
  |   |- Persist decisions to .claude/scaffold-decisions.md inline
  |   |- Maintain CONTEXT.md glossary inline
  |   '- Create ADRs sparingly (hard to reverse + surprising + real trade-off)
  |- Phase 3: Compose — map decisions to primitives, generate in dependency order
  |   |- Detect active tool — emit native formats
  |   |- Check for existing files — diff, don't overwrite
  |   |- CLAUDE.md      (shared context — everything references this)
  |   |- Rules          (constraints — agents and hooks enforce these)
  |   |- Skills         (capabilities — agents use these)
  |   |- Hooks          (reflexes — native to tool runtime)
  |   |- Agents         (specialists — native to tool format)
  |   |- Tools          (instruments — agents and skills use these)
  |   '- Workflows      (orchestration — compose everything into pipelines)
  '- Phase 4: Verify — consistency, completeness, coherence
```

## Standalone Use

Each generator works independently:

```bash
/generate-claudemd              # Just generate CLAUDE.md
/generate-hooks --tool=hermes   # Generate Python hooks for Hermes
/generate-hooks --all-tools     # Generate hooks for all detected tools
/generate-agents --tool=codex   # Generate agents with OpenAI model names
/generate-workflows --dual-track # Generate both .js workflow AND skill
/grill --topic=architecture     # Focused interrogation on architecture
/scaffold --scan-only           # Just scan, report findings
/scaffold --quick-grill         # Abbreviated interrogation (3-5 questions)
```

## Cross-Tool Event Mapping

The `generate-hooks` skill translates hook intent across tools:

| Intent | Claude Code | Antigravity | Hermes | Codex | Pi |
|--------|-----------|-------------|--------|-------|-----|
| Before tool | PreToolUse | BeforeTool | pre_tool_call | PreToolUse | tool_execution_start |
| After tool | PostToolUse | PostToolUse | post_tool_call | PostToolUse | tool_result |
| Session start | — | SessionStart | on_session_start | SessionStart | session_start |
| Turn/session end | Stop | SessionEnd | on_session_end | Stop | session_shutdown |

## References

- `references/workflow-dsl.md` — Claude Code Workflow DSL (agent, pipeline, parallel, phase, log)
- `references/grilling.md` — Grilling pattern definition (grill-me and grill-with-docs)

## Architecture Decisions

ADRs are stored in `docs/adr/` and created only when ALL THREE criteria are met:
1. Hard to reverse
2. Surprising without context
3. Result of a real trade-off

## License

MIT
