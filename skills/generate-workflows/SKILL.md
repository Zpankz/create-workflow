---
name: generate-workflows
description: Generate .workflow.js scripts that compose agents, skills, hooks, and tools into automated pipelines. Produces both .js scripts and equivalent skills by default. The workflow is the product — all other primitives serve it. Invoked by scaffold or standalone via /generate-workflows.
---

# Generate Workflows

Produce `.claude/workflows/*.js` scripts — the orchestration layer that composes all other primitives into automated pipelines.

## Role in the System

Workflows are the **nervous system** — they coordinate agents, invoke skills, respect hooks, use tools, and follow rules. Every other primitive exists to serve the workflow.

```
Workflow orchestrates:
  → Agents (who does each step)
    → Skills (what each agent knows)
      → Tools (what each agent uses)
  → Hooks (automatic quality gates)
    → Rules (what hooks enforce)
  → CLAUDE.md (shared context for all participants)
```

## Input

Read `.claude/scaffold-decisions.md` if it exists — this is the primary source for resolved grill decisions. Extract the end-to-end workflow from the decision records.

## Workflow Design Process

### 1. Identify the Pipeline

From grill decisions (in scaffold-decisions.md), extract the end-to-end flow:

```
Trigger → Step 1 → Step 2 → ... → Output
```

Each step maps to an `agent()` call with specific tools, model, and optional structured output.

### 2. Determine Composition Pattern

| Pattern | When | DSL |
|---------|------|-----|
| Sequential | Steps depend on previous output | `pipeline()` |
| Parallel | Steps are independent | `parallel()` |
| Fan-out/fan-in | Same task from multiple angles | `parallel()` + synthesis `agent()` |
| Phased | Logical grouping for progress | `phase()` markers |
| Nested | Workflow calls workflow | `workflow()` |

### 3. Map to the DSL

Reference: `@references/workflow-dsl.md`

```javascript
export const meta = {
  name: "deploy-pipeline",
  description: "Build, test, stage, smoke-test, and promote to production",
  phases: [
    { title: "build", detail: "Compile artifacts" },
    { title: "test", detail: "Run unit and integration tests" },
    { title: "stage", detail: "Deploy to staging" },
    { title: "verify", detail: "Smoke test staging" },
    { title: "promote", detail: "Promote to production" }
  ]
};

// DSL functions (agent, pipeline, parallel, phase, log, workflow)
// are top-level globals — no import or destructuring needed.

phase("build");
log("Building artifacts...");
const build = await agent("Run the build process and report results", {
  schema: {
    type: "object",
    properties: {
      success: { type: "boolean" },
      artifacts: { type: "array", items: { type: "string" } }
    }
  }
});

phase("test");
const [unit, integration] = await parallel(
  () => agent("Run unit tests"),
  () => agent("Run integration tests")
);

phase("stage");
const staging = await agent("Deploy to staging environment");

phase("verify");
const smoke = await agent("Run smoke tests against staging", {
  model: "sonnet"
});

phase("promote");
log("Promoting to production...");
const production = await agent("Promote staging to production");
```

## Common Workflow Templates

### Research Factory

```javascript
export const meta = {
  name: "research",
  description: "Fan-out research, verify claims, synthesize cited report",
  phases: ["gather", "verify", "synthesize"]
};
```

Pattern: `parallel()` research agents → verification `agent()` → synthesis `agent()` with structured output.

### Code Review Council

```javascript
export const meta = {
  name: "review-council",
  description: "Multi-perspective code review with adversarial verification",
  phases: ["review", "challenge", "verdict"]
};
```

Pattern: `parallel()` reviewer agents (security, perf, style) → adversarial challenger → verdict synthesizer.

### Bug Investigation

```javascript
export const meta = {
  name: "investigate",
  description: "Evidence → hypotheses → refutation → root-cause report",
  phases: ["evidence", "hypothesize", "refute", "report"]
};
```

Pattern: `pipeline()` stages with `schema` passing typed data between stages.

## Dual-Track Strategy

**Default: both.** Generate the `.workflow.js` script AND an equivalent skill for every workflow. The .js script is the primary artifact; the skill provides a fallback that works without the workflow gate.

1. **Workflow script** (`.claude/workflows/<name>.workflow.js`) — primary orchestration artifact **(always generated)**
2. **Skill** (`.claude/skills/<name>/SKILL.md`) — equivalent logic using Agent tool calls **(always generated)**

Use `--js-only` to skip skill generation, or `--skill-only` to skip .js generation.

**Cross-reference both artifacts** to prevent drift:
- In the skill: `<!-- Workflow equivalent: .claude/workflows/<name>.workflow.js -->`
- In the .js file: `// Skill equivalent: .claude/skills/<name>/SKILL.md`
- Add a comment in both: `// WARNING: If you modify this file, update its counterpart to stay in sync`

The skill mirrors the workflow's logic using Agent tool calls instead of DSL `agent()` calls.

### Workflow Gate Detection

The workflow DSL requires `CLAUDE_CODE_WORKFLOWS=1`. When generating:

1. Check if the gate is set — if yes, the .js file is immediately usable
2. If not set, note in the output that the user can enable it: `export CLAUDE_CODE_WORKFLOWS=1`
3. The skill fallback works regardless of gate status

## Sandbox Awareness

Workflow scripts run in a sandboxed JS VM:
- No filesystem or Node.js APIs
- No `Date.now()`, `new Date()` (argless), `Math.random()`
- Max 524KB script size
- Resume caching requires deterministic scripts

Design accordingly. All external interaction goes through `agent()` calls — agents have tool access, scripts don't.

### Sandbox Validation (when generating .js files)

After generating a workflow .js file, scan it for sandbox violations before writing:

- `require(`, `import` from `node:`, `fs.`, `path.` → filesystem/Node.js API violation
- `Date.now()`, `new Date()` (argless), `Math.random()` → nondeterminism violation
- Check file size < 524KB

Report violations inline and fix before writing. This prevents scripts from silently failing when the gate opens.

## Generation Rules

- Every `agent()` call gets explicit `tools` — don't leave it open
- Use `schema` for typed handoffs between stages
- Add `phase()` markers for any workflow with 3+ stages
- Use `log()` for user-visible progress, not debugging
- Keep scripts focused — one workflow per concern
- Name workflows by what they accomplish, not how they work

## Upstream Dependencies

When invoked standalone, check for upstream primitives:

- **Agents** (`.claude/agents/`): If empty, warn: "No agents found. Workflows orchestrate agents — consider running `/generate-agents` first."
- **Skills** (`.claude/skills/`): If empty, warn similarly.
- **CLAUDE.md**: If missing, warn: "No CLAUDE.md found. Workflows depend on shared context."

Informational, not blocking.

## Standalone Invocation

`/generate-workflows`

`$ARGUMENTS`:
- `--name=deploy,review` — Generate only specified workflows
- `--js-only` — Generate only .workflow.js scripts (skip skill fallbacks)
- `--skill-only` — Generate only skill equivalents (skip .js scripts)
- `--quick-grill` — Abbreviated interrogation (3-5 questions)
- `--template=research|review|deploy|investigate` — Start from a template
