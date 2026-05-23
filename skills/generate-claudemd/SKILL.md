---
name: generate-claudemd
description: Generate a project CLAUDE.md file — the shared memory layer of the workflow system. Produces minimal, high-signal instructions that every other primitive (rules, skills, hooks, agents, workflows) references. Invoked by scaffold or standalone via /generate-claudemd.
---

# Generate CLAUDE.md

Produce a CLAUDE.md at the project root. Every line must pass: "Would removing this cause Claude to make mistakes?" If no, cut it.

## Role in the System

CLAUDE.md is the **shared memory** — the system's wiki that every primitive references. Rules enforce what CLAUDE.md declares. Skills assume the context it provides. Agents inherit its conventions. Workflows rely on it for consistent behavior across all participants.

```
CLAUDE.md (shared memory)
  ← Rules reference for enforcement targets
  ← Skills assume for context
  ← Agents inherit for conventions
  ← Hooks enforce implicitly
  ← Workflows depend on for consistency
```

## Input

Scan results, grill decisions, and the workflow design that determines what shared context all primitives need. If invoked standalone, scan the repo first.

## Output Structure

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test

[Non-obvious commands only. Skip standard `npm test`, `cargo test`, `pytest`.]

## Code Style

[Rules that DIFFER from language defaults. Skip obvious conventions.]

## Architecture

[Key abstractions, boundaries, non-obvious patterns. Keep to 5-10 lines max.]

## Workflow

[Branch naming, PR conventions, commit style, deployment process.]

## Gotchas

[Things Claude gets wrong. Required env vars. Non-obvious dependencies.]
```

## Rules

### Include

- Build/test/lint commands Claude can't guess (non-standard scripts, flags, sequences)
- Code style rules that DIFFER from language defaults
- Testing quirks (e.g., "run single test with: pytest -k 'test_name'")
- Repo etiquette (branch naming, PR conventions, commit style)
- Required env vars or setup steps
- Non-obvious gotchas or architectural decisions
- Relevant content from existing AI tool configs (AGENTS.md, .cursor/rules, .cursorrules, .github/copilot-instructions.md)

### Exclude

- File-by-file structure (Claude discovers this by reading the codebase)
- Standard language conventions Claude already knows
- Generic advice ("write clean code", "handle errors")
- Detailed API docs or long references — use `@path/to/import` instead
- Information that changes frequently — reference the source file
- Commands obvious from manifest files (standard `npm test`, `cargo test`, `pytest`)

### Format Rules

- Be specific: "Use 2-space indentation in TypeScript" not "Format code properly"
- Use `@path/to/import` for content that changes or is long
- Prefix with the standard header (shown above)
- Keep total length under 100 lines for single-concern repos
- For monorepos, suggest `.claude/rules/` for shared rules and subdirectory CLAUDE.md files for module-specific instructions

## Monorepo Handling

If the scan found multiple distinct modules/packages:

1. Generate a root CLAUDE.md with shared conventions
2. Suggest per-module CLAUDE.md files for module-specific instructions
3. Suggest `.claude/rules/` for cross-cutting standards
4. Mention that subdirectory CLAUDE.md files load automatically when Claude works in those directories

## Migration from Other Tools

If existing AI tool configs were found (AGENTS.md, .cursor/rules, etc.):

1. Extract still-relevant instructions
2. Translate to Claude Code conventions
3. Note which original files the content came from (in a comment during generation, not in the final file)
4. Don't blindly copy — filter through the "would removing this cause mistakes?" test

## Standalone Invocation

`/generate-claudemd` — scan the repo first, then generate. Use `--quick-grill` for abbreviated interrogation.

`$ARGUMENTS`:
- `--local` — Generate CLAUDE.local.md (personal, gitignored) instead of project CLAUDE.md
- `--quick-grill` — Use scan defaults without interrogation
- `--append` — Add to existing CLAUDE.md instead of replacing
