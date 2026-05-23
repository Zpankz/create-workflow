---
name: generate-workflows
description: Generate .claude/workflows/*.js orchestration scripts that compose agents, skills, hooks, and tools into automated pipelines. The workflow is the product — all other primitives serve it. Uses the Workflow DSL (agent/pipeline/parallel/phase/log). Invoked by scaffold or standalone via /generate-workflows.
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

## Workflow Design Process

### 1. Identify the Pipeline

From grill decisions, extract the end-to-end flow:

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
  phases: ["build", "test", "stage", "verify", "promote"]
};

export default async function run({ agent, pipeline, parallel, phase, log }) {
  phase("build");
  log("Building artifacts...");
  const build = await agent("Run the build process and report results", {
    tools: ["Bash", "Read"],
    structuredOutput: {
      schema: {
        type: "object",
        properties: {
          success: { type: "boolean" },
          artifacts: { type: "array", items: { type: "string" } }
        }
      }
    }
  });

  phase("test");
  const [unit, integration] = await parallel(
    () => agent("Run unit tests", { tools: ["Bash"] }),
    () => agent("Run integration tests", { tools: ["Bash"] })
  );

  phase("stage");
  const staging = await agent("Deploy to staging environment", {
    tools: ["Bash", "Read"]
  });

  phase("verify");
  const smoke = await agent("Run smoke tests against staging", {
    tools: ["Bash", "Read"],
    model: "sonnet"
  });

  phase("promote");
  log("Promoting to production...");
  const production = await agent("Promote staging to production", {
    tools: ["Bash"]
  });

  return { build, unit, integration, staging, smoke, production };
}
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

Pattern: `pipeline()` stages with `structuredOutput` passing typed data between stages.

## Dual-Track Strategy

The Workflow DSL is gated (`CLAUDE_CODE_WORKFLOWS` + `tengu_workflows_enabled`). Generate both:

1. **Workflow script** (`.claude/workflows/<name>.js`) — ready for when the gate opens
2. **Equivalent skill** (`.claude/skills/<name>/SKILL.md`) — works today using subagents

The skill mirrors the workflow's logic using Agent tool calls instead of DSL `agent()` calls. When the workflow gate opens, the skill becomes a thin wrapper or is retired.

## Sandbox Awareness

Workflow scripts run in a sandboxed JS VM:
- No filesystem or Node.js APIs
- No `Date.now()`, `new Date()` (argless), `Math.random()`
- Max 524KB script size
- Resume caching requires deterministic scripts

Design accordingly. All external interaction goes through `agent()` calls — agents have tool access, scripts don't.

## Generation Rules

- Every `agent()` call gets explicit `tools` — don't leave it open
- Use `structuredOutput` for typed handoffs between stages
- Add `phase()` markers for any workflow with 3+ stages
- Use `log()` for user-visible progress, not debugging
- Keep scripts focused — one workflow per concern
- Name workflows by what they accomplish, not how they work

## Standalone Invocation

`/generate-workflows`

`$ARGUMENTS`:
- `--name=deploy,review` — Generate only specified workflows
- `--skill-only` — Generate equivalent skills, skip .js workflow scripts
- `--skip-grill` — Use scan defaults
- `--template=research|review|deploy|investigate` — Start from a template
