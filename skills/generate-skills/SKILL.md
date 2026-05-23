---
name: generate-skills
description: Generate .claude/skills/ definitions — the capability layer of the workflow system. Identifies recurring workflows and creates SKILL.md files that agents execute and workflows compose. Invoked by scaffold or standalone via /generate-skills.
---

# Generate Skills

Produce `.claude/skills/<name>/SKILL.md` files for recurring workflows identified during the grill.

## Role in the System

Skills are the **capabilities** — the procedures that agents execute and workflows compose into pipelines. Each skill is a reusable building block. Agents use skills to accomplish their responsibilities. Workflows chain skills into end-to-end automation.

```
Skills (capabilities)
  ← Identified from grill decisions + workflow design
  → Executed by Agents (specialist knowledge)
  → Composed by Workflows (pipeline steps)
  → Triggered by Users (slash commands)
```

## Input

Scan results, grill decisions, and the workflow design that determines what capabilities the system needs. Skills emerge from:
- Recurring multi-step workflows the user described
- Complex processes that benefit from structured instructions
- Domain-specific tasks requiring specialized knowledge
- Automations the user wants on-demand (not automatic — those are hooks)

## Skill Identification

During the grill, listen for:
- "I always have to..." → candidate skill
- "The process for X is..." → candidate skill
- "Claude keeps getting X wrong" → candidate skill (with corrective instructions)
- "We do X differently than most" → candidate skill (domain-specific)

## Output Format

Each skill at `.claude/skills/<name>/SKILL.md`:

```yaml
---
name: <kebab-case-name>
description: <what the skill does and when to use it — max 1024 chars>
---
```

Body follows progressive disclosure:
1. **Metadata** (frontmatter) — always loaded, used for skill discovery
2. **Body** — loaded when skill is triggered
3. **Bundled resources** — loaded on demand via file references

## Skill Writing Rules

- Imperative/infinitive voice ("Run the test suite" not "You should run the test suite")
- No second person ("Run X" not "You run X")
- Concrete, actionable steps — not philosophy
- Include examples when the pattern isn't obvious
- Reference bundled files with relative paths for large content
- Add `disable-model-invocation: true` for skills with side effects (deploy, publish, etc.)
- Use `$ARGUMENTS` for skills that accept input

## Common Skill Patterns

| Pattern | Example | Triggers |
|---------|---------|----------|
| Verify/validate | `/verify` — run all checks before commit | User says "before I commit I always..." |
| Deploy | `/deploy-staging` — deploy to staging env | User describes deployment process |
| Review | `/review` — structured code review checklist | User has specific review criteria |
| Generate | `/generate-component` — scaffold new component | User has boilerplate patterns |
| Debug | `/debug-<system>` — systematic debugging for specific system | User describes recurring debug patterns |

## Don't Create Skills For

- One-off tasks
- Standard practices well-documented elsewhere
- Project-specific conventions (those go in CLAUDE.md or rules)
- Simple commands (those are aliases, not skills)

## Standalone Invocation

`/generate-skills` — scan + grill + generate skills.

`$ARGUMENTS`:
- `--list` — List candidate skills without generating
- `--name=verify,deploy` — Generate only specified skills
- `--quick-grill` — Use scan defaults
