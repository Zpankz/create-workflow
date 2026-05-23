---
name: generate-workflows
description: Generate .workflow.js scripts that compose agents into automated pipelines using the Claude Code Workflow DSL. Produces both .js scripts and equivalent skills by default. Covers full DSL surface (agent, pipeline, parallel, phase, log, workflow, budget, args), sandbox constraints, anti-patterns, and production-ready generation guidance. Invoked by scaffold or standalone via /generate-workflows.
---

# Generate Workflows

Produce `.claude/workflows/*.workflow.js` scripts — the orchestration layer that composes agents into automated pipelines using deterministic JavaScript control flow.

## Role in the System

Workflows are the **nervous system** — they coordinate agents, invoke skills, respect hooks, and follow rules. Every other primitive exists to serve the workflow.

```
Workflow orchestrates:
  → Agents (who does each step)
    → Skills (what each agent knows)
  → Hooks (automatic quality gates)
    → Rules (what hooks enforce)
  → CLAUDE.md (shared context for all participants)
```

## Cross-Tool Scope

`.workflow.js` scripts are **Claude Code only** — gated behind `CLAUDE_CODE_WORKFLOWS=1`. For non-Claude-Code targets (Codex, Hermes, Pi, Antigravity), generate **skill-only** output. The skill fallback works on all tools.

## Input

Read `.claude/scaffold-decisions.md` if it exists — primary source for resolved grill decisions. Extract the end-to-end workflow from decision records.

---

## Workflow Design Process

### 1. Confirm the Gate

Check if `CLAUDE_CODE_WORKFLOWS=1` is set. If not, the .js file is still worth writing — but tell the user they must enable it:

```bash
export CLAUDE_CODE_WORKFLOWS=1 && claude
```

Or persistently in `.claude/settings.local.json`:
```jsonc
{ "env": { "CLAUDE_CODE_WORKFLOWS": "1" } }
```

### 2. Decide Whether a Workflow Is the Right Tool

| The job | Right tool |
|---|---|
| One subagent, one task | Plain **Agent** tool — no workflow |
| Reusable procedure where Claude picks steps | A **Skill** |
| Many subagents in a fixed shape, deterministic, resumable | A **Workflow** |

A workflow earns its cost when ALL of these hold: work is parallel or multi-stage; orchestration should be deterministic and resumable; isolating each step in fresh context is an advantage.

### 3. Find the Shape

Answer these before writing code — they pick the topology:

1. **Unit of work** — what one subagent does once (review one file, research one question)
2. **Count** — known list → map. Unknown count → loop.
3. **Topology** — independent units → fan-out. Ordered stages → pipeline. Target count or budget cap → loop.
4. **Barrier needed?** — Does a later step need ALL earlier results at once (dedup, merge, count-based exit)? Yes → `parallel()`. No → `pipeline()`.
5. **Structured handoff?** — Does a step need typed data back? → add `schema`.

### 4. The Decision That Matters Most: `pipeline` vs `parallel`

**`pipeline` is the default for multi-stage work.** Each item flows through every stage on its own — no barrier between stages. Item A can be in stage 3 while item B is in stage 1.

**`parallel` is a barrier.** It waits for every task before returning. Use ONLY when a step genuinely needs the entire previous result set:

- Dedup or merge across the full set
- Early-exit on a total count ("0 findings → skip verification")
- A prompt that compares one item against all others

Not justified by: "I need to flatten/filter first" (do that inside a pipeline stage) or "it is cleaner" (a pipeline models separate stages fine).

---

## The DSL — Complete Reference

### Script Structure

Every workflow has exactly two parts:

**Part 1 — `meta` block (must be the first statement)**

```javascript
export const meta = {
  name: "deploy-pipeline",
  description: "Build, test, stage, smoke-test, and promote",
  whenToUse: "Before deploying to production",
  phases: [
    { title: "build", detail: "Compile artifacts" },
    { title: "test", detail: "Run unit and integration tests" },
    { title: "verify", detail: "Smoke test staging", model: "haiku" }
  ]
};
```

