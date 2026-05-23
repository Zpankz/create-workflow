# Grilling Sessions

Two variants of the same pattern: structured interrogation that resolves
decisions one by one.

## grill-me (general purpose)

Interview the user relentlessly about every aspect of a plan until reaching
shared understanding. Walk each branch of the design tree, resolving
dependencies between decisions one by one. For each question, provide your
recommended answer. Ask one question at a time. If a question can be
answered by exploring the codebase, explore instead of asking.

## grill-with-docs (engineering — adds domain documentation)

Same interrogation pattern as grill-me, plus:

### Domain Awareness

Look for `CONTEXT.md` (glossary) and `docs/adr/` (decisions) during
codebase exploration.

File structure for single-context repos:
```
/
├── CONTEXT.md
├── docs/adr/
│   ├── 0001-event-sourced-orders.md
│   └── 0002-postgres-for-write-model.md
└── src/
```

Multi-context repos (monorepos) use `CONTEXT-MAP.md` at root pointing to
per-context `CONTEXT.md` files.

Create files lazily — only when you have something to write.

### During the Session

**Challenge against the glossary.** When the user uses a term conflicting
with CONTEXT.md, call it out immediately. "Your glossary defines
'cancellation' as X, but you seem to mean Y — which is it?"

**Sharpen fuzzy language.** When terms are vague or overloaded, propose a
precise canonical term. "You're saying 'account' — do you mean the
Customer or the User?"

**Discuss concrete scenarios.** Stress-test domain relationships with
specific edge-case scenarios that force precision about boundaries.

**Cross-reference with code.** When the user states how something works,
check whether the code agrees. Surface contradictions.

**Update CONTEXT.md inline.** When a term is resolved, update right there.
Don't batch — capture as decisions happen.

**Offer ADRs sparingly.** Only when ALL THREE are true:
1. Hard to reverse — meaningful cost to change later
2. Surprising without context — future reader will wonder why
3. Result of a real trade-off — genuine alternatives existed

If any is missing, skip the ADR.

## ADR Format

```markdown
# ADR-NNNN: <Decision Title>

## Status
Accepted | Superseded by ADR-MMMM | Deprecated

## Context
What forces are at play? What constraints exist?

## Decision
What was decided and why.

## Consequences
What follows from this decision — good, bad, and neutral.
```
