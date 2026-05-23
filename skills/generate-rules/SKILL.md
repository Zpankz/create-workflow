---
name: generate-rules
description: Generate .claude/rules/ files — the constraint layer of the workflow system. Produces focused rule files that hooks enforce and agents follow. Scoped by topic and optionally by file path. Invoked by scaffold or standalone via /generate-rules.
---

# Generate Rules

Produce `.claude/rules/` files. Each rule file is focused on one concern and loaded automatically alongside CLAUDE.md.

## Role in the System

Rules are the **constraints** — the laws that hooks enforce and agents follow. Every rule exists to protect a workflow invariant. Hooks are the enforcement mechanism; rules are what they enforce. Agents consult rules to stay within boundaries.

```
Rules (constraints)
  ← Declared from CLAUDE.md standards
  → Enforced by Hooks (automatic)
  → Followed by Agents (by instruction)
  → Respected by Skills (by convention)
```

## Input

Scan results, grill decisions, and the workflow design that determines what invariants need protection. If standalone, scan first.

## Output

Files in `.claude/rules/` with optional `paths` frontmatter for scoping:

```markdown
---
paths:
  - "src/api/**"
  - "src/middleware/**"
---

# API Conventions

[Rules specific to these paths]
```

## Rule Categories

Generate only categories that apply (based on scan + grill):

| Category | File | When |
|----------|------|------|
| Code style | `code-style.md` | Style rules beyond CLAUDE.md basics |
| Testing | `testing.md` | Test conventions, coverage requirements, framework-specific patterns |
| Security | `security.md` | Auth patterns, input validation, secret management |
| Git workflow | `git-workflow.md` | Commit format, branch naming, PR process |
| Architecture | `architecture.md` | Module boundaries, dependency rules, patterns |
| Performance | `performance.md` | Perf-critical paths, caching rules, query patterns |
| Accessibility | `accessibility.md` | A11y requirements, ARIA patterns, testing |

## Rules for Rules

- Each file: one concern, focused, under 50 lines
- Use `paths` frontmatter to scope rules to relevant directories
- Don't repeat what's in CLAUDE.md — rules extend, not duplicate
- Imperative voice ("Use parameterized queries" not "You should use parameterized queries")
- Include concrete examples when the pattern isn't obvious
- Skip rules that match language/framework defaults

## Path Scoping

Use `paths` frontmatter when rules only apply to specific directories:

```yaml
---
paths:
  - "src/components/**"    # React components
  - "src/hooks/**"         # Custom hooks
---
```

Rules without `paths` apply globally.

## Standalone Invocation

`/generate-rules` — scan + generate. Use `--quick-grill` for abbreviated interrogation.

`$ARGUMENTS`:
- `--category=security,testing` — Generate only specified categories
- `--quick-grill` — Use scan defaults
