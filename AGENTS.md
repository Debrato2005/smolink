## Project skills

Repository-scoped skills live in `.agents/skills/`:

- `fastapi` for FastAPI APIs, Pydantic contracts, dependencies, and serving.
- `python-testing` for Python test behavior, async lifecycles, and reliability.
- `graphify` for codebase architecture and relationship questions.

Read the selected skill before acting. The shared workflow and generated-output
policy are in [docs/agent-tooling.md](docs/agent-tooling.md).

## Testing

Use the canonical [README testing policy](README.md#testing-policy).
The README policy overrides generic testing-pyramid ratios and unconditional
test requirements in bundled skills. Preserve those external skill files.
Select E2E, realistic API/integration, or selective unit checks at the highest
practical boundary for the behavior. Browser E2E remains planned.
Use reproducible red → green → refactor checks for behavior changes and bugs.
Do not manufacture unit tests for every step or generate superficial batches
to increase test count or coverage. Before adding a test, use the
[Playbook selection questions](docs/ENGINEERING_PLAYBOOK.md#test-quality-and-coding-agents).

## Technical writing

Use ASD-STE100-inspired writing for human-readable technical prose. Use
STE-flavored mode for explanations and documentation. Use strict mode for
procedures, instructions, troubleshooting, error text, and safety-critical
content. Preserve technical terminology, identifiers, uncertainty, qualifiers,
and scientific, mathematical, and implementation meaning. Prefer clarity over
mechanical simplification. Use the installed `asd-ste100` skill for substantial
prose changes.

## Graphify

The knowledge graph in `graphify-out/` records central nodes, communities,
and relationships across files.

When the user invokes `/graphify`, use the repository's `graphify` skill before
doing anything else.

Rules:

- If `graphify-out/graph.json` exists, run `graphify query "<question>"` first for codebase questions.
- Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts.
- Use these scoped subgraphs before reading the full report or searching broadly.
- Dirty graph files are expected after hooks or updates. They do not justify skipping Graphify.
- Skip Graphify only for stale or incorrect graph output, or at the user's explicit request.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
