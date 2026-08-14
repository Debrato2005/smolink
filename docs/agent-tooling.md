# Agent Skills and Graphify

Smolink keeps reusable, repository-scoped agent skills in `.agents/skills/`.
They are shared project guidance, not application runtime dependencies.

## Available skills

- **FastAPI** (`.agents/skills/fastapi/`) — use for FastAPI routes,
  dependencies, Pydantic contracts, application lifecycles, streaming, and
  backend-serving conventions.
- **Python testing** (`.agents/skills/python-testing/`) — use when writing or
  reviewing Python tests, async reliability paths, test contracts, flakiness,
  or multi-version validation.
- **Graphify** (`.agents/skills/graphify/`) — use for codebase architecture,
  file relationships, dependency paths, and project-content questions.

Use the smallest relevant skill set. Read the selected skill's `SKILL.md`
before acting, and follow any linked, task-specific references it requires.

## Graphify workflow

Graphify is installed as a repository skill and stores its generated knowledge
graph in `graphify-out/`. Its inputs are parsed locally; the graph is a
navigation aid, not a replacement for source code, tests, or the canonical
architecture rules in `README.md`.

### Build or refresh the graph

From the repository root:

```text
/graphify .
```

The full build produces:

- `graphify-out/graph.html` — interactive architecture map.
- `graphify-out/GRAPH_REPORT.md` — report with communities, bridge nodes, and
  suggested questions.
- `graphify-out/graph.json` — machine-readable graph used by Graphify queries.

After source-code changes, refresh the structural graph with:

```bash
graphify update .
```

Run a full `/graphify .` build again when documentation or architecture has
materially changed, or when the incremental update reports that a semantic
refresh is needed.

### Query the graph first

When `graphify-out/graph.json` exists, prefer a scoped graph query before a
broad repository search:

```bash
graphify query "How does refresh-token rotation work?"
graphify explain "rotate_refresh_token"
graphify path "create_url" "Url"
```

Treat `EXTRACTED` relationships as parser-observed and `INFERRED` or
`AMBIGUOUS` relationships as leads to verify in source. Do not make a design or
implementation decision from an inferred edge alone.

## Generated files

`graphify-out/` is generated working data. It can be refreshed locally and may
be dirty after an update; do not hand-edit its JSON or HTML. Whether to commit
graph outputs is a repository policy decision—until one is made, leave them
uncommitted and do not treat their absence as an application defect.
