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
  phases: ["phase-1", "phase-2"]  // optional
};
```

## DSL Functions

### `agent(prompt, opts?)`

Spawn a Claude Code subagent. Core orchestration primitive.

```javascript
const result = await agent("Analyze the auth module for security issues", {
  model: "opus",
  tools: ["Read", "Grep", "Glob"],
  structuredOutput: { schema: myJsonSchema },
  permissionMode: "plan"
});
```

Options:
- `model` — Model selection (haiku, sonnet, opus)
- `tools` — Tool allowlist for this agent
- `structuredOutput` — JSON Schema for typed result
- `permissionMode` — Permission level for the agent

Cached on resume: completed `agent()` calls with unchanged prompt and opts are reused when `resumeFromRunId` is set.

### `pipeline(...stages)`

Stream items through staged transformations:

```javascript
const result = await pipeline(
  () => agent("Find all API endpoints"),
  (endpoints) => agent(`Review these endpoints: ${JSON.stringify(endpoints)}`),
  (findings) => agent(`Write a security report: ${JSON.stringify(findings)}`)
);
```

### `parallel(...thunks)`

Run async thunks concurrently:

```javascript
const [security, performance, style] = await parallel(
  () => agent("Security review of src/auth/"),
  () => agent("Performance review of src/db/"),
  () => agent("Style review of src/components/")
);
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

### `workflow(config)`

Top-level workflow invocation (for nested/chained workflows).

## Sandbox Constraints

| Constraint | Details |
|-----------|---------|
| Script size | 524,288 bytes max |
| Filesystem | No Node.js or filesystem APIs |
| Nondeterminism | `Date.now()`, argless `new Date()`, `Math.random()` blocked |
| Resume | Same session only, via `resumeFromRunId` |
| Remote isolation | `agent({isolation:'remote'})` not available in current build |
| SDK types | `WorkflowInput` absent from `sdk-tools.d.ts` |

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
