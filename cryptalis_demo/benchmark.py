"""Measure the original Smolink ASGI route and repository on the same trace.

Run native before protection, then protected, in separate processes. HTTP uses
ASGI transport, not a network load generator. No rate-limit dependency is replaced:
each simulated guest sends at most eight requests. Keep this limitation with results.
"""
import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import resource
import time

from .host import build_runtime, load_config, owner_engine


def percentile(values, fraction):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(len(ordered) * fraction) - 1)]


def summary(values, elapsed, cpu):
    return {'samples': len(values), 'p50_ms': percentile(values, .50),
            'p95_ms': percentile(values, .95), 'p99_ms': percentile(values, .99),
            'throughput_per_second': len(values) / elapsed, 'wall_seconds': elapsed,
            'application_cpu_seconds': cpu, 'application_cpu_percent_one_core': 100 * cpu / elapsed,
            'application_peak_rss_bytes': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            'latency_samples_ms': values}


def storage(config):
    from sqlalchemy import text
    engine = owner_engine(config)
    try:
        with engine.connect() as connection:
            row = connection.execute(text('SELECT count(*), sum(pg_column_size(destination)), '
                'pg_relation_size(\'urls\'), pg_indexes_size(\'urls\'), '
                'pg_total_relation_size(\'urls\') FROM urls')).one()
            return dict(zip(('rows', 'destination_bytes', 'table_bytes', 'all_index_bytes',
                             'total_relation_bytes'), row))
    finally:
        engine.dispose()


