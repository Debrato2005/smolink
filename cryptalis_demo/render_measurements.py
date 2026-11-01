# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["matplotlib>=3.6,<4"]
# ///
"""Render retained matched observations; this does not run a benchmark."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    native = json.loads((args.evidence / 'native.json').read_text())
    protected = json.loads((args.evidence / 'protected.json').read_text())
    assert native['status'] == protected['status'] == 'PASS'
    assert native['request_trace_sha256'] == protected['request_trace_sha256']
    names = list(native['workloads'])
    labels = [name.replace('repository_point_', 'Point ').replace('http_create_', 'POST ')
              for name in names]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), layout='constrained')
    for offset, data, color, label in ((-.18, native, '#52677d', 'Native'),
                                        (.18, protected, '#087f8c', 'Cryptalis')):
        axes[0].bar([i + offset for i in range(len(names))],
                    [data['workloads'][n]['p95_ms'] for n in names], width=.36, color=color, label=label)
        axes[1].bar([i + offset for i in range(len(names))],
                    [data['workloads'][n]['throughput_per_second'] for n in names],
                    width=.36, color=color, label=label)
    for ax in axes:
        ax.set_xticks(range(len(names)), labels, rotation=35, ha='right')
        ax.spines[['top', 'right']].set_visible(False)
        ax.legend(frameon=False)
    axes[0].set_ylabel('p95 latency (ms)')
    axes[1].set_ylabel('completed operations / second')
    fig.suptitle('Pinned Smolink, 10,000 rows, 256 samples per workload\n'
                 'Local ASGI; real PostgreSQL / Redis / OpenBao; sequential mode order')
    fig.savefig(args.evidence / 'measurements.svg')
    fig.savefig(args.evidence / 'measurements.png', dpi=160)
    plt.close(fig)
    lines = ['# Matched Smolink observations', '',
        'These are local application observations, not production qualification or a competitor benchmark.', '',
        'Original revision: `498d24bae999ed53ad85e1c1f1a09ea7fa151aa4`. '
        'Cryptalis wheel `0.1.0a1`, SHA-256 '
        '`eedecae8fd72a06bdf8ed95bd0aae377cabdfd51df325c50463f4f4f4b65060a`.', '',
        'Both processes use the same Python 3.13.5 dependency environment, PostgreSQL 16 '
        'cluster, 10,000 committed seed rows and deterministic trace. The native run '
        'precedes migration and the protected run; mode order is not randomized. '
        'Each process warms 32 repository reads. OpenBao roots are warm during '
        'measurement. ASGI HTTP includes original middleware, dependencies, real '
        'Redis rate limiting, service, repository, commit and refresh; it excludes '
        'network/proxy/TLS latency. Each simulated guest sends at most eight requests. '
        'No rate limiter is disabled. Resource values cover the Python application, '
        'not total PostgreSQL/Redis/OpenBao CPU and memory. Background host contention '
        'was not controlled, and samples do not establish stable performance bounds.', '',
        '| Workload | Native p50/p95/p99 ms | Protected p50/p95/p99 ms | Added p95 ms | Native/protected ops/s | Point target |',
        '|---|---:|---:|---:|---:|---|']
    table = []
    for name in names:
        a, b = native['workloads'][name], protected['workloads'][name]
        delta = b['p95_ms'] - a['p95_ms']
        outcome = ('PASS' if delta <= 3 else 'MISS') if name.startswith('repository') else 'No write budget'
        table.append({'workload': name, 'added_p95_ms': delta, 'target': outcome})
        cell = lambda d: '/'.join(f'{d[k]:.3f}' for k in ('p50_ms', 'p95_ms', 'p99_ms'))
        lines.append(f'| {name} | {cell(a)} | {cell(b)} | {delta:.3f} | '
                     f'{a["throughput_per_second"]:.1f}/{b["throughput_per_second"]:.1f} | {outcome} |')
    lines.extend(['', 'All measured repository-point concurrency cells miss the 3 ms added-p95 target. '
        'HTTP creates have no approved latency budget. Protected equality and IN-20 '
        'are unmeasured: this destination manifest is storage-only, and the original '
        'application exposes no such API operation. The 8 ms IN-20 target remains open.', '',
        '| Workload | Native/protected CPU % of one core | Native/protected peak RSS MiB |',
        '|---|---:|---:|'])
    for name in names:
        a, b = native['workloads'][name], protected['workloads'][name]
        lines.append(f'| {name} | {a["application_cpu_percent_one_core"]:.1f}/'
                     f'{b["application_cpu_percent_one_core"]:.1f} | '
                     f'{a["application_peak_rss_bytes"]/1048576:.1f}/'
                     f'{b["application_peak_rss_bytes"]/1048576:.1f} |')
    a, b = native['storage_before'], protected['storage_before']
    lines.extend(['', '| Storage observation | Native bytes | Protected bytes | Ratio |',
                  '|---|---:|---:|---:|'])
    for key in ('destination_bytes', 'table_bytes', 'all_index_bytes', 'total_relation_bytes'):
        lines.append(f'| {key} | {a[key]} | {b[key]} | {b[key]/a[key]:.4f}× |')
    lines.extend(['', 'The storage table uses the snapshot before each benchmark. '
        'Column bytes use SUM(pg_column_size(destination)). Relation/index sizes are '
        'observed allocations without VACUUM FULL '
        'or REINDEX. They include dead-space/allocation history and are not compact '
        'steady-state sizes. No encrypted destination search index exists, so this '
        'does not qualify the 2× protected-column-plus-search-index target. '
        'The observed total allocation exceeds 2× and is retained.', '',
        'Raw per-operation samples and process CPU/wall time are in native.json and '
        'protected.json. The initial host import failure is retained in native.log; '
        'the corrected native run is native-retry.log. Neither successful measurement '
        'contains an API error. All benchmark-created rows were removed through the '
        'normal ORM; both runs return to the same 10,000 seed rows.', '',
        '![Latency and throughput](measurements.svg)', ''])
    (args.evidence / 'MEASUREMENTS.md').write_text('\n'.join(lines))
    (args.evidence / 'target-results.json').write_text(json.dumps(table, indent=2) + '\n')


if __name__ == '__main__':
    main()
