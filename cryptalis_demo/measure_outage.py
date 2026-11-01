"""Measure a local writer stop through the first committed original HTTP POST.

Uses frozen demo APIs and a normally installed wheel. Provisions new private
services and retains their custody files. This is one local host with idle
writers, not a production outage/RTO qualification or a throughput benchmark.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from uuid import uuid4

from .host import load_config, owner_engine
from .measure_pair import git, snapshot
from .provision_provider import helpers, provision

ROOT = Path(__file__).resolve().parents[1]


def process_table():
    """Read only process identity, parent, CPU counters and resident pages."""
    result = {}
    for directory in Path('/proc').iterdir():
        if not directory.name.isdigit():
            continue
        try:
            raw = (directory / 'stat').read_text()
            fields = raw[raw.rfind(')') + 2:].split()
            result[int(directory.name)] = (int(fields[1]), int(fields[19]),
                int(fields[11]) + int(fields[12]), int(fields[21]) * os.sysconf('SC_PAGE_SIZE'))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    return result


class Samples(threading.Thread):
    """Bounded /proc observations; summed RSS can count shared pages repeatedly."""
    def __init__(self):
        super().__init__(daemon=True)
        self.finished = threading.Event()
        self.roots, self.observed, self.baselines, self.rows = {}, {}, {}, []
        self.phase = 'startup'
        self.failure = None
        self.lock = threading.Lock()

    def register(self, name, pid):
        table = process_table()
        with self.lock:
            self.roots[name] = (pid, table[pid][1]) if pid in table else (pid, None)
            baseline = self.baselines.setdefault(name, {})
            for current, values in table.items():
                baseline.setdefault((current, values[1]), values[2])
            self.observed.setdefault(name, {})

    def run(self):
        try:
            self.collect()
        except BaseException as error:
            self.failure = type(error).__name__
            self.finished.set()

    def collect(self):
        while not self.finished.is_set():
            table = process_table()
            groups = {}
            with self.lock:
                for name, (root, identity) in self.roots.items():
                    members = {root} if root in table and table[root][1] == identity else set()
                    while True:
                        expanded = members | {p for p, values in table.items() if values[0] in members}
                        if expanded == members:
                            break
                        members = expanded
                    rss, count = 0, 0
                    for pid in members:
                        if pid not in table:
                            continue
                        parent, started, cpu, resident = table[pid]
                        identity = (pid, started)
                        baseline = self.baselines[name].get(identity, 0)
                        self.observed[name][identity] = max(self.observed[name].get(identity, 0), cpu - baseline)
                        rss += resident
                        count += 1
                    groups[name] = {'processes_visible': count, 'summed_rss_bytes': rss,
                        'observed_cpu_seconds': sum(self.observed[name].values()) / os.sysconf('SC_CLK_TCK')}
                self.rows.append({'monotonic_ns': time.monotonic_ns(), 'phase': self.phase, 'groups': groups})
            self.finished.wait(.02)

    def summary(self, phase):
        selected = [row for row in self.rows if row['phase'] == phase]
        result = {}
        for group in {key for row in selected for key in row['groups']}:
            values = [row['groups'][group] for row in selected if group in row['groups']]
            visible = any(v['processes_visible'] for v in values)
            result[group] = {'processes_observed': visible,
                'observed_max_summed_rss_bytes': max(v['summed_rss_bytes'] for v in values) if visible else None,
                'observed_cpu_increment_seconds': values[-1]['observed_cpu_seconds'] - values[0]['observed_cpu_seconds'] if visible else None}
        return {'samples': len(selected), 'groups': result}


def request(base, path, payload=None):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(base + path, data=data,
        headers={} if payload is None else {'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.status, json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cryptalis-checkout', type=Path, required=True)
    parser.add_argument('--wheel', type=Path, required=True)
    parser.add_argument('--library-revision', required=True)
    parser.add_argument('--redis-server', type=Path, required=True)
    parser.add_argument('--private-workdir', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    if git('status', '--porcelain'):
        parser.error('Use a clean committed followup checkout.')
    if any(not p.is_absolute() or p.exists() for p in (args.private_workdir, args.evidence)):
        parser.error('Use new absolute private and evidence paths; preserve all earlier files.')
    os.umask(0o077)
    args.private_workdir.mkdir(mode=0o700, parents=True)
    args.evidence.mkdir(mode=0o700, parents=True)
    before = snapshot()
    report = {'status': 'INCOMPLETE', 'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'demo_revision': git('rev-parse', 'HEAD'), 'frozen_demo_revision': git('rev-parse', '269aed4'),
        'source_sha256_before': before, 'library_revision': args.library_revision,
        'wheel_sha256': hashlib.sha256(args.wheel.read_bytes()).hexdigest(),
        'provisioning_helper_revision': subprocess.check_output(['git', '-C', args.cryptalis_checkout, 'rev-parse', 'HEAD'], text=True).strip(),
        'provisioning_helper_sha256': {name: hashlib.sha256((args.cryptalis_checkout / 'scripts' / name).read_bytes()).hexdigest()
            for name in ('fresh_cluster_qualification.py', 'openbao_qualification.py', 'test_postgres.py')},
        'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
        'dependencies': {name: importlib.metadata.version(name) for name in
            ('cryptalis', 'cryptography', 'SQLAlchemy', 'psycopg', 'hvac', 'fastapi', 'uvicorn', 'redis')},
        'commands': [], 'transitions': [], 'cleanup': [],
        'timing_contract': {
            'start': 'time.monotonic_ns immediately before SIGTERM to the real running host',
            'stop': 'old Uvicorn process reaped; health connection refused before lifecycle mutation',
            'end': 'first HTTP201 response fully read; original route commits and refreshes before responding',
            'independent_commit_check': 'owner connection finds exact id/short_code after the201, outside interval',
            'readiness': 'fresh process health200 then actual POST201; health alone is not database readiness',
            'workload': '10000 deterministic seeded URLs; only one host and no in-flight requests at SIGTERM',
            'rate_limiter': 'original real Redis limiter remains enabled; fewer than10 guest creates per window',
            'limits': 'One observation per operation; warm local services, fresh interpreter and empty process key cache. Not production RTO/downtime, concurrency or tail evidence.'},
        'resource_contract': {'sampling_interval_seconds': .02,
            'scope': 'tracked application/operator subprocesses plus descendant local PostgreSQL, Redis and OpenBao processes when visible',
            'cpu': 'observed /proc CPU increments; missing final ticks/short-lived processes make these lower bounds',
            'memory': 'observed maximum summed RSS; shared pages can be counted repeatedly, and sparse samples do not establish true peak or physical memory',
            'exclusions': 'controller/sampler, Docker daemon and unrelated host processes; shared-host contention uncontrolled'}}
    environment = dict(os.environ)
    environment.pop('PYTHONPATH', None)
    sampler = Samples()
    sampler.start()
    service = helpers(args.cryptalis_checkout)
    sys.path.insert(0, str(args.cryptalis_checkout / 'scripts'))
    from fresh_cluster_qualification import stop_cluster
    provider = host = redis = None
    database = args.private_workdir / 'database'
    config_path = database / 'config.json'
    primary = None

    def run(stage, command, expected=0):
        argv = [str(part) for part in command]
        report['commands'].append({'stage': stage, 'argv': argv})
        started = time.monotonic_ns()
        with (args.evidence / (stage + '.log')).open('xb') as log:
            child = subprocess.Popen(argv, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
            sampler.register('operator', child.pid)
            try:
                code = child.wait(timeout=120)
            except BaseException:
                if child.poll() is None:
                    child.terminate()
                child.wait(timeout=15)
                raise
        result = {'exit_code': code, 'wall_seconds': (time.monotonic_ns() - started) / 1e9}
        if code != expected:
            raise RuntimeError('Command failed: ' + stage)
        return result

    with socket.socket() as probe:
        probe.bind(('127.0.0.1', 0))
        port = probe.getsockname()[1]
    base = f'http://127.0.0.1:{port}'

    def start_host(mode, stage):
        started = time.monotonic_ns()
        argv = [sys.executable, '-m', 'cryptalis_demo.host', '--config', str(config_path), '--mode', mode, '--port', str(port)]
        report['commands'].append({'stage': stage, 'argv': argv})
        with (args.evidence / (stage + '.log')).open('xb') as log:
            process = subprocess.Popen(argv, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
        success = False
        try:
            sampler.register('application', process.pid)
            deadline = time.monotonic() + 30
            polls = 0
            while time.monotonic() < deadline:
                polls += 1
                if process.poll() is not None:
                    raise RuntimeError('Host startup failed: ' + stage)
                try:
                    if request(base, '/health') == (200, {'status': 'ok'}):
                        success = True
                        return process, {'spawn_to_health200_seconds': (time.monotonic_ns() - started) / 1e9,
                                         'health_polls': polls}
                except urllib.error.URLError:
                    time.sleep(.01)
            raise RuntimeError('Host readiness timeout: ' + stage)
        finally:
            if not success:
                if process.poll() is None:
                    process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=15)

    def proof(stage):
        payload = {'destination': 'https://example.invalid/outage-proof-' + stage,
                   'alias': 'outage-' + uuid4().hex[:12]}
        started = time.monotonic_ns()
        status, body = request(base, '/api/v1/urls', payload)
        ended = time.monotonic_ns()
        if status != 201 or body['destination'] != payload['destination']:
            raise RuntimeError('Original committed HTTP proof failed.')
        sampler.phase = stage + '-commit-check'
        owner = owner_engine(load_config(config_path))
        try:
            with owner.connect() as connection:
                short_code, value = connection.exec_driver_sql('SELECT short_code,destination FROM urls WHERE id=%s', (body['id'],)).one()
            if short_code != body['short_code']:
                raise RuntimeError('Independent commit observation failed.')
        finally:
            owner.dispose()
        return ended, {'status': status, 'json': body, 'request_seconds': (ended - started) / 1e9,
                       'independent_committed_row': True, 'storage_kind': 'bytea' if isinstance(value, (bytes, memoryview)) else type(value).__name__}

    try:
        report['runtime_binding'] = run('installed-runtime', [sys.executable, args.cryptalis_checkout / 'scripts/test_postgres.py',
            '--installed-wheel', args.wheel, '--runtime-binding-only'])
        started = time.monotonic_ns()
        provider = provision(args.cryptalis_checkout, args.private_workdir / 'openbao')
        report['provider_provision_seconds'] = (time.monotonic_ns() - started) / 1e9
        provider_config = args.private_workdir / 'openbao/provider-config.json'
        provider_pid = int(service.docker('inspect', '--format', '{{.State.Pid}}', provider['container']))
        sampler.register('openbao', provider_pid)
        report['openbao_process_visible'] = provider_pid in process_table()
        report['openbao'] = {key: provider[key] for key in ('image', 'version', 'custody', 'limits')}
        report['setup'] = run('setup', [sys.executable, '-m', 'cryptalis_demo.setup', '--workdir', database,
            '--provider-config', provider_config, '--cryptalis-checkout', args.cryptalis_checkout, '--rows', '10000'])
        sampler.register('postgresql', int((database / 'cluster/postmaster.pid').read_text().splitlines()[0]))
        report['dataset'] = json.loads((database / 'dataset.json').read_bytes())
        configuration = load_config(config_path)
        configuration['settings']['PUBLIC_BASE_URL'] = base
        from .manage import save_config
        save_config(config_path, configuration)
        report['public_base_url'] = base
        report['providers'] = [{key: spec[key] for key in ('endpoint', 'provider_id', 'key_name', 'key_version')}
            for spec in configuration['providers']]
        with (database / 'redis.log').open('xb') as log:
            redis = subprocess.Popen([args.redis_server, '--port', '0', '--unixsocket', database / 'redis.sock',
                '--unixsocketperm', '700', '--save', '', '--appendonly', 'no'], stdout=log, stderr=log)
        sampler.register('redis', redis.pid)
        deadline = time.monotonic() + 5
        while not (database / 'redis.sock').exists() and redis.poll() is None and time.monotonic() < deadline:
            time.sleep(.01)
        if not (database / 'redis.sock').exists() or redis.poll() is not None:
            raise RuntimeError('Private Redis failed.')
        report['redis_version'] = subprocess.check_output([args.redis_server, '--version'], text=True).strip()
        probe_code = '''import json,os,sys,time
from uuid import UUID,uuid4
started=time.monotonic_ns()
import cryptalis
library_import=(time.monotonic_ns()-started)/1e9
from cryptalis_demo.host import load_config,import_application,make_provider
c=load_config(sys.argv[1])
started=time.monotonic_ns(); import_application(c); app_import=(time.monotonic_ns()-started)/1e9
started=time.monotonic_ns(); p=make_provider(c['providers'][c.get('active_provider',0)]); construction=(time.monotonic_ns()-started)/1e9
from cryptalis.crypto import KeyContext
context=KeyContext(UUID('b62c0af3-f128-4d0b-ac6a-dfc40ae6d128'),UUID(int=901),'payload',uuid4(),1)
root=os.urandom(32)
started=time.monotonic_ns(); wrapped=p.wrap(root,context); wrapping=(time.monotonic_ns()-started)/1e9
started=time.monotonic_ns(); recovered=p.unwrap(wrapped,context); unwrapping=(time.monotonic_ns()-started)/1e9
if recovered!=root: raise RuntimeError('Provider roundtrip failed')
print(json.dumps(dict(installed_library_import_seconds=library_import,original_application_import_seconds=app_import,provider_construct_seconds=construction,provider_wrap_seconds=wrapping,provider_unwrap_seconds=unwrapping,provider_roundtrip='PASS',scope='Fresh interpreter and provider object; separate HTTPS sessions with metadata+Transit requests; local provider service warmed by provisioning; no raw root output')))
'''
        report['cold_probe_process'] = run('cold-import-provider-probe', [sys.executable, '-c', probe_code, config_path])
        report['cold_import_provider_probe'] = json.loads((args.evidence / 'cold-import-provider-probe.log').read_text())
        sampler.phase = 'initial-native-host'
        host, report['native_cold_start'] = start_host('native', 'native-host')
        _, report['initial_committed_post'] = proof('native-initial')
        for operation in ('protect', 'rotate-wrapping', 'rotate-payload'):
            sampler.phase = operation
            started = time.monotonic_ns()
            host.terminate()
            stop_code = host.wait(timeout=15)
            if stop_code != 0:
                raise RuntimeError('Old host reported shutdown failure.')
            stopped = time.monotonic_ns()
            try:
                request(base, '/health')
            except urllib.error.URLError:
                pass
            else:
                raise RuntimeError('Writer port still serves after old host exit.')
            command = [sys.executable, '-m', 'cryptalis_demo.manage', operation, '--config', config_path,
                       '--writers-stopped', 'One local host gracefully stopped and reaped; no other writer or in-flight request']
            command_result = run(operation, command)
            project_result = json.loads((args.evidence / (operation + '.log')).read_text())
            host, startup = start_host('protected', operation + '-host')
            ended, committed = proof(operation)
            row = {'operation': operation, 'stop_to_first_committed_post_seconds': (ended - started) / 1e9,
                'graceful_stop_seconds': (stopped - started) / 1e9, 'stopped_host_exit_code': stop_code,
                'lifecycle_process_wall_seconds': command_result['wall_seconds'],
                'public_project_call_seconds': project_result['elapsed_seconds'],
                'process_time_outside_project_call_seconds': command_result['wall_seconds'] - project_result['elapsed_seconds'],
                'project_result': project_result['result'], 'fresh_host': startup, 'first_write': committed}
            time.sleep(.04)
            row['resources'] = sampler.summary(operation)
            report['transitions'].append(row)
        sampler.phase = 'search-refusal'
        host.terminate()
        host.wait(timeout=15)
        host = None
        refusal = run('search-refusal', [sys.executable, '-m', 'cryptalis_demo.manage', 'rotate-search', '--config', config_path,
            '--writers-stopped', 'All one-host writers stopped; search capability check only'], expected=1)
        error = json.loads((args.evidence / 'search-refusal.log').read_text())
        if error.get('code') != 'search_rotation_requires_searchable_fields':
            raise RuntimeError('Unexpected search refusal.')
        report['search_rotation'] = {'outcome': 'REFUSED', 'writer_interruption': 'UNMEASURED', 'error': error,
                                    'command_wall_seconds': refusal['wall_seconds']}
        report['source_sha256_after'] = snapshot()
        report['source_stable'] = before == report['source_sha256_after']
        report['clean_after'] = not bool(git('status', '--porcelain'))
        if not report['source_stable'] or not report['clean_after']:
            raise RuntimeError('Source changed during outage measurement.')
        report['status'] = 'PASS'
    except BaseException as error:
        primary = error
        report.update(status='FAIL', error_type=type(error).__name__)
    finally:
        sampler.phase = 'cleanup'
        for name, process in (('host', host), ('redis', redis)):
            if process is None:
                continue
            try:
                if process.poll() is None:
                    process.terminate()
                code = process.wait(timeout=15)
                report['cleanup'].append({'service': name, 'stopped': True, 'exit_code': code})
            except BaseException as error:
                report['cleanup'].append({'service': name, 'stopped': False, 'error': type(error).__name__})
        if (database / 'cluster/postmaster.pid').exists():
            try:
                stop_cluster(database / 'cluster')
                report['cleanup'].append({'service': 'postgresql', 'stopped': True})
            except BaseException as error:
                report['cleanup'].append({'service': 'postgresql', 'stopped': False, 'error': type(error).__name__})
        if provider is not None:
            try:
                service.retire_container(args.private_workdir / 'openbao', provider['container'])
                report['cleanup'].append({'service': 'openbao', 'stopped': True, 'custody_files_retained': True})
            except BaseException as error:
                report['cleanup'].append({'service': 'openbao', 'stopped': False, 'error': type(error).__name__})
        sampler.finished.set()
        sampler.join(timeout=5)
        report['resource_sampler'] = {'terminated': not sampler.is_alive(), 'error_type': sampler.failure}
        if sampler.is_alive() or sampler.failure is not None:
            report['status'] = 'FAIL'
        if any(not item['stopped'] for item in report['cleanup']):
            report['status'] = 'FAIL'
        with (args.evidence / 'resource-samples.json').open('x') as stream:
            json.dump(sampler.rows, stream)
        report['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
        report['outputs_sha256'] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(args.evidence.iterdir()) if path.is_file()}
        (args.evidence / 'outage-receipt.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'transitions': [
        {'operation': row['operation'], 'stop_to_first_committed_post_seconds': row['stop_to_first_committed_post_seconds']}
        for row in report['transitions']]}))
    if primary is not None or report['status'] != 'PASS':
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
