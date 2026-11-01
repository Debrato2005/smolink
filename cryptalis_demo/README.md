# Cryptalis preview in the original Smolink backend

For the saved revisions, completed evidence, stopped-service state and next
steps, start with the [demonstration handoff](HANDOFF.md). The
[report](REPORT.md) and [supplemental writer-interruption measurements](evidence/writer-interruption-20261101/README.md)
retain their own exact measurement revisions and limits.

This branch uses Smolink commit `498d24bae999ed53ad85e1c1f1a09ea7fa151aa4`.
All original application, model, query and route files stay unchanged. The
integration replaces the FastAPI session dependency and uses an installed
Cryptalis wheel through its public `Project` API.

The protected field is `Url.destination`, with native `VARCHAR(2048)` values
and an explicit single-tenant storage-only profile. URL ownership and account
authorization stay with Smolink. The manifest does not supply authorization.
Search over destination is outside this demonstration. This storage-only profile
refuses search-key rotation with `search_rotation_requires_searchable_fields`.
The independent searchable backend supplies separate search-rotation evidence.

The original app implements `POST /api/v1/urls`, `/health`, and the documented
auth routes. Its `/docs` and `/openapi.json` are the existing Swagger/OpenAPI
interfaces. URL lookup, edits and deletion use its existing repository and ORM;
this branch adds no URL management or redirect endpoint. Email, Google OAuth,
production deployment and all seven Cryptalis production gates remain unqualified.

## Install the artifact normally

Use Python 3.13.5 for this Smolink revision. From this clone's root, create a
fresh environment and supply the verified wheel directory:

```sh
uv venv --python 3.13.5 .venv
uv pip install --python .venv/bin/python --find-links /absolute/wheel-directory \
  -r cryptalis_demo/requirements.txt
```

The retained requirements file records the exact installed dependency versions.
It does not use an editable Cryptalis dependency or `PYTHONPATH`. The original
backend allows newer compatible dependencies; the demonstration pins the
resolved cell. Cryptalis uses psycopg for both matched configurations, instead
of the asyncpg URL shown in Smolink's original `.env.example`.

## Prepare private local services

Prerequisites are PostgreSQL 16 server/client tools, Redis, Docker and uv.
Run as a normal operating-system account. Add PostgreSQL and Redis binaries
to `PATH`. Run from this clone's root without a `.env` file. The host refuses
a current-directory `.env` so explicit settings cannot be mixed with that file.
Create new private work directories outside both repositories.
Do not put configuration, tokens, database dumps or state into Git.

```sh
.venv/bin/python -m cryptalis_demo.provision_provider \
  --workdir /absolute/private/openbao --cryptalis-source /absolute/cryptalis
.venv/bin/python -m cryptalis_demo.setup \
  --workdir /absolute/private/database \
  --provider-config /absolute/private/openbao/provider-config.json \
  --cryptalis-checkout /absolute/cryptalis --rows 10000
redis-server --port 0 --unixsocket /absolute/private/database/redis.sock \
  --unixsocketperm 700 --save '' --appendonly no
```

The PostgreSQL helper reuses Cryptalis's existing disposable-cluster and role
provisioning code. It creates distinct owner, runtime and plaintext roles with
random credentials. It loads 10,000 deterministic synthetic original `Url`
rows and one verified user. The dataset receipt records the exact input hash.
The provider helper runs a real TLS OpenBao service and provisions two narrow
Transit keys and tokens. The service is local demonstration custody, with no
production identity, HA or durable external-audit claim.

The private `config.json` names credential and token files, schema, provider
identities and an external deployment-state directory. `host.py` checks private
file ownership and permissions before use. Keep the state directory outside
database backups. Preserve the provider recovery material and earlier readers.

## API works, then encryption works

Start native Smolink first:

```sh
.venv/bin/python -m cryptalis_demo.host \
  --config /absolute/private/database/config.json --mode native --port 8000
```

Open `http://127.0.0.1:8000/docs` and execute the existing URL creation route.
Use `/health` and `/openapi.json` to inspect the actual app. Stop this process
before changing the data lifecycle. Collect the native benchmark before protection.

```sh
.venv/bin/python -m cryptalis_demo.manage doctor \
  --config /absolute/private/database/config.json
.venv/bin/python -m cryptalis_demo.manage protect \
  --config /absolute/private/database/config.json \
  --writers-stopped 'Only this disposable host writes; all host workers stopped'
.venv/bin/python -m cryptalis_demo.host \
  --config /absolute/private/database/config.json --mode protected --port 8000
```

Use the same API request after protection. The response contains the authorized
plaintext destination. Read `urls.destination` through an independent owner
connection to observe a CF1 binary frame. Keep raw credentials and backup files
private. The host supplies authorization; possession of the source, manifest
and database dump does not grant access to the external Transit keys.

## Lifecycle and removal

Stop every application writer before each command. Each CLI call reports its
phase and measured duration. The public `Project` API records resumable plans
and deployment pins in its external state directory. Inspect `status` after an
interruption; repeat the interrupted operation to resume it. Do not repeat a
completed rotation merely to obtain status, because that starts a new rotation.

