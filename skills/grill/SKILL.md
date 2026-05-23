---
name: grill
description: Run a grill-with-docs interrogation session on the current repo. Structured one-question-at-a-time interview that resolves design decisions while maintaining CONTEXT.md glossary and docs/adr/ records inline. Standalone entry point for the grilling pattern used by /scaffold.
---

# Grill

Structured interrogation that resolves decisions one by one while maintaining domain documentation.

## Reference

Full grilling pattern: `@references/grilling.md`

## Quick Start

1. Scan the repo (languages, structure, existing docs, CONTEXT.md, docs/adr/)
2. Begin interrogation — one question at a time
3. For each question: recommend an answer based on what you found
4. If code answers the question, explore instead of asking
5. When a term resolves, update CONTEXT.md immediately
6. When a decision resolves, write it to `.claude/scaffold-decisions.md` immediately
7. When a decision meets all 3 ADR criteria, write the ADR

## Modes

### `/grill` (default — grill-with-docs)

Full engineering interrogation with domain documentation:
- Challenge terms against CONTEXT.md glossary
- Sharpen fuzzy language with precise canonical terms
- Cross-reference claims with code
- Update CONTEXT.md inline as terms resolve
- Create ADRs when ALL THREE: hard to reverse + surprising + real trade-off

### `/grill --lite` (grill-me)

General-purpose interrogation without documentation maintenance:
- Same one-at-a-time pattern
- Same explore-before-asking behavior
- No CONTEXT.md or ADR management

### `/grill --topic=<topic>`

Focused grill on a specific area:
- `--topic=architecture` — System boundaries, patterns, abstractions
- `--topic=workflow` — Development lifecycle, CI/CD, deployment
- `--topic=conventions` — Code style, naming, patterns
- `--topic=agents` — Agent needs, automation boundaries
- `--topic=security` — Auth, data handling, threat model

## Output

The grill produces:
- **Decision records** — Resolved decisions that feed generators
- **Updated CONTEXT.md** — Glossary with precise, tested terms
- **ADRs in docs/adr/** — Architectural decisions (sparingly)
- **System understanding** — Enough context to invoke any generator

## Integration

After grilling, invoke generators with the resolved decisions:
- `/generate-claudemd` — Uses decisions about conventions, gotchas
- `/generate-rules` — Uses decisions about standards, constraints
- `/generate-skills` — Uses decisions about workflows, automation
- `/generate-hooks` — Uses decisions about automatic behaviors
- `/generate-agents` — Uses decisions about specialist roles
- `/generate-workflows` — Uses decisions about orchestration pipelines

Or use `/scaffold` to run the full pipeline (grill + all generators).
