# Domain Glossary

## Core Terms

| Term | Definition |
|------|-----------|
| **Scaffold** | The complete set of Claude Code configuration files generated for a target repo. Includes CLAUDE.md, rules, skills, hooks, agents, tools, and workflows. |
| **Grill** | Structured interrogation pattern — one question at a time, recommended answer provided, codebase explored before asking. Resolves decisions incrementally. |
| **Grill-with-docs** | Engineering variant of grill that maintains domain documentation (CONTEXT.md glossary + docs/adr/) inline as decisions resolve. |
| **Target repo** | The repository being scaffolded. The plugin runs inside it and generates config based on what it finds. |
| **Generator** | A skill that produces one primitive of the workflow system (e.g., generate-claudemd produces shared memory, generate-rules produces constraints). Each generator is invoked by the orchestrator after the grill phase, building the workflow from its component primitives. |
| **Orchestrator** | The `/scaffold` skill that drives the full pipeline: scan → grill → compose → verify. Composes all primitives into a coherent workflow system. |
| **Primitive** | A building block of the workflow system: CLAUDE.md (shared memory), Rules (constraints), Skills (capabilities), Hooks (reflexes), Agents (specialists), Tools (instruments), Workflows (nervous system). The workflow is the product; primitives serve it. |
| **ADR** | Architectural Decision Record. Created only when a decision is hard to reverse, surprising without context, AND involves a real trade-off. All three must be true. |
| **Progressive disclosure** | SKILL.md loading strategy: metadata always loaded, body loaded when triggered, bundled resources loaded on demand. Keeps context lean. |
| **DSL** | Domain-Specific Language. For workflows, refers to the JavaScript orchestration functions: `agent()`, `pipeline()`, `parallel()`, `phase()`, `log()`, `workflow()`. |
| **Scaffold Decisions** | Persistent decision record at `.claude/scaffold-decisions.md`. Written inline during the grill as each decision resolves. Generators read this as primary input; conversation context is supplemental. Survives context compaction. |
| **Quick Grill** | Abbreviated interrogation mode (`--quick-grill`) that asks 3-5 high-signal questions instead of full grill. Produces generic output — warns the user accordingly. |
| **Dual-Track** | Optional generation mode (`--dual-track`) that produces both a `.claude/workflows/*.js` script and an equivalent skill. Default is skill-only. Cross-reference comments prevent drift. |

## Boundaries

| This plugin IS | This plugin IS NOT |
|----------------|-------------------|
| A workflow system designer that composes primitives | A runtime framework or library |
| Grill-driven (interrogation produces decisions) | Template-driven (no fill-in-the-blanks) |
| Self-contained (no external plugin dependencies at runtime) | Dependent on customaize-agent or other plugins |
| Repo-aware (scans code before asking questions) | Generic (it always explores first) |
| Decision-persistent (survives context compaction) | Context-dependent (decisions in conversation only) |