**`meta` MUST be a pure literal** — no variables, function calls, spreads, or template strings inside it. Build dynamic values in the body, never in `meta`.

**`meta.phases[].model` is display-only** — it appears in the permission dialog but does NOT set the model at runtime. Set `model` on each `agent()` call separately.

**Part 2 — Body (async JavaScript)**

Everything after `meta` is the body. Top-level `await` works. These globals are injected — **do not import anything**:

| Global | Purpose |
|---|---|
| `agent(prompt, opts?)` | Spawn one fresh-context subagent |
| `pipeline(items, s1, s2, …)` | Stream items through stages, no barrier |
| `parallel(thunks)` | Run an array of thunks concurrently (a barrier) |
| `phase(title)` | Group agents under a heading in `/workflows` |
| `log(msg)` | Emit a narrator line above the progress tree |
| `console` | Standard console, routed into the workflow log |
| `budget` | `{ total, spent(), remaining() }` — for budget-aware loops |
| `args` | Whatever was passed — passed through unchanged. `undefined` if nothing |
| `workflow(name, args?)` | Run another workflow inline (one level of nesting only) |

The body's `return` value becomes the tool result handed back to Claude.

### `agent(prompt, opts?)`

The core primitive. Returns the agent's final text as a string, or a validated object if `schema` is set. Returns `null` if the user skips it.

**Valid options:**

| Option | Type | Purpose |
|---|---|---|
| `model` | `'haiku' \| 'sonnet' \| 'opus' \| 'inherit' \| modelId` | Model selection. Omit → inherits session model |
| `schema` | JSON Schema object | Force structured output. AJV-validated, agent retries on mismatch |
| `label` | string | Display label for the agent call |
| `phase` | string | Associate with a named phase |
| `isolation` | `'worktree'` | Run in fresh git worktree (~200-500ms overhead) |
| `agentType` | string | Agent definition to use (e.g., custom `.claude/agents/*.md`) |
| `stallMs` | number | Override stall timeout (default 180000ms = 3min) |

**There is NO `tools` option.** Agents have access to all tools in the session — you cannot restrict per-agent.

### `pipeline(items, stage1, stage2, …)`

Stream items through staged functions with NO barrier between stages:

```javascript
const results = await pipeline(
  files,
  (file) => agent(`Review ${file} for bugs`, { schema: FINDINGS }),
  (review) => parallel(
    (review?.findings ?? []).map(f => () =>
      agent(`Verify finding: ${f.title}`, { schema: VERDICT })
    )
  )
);
```

Each item flows independently — item A can finish stage 2 while item B is still in stage 1.

### `parallel(thunks)`

Run an array of thunks concurrently and wait for all. **Takes a single array argument, NOT variadic.**

```javascript
// CORRECT — single array argument
const results = await parallel([
  () => agent("Security review"),
  () => agent("Performance review"),
  () => agent("Style review")
]);

// WRONG — variadic form throws
const results = await parallel(
  () => agent("Security review"),
  () => agent("Performance review")
);
```

**Thunks, not promises.** Must be `[() => agent(…)]`, never `[agent(…)]`. Bare calls start immediately and defeat the concurrency limiter.

**Always `.filter(Boolean)`.** A thunk that throws or is skipped resolves to `null`. Result arrays have holes by design:

```javascript
const results = await parallel(items.map(i => () =>
  agent(`Process ${i}`, { schema: RESULT })
));
const valid = results.filter(Boolean);
```

### `args` Normalization

`args` is passed through unchanged — an object stays an object, a string stays a string, nothing gives `undefined`. Always normalize before reading fields:

```javascript
const input = typeof args === 'string'
  ? (() => { try { return JSON.parse(args) } catch { return args } })()
  : args;
const threshold = input?.minUsers ?? 20;
```

