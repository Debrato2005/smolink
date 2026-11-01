# Supplemental local writer interruption

This followup preserves frozen demo tag `cryptalis-demo-0.1.0a1-20261101-final`
at `269aed4`. It adds one maintenance observation per operation at committed
controller revision [`e2c1be8`](https://github.com/Debrato2005/smolink/commit/e2c1be8f2001884d9e0bed14f3c24097590ff8b4).
It uses the **same installed wheel** as the frozen demonstration, built from
Cryptalis `655d52271d90effb4df918a9547f61c89055fbc7`, with SHA-256
`eedecae8fd72a06bdf8ed95bd0aae377cabdfd51df325c50463f4f4f4b65060a`.
Provisioning reuses helper revision `fb53e9f46941c80a989c47651bca455adf488977`;
the receipt records each helper file hash separately from the library artifact.
No Cryptalis runtime or original Smolink application file changed.

## Timing definition and observations

The interval starts with `time.monotonic_ns()` immediately before SIGTERM to
a real running Uvicorn host. The old host is reaped and its health port must
refuse connections before the lifecycle command starts. It ends after a fresh
host returns the first fully read `201` from the original `POST /api/v1/urls`.
That route commits and refreshes before responding. A subsequent independent
owner connection confirms the exact ID and short code; this check is outside
the measured interval. Health alone is not database readiness.

The fixture starts with 10,000 deterministic original URL rows. Each readiness
proof creates another committed row, so the exact transition row counts below
increase. The original Redis limiter stays enabled. There is one local writer
host and no in-flight request when SIGTERM is sent. PostgreSQL, Redis and
OpenBao remain warm; each operator/host runs in a fresh interpreter with a
fresh process key cache. Components do not sum exactly because the total also
contains controller checks and process-registration work.

| Operation | Rows transitioned | Stop → POST201 (s) | Host stop (s) | Lifecycle subprocess (s) | Public Project call (s) | New host → health200 (s) | First POST (s) |
|---|---:|---:|---:|---:|---:|---:|---:|
| protect | 10,001 | 4.071012 | 0.214267 | 2.772633 | 1.772355 | 0.972307 | 0.111131 |
| rotate-wrapping | 10,002 | 4.501487 | 0.165099 | 3.232825 | 2.093462 | 0.979110 | 0.123839 |
| rotate-payload | 10,003 | 12.169280 | 0.163874 | 10.943761 | 9.906424 | 0.934752 | 0.126386 |

These are individual local observations, without a production downtime/RTO,
concurrency, repeated-tail or scaling guarantee. Earlier library-call durations
are retained separately. A search-key rotation correctly returns
`search_rotation_requires_searchable_fields` for this storage-only manifest;
its writer interruption remains **UNMEASURED**.

The fresh import/provider probe records `import cryptalis`, original application
import, provider construction, and one direct provider wrap/unwrap roundtrip.
`import cryptalis` is a lightweight package import, not full application setup.
The first wrap includes lazy SDK loading, metadata inspection, TLS and Transit
requests; these are not isolated network-latency measurements. The probe uses a
fresh process/provider while the local OpenBao service has already been warmed
by provisioning. Exact values and commands are in the receipt.

## Resource observations

The controller samples standard `/proc` counters at a requested 20 ms interval.
CPU values are **observed lower bounds**: a process can exit between samples,
and trailing ticks or short-lived workers can be missed. Memory values are
**observed maximum summed RSS**, not true peak or physical memory. Shared pages
can be counted more than once, and samples can miss bursts. These figures cover
tracked application/operator subprocesses and visible descendant local services.
They exclude the controller/sampler, Docker daemon and unrelated host work.
Shared-host contention is uncontrolled. Raw samples retain actual monotonic times.

| Operation | Process group | Observed CPU increment (s) | Observed maximum summed RSS (MiB) |
|---|---|---:|---:|
| protect | application | 1.030 | 115.223 |
| protect | openbao | 0.060 | 90.047 |
| protect | operator | 2.060 | 112.660 |
| protect | postgresql | 0.670 | 74.797 |
| protect | redis | 0.000 | 4.836 |
| rotate-wrapping | application | 1.050 | 116.777 |
| rotate-wrapping | openbao | 0.110 | 90.797 |
| rotate-wrapping | operator | 2.990 | 112.215 |
| rotate-wrapping | postgresql | 0.130 | 68.500 |
| rotate-wrapping | redis | 0.010 | 4.836 |
| rotate-payload | application | 1.000 | 116.777 |
| rotate-payload | openbao | 0.130 | 90.922 |
| rotate-payload | operator | 9.670 | 113.297 |
| rotate-payload | postgresql | 1.280 | 80.766 |
| rotate-payload | redis | 0.000 | 4.836 |

## Failure, identities and cleanup

The first controller at `806152e` safely stopped after an incorrect assumption
that Uvicorn would exit zero. Uvicorn 0.54.0 re-raises captured SIGTERM after
server shutdown, producing `-15`. Its failed receipt, logs and diagnosis remain
in [failed-806152e](failed-806152e/outage-receipt.json). No lifecycle transition
ran in that attempt. The correction accepts zero or expected SIGTERM, records
the actual code and still requires the old port to stop serving. Signal replay
does not establish that every Python finalizer ran.

The [successful receipt](verified-e2c1be8/outage-receipt.json) binds the clean
revision, before/after source hashes, interpreter and dependency versions,
provider public identities, installed-wheel binding, helper hashes, commands,
raw responses and counter definitions. All source hashes remain unchanged.
The resource thread terminated without error. Newly created host, PostgreSQL,
Redis and OpenBao services stopped; private recovery files, keys and state were
retained outside Git. Earlier receipts and private state were not reused.
The [hardware observation](environment-observed-after.json) was collected after
the run and is labelled accordingly. SHA256SUMS covers all retained public files.

Reproduce from the measured clean commit with new private and evidence paths:

```sh
PATH=/absolute/postgresql16/bin:$PATH .venv/bin/python -m cryptalis_demo.measure_outage \
  --cryptalis-checkout /absolute/cryptalis-production \
  --wheel /absolute/cryptalis-0.1.0a1-py3-none-any.whl \
  --library-revision 655d52271d90effb4df918a9547f61c89055fbc7 \
  --redis-server /absolute/redis-server \
  --private-workdir /absolute/new-private-directory \
  --evidence /absolute/new-public-evidence-directory
```
