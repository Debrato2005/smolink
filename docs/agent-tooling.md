# Agent skills and Graphify

Smolink stores shared project skills in `.agents/skills/`. These skills guide
repository work. They are not application dependencies.

## Skills

| Skill | Use |
|---|---|
| `.agents/skills/fastapi/` | Routes, dependencies, Pydantic contracts, lifecycles, streaming, and serving |
| `.agents/skills/python-testing/` | Test behavior, async reliability, isolation, and Python-version checks |
| `.agents/skills/graphify/` | Architecture, file relationships, and dependency paths |
| Installed `asd-ste100` | Substantial technical prose changes |

Read each selected skill's `SKILL.md` before work. Read its task-specific
references when required. Use the smallest relevant skill set.

## Technical writing

The root [AGENTS.md](../AGENTS.md#technical-writing) defines the permanent
writing policy. The canonical Chele
[asd-ste100 skill](https://github.com/woosal1337/blog/tree/main/videos/ep01-the-cure-for-ai-slop/asd-ste100)
is installed in the agent's skill directory, outside this repository. If the
skill is absent, install it with the agent's normal skill installer.
Do not copy its complete rules into repository instructions.

Use Layer 1 to reduce ambiguity. Layer 2 concerns reply structure and does
not control reference-document layouts. Preserve technical names and meaningful
uncertainty even when a linter suggests simpler words.

Keep these terms consistent:

| Term | Meaning |
|---|---|
| Smolink | Product name. Preserve `smolink` in exact identifiers and values |
| PostgreSQL | Durable database. Preserve `postgres` as the Compose service name |
| Short code / `short_code` | Public lookup value, generated or custom |
| Custom alias / `alias` | User-supplied input stored as `short_code` |
| URL owner / `owner_id` | Nullable user reference on `Url` |
| Refresh-token family / `family_id` | Refresh records from one login session |
| Token identifier / `jti` | JWT claim hashed for refresh-record lookup |
| `auth_version` | User value checked against an access-token claim |
| Cache-aside | Redis lookup with PostgreSQL fallback for planned redirects |
| Sliding-window log | Redis sorted set of allowed requests in a rolling window |

Keep model and API names exact: `User`, `Url`, `ClickEvent`, `AuthIdentity`,
`RefreshToken`, and `OAuthAuthorizationRequest`. Define JWT (JSON Web Token),
OIDC (OpenID Connect), and PKCE (Proof Key for Code Exchange) at first meaningful
use in a document.

### Lint prose

Prerequisite: locate the installed skill directory. Replace `<skill-directory>`
in these commands with that path. Run from the repository root.

1. Lint normal prose:

   ```text
   python3 <skill-directory>/scripts/ste-lint.py README.md
   ```

2. Lint a procedure in strict mode:

   ```text
   python3 <skill-directory>/scripts/ste-lint.py --strict docs/development.md
   ```

3. Review each finding against the source and intended meaning.

The score counts mechanical violations per 100 words. It does not certify
ASD-STE100 compliance or factual correctness. Do not weaken a qualifier,
change an identifier, or damage technical meaning to lower the score.

## Graphify

Graphify stores a generated knowledge graph in `graphify-out/`. Use it to
locate relevant files. Check conclusions against source, tests, and README
architecture decisions.

### Query an existing graph

Prerequisite: `graphify-out/graph.json` exists. Run from the repository root.

1. Query the relevant behavior:

   ```bash
   graphify query "How does refresh-token rotation work?"
   ```

2. If needed, inspect a focused concept or relationship:

   ```bash
   graphify explain "rotate_refresh_token"
   graphify path "create_url" "Url"
   ```

`EXTRACTED` edges describe parser observations. `INFERRED` and `AMBIGUOUS` edges
are leads. Check inferred relationships in source before a design decision.
If `graphify-out/wiki/index.md` exists, use it for broad navigation.

### Refresh

After source changes, run from the repository root:

```bash
graphify update .
```

This updates structural data locally without an API call. It does not rewrite
documentation semantics. After substantial architecture or documentation
changes, a full semantic build is needed to refresh those relationships.
Invoke the repository skill for that build:

```text
/graphify .
```

The full build produces `graph.html`, `GRAPH_REPORT.md`, and `graph.json` in
`graphify-out/`. Those files contain the interactive map, community report,
and query data respectively. A full semantic build has a separate cost and
workflow from the structural update.

## Generated and historical material

`graphify-out/` is generated working data, including dated snapshots. Do not
edit its JSON, HTML, reports, or caches by hand. Updates can leave generated
files dirty. Leave them uncommitted until the repository sets a commit policy.
Missing graph outputs do not indicate an application defect.

Repository skill bundles are external guidance. Preserve their original
wording. Also preserve generated Alembic boilerplate, applied migration
history, dependency lockfiles, licenses, quotations, and dated progress records.
Use current guides to explain differences from historical designs.