Do NOT call `JSON.parse(args)` unconditionally — if `args` is already an object, that throws.

### Budget-Aware Loops

```javascript
while (budget.total && budget.remaining() > 50_000) {
  const batch = await agent(`Find more issues`, { schema: FINDINGS });
  if (!batch?.findings?.length) break;
  allFindings.push(...batch.findings);
}
```

**Critical:** Without the `budget.total` guard, `remaining()` is `Infinity` → the loop sprints into the 1000-agent lifetime cap and throws. Always guard with `budget.total &&`.

---

## Sandbox Constraints

| Constraint | Details |
|---|---|
| Script size | 524,288 bytes max |
| No filesystem | No `require`, `import`, `fs`, `path`, `process` |
| No nondeterminism | `Date.now()`, argless `new Date()`, `Math.random()` throw |
| Lifetime cap | 1000 total agent calls per workflow run |
| Concurrent agents | min(16, max(2, cores-2)) — excess calls queue |
| Stall timeout | 3 minutes default per agent (override with `stallMs`) |
| VM timeout | 30 seconds synchronous execution |
| Nesting | `workflow()` calls limited to one level |

**Why nondeterminism is banned:** Resume caching. `resumeFromRunId` replays completed `agent()` calls when prompt+opts are unchanged. Timestamps would break cache keys.

**Pass timestamps via `args`** and stamp results after the workflow returns. Vary "randomness" by loop index.

All file read/write/Bash work belongs **inside an `agent()` call** — agents have tools, the orchestrator does not.

---

## Model Selection Strategy

| Work type | Model | Rationale |
|---|---|---|
| Cheap, high-volume, mechanical (classification, summarization) | `'haiku'` | 3x cost savings, 90% capability |
| Judgment-heavy analysis, code review | `'sonnet'` or inherited | Best coding balance |
| Architecture decisions, complex reasoning | `'opus'` | Deepest reasoning |

Set `model` in BOTH the `meta.phases[]` entry (honest permission dialog) and the `agent()` call (actual runtime effect).

**No validation on model strings.** A typo (`'hauku'`) is silently passed through and the agent fails later. Spell exactly.

---

## Resume and Caching

Same script + same args = 100% cache hit on resume. To iterate:

1. Edit the saved workflow file
2. Re-invoke with `Workflow({ scriptPath, resumeFromRunId })`
3. Every `agent()` call before your edit replays instantly from cache
4. Only the changed call and everything after it re-runs

Never re-paste the whole script after the first run — edit the file.

---

## Sandbox Validation

After generating a .js file, scan for violations before writing:

```bash
# Check for filesystem/Node.js API violations
grep -nE 'require\(|import .* from .node:|fs\.|path\.' "$FILE"

# Check for nondeterminism violations
grep -nE 'Date\.now\(\)|new Date\(\)|Math\.random\(\)' "$FILE"

# Check file size
wc -c < "$FILE"  # must be < 524288
```

If the plugin's linter is available, run it from the plugin root:
```bash
node scripts/validate-workflow.mjs "$FILE"
```

Fix all violations before writing the file.

---

## Common Workflow Patterns

### Fan-Out Research

Independent research from multiple angles, then synthesize.

```javascript
export const meta = {
  name: "research",
  description: "Fan-out research, verify claims, synthesize cited report",
  phases: [
    { title: "Gather" },
    { title: "Verify" },
    { title: "Synthesize" }
  ]
};

const QUESTIONS = typeof args === 'string'
  ? (() => { try { return JSON.parse(args) } catch { return { questions: [args] } } })()
  : args;
const questions = QUESTIONS?.questions ?? ["What are the main findings?"];

phase("Gather");
const research = await parallel(
  questions.map(q => () =>
    agent(`Research: ${q}`, { label: `research:${q.slice(0, 30)}`, phase: "Gather", schema: {
      type: "object",
      required: ["findings"],
      properties: { findings: { type: "array", items: { type: "string" } } }
    }})
  )
);

phase("Verify");
const verified = await parallel(
  research.filter(Boolean).flatMap(r =>
    (r.findings ?? []).map(f => () =>
      agent(`Verify this claim. Try to refute it: ${f}`, { model: "haiku", phase: "Verify", schema: {
        type: "object",
        required: ["isReal"],
        properties: { isReal: { type: "boolean" }, evidence: { type: "string" } }
      }})
    )
  )
);

phase("Synthesize");
const report = await agent(
  `Synthesize a cited report from verified findings:\n${JSON.stringify(verified.filter(Boolean))}`,
  { model: "opus", phase: "Synthesize" }
);

return report;
```

