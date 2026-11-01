"""Restore this actual protected Smolink backup on a newly initialized cluster.

Retains backup/state/recovery credentials privately. Stops the source cluster
before target admission. This is an isolated local exercise, not deployment fencing.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from uuid import uuid4

from .host import (build_runtime, import_application, load_config, owner_engine,
                   private_bytes, project)
from .journey import BEFORE_BACKUP
from .setup import private_json


def database_environment(conninfo_file):
    import psycopg
    values = psycopg.conninfo.conninfo_to_dict(private_bytes(conninfo_file).decode().strip())
    return dict(os.environ, PGHOST=values.get('host', ''), PGPORT=values.get('port', '5432'),
                PGUSER=values['user'], PGPASSWORD=values['password'], PGDATABASE=values['dbname'])


async def first_write(config):
    from httpx import ASGITransport, AsyncClient
    runtime = await build_runtime(config, 'protected')
    try:
        from app.repositories.url_repository import get_url_by_short_code
        async with runtime.factory() as session:
            row = await get_url_by_short_code(session, 'seed-00000000')
            if row.destination != BEFORE_BACKUP:
                raise RuntimeError('Latest protected edit was not recovered.')
        async with AsyncClient(transport=ASGITransport(app=runtime.app, client=('127.0.0.3', 1234)),
                               base_url='http://127.0.0.1:8000') as client:
            response = await client.post('/api/v1/urls', json={
                'destination': 'https://example.invalid/first-write-after-fresh-restore',
                'alias': 'restored-' + uuid4().hex[:12]})
            if response.status_code != 201:
                raise RuntimeError('Original HTTP creation failed after fresh recovery.')
            return {'status': response.status_code, 'json': response.json()}
    finally:
        await runtime.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--source-cluster', type=Path, required=True)
    parser.add_argument('--workdir', type=Path, required=True)
    parser.add_argument('--cryptalis-checkout', type=Path, required=True)
    parser.add_argument('--receipt', type=Path, required=True)
    args = parser.parse_args()
    if not args.workdir.is_absolute() or args.receipt.exists():
        parser.error('Use new absolute work and receipt paths.')
    args.workdir.mkdir(mode=0o700, parents=True, exist_ok=False)
    sys.path.insert(0, str(args.cryptalis_checkout / 'scripts'))
    from fresh_cluster_qualification import provision, start_cluster, stop_cluster, write_home
    import psycopg
    config = load_config(args.config)
    started = time.perf_counter()
    backup = args.workdir / 'protected.sql'
    with backup.open('xb') as stream:
        backup.chmod(0o600)
        result = subprocess.run(['pg_dump', '--schema=' + config['schema']],
            env=database_environment(config['owner_conninfo_file']), stdout=stream, stderr=subprocess.PIPE)
    if result.returncode:
        raise RuntimeError('Protected backup failed; diagnostics withheld.')
    dump_seconds = time.perf_counter() - started
    shutil.copytree(config['state_dir'], args.workdir / 'project-state')
    source_values = psycopg.conninfo.conninfo_to_dict(private_bytes(config['owner_conninfo_file']).decode().strip())
    runtime_values = psycopg.conninfo.conninfo_to_dict(private_bytes(config['runtime_conninfo_file']).decode().strip())
    stopped = time.perf_counter()
    stop_cluster(args.source_cluster)
    if (args.source_cluster / 'postmaster.pid').exists():
        raise RuntimeError('Source shutdown could not be verified.')
    manifest = {'owner_role': source_values['user'], 'runtime_role': runtime_values['user'],
                'database': source_values['dbname']}
    target = args.workdir / 'target'
    target.mkdir(mode=0o700)
    cluster = None
    try:
        cluster, port, password = start_cluster(target)
        credentials = provision(port, password, manifest, 'cryptalis_preview_restored_unused_native')
        home = write_home(target, port, manifest, credentials, source_database=manifest['database'])
        recovered = {**config, 'state_dir': str(args.workdir / 'project-state'),
            'owner_conninfo_file': str(home / '.cryptalis-test-url'),
            'runtime_conninfo_file': str(home / '.cryptalis-test-runtime-url'),
            'plaintext_conninfo_file': str(home / '.cryptalis-test-source-url')}
        restore_started = time.perf_counter()
        restored = subprocess.run(['psql', '-X', '-v', 'ON_ERROR_STOP=1', '-f', str(backup)],
            env=database_environment(recovered['owner_conninfo_file']),
            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if restored.returncode:
            raise RuntimeError('Fresh target restore failed; diagnostics withheld.')
        restore_seconds = time.perf_counter() - restore_started
        _, registry = import_application(recovered)
        owner = owner_engine(recovered)
        try:
            recovery_started = time.perf_counter()
            project(recovered, registry).recover(owner, host='isolated local demonstration operator',
                quarantine='New loopback PostgreSQL cluster; no application workers before adoption', source_fenced=True)
            recovery_seconds = time.perf_counter() - recovery_started
        finally:
            owner.dispose()
        private_json(args.workdir / 'config.json', recovered)
        ready = asyncio.run(first_write(recovered))
        interruption = time.perf_counter() - stopped
        with args.receipt.open('x') as stream:
            json.dump({'backup_seconds': dump_seconds, 'protected_backup_bytes': backup.stat().st_size,
                'restore_seconds': restore_seconds, 'recovery_seconds': recovery_seconds,
                'source_stop_to_first_committed_http_create_seconds': interruption,
                'source_postmaster_pid_absent': True, 'source_cluster_stopped_before_target_start': True,
                'latest_committed_edit_recovered': True, 'first_write': ready,
                'limits': 'Local one-host stop/start exercise; no production RPO/RTO or distributed fencing claim'},
                stream, indent=2)
            stream.write('\n')
        print(json.dumps({'config': str(args.workdir / 'config.json'), 'source_stopped': True,
                          'restored_cluster_running': True, 'first_http_create': ready['status']}))
        cluster = None  # Retain target for latest edits, native exit and final API evidence.
    finally:
        if cluster is not None:
            stop_cluster(cluster)


if __name__ == '__main__':
    main()
