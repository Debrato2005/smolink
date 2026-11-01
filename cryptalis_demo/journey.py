"""Observe actual application reads/edits and independent at-rest storage."""
import argparse
import asyncio
import hashlib
import importlib.util
import json
from pathlib import Path

from .host import build_runtime, load_config, owner_engine

BEFORE_BACKUP = 'https://example.invalid/latest-committed-edit-before-backup'
AFTER_RECOVERY = 'https://example.invalid/latest-committed-edit-after-recovery'


async def observe(config, mode, edit=None, expected=None):
    runtime = await build_runtime(config, mode)
    try:
        from app.repositories.url_repository import get_url_by_short_code
        async with runtime.factory() as session:
            row = await get_url_by_short_code(session, 'seed-00000000')
            if expected is not None and row.destination != expected:
                raise RuntimeError('Latest committed destination did not survive the lifecycle.')
            if edit is not None:
                row.destination = edit
                await session.commit()
                await session.refresh(row)
            current = {'id': row.id, 'destination': row.destination}
        owner = owner_engine(config)
        try:
            with owner.connect() as connection:
                stored = connection.exec_driver_sql('SELECT destination FROM urls WHERE id=%s', (current['id'],)).scalar_one()
                column_type = connection.exec_driver_sql("SELECT data_type,character_maximum_length FROM information_schema.columns "
                    "WHERE table_schema=current_schema() AND table_name='urls' AND column_name='destination'").one()
                owned_objects = connection.exec_driver_sql("SELECT count(*) FROM pg_catalog.pg_class c JOIN pg_catalog.pg_namespace n "
                    "ON n.oid=c.relnamespace WHERE n.nspname=current_schema() AND c.relname LIKE '_cryptalis_%%'").scalar_one()
                rows = connection.exec_driver_sql('SELECT count(*) FROM urls').scalar_one()
            if mode == 'protected':
                frame = bytes(stored)
                if not frame.startswith(b'CF1\0') or current['destination'].encode() in frame:
                    raise RuntimeError('At-rest ciphertext observation failed.')
                storage = {'type': column_type[0], 'frame_prefix_hex': frame[:4].hex(),
                           'stored_bytes': len(frame), 'sha256': hashlib.sha256(frame).hexdigest(),
                           'plaintext_marker_present': False}
            else:
                if stored != current['destination'] or tuple(column_type) != ('character varying', 2048):
                    raise RuntimeError('Native destination or VARCHAR constraint was not restored.')
                storage = {'type': column_type[0], 'character_limit': column_type[1],
                           'latest_value_matches': True}
            return {'mode': mode, 'application_read': current, 'independent_database': storage,
                    'url_rows': rows, 'cryptalis_owned_relations': owned_objects,
                    'cryptalis_installed': importlib.util.find_spec('cryptalis') is not None}
        finally:
            owner.dispose()
    finally:
        await runtime.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--mode', choices=('native', 'protected', 'removed'), required=True)
    parser.add_argument('--edit', choices=('before-backup', 'after-recovery'))
    parser.add_argument('--expect', choices=('before-backup', 'after-recovery'))
    args = parser.parse_args()
    values = {'before-backup': BEFORE_BACKUP, 'after-recovery': AFTER_RECOVERY}
    result = asyncio.run(observe(load_config(args.config), args.mode,
        values.get(args.edit), values.get(args.expect)))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