### Multi-Stage Pipeline (Review → Verify)

Each item flows through stages independently — no wasted wall-clock.

```javascript
export const meta = {
  name: "review-verify",
  description: "Review across dimensions, adversarially verify each finding",
  phases: [{ title: "Review" }, { title: "Verify" }]
};

const FINDINGS = { type: "object", required: ["findings"], properties: {
  findings: { type: "array", items: { type: "object", required: ["title", "file"],
    properties: { title: { type: "string" }, file: { type: "string" } } } } } };

const VERDICT = { type: "object", required: ["isReal"], properties: {
  isReal: { type: "boolean" }, reason: { type: "string" } } };

const DIMENSIONS = [
  { key: "bugs", prompt: "Find logic bugs in changed files." },
  { key: "perf", prompt: "Find performance regressions." },
  { key: "tests", prompt: "Find missing test coverage." }
];

const results = await pipeline(
  DIMENSIONS,
  d => agent(d.prompt, { label: `review:${d.key}`, phase: "Review", schema: FINDINGS }),
  review => parallel(
    (review?.findings ?? []).map(f => () =>
      agent(`Adversarially verify: ${f.title} (${f.file})`,
        { label: `verify:${f.file}`, phase: "Verify", model: "haiku", schema: VERDICT })
        .then(v => ({ ...f, verdict: v }))
    )
  )
);

const confirmed = results.flat().filter(Boolean).filter(f => f.verdict?.isReal);
return { confirmedCount: confirmed.length, confirmed };
```

### Dev Pipeline (Build → Quality → Review)

Sequential phases with parallel quality gates.

```javascript
export const meta = {
  name: "dev-pipeline",
  description: "Implement, run quality gates in parallel, review, verify",
  phases: [
    { title: "implement" },
    { title: "quality", model: "haiku" },
    { title: "review" },
    { title: "verify" }
  ]
};

const input = typeof args === 'string'
  ? (() => { try { return JSON.parse(args) } catch { return args } })()
  : args;
const task = input?.task ?? input ?? "Implement the requested change";

phase("implement");
log("Implementing changes...");
const impl = await agent(`Read CLAUDE.md for architecture. Task: ${task}`, {
  model: "opus", label: "implementer", phase: "implement"
});

phase("quality");
log("Running quality gates...");
const [lint, types, tests] = await parallel([
  () => agent("Run linter, fix issues, report remaining", {
    model: "haiku", label: "linter", phase: "quality"
  }),
  () => agent("Run type checker, report errors", {
    model: "sonnet", label: "type-check", phase: "quality"
  }),
  () => agent("Run test suite, report failures", {
    model: "sonnet", label: "test-runner", phase: "quality"
  })
]);

phase("review");
const review = await agent(
  `Review changes. Quality results:\nLint: ${lint ?? "skipped"}\nTypes: ${types ?? "skipped"}\nTests: ${tests ?? "skipped"}`,
  { model: "opus", label: "reviewer", phase: "review", schema: {
    type: "object",
    required: ["approved", "blocking"],
    properties: {
      approved: { type: "boolean" },
      blocking: { type: "number" },
      findings: { type: "array", items: { type: "string" } }
    }
  }}
);

if (review && !review.approved && review.blocking > 0) {
  log(`Fixing ${review.blocking} blocking issues...`);
  await agent(`Fix these issues:\n${JSON.stringify(review.findings)}`, {
    model: "opus", label: "fix-blockers", phase: "review"
  });
}

phase("verify");
const result = await agent("Run full quality suite. Report pass/fail with evidence.", {
  model: "sonnet", label: "verifier", phase: "verify", schema: {
    type: "object",
    required: ["passed"],
    properties: { passed: { type: "boolean" }, summary: { type: "string" } }
  }
});

log(`Pipeline ${result?.passed ? "PASSED" : "FAILED"}`);
return result;
```

