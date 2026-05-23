---
name: scaffold
description: Design and build a complete Claude Code workflow from the ground up. Uses grill-with-docs interrogation to understand the target system, then composes CLAUDE.md, rules, skills, hooks, agents, tools, and workflows as primitives within a systems-thinking architecture. The workflow is the product — primitives are the building blocks.
---

# Scaffold

Design a workflow system, then build it from primitives.

## Core Principle

**The workflow is the product.** CLAUDE.md, rules, hooks, skills, agents, and tools are primitives — building blocks that compose into a coherent workflow system. This plugin doesn't generate config files in isolation. It designs a workflow first, then determines which primitives implement each part.

```
Workflow (the goal)
├── Agents (who does the work)
│   └── Skills (what they know how to do)
│       └── Tools (what they use)
├── Hooks (automatic triggers)
│   └── Rules (constraints they enforce)
└── CLAUDE.md (shared context for everything)
```

## Pipeline

### Phase 1: Scan the System

Explore the target repo to understand the existing system:

- Languages, frameworks, package manager (manifest files)
- Build, test, lint commands (Makefile, scripts, CI config)
- Project structure (monorepo vs single, workspace layout)
- Existing Claude Code config (.claude/, CLAUDE.md, settings)
- Existing AI tool configs (AGENTS.md, .cursor/rules, etc.)
- Formatter and linter configuration
- Git conventions (commit style, branch naming from history)
- Documentation, architecture docs
- CONTEXT.md and docs/adr/ if present
- Environment setup (services, env vars, dependencies)
- CI/CD pipeline structure
- Deployment targets and process

Synthesize findings into a **system map** — not raw output, but a concise model of how the repo's development system works today.

### Phase 2: Grill — Design the Workflow

Run grill-with-docs to design the target workflow system. The grill isn't about config preferences — it's about understanding the workflow the user needs.

#### Grill Rules

1. **One question at a time.** Never batch.
2. **Recommend an answer.** Based on scan findings.
3. **Explore before asking.** If code answers it, don't ask.
4. **Challenge the glossary.** Check terms against CONTEXT.md.
5. **Sharpen fuzzy language.** Propose precise terms.
6. **Cross-reference with code.** Verify claims against the codebase.
7. **Update CONTEXT.md inline.** As terms resolve, write immediately.
8. **ADRs sparingly.** Only when ALL THREE: hard to reverse + surprising + real trade-off.

#### Grill Topics (workflow-oriented)

1. **System purpose** — What does this repo do? Who uses it? What's the development lifecycle?
2. **Current workflow** — How does work flow from idea to production today? Where are the bottlenecks?
3. **Desired workflow** — What should the ideal workflow look like? What's missing?
4. **Actors** — Who (or what agent) performs each step? Where does Claude fit?
5. **Automation boundaries** — What should be automatic (hooks) vs on-demand (skills) vs orchestrated (workflows)?
6. **Quality gates** — What checks must pass? When? Who enforces them?
7. **Domain knowledge** — What does Claude need to know to participate effectively? What does it get wrong?
8. **Failure modes** — What goes wrong? How should errors be handled? Escalation paths?

#### Decision Tracking

Each resolved decision maps to one or more primitives:

```
Decision: "All PRs must pass type checking before review"
→ Hook: pre-commit type check
→ Rule: type-safety.md with path scope
→ CLAUDE.md: mention typecheck command
```

```
Decision: "Deploy process is: build → test → stage → smoke test → promote"
→ Workflow: deploy.js with pipeline() stages
→ Skill: /deploy for manual trigger
→ Agent: deploy-verifier for smoke tests
```

### Phase 3: Compose the System

Map resolved decisions to primitives. This is systems thinking — each primitive has a role:

| Primitive | Role in System | When to Use |
|-----------|---------------|-------------|
| **CLAUDE.md** | Shared context — the system's "memory" | Knowledge every primitive needs |
| **Rules** | Constraints — the system's "laws" | Standards that must be enforced |
| **Skills** | Capabilities — the system's "procedures" | On-demand multi-step workflows |
| **Hooks** | Reflexes — the system's "autonomic responses" | Automatic reactions to events |
| **Agents** | Specialists — the system's "team members" | Focused roles with specific expertise |
| **Tools** | Instruments — the system's "equipment" | External integrations and utilities |
| **Workflows** | Orchestration — the system's "nervous system" | Multi-step automated pipelines |

Generate in dependency order:

```
1. CLAUDE.md        (shared context — everything references this)
2. Rules            (constraints — agents and hooks enforce these)
3. Skills           (capabilities — agents use these)
4. Hooks            (reflexes — automatic enforcement of rules)
5. Agents           (specialists — use skills, follow rules)
6. Tools            (instruments — agents and skills use these)
7. Workflows        (orchestration — compose agents, skills, tools into pipelines)
```

Invoke each generator: `/generate-claudemd`, `/generate-rules`, etc.

Skip generators when the grill determined they're not needed.

### Phase 4: Verify the System

After generation:

1. **Consistency check** — Do primitives reference each other correctly? Does a hook reference a rule that exists? Does a workflow invoke agents that are defined?
2. **Completeness check** — Does every grill decision map to at least one primitive? Are there gaps?
3. **Coherence check** — Do the primitives compose into the workflow the user described? Walk through the workflow end-to-end using the generated primitives.
4. **Security check** — No hardcoded secrets, no sensitive data in generated files.
5. **Present the system** — Show the full primitive tree with one-line descriptions. Explain how the workflow flows through the primitives.

## Invocation

`/scaffold` — Full pipeline: scan → grill → compose → verify.

`$ARGUMENTS`:
- `--scan-only` — Phase 1 only, report system map
- `--skip-grill` — Use scan defaults (fast, less accurate)
- `--generators=claudemd,rules,hooks` — Run only specified generators
- `--dry-run` — Show the workflow design without writing files
- `--workflow=deploy` — Focus scaffold on a specific workflow

## Context Management

Long-running skill. Protect context:

- Subagents for deep file reads (>100 lines)
- Synthesize, don't dump raw output
- Track decisions as structured records, not prose
- Each generator is a separate skill invocation — keeps context focused
