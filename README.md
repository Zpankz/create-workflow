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

### Hermes (skills only)

Individual skills can be installed directly:

```bash
hermes skills install https://github.com/Zpankz/create-workflow/tree/main/skills/scaffold
hermes skills install https://github.com/Zpankz/create-workflow/tree/main/skills/grill
```

> Hermes `plugins install` accepts git URLs but its plugin manifest format is undocumented. Skill-level install is the verified path.

### Codex

Codex uses marketplace-based plugin distribution. Direct git install is not supported. To use the skills manually:

```bash
git clone https://github.com/Zpankz/create-workflow.git
ln -s "$(pwd)/create-workflow/skills" ~/.codex/skills/create-workflow
```

> This symlinks skills into Codex's skill directory. It bypasses the plugin system — hooks and metadata from `.claude-plugin/plugin.json` are not loaded.

### Antigravity / Cursor

These are IDE forks that run Claude Code as their agent backend. Install via Claude Code (see above), then use skills normally in any Antigravity or Cursor workspace.

> Antigravity and Cursor do not have their own agent plugin systems.

## Compatibility Matrix

| Tool | Method | Plugin metadata | Skills | Hooks |
|------|--------|----------------|--------|-------|
| Claude Code | `claude plugin install` | Yes | Yes | Yes |
| Pi | `pi install` | Yes | Yes | No |
| Hermes | `hermes skills install` | No | Yes | No |
| Codex | Manual symlink | No | Yes | No |
| Antigravity | Via Claude Code | Via Claude Code | Via Claude Code | Via Claude Code |

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
| **generate-hooks** | `/generate-hooks` | Generate hooks in settings.json (reflexes) |
| **generate-agents** | `/generate-agents` | Generate .claude/agents/ (specialists) |
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
  |   |- Check for existing files — diff, don't overwrite
  |   |- CLAUDE.md      (shared context — everything references this)
  |   |- Rules          (constraints — agents and hooks enforce these)
  |   |- Skills         (capabilities — agents use these)
  |   |- Hooks          (reflexes — automatic enforcement)
  |   |- Agents         (specialists — use skills, follow rules)
  |   |- Tools          (instruments — agents and skills use these)
  |   '- Workflows      (orchestration — compose everything into pipelines)
  '- Phase 4: Verify — consistency, completeness, coherence
```

## Standalone Use

Each generator works independently:

```bash
/generate-claudemd              # Just generate CLAUDE.md
/generate-workflows --template=deploy  # Generate a deploy skill from template
/generate-workflows --dual-track       # Generate both .js workflow AND skill
/grill --topic=architecture     # Focused interrogation on architecture
/scaffold --scan-only           # Just scan, report findings
/scaffold --quick-grill         # Abbreviated interrogation (3-5 questions)
```

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