### Budget-Aware Bug Hunt

Loop until budget exhausted or target count reached.

```javascript
export const meta = {
  name: "bughunt",
  description: "Find bugs until budget runs out or target count reached",
  phases: [{ title: "Hunt" }, { title: "Verify" }]
};

const input = typeof args === 'string'
  ? (() => { try { return JSON.parse(args) } catch { return args } })()
  : args;
const target = input?.target ?? 10;

const allBugs = [];
let round = 0;

phase("Hunt");
while (budget.total && budget.remaining() > 50_000 && allBugs.length < target) {
  round++;
  log(`Round ${round}, ${allBugs.length} bugs so far...`);
  const batch = await agent(
    `Find bugs not in this list:\n${JSON.stringify(allBugs.map(b => b.title))}`,
    { label: `hunt:r${round}`, phase: "Hunt", schema: {
      type: "object", required: ["bugs"],
      properties: { bugs: { type: "array", items: {
        type: "object", required: ["title", "file"],
        properties: { title: { type: "string" }, file: { type: "string" } }
      }}}
    }}
  );
  if (!batch?.bugs?.length) break;
  allBugs.push(...batch.bugs);
}

phase("Verify");
const verified = await parallel(
  allBugs.map(b => () =>
    agent(`Verify bug: ${b.title} in ${b.file}. Is it real?`, {
      model: "haiku", label: `verify:${b.title.slice(0, 20)}`, phase: "Verify", schema: {
        type: "object", required: ["isReal"],
        properties: { isReal: { type: "boolean" }, reason: { type: "string" } }
      }
    }).then(v => ({ ...b, verdict: v }))
  )
);

const confirmed = verified.filter(Boolean).filter(b => b.verdict?.isReal);
return { total: allBugs.length, confirmed: confirmed.length, bugs: confirmed };
```

### Using Custom Agent Types

Reference `.claude/agents/*.md` definitions:

```javascript
const review = await agent("Review the auth module for vulnerabilities", {
  agentType: "security-reviewer",
  label: "security-audit",
  phase: "review"
});
```

The definition's model, instructions, and persona are honored. The agent still has full tool access.

---

## Anti-Patterns — What NOT to Generate

| Anti-pattern | Problem | Fix |
|---|---|---|
| `parallel(() => agent(...), () => agent(...))` | Variadic form — throws | `parallel([() => agent(...), () => agent(...)])` |
| `[agent(...), agent(...)]` inside parallel | Bare calls, not thunks | `[() => agent(...), () => agent(...)]` |
| Missing null handling after parallel/pipeline | Null slots from skipped/failed agents | `.filter(Boolean)` on arrays, or `?? fallback` on destructured vars |
| `const [a, b] = await parallel([...]).then(r => r.filter(Boolean))` | Filtering shifts positions — `b` gets `a`'s value if `a` is null | Destructure without filter, handle nulls: `a ?? "skipped"` |
| Dynamic values in `meta` block | Parser rejects non-literal meta | Keep meta pure literal, compute in body |
| `agent(prompt, { tools: [...] })` | `tools` is not a valid option | Remove — agents inherit session tools |
| `Math.random()` / `Date.now()` | Sandbox throws on nondeterminism | Pass timestamps via `args`, vary by index |
| `require('fs')` / `import` | No Node APIs in sandbox | All file work inside `agent()` calls |
| Unguarded budget loop | Runs to 1000-agent cap | Guard: `budget.total && budget.remaining() > 50_000` |
| Barrier when not needed | `parallel()` wastes fast items' idle time | Use `pipeline()` unless you need the full set |
| Model set only on `meta.phases[]` | Display-only, doesn't set runtime model | Set `model` on each `agent()` call |
| `JSON.parse(args)` unconditionally | Throws if args is already an object | Normalize: parse only when `typeof args === 'string'` |

