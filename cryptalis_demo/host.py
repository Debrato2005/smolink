"""Serve the original Smolink application with one replaced session dependency.

Run from this clone: python -m cryptalis_demo.host --config /private/config.json
Credentials, provider tokens and Cryptalis deployment state stay outside Git.
"""
import argparse
import asyncio
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import stat
import sys
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]


def private_bytes(path):
    path = Path(path)
    info = path.lstat()
    if (not path.is_absolute() or not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid() or info.st_mode & 0o077):
        raise ValueError('Private input must be an absolute owner-only regular file.')
    return path.read_bytes()


def load_config(path):
    result = json.loads(private_bytes(path))
    if not re.fullmatch(r'[a-z][a-z0-9_]{0,62}', result['schema']):
        raise ValueError('Use a simple lowercase private schema name.')
    return result


def import_application(config):
    # Set every required application setting explicitly. Do not consume a .env.
    if (Path.cwd() / '.env').exists():
        raise ValueError('Run from a directory without .env; use the explicit private config.')
    os.environ.update({name: str(value) for name, value in config['settings'].items()})
    os.environ['DATABASE_URL'] = 'postgresql+psycopg://'
    backend = str(ROOT / 'backend')
    if backend not in sys.path:
        sys.path.insert(0, backend)
    from app.main import app
    from app.db.base import Base
    from app import models  # Register the original eight models; change no declaration.
    return app, Base.registry


def make_provider(spec):
    from cryptalis.crypto.openbao import OpenBaoTransitKeyProvider
    return OpenBaoTransitKeyProvider(
        endpoint=spec['endpoint'], ca_cert=spec['ca_cert'],
        token=lambda: private_bytes(spec['token_file']).decode().strip(),
        provider_id=UUID(spec['provider_id']), key_name=spec.get('key_name', spec.get('transit_key')),
        key_version=spec.get('key_version', 1), timeout=10,
    )


def project(config, registry):
    from cryptalis import Project
    return Project(ROOT / 'cryptalis_demo/manifest.json', registry,
                   provider=make_provider(config['providers'][config.get('active_provider', 0)]),
                   state_dir=config['state_dir'])


def sync_engine(config, role='owner'):
    import psycopg
    from sqlalchemy import create_engine
    return create_engine('postgresql+psycopg://', hide_parameters=True,
        creator=lambda: psycopg.connect(private_bytes(config[role + '_conninfo_file']).decode().strip(),
                                       options='-csearch_path=' + config['schema']))


def owner_engine(config):
    return sync_engine(config, 'owner')


def role_name(config, role='runtime'):
    import psycopg
    values = psycopg.conninfo.conninfo_to_dict(private_bytes(config[role + '_conninfo_file']).decode().strip())
    return values['user']


@dataclass
class Runtime:
    app: object
    factory: object
    engine: object

    async def close(self):
        from app.core.redis import get_redis_client
        from app.db.session import engine as unused_original_engine
        try:
            await get_redis_client().aclose()
        finally:
            try:
                await self.engine.dispose()
            finally:
                await unused_original_engine.dispose()


async def build_runtime(config, mode='protected'):
    """Return original app, a session factory and its async engine.

    Use one mode per fresh process. Attaching changes the process's ORM registry.
    Native and removed modes do not import Cryptalis.
    """
    import psycopg
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    app, registry = import_application(config)
    role = 'plaintext' if mode == 'removed' else 'runtime'
    engine = create_async_engine('postgresql+psycopg://', hide_parameters=True, pool_pre_ping=True,
        async_creator=lambda: psycopg.AsyncConnection.connect(
            private_bytes(config[role + '_conninfo_file']).decode().strip(),
            options='-csearch_path=' + config['schema']))
    try:
        if mode == 'protected':
            attached = await project(config, registry).attach(engine)
            factory = lambda: attached(tenant_id=UUID('00000000-0000-0000-0000-000000000385'),
                                        expire_on_commit=False)
        elif mode in ('native', 'removed'):
            factory = async_sessionmaker(engine, expire_on_commit=False)
        else:
            raise ValueError('Mode must be native, protected or removed.')
    except BaseException as primary:
        try:
            await engine.dispose()
        except BaseException as cleanup:
            primary.add_note("Engine cleanup failed: " + type(cleanup).__name__)
        raise
    from app.db.session import get_session

    async def sessions():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = sessions
    return Runtime(app, factory, engine)


async def serve(config, mode, port):
    import uvicorn
    runtime = await build_runtime(config, mode)
    try:
        server = uvicorn.Server(uvicorn.Config(runtime.app, host='127.0.0.1', port=port,
            access_log=False, log_level='warning'))
        await server.serve()
    finally:
        await runtime.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--mode', choices=('native', 'protected', 'removed'), default='protected')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    asyncio.run(serve(load_config(args.config), args.mode, args.port))


if __name__ == '__main__':
    main()
