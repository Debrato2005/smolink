# Matched Smolink observations

These are local application observations, not production qualification or a competitor benchmark.

Original revision: `498d24bae999ed53ad85e1c1f1a09ea7fa151aa4`. Cryptalis wheel `0.1.0a1`, SHA-256 `eedecae8fd72a06bdf8ed95bd0aae377cabdfd51df325c50463f4f4f4b65060a`.

Both processes use the same Python 3.13.5 dependency environment, PostgreSQL 16 cluster, 10,000 committed seed rows and deterministic trace. The native run precedes migration and the protected run; mode order is not randomized. Each process warms 32 repository reads. OpenBao roots are warm during measurement. ASGI HTTP includes original middleware, dependencies, real Redis rate limiting, service, repository, commit and refresh; it excludes network/proxy/TLS latency. Each simulated guest sends at most eight requests. No rate limiter is disabled. Resource values cover the Python application, not total PostgreSQL/Redis/OpenBao CPU and memory. Background host contention was not controlled, and samples do not establish stable performance bounds.

| Workload | Native p50/p95/p99 ms | Protected p50/p95/p99 ms | Added p95 ms | Native/protected ops/s | Point target |
|---|---:|---:|---:|---:|---|
| repository_point_c1 | 1.151/1.672/2.569 | 5.271/6.279/7.616 | 4.607 | 800.4/178.6 | MISS |
| http_create_c1 | 5.832/8.433/17.990 | 14.558/16.167/20.535 | 7.734 | 153.6/67.4 | No write budget |
| repository_point_c4 | 3.859/5.332/20.421 | 20.105/23.734/36.243 | 18.401 | 934.1/194.4 | MISS |
| http_create_c4 | 20.274/23.677/27.403 | 54.727/61.159/64.898 | 37.482 | 195.9/72.9 | No write budget |
| repository_point_c16 | 18.010/47.231/64.602 | 83.039/136.302/172.712 | 89.071 | 733.0/181.9 | MISS |
| http_create_c16 | 92.029/134.761/157.945 | 218.531/318.149/363.226 | 183.388 | 158.9/67.0 | No write budget |

All measured repository-point concurrency cells miss the 3 ms added-p95 target. HTTP creates have no approved latency budget. Protected equality and IN-20 are unmeasured: this destination manifest is storage-only, and the original application exposes no such API operation. The 8 ms IN-20 target remains open.

| Workload | Native/protected CPU % of one core | Native/protected peak RSS MiB |
|---|---:|---:|
| repository_point_c1 | 84.7/97.8 | 100.2/120.2 |
| http_create_c1 | 80.3/91.9 | 108.0/121.0 |
| repository_point_c4 | 99.1/99.9 | 108.0/121.2 |
| http_create_c4 | 100.5/100.3 | 108.0/121.8 |
| repository_point_c16 | 99.7/99.9 | 108.0/122.5 |
| http_create_c16 | 100.5/100.2 | 108.2/123.3 |

| Storage observation | Native bytes | Protected bytes | Ratio |
|---|---:|---:|---:|
| destination_bytes | 880000 | 1330000 | 1.5114× |
| table_bytes | 1785856 | 5169152 | 2.8945× |
| all_index_bytes | 671744 | 1318912 | 1.9634× |
| total_relation_bytes | 2498560 | 6529024 | 2.6131× |

The storage table uses the snapshot before each benchmark. Column bytes use SUM(pg_column_size(destination)). Relation/index sizes are observed allocations without VACUUM FULL or REINDEX. They include dead-space/allocation history and are not compact steady-state sizes. No encrypted destination search index exists, so this does not qualify the 2× protected-column-plus-search-index target. The observed total allocation exceeds 2× and is retained.

Raw per-operation samples and process CPU/wall time are in native.json and protected.json. The initial host import failure is retained in native.log; the corrected native run is native-retry.log. Neither successful measurement contains an API error. All benchmark-created rows were removed through the normal ORM; both runs return to the same 10,000 seed rows.

![Latency and throughput](measurements.svg)