```sh
.venv/bin/python -m cryptalis_demo.manage rotate-payload \
  --config /absolute/private/database/config.json --writers-stopped 'All local host workers stopped'
.venv/bin/python -m cryptalis_demo.manage rotate-wrapping \
  --config /absolute/private/database/config.json --writers-stopped 'All local host workers stopped'
.venv/bin/python -m cryptalis_demo.manage decrypt \
  --config /absolute/private/database/config.json --writers-stopped 'All local host workers stopped' \
  --retained-backups 'Retain both Transit keys, wrappers and required readers for retained encrypted backups'
```

Wrapping rotation leaves payloads unchanged and moves the root wrappers to the
second provisioned Transit key. After success the helper publishes the new
provider selection in the private config. If the process stops between those
steps, inspect the external Project state before selecting the provider for resume.
This local helper does not implement distributed provider publication.

Start `host.py --mode removed` with the plaintext role in a fresh process.
Check that the latest committed edit is present and that native creation still
works. Then stop writers and remove generated objects:

```sh
.venv/bin/python -m cryptalis_demo.manage remove \
  --config /absolute/private/database/config.json --writers-stopped 'All local host workers stopped' \
  --application-verified 'Fresh native host returned the latest committed value and created a URL'
```

Verify another native restart in an environment without Cryptalis. Native and
removed modes import no Cryptalis module. Keep recovery keys and state; removal
does not authorize key retirement or backup destruction.

## Fresh restore and current edits

After stopping the live host, edit through the original ORM and export the
actual protected database with its matching external Project state:

```sh
.venv/bin/python -m cryptalis_demo.journey \
  --config /absolute/private/database/config.json --mode protected --edit before-backup
.venv/bin/python -m cryptalis_demo.recover \
  --config /absolute/private/database/config.json \
  --source-cluster /absolute/private/database/cluster \
  --workdir /absolute/private/fresh-recovery --cryptalis-checkout /absolute/cryptalis \
  --receipt /absolute/public-evidence/fresh-recovery.json
.venv/bin/python -m cryptalis_demo.journey \
  --config /absolute/private/fresh-recovery/config.json \
  --mode protected --expect before-backup --edit after-recovery
```

The recovery helper retains the protected dump and copied state privately. It
stops the source PostgreSQL cluster before starting a new target, restores
with native PostgreSQL tools, calls public `Project.recover`, verifies the
latest committed edit and creates a URL through the original route. Its receipt
measures backup, restore, adoption and source-stop-to-first-committed-HTTP-write
intervals. These are local measurements, with no production RPO/RTO guarantee.
Use the new `fresh-recovery/config.json` for decrypt and removal.

After removal, use `journey --mode removed --expect after-recovery` from a fresh
environment with the same pinned dependencies except Cryptalis. It checks the
latest value, native `VARCHAR(2048)` type and absence of Cryptalis-owned
relations through an independent connection. Start the original API with
`host --mode removed` and capture its existing Swagger UI with
`python -m cryptalis_demo.capture_swagger --url http://127.0.0.1:8000
--output /absolute/evidence/swagger.png --receipt /absolute/evidence/swagger.json`.

Stop the disposable Redis and PostgreSQL services when finished. Retain all
private data, provider recovery material, state and backup keys. This exercise
authorizes no key destruction.

## Reproduce a source-bound measurement pair

Commit the demo source first. Keep the wheel and initialized OpenBao service
from the preceding setup. Choose new absolute directories outside both Git
checkouts and include PostgreSQL 16 tools in PATH:

```sh
PATH=/absolute/postgresql16/bin:$PATH .venv/bin/python -m cryptalis_demo.measure_pair \
  --provider-config /absolute/private/openbao/provider-config.json \
  --cryptalis-checkout /absolute/cryptalis \
  --library-revision 655d52271d90effb4df918a9547f61c89055fbc7 \
  --wheel /absolute/artifacts/cryptalis-0.1.0a1-py3-none-any.whl \
  --redis-server /absolute/redis-server \
  --private-workdir /absolute/private/new-pair \
  --evidence /absolute/evidence/new-pair --samples 256
uv run --locked cryptalis_demo/render_measurements.py --evidence /absolute/evidence/new-pair
```

The helper requires a clean demo checkout, verifies installed Cryptalis bytes
against the wheel, creates a new 10,000-row database and private Redis service,
runs native and protected modes, and stops those services. It retains recovery
files privately. `pair-receipt.json` records the demo commit, source hashes before
and after, wheel identity, deterministic dataset, exact commands, service versions,
provider identities, pool/cache settings and cleanup outcomes. It records CPU
quota and memory limit; shared-host contention is not controlled. Rendering reads
the existing raw samples and performs no new database measurement.

## Evidence limits

Measure native and protected modes in separate fresh processes with identical
rows, driver, dependency versions, request trace and resource conditions. Retain
raw latency samples, errors and storage costs. The supported latency/storage
targets are targets; a measured miss remains a miss. Historical Cryptalis
microbenchmarks are not current Smolink measurements.

Run PostgreSQL pytest journeys only through Cryptalis's mandatory
`scripts/test_postgres.py` wrapper. The existing installed-wheel Smolink
qualification includes interruption, backup/fresh adoption, current-value
removal and an import-denied native restart. It is separate from this live-host
presentation and must have its own exact receipt. Never archive the private
service directories as public evidence.
