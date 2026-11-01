"""Create an isolated PostgreSQL cluster and deterministic original Smolink rows.

This setup is disposable local demonstration infrastructure, never deployment code.
It reuses Cryptalis's existing private-role provisioning helpers; all pytest
journeys still run through scripts/test_postgres.py.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import sys

from .host import import_application, owner_engine, private_bytes


def private_json(path, value):
    with path.open('x') as stream:
        path.chmod(0o600)
        json.dump(value, stream, indent=2)
        stream.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workdir', type=Path, required=True)
    parser.add_argument('--provider-config', type=Path, required=True)
    parser.add_argument('--cryptalis-checkout', type=Path, required=True)
    parser.add_argument('--rows', type=int, default=10000)
    args = parser.parse_args()
    if not args.workdir.is_absolute() or not 1 <= args.rows <= 1000000:
        parser.error('Use a new absolute work directory and 1..1000000 rows.')
    args.workdir.mkdir(mode=0o700, parents=True, exist_ok=False)
    sys.path.insert(0, str(args.cryptalis_checkout / 'scripts'))
    from fresh_cluster_qualification import provision, start_cluster, stop_cluster, write_home
    from sqlalchemy import text
    providers = json.loads(private_bytes(args.provider_config))
    manifest = {'owner_role': 'cryptalis_preview_owner', 'runtime_role': 'cryptalis_preview_runtime',
                'database': 'cryptalis_preview'}
    cluster = None
    try:
        cluster, port, password = start_cluster(args.workdir)
        credentials = provision(port, password, manifest, 'cryptalis_preview_unused_native')
        private = write_home(args.workdir, port, manifest, credentials,
                             source_database=manifest['database'])
        secret = secrets.token_urlsafe(48)
        config = {**providers, 'schema': 'smolink_preview',
            'owner_conninfo_file': str(private / '.cryptalis-test-url'),
            'runtime_conninfo_file': str(private / '.cryptalis-test-runtime-url'),
            'plaintext_conninfo_file': str(private / '.cryptalis-test-source-url'),
            'state_dir': str(args.workdir / 'project-state'),
            'settings': {
                'REDIS_URL': 'unix://' + str(args.workdir / 'redis.sock'),
                'JWT_SECRET': secret, 'IP_HASH_SECRET': secret, 'TOKEN_HASH_SECRET': secret,
                'PUBLIC_BASE_URL': 'http://127.0.0.1:8000', 'APP_PUBLIC_URL': 'https://app.example.invalid',
                'JWT_ISSUER': 'smolink-preview', 'JWT_AUDIENCE': 'smolink-preview',
                'ACCESS_TOKEN_TTL_SECONDS': 300, 'REFRESH_TOKEN_TTL_SECONDS': 600,
                'EMAIL_FROM': 'preview@example.invalid', 'RESEND_API_KEY': 'unused-no-mail-route-exercised',
                'GOOGLE_CLIENT_ID': 'unused', 'GOOGLE_CLIENT_SECRET': 'unused',
                'GOOGLE_REDIRECT_URI': 'https://app.example.invalid/callback',
            }}
        _, registry = import_application(config)
        from app.db.base import Base
        from app.models.url import Url
        from app.models.user import User
        owner = owner_engine(config)
        try:
            with owner.begin() as connection:
                connection.exec_driver_sql('CREATE SCHEMA smolink_preview')
            Base.metadata.create_all(owner)
            with owner.begin() as connection:
                connection.execute(User.__table__.insert().values(id=10001, email='owner@example.invalid',
                    password_hash=None, email_verified_at=datetime.now(timezone.utc)))
                values = [{'id': 5000000000 + i, 'short_code': f'seed-{i:08d}',
                    'destination': f'https://catalog.example.invalid/resources/{i:08d}?campaign=preview&source=matched-data',
                    'owner_id': 10001 if i % 3 else None} for i in range(args.rows)]
                for start in range(0, len(values), 1000):
                    connection.execute(Url.__table__.insert(), values[start:start + 1000])
                role = manifest['runtime_role']
                plain = credentials['plaintext'][0]
                connection.exec_driver_sql('REVOKE ALL ON SCHEMA smolink_preview FROM PUBLIC')
                for current in (role, plain):
                    connection.exec_driver_sql(f'GRANT USAGE ON SCHEMA smolink_preview TO "{current}"')
                    connection.exec_driver_sql(f'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA smolink_preview TO "{current}"')
            digest = hashlib.sha256(json.dumps(values, sort_keys=True).encode()).hexdigest()
            private_json(args.workdir / 'config.json', config)
            with owner.connect() as connection:
                server_version = connection.execute(text('SHOW server_version')).scalar_one()
            private_json(args.workdir / 'dataset.json', {'rows': args.rows, 'sha256': digest,
                'pattern': 'same original Url fields, deterministic IDs, 2/3 seeded verified owner',
                'server_version': server_version})
        finally:
            owner.dispose()
        print(json.dumps({'config': str(args.workdir / 'config.json'), 'rows': args.rows,
                          'dataset_sha256': digest, 'cluster_running': True}))
        cluster = None  # Retain the service for the matched demonstration.
    finally:
        if cluster is not None:
            stop_cluster(cluster)


if __name__ == '__main__':
    main()
