# Claude Code Workflow DSL Reference

> Source: Binary extraction from `@anthropic-ai/claude-code@2.1.147` npm artifact (G2 evidence).
> Status: Shipped but gated. Not in public docs or SDK type union. Use for design, not production lock-in.

## Gates

| Gate | Type | Control |
|------|------|---------|
| `CLAUDE_CODE_WORKFLOWS` | Environment variable | Local feature visibility |
| `tengu_workflows_enabled` | Server-side flag | Account/rollout eligibility |

Both must be active for Workflow tool to appear.

## Script Format

Scripts live at `.claude/workflows/*.js` (project) or `~/.claude/workflows/*.js` (user).

Every script must export a `meta` object as a pure literal:

```javascript
export const meta = {
  name: "my-workflow",
  description: "What this workflow does",
  whenToUse: "Use when ...",  // optional
  phases: [                    // optional
    { title: "phase-1", detail: "..." },
    { title: "phase-2", detail: "..." }
  ]
};
```

DSL functions (`agent`, `pipeline`, `parallel`, `phase`, `log`, `workflow`) are available as **top-level globals** in the script scope. Two additional globals:

- `args` — optional input value passed by the Workflow tool invocation
- `budget` — token-budget object with `total()`, `spent()`, `remaining()` functions

## DSL Functions

### `agent(prompt, opts?)`

Spawn a Claude Code subagent. Core orchestration primitive.

```javascript
const result = await agent("Analyze the auth module for security issues", {
  model: "opus",
  schema: myJsonSchema,
  label: "security-audit",
  phase: "analysis",
  isolation: "worktree",
  agentType: "security-reviewer"
});
```

Options:
- `model` — Model selection (haiku, sonnet, opus)
- `schema` — JSON Schema for typed/structured result
- `label` — Display label for the agent call
- `phase` — Associate with a named phase
- `isolation` — `"worktree"` for git worktree isolation
- `agentType` — Agent definition to use (e.g., custom agent type)

> **Note**: Binary extraction also shows `tools` and `permissionMode` in some code paths but these are not confirmed in the PRD schema. Use with caution.

Cached on resume: completed `agent()` calls with unchanged prompt and opts are reused when `resumeFromRunId` is set.

### `pipeline(items, stage1, stage2, ...)`

Stream items through staged functions with no barrier between stages:

```javascript
const result = await pipeline(
  items,
  (batch) => agent(`Classify these items: ${JSON.stringify(batch)}`),
  (classified) => agent(`Review classified items: ${JSON.stringify(classified)}`),
  (findings) => agent(`Write a report: ${JSON.stringify(findings)}`)
);
```

### `parallel(thunks)`

Run an array of thunks concurrently. **Takes a single array**, not variadic arguments. A thunk that throws resolves to `null`. Use `.filter(Boolean)` to remove nulls — but **never combine with positional destructuring** (filtering shifts positions).

```javascript
// Destructure when positions matter — handle nulls individually
const [security, performance, style] = await parallel([
  () => agent("Security review of src/auth/"),
  () => agent("Performance review of src/db/"),
  () => agent("Style review of src/components/")
]);

// Or filter when positions don't matter — never combine with destructure
const results = await parallel([
  () => agent("Security review of src/auth/"),
  () => agent("Performance review of src/db/"),
  () => agent("Style review of src/components/")
]);
const valid = results.filter(Boolean);
```

### `phase(name)`

Group progress under named phases (for UI reporting):

```javascript
phase("analysis");
const analysis = await agent("Analyze the codebase");

phase("implementation");
const impl = await agent(`Implement: ${JSON.stringify(analysis)}`);

phase("verification");
const verified = await agent(`Verify: ${JSON.stringify(impl)}`);
```

### `log(message)`

Emit progress messages:

```javascript
log("Starting security audit...");
```

### `workflow(nameOrRef, args?)`

Invoke another workflow inline. **One nesting level only** — a child workflow cannot invoke further workflows.

```javascript
const subResult = await workflow("review-branch", { target: "src/auth/" });
```

## Sandbox Constraints

| Constraint | Details |
|-----------|---------|
| Script size | 524,288 bytes max |
| Filesystem | No Node.js or filesystem APIs |
| Nondeterminism | `Date.now()`, argless `new Date()`, `Math.random()` blocked |
| Resume | Same session only, via `resumeFromRunId` |
| Remote isolation | `agent({isolation:'remote'})` not available in current build |
| SDK types | `WorkflowInput` absent from `sdk-tools.d.ts` |
| Nesting depth | `workflow()` calls limited to one nesting level |
| Plugin paths | Plugin-scoped workflow directories are resolved but not publicly documented |

Nondeterminism is blocked to enable deterministic replay — `resumeFromRunId` skips completed agent calls when prompt+opts are unchanged.

## Built-in Workflows

| Name | Function |
|------|----------|
| `bugfix` | Reproduce → root-cause → patch → regression test → PR |
| `bughunt` | Multi-agent adversarial bug sweep |
| `bughunt-lite` | Bounded bug sweep, fewer finders |
| `dashboard` | Discover data sources → implement dashboard panels |
| `deep-research` | Fan-out research → verify claims → synthesize cited report |
| `docs` | Discover features → write docs → verify examples/links |
| `investigate` | Gather evidence → hypotheses → refute → root-cause report |
| `plan-hunter` | Generate plan styles → parallel judges → synthesize winner |
| `review-branch` | Review for bugs, simplicity, architecture, dead code, consistency |

## Script Path Resolution

Priority: inline script > built-in > project `.claude/workflows/` > user `~/.claude/workflows/`

## Composition Levels

| Level | What | Examples |
|-------|------|---------|
| L0 Primitives | Atomic DSL functions | `agent()`, `parallel()`, `pipeline()`, `phase()`, `log()` |
| L1 Composites | Tactical combinations | Typed agent pipeline, deterministic orchestration, guardrailed fanout |
| L2 Strategic | Full workflow patterns | Research factory, model council review, spec-to-skill compiler |

## Practical Guidance

Build workflow-shaped assets now using Skills, Subagents, Hooks, and MCP so they can move into `.claude/workflows/` with minimal translation once publicly documented.

The strongest pattern: design your workflow as a sequence of agent calls with typed handoffs, then implement it as a skill today and migrate to a workflow script when the gate opens.
