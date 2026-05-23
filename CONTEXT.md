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

## Boundaries

| This plugin IS | This plugin IS NOT |
|----------------|-------------------|
| A scaffolding tool that generates Claude Code config | A runtime framework or library |
| Grill-driven (interrogation produces decisions) | Template-driven (no fill-in-the-blanks) |
| Self-contained (no external plugin dependencies at runtime) | Dependent on customaize-agent or other plugins |
| Repo-aware (scans code before asking questions) | Generic (it always explores first) |
