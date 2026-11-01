"""Measure Smolink's own email lookup on the same data, native and protected.

get_user_by_email is the query behind the original login and registration routes.
get_user_by_id is the point read behind authenticated requests. IN-20 has no
Smolink route: it uses the same ORM model and is labelled as such in results.
Run native before protection, protected after it, removed after removal, each in
a fresh process. Read latencies exclude Argon2 and all HTTP handling.
"""
import argparse
import asyncio
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import time

from .benchmark import summary
from .host import build_runtime, load_config, owner_engine


def email(i):
    return f'user-{i:08d}@example.invalid'


def storage(config):
    from sqlalchemy import text
    engine = owner_engine(config)
    try:
        with engine.connect() as connection:
            row = connection.execute(text(
                "SELECT count(*), sum(pg_column_size(email)), pg_relation_size('users'), "
                "pg_indexes_size('users'), pg_total_relation_size('users') FROM users")).one()
            indexes = connection.execute(text(
                "SELECT indexrelname, pg_relation_size(indexrelid) FROM pg_stat_user_indexes "
                "WHERE relname = 'users' ORDER BY 1")).all()
            kind = connection.execute(text(
                "SELECT data_type FROM information_schema.columns WHERE table_name = 'users' "
                "AND column_name = 'email' AND table_schema = current_schema()")).scalar_one()
        return dict(zip(('rows', 'email_column_bytes', 'table_bytes', 'all_index_bytes', 'total_relation_bytes'), row),
                    indexes={name: size for name, size in indexes}, email_type=kind)
    finally:
        engine.dispose()


async def cell(runtime, operation, count, concurrency):
    queue = asyncio.Queue()
    for i in range(count):
        queue.put_nowait(i)
    latencies = []

    async def worker():
        while not queue.empty():
            i = queue.get_nowait()
            start = time.perf_counter_ns()
            async with runtime.factory() as session:
                await operation(session, i)
            latencies.append((time.perf_counter_ns() - start) / 1e6)

    start, cpu = time.perf_counter(), time.process_time()
    outcomes = await asyncio.gather(*(worker() for _ in range(concurrency)), return_exceptions=True)
    for outcome in outcomes:
        if isinstance(outcome, BaseException):
            raise outcome
    return summary(latencies, time.perf_counter() - start, time.process_time() - cpu)


async def measure(config, mode, count, users, levels, report):
    from sqlalchemy import select
    runtime = await build_runtime(config, mode)
    from app.models.user import User
    from app.repositories.user_repository import get_user_by_email, get_user_by_id
    picks = random.Random(20261102)
    trace = [picks.randrange(users) for _ in range(count)]
    lists = [[email(picks.randrange(users)) for _ in range(20)] for _ in range(count)]

    async def by_email(session, i):
        expected = email(trace[i])
        assert (await get_user_by_email(session, expected)).email == expected

    async def by_id(session, i):
        assert (await get_user_by_id(session, 7000000000 + trace[i])).email == email(trace[i])

    async def in_twenty(session, i):
        rows = (await session.execute(select(User).where(User.email.in_(lists[i])))).scalars().all()
        assert {row.email for row in rows} == set(lists[i])

    report.update({'mode': mode, 'python': platform.python_version(), 'platform': platform.platform(),
                   'cpu_count': os.cpu_count(), 'samples_per_cell': count, 'users': users,
                   'transport': 'original repository functions, real PostgreSQL, no HTTP',
                   'provider': 'DevelopmentKeyProvider key file, warm cached roots after warmup',
                   'versions': {name: importlib.metadata.version(name) for name in
                                ('SQLAlchemy', 'psycopg', 'fastapi')},
                   'cryptalis': None if mode != 'protected' else importlib.metadata.version('cryptalis'),
                   'storage': storage(config), 'workloads': {}})
    try:
        for name, operation in (('email_equality', by_email), ('id_point', by_id), ('orm_in20', in_twenty)):
            await cell(runtime, operation, min(count, 64), 1)  # Warm imports, pools and key cache.
            for concurrency in levels:
                report['workloads'][f'{name}_c{concurrency}'] = await cell(runtime, operation, count, concurrency)
        report['status'] = 'PASS'
    finally:
        await runtime.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--mode', choices=('native', 'protected', 'removed'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=512)
    parser.add_argument('--users', type=int, default=10000)
    parser.add_argument('--concurrency', type=int, action='append', help='Repeat to choose levels; default 1, 4, 16.')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Use a new output path; preserve previous results.')
    report = {'status': 'INCOMPLETE'}
    try:
        asyncio.run(measure(load_config(args.config), args.mode, args.samples, args.users,
                            tuple(args.concurrency or (1, 4, 16)), report))
    except BaseException as error:
        report.update(status='FAIL', failure_type=type(error).__name__)
        raise
    finally:
        with args.output.open('x') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
    print(json.dumps({name: {key: round(value[key], 3) for key in ('p50_ms', 'p95_ms', 'throughput_per_second')}
                      for name, value in report['workloads'].items()}))


if __name__ == '__main__':
    main()
