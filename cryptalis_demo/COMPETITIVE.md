# Developer outcomes and alternatives

Sources retrieved **1 November 2026**. This compares concrete integration and
operating requirements. **No matched competitor benchmark was run.** CipherStash,
pgcrypto and SQLAlchemy-Utils were not installed or exercised in this environment;
their rows describe official documentation and inspected source, not reproduced
runtime results. No claim of being faster, safer or better follows.

The Cryptalis candidate is `0.1.0a1`, prepared at
[`655d522`](https://github.com/Debrato2005/cryptalis/tree/655d52271d90effb4df918a9547f61c89055fbc7).
It remains a research prototype; all seven production gates are UNKNOWN. This
Smolink demonstration protects only `Url.destination`, storage-only. Its existing
URL creation API and repository operations do not demonstrate destination search.
Use the demonstration receipts for executed outcomes, rather than inferring them
from this comparison or from vendor feature lists.

## Cryptalis and CipherStash

| Developer outcome | Cryptalis candidate | CipherStash documented path | Practical decision |
|---|---|---|---|
| Add encryption to a Python SQLAlchemy/SQLModel app | Install a Python wheel, declare a manifest, supply an external provider and private deployment state, then replace the session factory. Exact ORM/driver versions and admitted query shapes apply. Host authorization and writer inventory remain required. [K1] | Stack SDK is TypeScript/JavaScript; listed wrappers cover Drizzle, Supabase JS and Prisma. The documented path for other languages is a PostgreSQL-wire Proxy container: redirect the connection and install EQL database objects. [C1,C2] | Cryptalis offers a direct Python library path for its bounded SQLAlchemy cell. CipherStash offers a proxy path across languages. Neither source establishes arbitrary ORM/SQL equivalence; run the actual application's workflows. |
| Decide where plaintext and key authority live | Encryption runs in the application before persistence. Generic `KeyProvider` supports external custody, including OpenBao and optional cloud adapters; PostgreSQL holds no secret keys. The host still supplies policy, credentials and authorization. [K1] | SDK encrypts in the application; Proxy encrypts in its own process. ZeroKMS participates in derivation, with separate client-side material and authority-side control. The client key alone is insufficient to derive data keys. Current Proxy source confirms ZeroKMS calls and scoped cipher caching. [C1,C3,S2] | Choose the custody and plaintext-processing boundary explicitly. CipherStash's split-control/OIDC model is a different service/authority contract; it is not established by Cryptalis's provider abstraction. This local OpenBao demonstration does not qualify production custody. |
| Query protected data | The library admits bounded equality/IN/scoped uniqueness and selected order operations with explicit leakage acceptance. JSONB storage is implemented; JSON search and ordinary prefix search remain unadmitted. Smolink here demonstrates storage only. [K1] | EQL 3.0.4 documents equality, ordering/ranges, text matching and structured JSON capabilities through domain types, extractors and indexes. Its broader published surface is not reproduced in this demo. [C4,C5] | Choose the exact operations, types and result semantics first. The present Cryptalis candidate does not supply the vendor's full documented query surface. Schema/index and query-admission work is part of adoption. |
| Understand dump/search leakage | Storage-only has randomized authenticated payloads; metadata, nullness, size and access patterns still matter. Equality reveals equal-value classes/frequency; order adds relative order. Keys or rotation do not erase inference from already-observed relationships. [K1] | CipherStash explicitly documents equality/frequency, ordering, text-token overlap and JSON structure/path leakage by capability, plus observable search/access patterns and auxiliary-information risks. [C5] | Both require a leakage decision per field. The presence of ciphertext or keyed terms does not establish that a dump reveals nothing. There is no confidentiality ranking here. |
| Move an existing populated application | `Project` orchestrates bounded resumable maintenance or online transitions, verification and publication; real writer exclusion, role separation, supported schema and worker restarts are prerequisites. [K1] | The migration guide describes nullable encrypted mirrors, deployed transactional dual-writes in every writer, resumable backfill, coverage checks/indexes, encrypted read cutover and later plaintext removal. [C6] | Count all code/configuration changes and rollout work. The vendor's proxy connection-change claim is not evidence that a populated-data migration requires no operational changes. No setup-effort comparison was timed. |
| Exit after subsequent edits | `Project.decrypt` restores current committed values; verified removal retires owned objects, then the original app must restart without the package. Retained backups still require keys/readers until approved retirement. [K1] | EQL uninstall removes operator/function schemas but leaves encrypted public domains/columns/data. The migration guide says rollback after plaintext removal requires an approved backup or a new decrypting migration. These pages do not establish an automated latest-data/package-free exit. [C4,C6] | Current-data removal is a concrete Cryptalis workflow to verify in the receipts. Schema uninstall alone is not plaintext recovery. This bounded read does **not** prove CipherStash has no other offboarding workflow. |

CipherStash source also advertises BYOK. That statement does not establish that
ZeroKMS can be replaced by an arbitrary provider in the documented Stack/Proxy
path. This comparison does not reproduce its revocation, audit or rotation claims.
[S1,C3]

## Relevant smaller alternatives

| Alternative | Evidenced developer work and boundary | What to compare fairly |
|---|---|---|
| PostgreSQL `pgcrypto` | Install/use database-side crypto functions and supply their keys/passwords. PostgreSQL's own documentation says these functions run inside the server and requires trusting system/database administrators and using a local or TLS connection. Thus it does not meet this milestone's requirement to encrypt before PostgreSQL receives the plaintext. [A1] | It is a useful SQL crypto toolbox under a different server-trust model. Client key handling, query design, migrations and current-data exit need their own application procedure. A dump-only protection scenario must specify which keys are retained outside the dump. No same-threat-model performance comparison was run. |
| SQLAlchemy-Utils `StringEncryptedType` | Change mapped column types, supply a key or key callback and select an engine. Inspected source performs encryption/decryption in bind/result hooks. Its randomized authenticated `AesGcmEngine` documentation explicitly excludes encrypted-value search; its deterministic `AesEngine` supports lookup under a different security contract. [A2] | This is a direct client-side column-encryption alternative for simpler needs. The inspected type does not itself supply Cryptalis-style blind-index terms, authenticated tenant/record context or complete migration/rotation/removal orchestration. That is a boundary of the inspected file, not a claim about every possible application built around it. Verify native semantics and lifecycle work separately. |

## Evidence and source boundaries

The existing Cryptalis [prior-art notes](https://github.com/Debrato2005/cryptalis/blob/655d52271d90effb4df918a9547f61c89055fbc7/docs/prior-art.md)
and [dated capability matrix](https://github.com/Debrato2005/cryptalis/blob/655d52271d90effb4df918a9547f61c89055fbc7/docs/research/capability-matrix.md)
were reused as navigation. The following primary pages were re-read on
1 November 2026, requesting live retrieval; all returned HTTP 200 with the
expected final URL/title and non-empty content. Their update/version labels are
the publisher's statements. Source HEADs are pinned below and are **not** asserted
to match a released SDK or container. No vendor cryptographic audit was performed.

| ID | Primary source checked |
|---|---|
| K1 | Cryptalis candidate [API](https://github.com/Debrato2005/cryptalis/blob/655d52271d90effb4df918a9547f61c89055fbc7/docs/application.md), [compatibility](https://github.com/Debrato2005/cryptalis/blob/655d52271d90effb4df918a9547f61c89055fbc7/docs/compatibility.md), [security](https://github.com/Debrato2005/cryptalis/blob/655d52271d90effb4df918a9547f61c89055fbc7/docs/security.md) and [status](https://github.com/Debrato2005/cryptalis/blob/655d52271d90effb4df918a9547f61c89055fbc7/docs/status.md). Contract scope and recorded bounded evidence; no production qualification. |
| C1 | [Choose your stack](https://cipherstash.com/docs/get-started/choose-your-stack), updated 13 October 2026: SDK/Proxy and ORM paths, pooler placement and identity prerequisites. |
| C2 | [Proxy](https://cipherstash.com/docs/reference/proxy), updated 30 July 2026: container, PostgreSQL protocol and plaintext processing location. |
| C3 | [Key management](https://cipherstash.com/docs/concepts/key-management), updated 30 July 2026: ZeroKMS/client split, keyset scope, derivation, audit and caching distinctions. |
| C4 | [EQL](https://cipherstash.com/docs/reference/eql), updated 31 August 2026, states version 3.0.4: SQL objects, install and exact uninstall behavior. |
| C5 | [Searchable encryption](https://cipherstash.com/docs/concepts/searchable-encryption), updated 31 August 2026: capability and leakage tables. Its benchmark claims were not used as local results. |
| C6 | [Data migration](https://cipherstash.com/docs/guides/migration), updated 30 July 2026: dual-writes, staged cutover and rollback after plaintext removal. |
| S1 | Stack [README at `3a923ef`](https://github.com/cipherstash/stack/blob/3a923ef0796aefd1cfae47598010f3a47c5e2516/README.md): current package/integration overview, ZeroKMS authentication and BYOK statement. |
| S2 | Proxy [README](https://github.com/cipherstash/proxy/blob/c5389a6386e8cd29e277ba3e1c85a4a0368a7ebb/README.md) and [architecture at `c5389a6`](https://github.com/cipherstash/proxy/blob/c5389a6386e8cd29e277ba3e1c85a4a0368a7ebb/ARCHITECTURE.md): rewriting, result decryption and scoped cipher caching. |
| A1 | PostgreSQL 16 branch [pgcrypto documentation at `a2732c9`](https://github.com/postgres/postgres/blob/a2732c98671d86a06f7ec21d469a52a7bf4efdc9/doc/src/sgml/pgcrypto.sgml#L1221): server execution and security limitations. |
| A2 | SQLAlchemy-Utils [encrypted type implementation at `fbffdac`](https://github.com/kvesteri/sqlalchemy-utils/blob/fbffdaca45a7835f128b79d392602a3c088df794/sqlalchemy_utils/types/encrypted/encrypted_type.py): engine contracts, key callback and bind/result behavior. Source inspection only; no version-compatibility claim. |

A defensible next comparison would use the same app revision, field/capability,
data distribution, workload, hardware, concurrency and provider conditions. It
would check native results and refusal cases before comparing p50/p95/p99,
throughput, CPU, memory, isolated storage, setup changes and full lifecycle costs.
Those competitor measurements remain unmeasured.
