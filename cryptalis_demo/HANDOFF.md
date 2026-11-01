# Smolink Cryptalis demonstration handoff

This is the resume guide for the separate demonstration checkout. The
[Cryptalis handoff](https://github.com/Debrato2005/cryptalis/blob/main/docs/handoff.md)
owns the library continuation; its objective ledger retains all 34 objectives.
This demonstration does not qualify a production deployment.

## Saved revisions

| Purpose | Revision / branch |
|---|---|
| Original application | `498d24bae999ed53ad85e1c1f1a09ea7fa151aa4` |
| Frozen library | Cryptalis `v0.1.0a1`, `655d52271d90effb4df918a9547f61c89055fbc7` |
| Frozen demonstration | `cryptalis-demo-0.1.0a1-20261101-final`, `269aed4bcfcbbf40ffea444f2e2a748013c862d4` |
| Matched latency/resource measurement code | `2a6622311359f470412c22c53907b5fe3623a370` |
| Local writer-interruption measurement code | `e2c1be8f2001884d9e0bed14f3c24097590ff8b4` |
| Supplemental interruption evidence | `b84f54d2fde83105c3e208be1ef16af68dd54801` |
| Frozen demo branch | `demo/cryptalis-preview-20261101` |
| Follow-up branch, including this handoff | `demo/cryptalis-preview-followup-20261101` |

Original `backend/app` files, models, queries and route handlers are unchanged.
The original Smolink checkout/main branch was not used for integration edits.
The integration, tooling and reports live under `cryptalis_demo/` in this fresh
clone. Cryptalis is installed from a wheel, without an editable dependency or
`PYTHONPATH`.

## Read the evidence

- [Demonstration report](REPORT.md): original Swagger POST201, independent CF1
  database observation, current edits, wrapping/payload rotation, source-stopped
  fresh restore, current-value decrypt-back/removal and an environment without
  Cryptalis serving the original API.
- [Final matched measurements](evidence/final-pair/MEASUREMENTS.md) and
  [source/wheel binding](evidence/final-pair/pair-receipt.json): 10,000 seeded rows,
  256 samples per workload, concurrency 1/4/16. Point-read added p95 at concurrency
  1 is 4.849 ms, a MISS against 3 ms. Destination bytes are 1.5114× native;
  observed total relation/index allocation is 2.5987×, including allocation history.
- [Actual writer interruption](evidence/writer-interruption-20261101/README.md):
  running-host stop through first committed POST201 is 4.071 s for protection,
  4.501 s for wrapping rewrap and 12.169 s for payload rotation. These are single
  local observations with raw service counters and explicit resource limits.
- [Supplemental installed application journeys](evidence/supplemental/):
  Smolink crash/resume/recovery and a separate original searchable backend,
  including three distinct rotations. Their public deterministic test providers
  are separate from this demonstration's real TLS OpenBao service.
- [Primary-source comparison](COMPETITIVE.md): documented developer outcomes;
  no equivalent CipherStash runtime benchmark was executed.

The protected scope is `Url.destination`, storage-only VARCHAR(2048), with
explicit single tenancy. Destination equality/IN and search-key rotation are
not demonstrated. The typed search-rotation refusal is retained. Smolink's
existing URL API implements creation; lookup/updates/deletion in this report use
its original repository/ORM. No new management or redirect endpoint was added.
Mail/OAuth and production operation remain unqualified.

## Resume or reproduce

1. Inspect the actual checkout root, branch and Git status. Preserve the frozen
   tag and original backend source. Use the follow-up branch or a new branch for
   further work; retain each existing receipt unchanged.
2. Read [setup and integration procedures](README.md). Use Python 3.13.5 and the
   inspected wheel with SHA-256
   `eedecae8fd72a06bdf8ed95bd0aae377cabdfd51df325c50463f4f4f4b65060a`.
3. Use new absolute private/evidence directories. PostgreSQL 16 tools, Redis,
   Docker and uv are prerequisites. Source-bound helpers require a clean
   committed demo checkout and record source, artifact and provider identities.
4. Follow `measure_pair` for the native/protected pair, or the interruption
   report's `measure_outage` command for actual stop-to-commit timing. Record the
   selected Cryptalis provisioning-helper revision separately from the wheel.
   The strict-TLS helper fix is integrated into Cryptalis main.
5. Run PostgreSQL pytest checks through Cryptalis's mandatory
   `scripts/test_postgres.py` wrapper. A failed role probe stops that run; resolve
   the cause before retrying. Do not substitute another database silently.

All local app, PostgreSQL, Redis and OpenBao services from the recorded runs have
stopped. Container shells were removed after private-log retention. Original
recovery state remains outside Git. The machine-local directories are
`/workspace/scratch/smolink-preview-private`,
`/workspace/scratch/smolink-writer-interruption-private-20261101` and
`/workspace/scratch/smolink-writer-interruption-private-20261101-r2`.
They are retained custody, not new disposable targets. Keep raw dumps, keys,
tokens, credentials and external Project state private; removal did not authorize
key retirement or backup destruction. These paths are session locations, not
requirements on another machine.

## Scope of the remaining blockers

CipherStash credentials are needed only to execute CipherStash itself for the
live competitor comparison. Cryptalis and this Smolink demonstration use the
independent OpenBao provider and can be developed or reproduced without a
CipherStash account. Continue their work using native PostgreSQL oracles.

The library's remote draft GitHub Release was not created because the available
connector has no release-create operation and direct API access is denied by the
environment policy. Local release notes, payloads and artifacts are prepared.
Public package-index publication remains unapproved. Independent human review
and all seven production gates remain UNKNOWN.

This handoff changes documentation only. It does not rerun the application,
change a frozen measurement or add a new verified capability.
