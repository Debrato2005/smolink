"""Run public Cryptalis lifecycle calls with explicit local operator statements."""
import argparse
import json
import os
from pathlib import Path
import tempfile
import time

from .host import (import_application, load_config, make_provider, owner_engine,
                   project, role_name, sync_engine)


def save_config(path, config):
    # Publication follows the successful wrapping transition. Never rewrite secrets.
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix='.provider-')
    try:
        with os.fdopen(descriptor, 'w') as stream:
            json.dump(config, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def execute(args):
    config = load_config(args.config)
    if args.provider_index is not None:
        if not 0 <= args.provider_index < len(config['providers']):
            raise ValueError('Provider index is outside the configured list.')
        config['active_provider'] = args.provider_index
    _, registry = import_application(config)
    current = project(config, registry)
    owner = owner_engine(config)
    statement = args.writers_stopped
    started = time.perf_counter()
    try:
        if args.command == 'doctor':
            progress = current.status(owner)
            if progress is None:
                result = current.doctor(owner)
            else:
                runtime = sync_engine(config, 'runtime')
                try:
                    result = current.doctor(runtime)
                finally:
                    runtime.dispose()
        elif args.command == 'status':
            progress = current.status(owner)
            result = {'phase': None if progress is None else progress.phase}
        elif args.command == 'protect':
            result = current.protect(owner, runtime_role=role_name(config), writers_stopped=statement)
        elif args.command in ('rotate-payload', 'rotate-search'):
            result = current.rotate(owner, args.command.split('-')[1], writers_stopped=statement)
        elif args.command == 'rotate-wrapping':
            following = config.get('active_provider', 0) + 1
            result = current.rotate(owner, 'wrapping', provider=make_provider(config['providers'][following]),
                                    writers_stopped=statement)
            config['active_provider'] = following
            save_config(args.config, config)
        elif args.command == 'decrypt':
            result = current.decrypt(owner, plaintext_role=role_name(config, 'plaintext'),
                writers_stopped=statement, accept_plaintext=True,
                retained_backups=args.retained_backups)
        elif args.command == 'remove':
            result = current.remove(owner, writers_stopped=statement,
                application_verified=args.application_verified, old_workers_stopped=True)
        else:
            raise ValueError('Unknown command.')
        if not isinstance(result, dict):
            result = {'phase': getattr(result, 'phase', None),
                      'committed_rows': getattr(result, 'committed_rows', None)}
        return {'operation': args.command, 'elapsed_seconds': time.perf_counter() - started,
                'result': result}
    finally:
        owner.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('doctor', 'status', 'protect', 'rotate-payload',
        'rotate-search', 'rotate-wrapping', 'decrypt', 'remove'))
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--provider-index', type=int, help='Explicit provider selection after inspecting an interrupted wrapping publication.')
    parser.add_argument('--writers-stopped', help='Required operator statement for every mutation.')
    parser.add_argument('--retained-backups', help='Required recovery-key retention statement for decrypt.')
    parser.add_argument('--application-verified', help='Required native restart evidence for remove.')
    args = parser.parse_args()
    if args.command not in ('doctor', 'status') and not args.writers_stopped:
        parser.error('Supply --writers-stopped with the actual writer-exclusion statement.')
    if args.command == 'decrypt' and not args.retained_backups:
        parser.error('Supply --retained-backups; this command retires no key.')
    if args.command == 'remove' and not args.application_verified:
        parser.error('Supply --application-verified after a native restart and current-value check.')
    try:
        result = execute(args)
    except Exception as error:
        # Public demo output must not echo driver SQL, credentials or provider bodies.
        import sys
        print(json.dumps({'operation': args.command, 'error': type(error).__name__,
            'code': getattr(error, 'code', None), 'remedy': getattr(error, 'remedy', None)}),
            file=sys.stderr)
        raise SystemExit(1) from None
    print(json.dumps(result, indent=2, default=str))


if __name__ == '__main__':
    main()
