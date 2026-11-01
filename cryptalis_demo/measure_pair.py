"""Bind a fresh native/protected measurement pair to committed code and wheel.

Requires an already provisioned private OpenBao service. All databases, Redis
state and generated credentials are disposable and isolated; recovery files stay
in --private-workdir. Public reports contain no credentials or database dump.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def snapshot():
    paths = [*ROOT.joinpath('backend/app').rglob('*.py'),
             *ROOT.joinpath('cryptalis_demo').glob('*.py'),
             ROOT / 'cryptalis_demo/manifest.json', ROOT / 'cryptalis_demo/requirements.txt',
             ROOT / 'backend/pyproject.toml', ROOT / 'backend/uv.lock']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--provider-config', type=Path, required=True)
    parser.add_argument('--cryptalis-checkout', type=Path, required=True)
    parser.add_argument('--library-revision', required=True)
    parser.add_argument('--wheel', type=Path, required=True)
    parser.add_argument('--redis-server', type=Path, required=True)
    parser.add_argument('--private-workdir', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--samples', type=int, default=256)
    args = parser.parse_args()
    if git('status', '--porcelain'):
        parser.error('Commit the demonstration source first; use a clean checkout.')
    if any(not p.is_absolute() for p in (args.private_workdir, args.evidence)):
        parser.error('Use new absolute private and evidence directories.')
    if args.private_workdir.exists():
        parser.error('Preserve prior private work; select a new directory.')
    args.evidence.mkdir(mode=0o700, parents=True, exist_ok=False)
    before = snapshot()
    record = {'status': 'INCOMPLETE', 'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'demo_revision': git('rev-parse', 'HEAD'), 'demo_clean_before': True,
        'library_revision': args.library_revision,
        'wheel_sha256': hashlib.sha256(args.wheel.read_bytes()).hexdigest(),
        'source_sha256_before': before, 'commands': [], 'cleanup_failures': [],
        'hardware': {'cpu_count_visible': os.cpu_count(), 'architecture': platform.machine(),
                     'kernel': platform.release()},
        'measurement': {'samples_per_workload': args.samples, 'concurrency': [1, 4, 16],
            'warmup_repository_reads': 32, 'keyring_default_max_age_seconds': 60,
            'pool_pre_ping': True, 'pool_size': 5, 'max_overflow': 10,
            'expire_on_commit': False, 'provider': 'real HTTPS local OpenBao',
            'mode_order': 'native then protection then protected; not randomized',
            'contention': 'shared managed host, background contention not controlled'}}
    for name, path in (('cpu_quota', '/sys/fs/cgroup/cpu.max'),
                       ('memory_limit', '/sys/fs/cgroup/memory.max')):
        record['hardware'][name] = Path(path).read_text().strip()
    record['hardware']['cpu_model'] = next(line.split(':', 1)[1].strip()
        for line in Path('/proc/cpuinfo').read_text().splitlines() if line.startswith('model name'))
    environment = dict(os.environ)
    environment.pop('PYTHONPATH', None)

    def run(name, command):
        record['commands'].append({'stage': name, 'argv': [str(x) for x in command]})
        with (args.evidence / (name + '.log')).open('xb') as log:
            result = subprocess.run(command, cwd=ROOT, env=environment, stdout=log, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError('Measurement stage failed: ' + name)

    redis = None
    primary_failure = None
    sys.path.insert(0, str(args.cryptalis_checkout / 'scripts'))
    from fresh_cluster_qualification import stop_cluster
    try:
        run('installed-runtime', [sys.executable, args.cryptalis_checkout / 'scripts/test_postgres.py',
            '--installed-wheel', args.wheel, '--runtime-binding-only'])
        run('setup', [sys.executable, '-m', 'cryptalis_demo.setup', '--workdir', args.private_workdir,
            '--provider-config', args.provider_config, '--cryptalis-checkout', args.cryptalis_checkout,
            '--rows', '10000'])
        socket = args.private_workdir / 'redis.sock'
        with (args.private_workdir / 'redis.log').open('xb') as log:
            redis = subprocess.Popen([args.redis_server, '--port', '0', '--unixsocket', socket,
                '--unixsocketperm', '700', '--save', '', '--appendonly', 'no'], stdout=log, stderr=log)
        deadline = time.monotonic() + 5
        while not socket.exists() and redis.poll() is None and time.monotonic() < deadline:
            time.sleep(.02)
        if not socket.exists() or redis.poll() is not None:
            raise RuntimeError('Private Redis startup failed.')
        record['redis_server'] = subprocess.check_output([args.redis_server, '--version'], text=True).strip()
        config = args.private_workdir / 'config.json'
        for mode in ('native', 'protected'):
            if mode == 'protected':
                run('protect', [sys.executable, '-m', 'cryptalis_demo.manage', 'protect', '--config', config,
                    '--writers-stopped', 'Only this isolated benchmark process; all known writers stopped'])
            run(mode, [sys.executable, '-m', 'cryptalis_demo.benchmark', '--config', config,
                '--mode', mode, '--output', args.evidence / (mode + '.json'), '--samples', str(args.samples)])
        dataset = args.private_workdir / 'dataset.json'
        record['dataset'] = json.loads(dataset.read_bytes())
        record['dataset_file_sha256'] = hashlib.sha256(dataset.read_bytes()).hexdigest()
        providers = json.loads(args.provider_config.read_bytes())
        record['providers'] = [{key: spec[key] for key in
            ('provider_id', 'endpoint', 'key_name', 'key_version') if key in spec}
            for spec in providers['providers']]
        service = args.provider_config.parent / 'service-receipt.json'
        if service.exists():
            native_service = json.loads(service.read_bytes())
            record['openbao'] = {key: native_service[key] for key in ('version', 'image', 'custody', 'limits')}
        record['source_sha256_after'] = snapshot()
        record['demo_clean_after'] = not bool(git('status', '--porcelain'))
        record['source_stable'] = before == record['source_sha256_after']
        if not record['source_stable'] or not record['demo_clean_after']:
            raise RuntimeError('Demonstration source changed during measurement.')
        record['status'] = 'PASS'
    except BaseException as error:
        primary_failure = error
        record.update(status='FAIL', failure_type=type(error).__name__)
        raise
    finally:
        if redis is not None:
            try:
                if redis.poll() is None:
                    redis.terminate()
                redis.wait(timeout=10)
            except BaseException as error:
                record['cleanup_failures'].append({'stage': 'redis', 'error': type(error).__name__})
        cluster = args.private_workdir / 'cluster'
        if (cluster / 'postmaster.pid').exists():
            try:
                stop_cluster(cluster)
            except BaseException as error:
                record['cleanup_failures'].append({'stage': 'postgres', 'error': type(error).__name__})
        if record['cleanup_failures']:
            record['status'] = 'FAIL'
        record['finished_at_utc'] = datetime.now(timezone.utc).isoformat()
        record['outputs_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(args.evidence.iterdir()) if p.is_file()}
        (args.evidence / 'pair-receipt.json').write_text(json.dumps(record, indent=2) + '\n')
        if record['cleanup_failures'] and primary_failure is None:
            raise RuntimeError('Service cleanup failed; inspect pair-receipt.json.')


if __name__ == '__main__':
    main()