async def measure(config, mode, count, report):
    import httpx
    from sqlalchemy import select
    runtime = await build_runtime(config, mode)
    from app.models.url import Url
    from app.repositories.url_repository import get_url_by_short_code
    from app.core.redis import get_redis_client
    report.update({'mode': mode, 'python': platform.python_version(), 'platform': platform.platform(),
              'cpu_count': os.cpu_count(), 'timing': 'perf_counter_ns; monotonic',
              'transport': 'in-process HTTP ASGI; real PostgreSQL and Redis; no network latency',
              'provider': 'real local HTTPS OpenBao; warm cached roots after warmup',
              'order': 'native run precedes protection and protected run; no randomized mode order',
              'versions': {name: importlib.metadata.version(name) for name in
                  ('cryptalis', 'SQLAlchemy', 'cryptography', 'psycopg', 'fastapi', 'redis', 'httpx', 'hvac')},
              'storage_before': storage(config), 'workloads': {}, 'failures': []})
    created_ids = []
    primary_failure = None
    try:
        # Warm imports, database pools, key cache and the exact original repository path.
        for i in range(32):
            async with runtime.factory() as session:
                value = await get_url_by_short_code(session, f'seed-{i:08d}')
                assert value.destination.endswith('source=matched-data')
        for concurrency in (1, 4, 16):
            latencies = []
            queue = asyncio.Queue()
            for i in range(count):
                queue.put_nowait(i)

            async def points():
                while not queue.empty():
                    i = queue.get_nowait()
                    start = time.perf_counter_ns()
                    async with runtime.factory() as session:
                        value = await get_url_by_short_code(session, f'seed-{(i * 37) % 10000:08d}')
                        assert value.destination.endswith('source=matched-data')
                    latencies.append((time.perf_counter_ns() - start) / 1e6)

            start, cpu = time.perf_counter(), time.process_time()
            outcomes = await asyncio.gather(*(points() for _ in range(concurrency)), return_exceptions=True)
            for outcome in outcomes:
                if isinstance(outcome, BaseException):
                    raise outcome
            report['workloads'][f'repository_point_c{concurrency}'] = summary(
                latencies, time.perf_counter() - start, time.process_time() - cpu)

            await get_redis_client().flushdb()  # Private disposable service; reset between matched cells.
            latencies = []
            groups = asyncio.Queue()
            for begin in range(0, count, 8):
                groups.put_nowait(begin)

            async def creates():
                while not groups.empty():
                    begin = groups.get_nowait()
                    transport = httpx.ASGITransport(app=runtime.app,
                        client=(f'198.18.{begin // 256}.{begin % 256}', 12345))
                    async with httpx.AsyncClient(transport=transport, base_url='http://preview.invalid') as client:
                        for i in range(begin, min(begin + 8, count)):
                            payload = {'alias': f'bench-{concurrency}-{i:06d}',
                                'destination': f'https://catalog.example.invalid/created/{i:08d}?source=matched-api'}
                            start = time.perf_counter_ns()
                            response = await client.post('/api/v1/urls', json=payload)
                            duration = (time.perf_counter_ns() - start) / 1e6
                            if response.status_code != 201:
                                report['failures'].append({'workload': f'http_create_c{concurrency}',
                                    'sample': i, 'status': response.status_code})
                                raise RuntimeError('Original API refused a matched benchmark request.')
                            result = response.json()
                            assert result['destination'] == payload['destination']
                            created_ids.append(result['id'])
                            latencies.append(duration)

            start, cpu = time.perf_counter(), time.process_time()
            outcomes = await asyncio.gather(*(creates() for _ in range(concurrency)), return_exceptions=True)
            for outcome in outcomes:
                if isinstance(outcome, BaseException):
                    raise outcome
            report['workloads'][f'http_create_c{concurrency}'] = summary(
                latencies, time.perf_counter() - start, time.process_time() - cpu)
        report['request_trace_sha256'] = hashlib.sha256(json.dumps(
            {'count': count, 'concurrency': [1, 4, 16], 'seed_step': 37,
             'aliases': 'bench-{concurrency}-{i:06d}', 'guest_requests_per_identity': 8},
            sort_keys=True).encode()).hexdigest()
    except BaseException as error:
        primary_failure = error
        raise
    finally:
        # Restore the identical committed seed membership with normal ORM deletes.
        cleanup_failures = []
        try:
            for begin in range(0, len(created_ids), 100):
                async with runtime.factory() as session:
                    rows = (await session.execute(select(Url).where(
                        Url.id.in_(created_ids[begin:begin + 100])))).scalars().all()
                    for row in rows:
                        await session.delete(row)
                    await session.commit()
        except BaseException as error:
            cleanup_failures.append({'stage': 'orm_cleanup', 'error': type(error).__name__})
        try:
            await get_redis_client().flushdb()
        except BaseException as error:
            cleanup_failures.append({'stage': 'private_redis_cleanup', 'error': type(error).__name__})
        try:
            await runtime.close()
        except BaseException as error:
            cleanup_failures.append({'stage': 'runtime_close', 'error': type(error).__name__})
        report['cleanup_failures'] = cleanup_failures
        if cleanup_failures and primary_failure is None:
            raise RuntimeError('Benchmark cleanup failed; inspect the receipt.')
    report['storage_after'] = storage(config)
    assert report['storage_before']['rows'] == report['storage_after']['rows'] == 10000
    report['targets'] = {'repository_point_added_p95_ms': 3,
        'http_create': 'no approved latency budget', 'encrypted_equality_and_in20':
        'not measured: destination storage-only; no implemented API endpoint performs these queries',
        'indexed_storage_2x': 'not applicable to storage-only destination; raw column ratio still reported'}
    report['status'] = 'PASS'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--mode', choices=('native', 'protected'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=256)
    args = parser.parse_args()
    if not 128 <= args.samples <= 10000:
        parser.error('Use 128..10000 samples per workload.')
    if args.output.exists():
        parser.error('Use a new output path; preserve previous results.')
    report = {'mode': args.mode, 'status': 'INCOMPLETE'}
    try:
        asyncio.run(measure(load_config(args.config), args.mode, args.samples, report))
    except BaseException as error:
        report.update(status='FAIL', failure_type=type(error).__name__)
        raise
    finally:
        with args.output.open('x') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
    print(json.dumps({'mode': args.mode, 'output': str(args.output),
                      'workloads': len(report['workloads']), 'failures': report['failures']}))


if __name__ == '__main__':
    main()
