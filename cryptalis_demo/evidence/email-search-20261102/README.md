# Protected account email in the original Smolink API

This run protects `User.email` with blind-index equality and uniqueness, alongside the
earlier storage-only `Url.destination`. It answers what the frozen demonstration left
unmeasured: real-application equality search, uniqueness, search-key rotation and the
equality and indexed-storage targets. Files under `backend/` are unchanged.

| Item | Identity |
|---|---|
| Library | Cryptalis `0.1.0a2.dev2`, development commit [`bd223c1`](https://github.com/Debrato2005/cryptalis/commit/bd223c1) |
| Wheel SHA-256 | `ccebae5628e991eb4e8faf5e44e049a3c97aca3a41ff67f3cbb73ada72a1c3ec`, rebuilt identically from a clean checkout of that commit |
| Stack | Python 3.13.12, PostgreSQL 16.2, Redis 6.2.14, SQLAlchemy 2.1.3, psycopg 3.3.6, FastAPI 0.162.0 |
| Data | 10,001 deterministic accounts and 1,000 URLs, dataset SHA-256 `5f5ae0fb1a090ac649b72cb9b108fb85128377c6a53d49d106d12ac93f1d46b8` |
| Provider | `DevelopmentKeyProvider` key file, not the frozen demonstration's OpenBao |

This does not replace the [frozen demonstration](../../REPORT.md), which keeps library
`v0.1.0a1` and its own results. It is development evidence, not a production qualification.

## API behavior

[`journey.log`](journey.log) records one complete run on a fresh cluster. These five
responses are identical before protection, while protected, after payload rotation,
after search rotation and after removal:

| Request | Status |
|---|---|
| `POST /auth/login` with a mixed-case email | 200 |
| `GET /auth/me` | 200, returning the stored email |
| `POST /auth/login`, wrong password | 401 |
| `POST /auth/login`, unknown email | 401 |
| `POST /auth/register`, taken email | 409 |

- **Uniqueness under concurrency.** Eight sessions pass the application's own check, then
  insert the same email at once. Exactly one commits and seven receive SQLSTATE 23505,
  before and after search-key rotation.
- **Independent observation.** An owner connection sees `users.email` as `bytea`, 99
  stored bytes, no plaintext, and a unique index on only the 32-byte search term.
- **Removal.** Afterwards `users.email` is `VARCHAR(320)` with `ix_users_email`
  restored and no Cryptalis objects remain. The final API run happens after
  `uv pip uninstall cryptalis`, with `cryptalis importable: False` in the log.

Registration of a *new* account is not exercised, because it needs mail delivery. The
test account is written through the ORM as that route would.

## Latency and throughput

Native and protected ran on two identical clusters, alternating in fresh processes for
three rounds, so host drift cancels instead of appearing as overhead. Each cell has 512
samples. A result counts as MEET only if every round meets the target.

### One process

| Workload | Concurrency | Native p95 | Protected p95 | Added p95 per round | Median added | Target | Result | Throughput native / protected |
|---|---:|---:|---:|---|---:|---:|---|---:|
| Email equality | 1 | 1.69 | 3.58 | 1.91, 1.88, 1.95 | 1.91 | 3 | MEET | 943 / 338 |
| Email equality | 4 | 1.86 | 9.65 | 6.81, 7.94, 7.65 | 7.65 | 3 | MISS | 2827 / 506 |
| Email equality | 16 | 10.41 | 60.85 | 48.36, 49.62, 53.84 | 49.62 | 3 | MISS | 2467 / 470 |
| Point read | 1 | 1.55 | 3.27 | 1.88, 1.71, 2.46 | 1.88 | 3 | MEET | 1005 / 364 |
| Point read | 4 | 1.73 | 8.43 | 6.36, 6.71, 9.91 | 6.71 | 3 | MISS | 2993 / 575 |
| Point read | 16 | 9.13 | 53.69 | 45.79, 33.89, 56.07 | 45.79 | 3 | MISS | 2466 / 522 |
| IN-20 (ORM, no Smolink route) | 1 | 1.71 | 4.44 | 2.36, 3.71, 2.64 | 2.64 | 8 | MEET | 828 / 261 |
| IN-20 (ORM, no Smolink route) | 4 | 2.32 | 12.94 | 10.51, 11.49, 10.52 | 10.52 | 8 | MISS | 2161 / 369 |
| IN-20 (ORM, no Smolink route) | 16 | 10.11 | 69.81 | 57.73, 44.66, 66.30 | 57.73 | 8 | MISS | 1985 / 357 |

### Four worker processes, each at concurrency 1

| Workload | Native p95 | Protected p95 | Added p95 per round | Median added | Target | Result | Aggregate throughput native / protected |
|---|---:|---:|---|---:|---:|---|---:|
| Email equality | 1.17 | 4.19 | 3.06, 3.01, 3.16 | 3.06 | 3 | MISS | 4964 / 1110 |
| Point read | 1.13 | 3.83 | 2.69, 2.73, 2.65 | 2.69 | 3 | MEET | 5093 / 1281 |
| IN-20 (ORM, no Smolink route) | 1.65 | 5.43 | 3.78, 3.84, 3.76 | 3.78 | 8 | MEET | 3517 / 858 |

**At concurrency 1, every target is met in every round.** At concurrency 4 and 16 in one
process, every target is missed. Protected work is CPU-bound Python on one event loop, so
added latency grows with concurrency, about 2 ms of work per queued request. Four worker
processes more than halve equality latency against one process at concurrency 4 and
double throughput, yet email equality still misses at 3.06 ms. Native throughput remains
about 4.5 times higher, and that cost is real.

## Storage

| Measure (`users.email`) | Native | Compacted | Immediately after rotations |
|---|---:|---:|---:|
| Column bytes | 300,022 | 1,040,196 (3.47×) | 1,040,196 (3.47×) |
| Column plus index bytes, target 2× | 816,118 | 1,646,404 (**2.017×, MISS**) | 3,456,836 (**4.24×, MISS**) |
| Whole table and indexes | 1,818,624 | 2,605,056 (1.43×) | 17,055,744 (9.38×) |

Rotations rewrite rows, so plan for `VACUUM FULL` or equivalent space reclamation.
The protected table holds one more row than the native one. Sizes come from the
`storage` field of `pair/native-1.json`, `pair/protected-1.json` and
`superseded/protected-after-rotations.json`.

## Lifecycle timing

Wall time for one process on 10,002 accounts and 1,000 URLs, including Python start-up:

| Step | Seconds |
|---|---:|
| Doctor and protection | 1.88 |
| Payload rotation | 8.20 |
| Search rotation | 8.43 |
| Decrypt and removal | 1.94 |

## Limits

- Latency is measured at the original repository functions, without HTTP or Argon2.
  IN-20 has no Smolink route, so it uses the same ORM model.
- One shared workstation, with uncontrolled load from other applications.
- Warm keys only. Cold provider latency and OpenBao were not measured here.
- Each timing is a single observation with synthetic data. These are not outage budgets.
- A real deployment adds network latency. Native throughput here benefits from loopback.

## Reproduce

```console
python -m cryptalis_demo.setup --workdir ... --provider-config ... --cryptalis-checkout ... \
  --rows 1000 --users 10000 --manifest manifest-search.json
python -m cryptalis_demo.journey_search --config CONFIG STEP
python -m cryptalis_demo.benchmark_search --config CONFIG --mode native --output NEW.json
python -m cryptalis_demo.render_search --evidence DIRECTORY
```

Provider configuration for this run is
`{"providers": [{"kind": "development", "key_file": "/absolute/private/key"}], "active_provider": 0}`.
Use a new private work directory and a Redis server on its `redis.sock`, as the
[setup guide](../../README.md) describes.
