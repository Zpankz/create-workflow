# create-workflow

Claude Code plugin that designs and builds complete workflow systems from the ground up. Uses grill-with-docs interrogation to understand your project, then composes CLAUDE.md, rules, skills, hooks, agents, tools, and workflows as primitives within a systems-thinking architecture.

**The workflow is the product.** Everything else is a building block.

## Install

```bash
# From local directory
claude /install /path/to/create-workflow
```

## Skills

| Skill | Command | Purpose |
|-------|---------|---------|
| **scaffold** | `/scaffold` | Full pipeline: scan → grill → generate → verify |
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
  ├── Phase 1: Scan — explore the repo, build a system map
  ├── Phase 2: Grill — structured interrogation, one question at a time
  │   ├── Recommend answers based on scan findings
  │   ├── Explore code before asking
  │   ├── Persist decisions to .claude/scaffold-decisions.md inline
  │   ├── Maintain CONTEXT.md glossary inline
  │   └── Create ADRs sparingly (hard to reverse + surprising + real trade-off)
  ├── Phase 3: Compose — map decisions to primitives, generate in dependency order
  │   ├── Check for existing files — diff, don't overwrite
  │   ├── CLAUDE.md      (shared context — everything references this)
  │   ├── Rules          (constraints — agents and hooks enforce these)
  │   ├── Skills         (capabilities — agents use these)
  │   ├── Hooks          (reflexes — automatic enforcement)
  │   ├── Agents         (specialists — use skills, follow rules)
  │   ├── Tools          (instruments — agents and skills use these)
  │   └── Workflows      (orchestration — compose everything into pipelines)
  └── Phase 4: Verify — consistency, completeness, coherence
```

## Systems Thinking

Each primitive has a role in the workflow system:

| Primitive | System Role | Analogy |
|-----------|------------|---------|
| CLAUDE.md | Shared memory | The team's wiki |
| Rules | Laws | Constraints everyone follows |
| Skills | Procedures | How-to guides for specific tasks |
| Hooks | Reflexes | Automatic responses to events |
| Agents | Team members | Specialists with focused expertise |
| Tools | Equipment | External integrations |
| Workflows | Nervous system | Orchestration that connects everything |

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