---

## Dual-Track Strategy

**Default: generate both.** Every workflow gets a `.workflow.js` script AND an equivalent skill.

1. **Workflow script** (`.claude/workflows/<name>.workflow.js`) — primary orchestration artifact
2. **Skill** (`.claude/skills/<name>/SKILL.md`) — equivalent logic using Agent tool calls

Use `--js-only` to skip skill generation, or `--skill-only` to skip .js generation.

**Cross-reference both artifacts** to prevent drift:
- In the skill: `<!-- Workflow equivalent: .claude/workflows/<name>.workflow.js -->`
- In the .js: `// Skill equivalent: .claude/skills/<name>/SKILL.md`
- Both: `// WARNING: If you modify this file, update its counterpart to stay in sync`

The skill mirrors workflow logic using Agent tool calls instead of DSL `agent()` calls.

### Cross-Tool Target Matrix

| Target tool | .workflow.js | Skill | Notes |
|---|---|---|---|
| Claude Code | Yes | Yes | Full dual-track |
| Antigravity/Gemini | No | Yes | .workflow.js is Claude Code only |
| Codex | No | Yes | Skill uses Agent tool |
| Hermes | No | Yes | Skill adapted to Hermes patterns |
| Pi | No | Yes | Skill adapted to Pi patterns |

---

## Caps and Limits

| Limit | Value | Behavior |
|---|---|---|
| Lifetime agents | 1000 per workflow run | Throws on exceed |
| Concurrent agents | min(16, max(2, cores-2)) | Excess calls queue, all finish |
| Script size | 524,288 bytes | Rejected at parse time |
| Stall timeout | 180,000ms (3min) default | Override with `stallMs` per agent |
| VM timeout | 30,000ms synchronous | Throws if orchestrator JS blocks |
| Nesting depth | 1 level | `workflow()` from child throws |
| Worktree overhead | ~200-500ms + disk per agent | Use only when parallel agents mutate files |

---

## Generation Rules

- Use `schema` for any result a later line reads a field off — keep schemas small and `required`-tight
- Add `phase()` markers for any workflow with 3+ stages
- Use `log()` for user-visible progress, not debugging
- Keep scripts focused — one workflow per concern
- Name workflows by what they accomplish, not how they work
- Stringify data into next prompt for inter-stage handoff (`JSON.stringify`) — orchestrator shares no memory with subagents
- Always normalize `args` before reading fields
- Always handle nulls from `parallel()` and `pipeline()` — `.filter(Boolean)` on arrays, `?? fallback` on destructured vars (never both)
- For Haiku phases, set `model` in both `meta.phases[]` AND `agent()` calls

## Upstream Dependencies

When invoked standalone, check for upstream primitives:

- **Agents** (`.claude/agents/`): If empty, warn: "No agents found. Workflows can use `agentType` to reference agent definitions."
- **Skills** (`.claude/skills/`): If empty, warn similarly.
- **CLAUDE.md**: If missing, warn: "No CLAUDE.md found. Agent prompts should reference it for shared context."

Informational, not blocking.

## Standalone Invocation

`/generate-workflows`

`$ARGUMENTS`:
- `--name=deploy,review` — Generate only specified workflows
- `--js-only` — Generate only .workflow.js scripts (skip skill fallbacks)
- `--skill-only` — Generate only skill equivalents (skip .js scripts)
- `--quick-grill` — Abbreviated interrogation (3-5 questions)
- `--template=research|review|deploy|investigate|bughunt` — Start from a template
