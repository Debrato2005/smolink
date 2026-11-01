"""Render email-search measurements from raw receipts; never edit the tables by hand."""
import argparse
import json
import math
from pathlib import Path
import statistics


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


TARGETS = {'email_equality': ('Email equality', 3), 'id_point': ('Point read', 3), 'orm_in20': ('IN-20 (ORM, no Smolink route)', 8)}


def verdict(added, target):
    return 'MEET' if max(added) <= target else 'MISS'


def single(pair):
    lines = ['| Workload | Concurrency | Native p95 | Protected p95 | Added p95 per round | Median added | Target | Result | Throughput native / protected |',
             '|---|---:|---:|---:|---|---:|---:|---|---:|']
    for key, (label, target) in TARGETS.items():
        for level in (1, 4, 16):
            cell = f'{key}_c{level}'
            native = [json.loads((pair / f'native-{r}.json').read_text())['workloads'][cell] for r in (1, 2, 3)]
            protected = [json.loads((pair / f'protected-{r}.json').read_text())['workloads'][cell] for r in (1, 2, 3)]
            added = [b['p95_ms'] - a['p95_ms'] for a, b in zip(native, protected)]
            lines.append(f"| {label} | {level} | {statistics.median(x['p95_ms'] for x in native):.2f} | "
                         f"{statistics.median(x['p95_ms'] for x in protected):.2f} | "
                         f"{', '.join(f'{a:.2f}' for a in added)} | {statistics.median(added):.2f} | {target} | "
                         f"{verdict(added, target)} | {statistics.median(x['throughput_per_second'] for x in native):.0f} / "
                         f"{statistics.median(x['throughput_per_second'] for x in protected):.0f} |")
    return lines


def workers(directory):
    lines = ['| Workload | Native p95 | Protected p95 | Added p95 per round | Median added | Target | Result | Aggregate throughput native / protected |',
             '|---|---:|---:|---|---:|---:|---|---:|']
    for key, (label, target) in TARGETS.items():
        cell, added, native_p95, protected_p95, native_rate, protected_rate = f'{key}_c1', [], [], [], [], []
        for round_number in (1, 2, 3):
            observed = {}
            for mode in ('native', 'protected'):
                documents = [json.loads((directory / f'{mode}-{round_number}-{worker}.json').read_text()) for worker in (1, 2, 3, 4)]
                samples = [value for document in documents for value in document['workloads'][cell]['latency_samples_ms']]
                observed[mode] = percentile(samples, .95), sum(d['workloads'][cell]['throughput_per_second'] for d in documents)
            added.append(observed['protected'][0] - observed['native'][0])
            native_p95.append(observed['native'][0])
            protected_p95.append(observed['protected'][0])
            native_rate.append(observed['native'][1])
            protected_rate.append(observed['protected'][1])
        lines.append(f"| {label} | {statistics.median(native_p95):.2f} | {statistics.median(protected_p95):.2f} | "
                     f"{', '.join(f'{a:.2f}' for a in added)} | {statistics.median(added):.2f} | {target} | {verdict(added, target)} | "
                     f"{statistics.median(native_rate):.0f} / {statistics.median(protected_rate):.0f} |")
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    arguments = parser.parse_args()
    evidence = arguments.evidence
    print('\n'.join(['### One process', '', *single(evidence / 'pair'), '', '### Four worker processes, each at concurrency 1', '',
                     *workers(evidence / 'workers')]))


if __name__ == '__main__':
    main()
