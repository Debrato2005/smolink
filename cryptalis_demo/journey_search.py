"""Exercise Smolink's own account API over protected email, step by step.

Each command runs in a fresh process, because workers restart after a lifecycle
change. No route, model or query is edited. Run from this clone's root:

    python -m cryptalis_demo.journey_search --config CONFIG STEP

The fresh-process steps print their observations; nothing here reads a credential
into its output. Mail delivery is not exercised: verification is an ORM write.
"""
import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path

from .host import build_runtime, load_config, owner_engine, project, role_name, import_application

ACCOUNT = 'Alice.Example@Example.com'
STORED = 'alice.example@example.com'
PASSWORD = 'correct horse battery staple'
RACE = 'race@example.invalid'
STOPPED = 'Demonstration: the host process is stopped; this command is the only writer.'


def client(runtime, address='198.18.200.1'):
    import httpx
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=runtime.app, client=(address, 12345)),
                             base_url='http://preview.invalid')


async def seed_account(runtime):
    """Registration needs mail delivery, so create the account as that route would."""
    from app.utils.security import hash_password
    from app.models.user import User
    async with runtime.factory() as session:
        session.add(User(id=8000000001, email=STORED, password_hash=hash_password(PASSWORD),
                         email_verified_at=datetime.now(timezone.utc)))
        await session.commit()


async def accounts(config, mode):
    runtime = await build_runtime(config, mode)
    try:
        from sqlalchemy import select
        from app.core.redis import get_redis_client
        from app.models.user import User
        await get_redis_client().flushdb()  # Private disposable service; rate limits reset per step.
        async with runtime.factory() as session:
            if await session.scalar(select(User.id).where(User.email == STORED)) is None:
                await seed_account(runtime)
        async with client(runtime) as http:
            login = await http.post('/api/v1/auth/login', json={'email': ACCOUNT, 'password': PASSWORD})
            print('POST /auth/login', login.status_code)
            assert login.status_code == 200, login.text
            token = login.json()['access_token']
            me = await http.get('/api/v1/auth/me', headers={'Authorization': 'Bearer ' + token})
            print('GET /auth/me', me.status_code, me.json()['email'])
            assert me.json()['email'] == STORED
            wrong = await http.post('/api/v1/auth/login', json={'email': ACCOUNT, 'password': 'not the password'})
            print('POST /auth/login, wrong password', wrong.status_code)
            assert wrong.status_code == 401
            missing = await http.post('/api/v1/auth/login', json={'email': 'nobody@example.com', 'password': PASSWORD})
            print('POST /auth/login, unknown email', missing.status_code)
            assert missing.status_code == 401
            taken = await http.post('/api/v1/auth/register', json={'email': ACCOUNT, 'password': PASSWORD})
            print('POST /auth/register, taken email', taken.status_code)
            assert taken.status_code == 409
    finally:
        await runtime.close()


async def race(config, mode):
    """Two sessions pass the application check; only the database can refuse one."""
    runtime = await build_runtime(config, mode)
    try:
        from sqlalchemy.exc import IntegrityError
        from app.models.user import User
        from app.repositories.user_repository import get_user_by_email
        ready = asyncio.Barrier(8)
        outcomes = []

        async def attempt(i):
            async with runtime.factory() as session:
                assert await get_user_by_email(session, RACE) is None
                await ready.wait()
                session.add(User(id=8100000000 + i, email=RACE))
                try:
                    await session.commit()
                    outcomes.append('committed')
                except IntegrityError as failure:
                    outcomes.append(getattr(failure.orig, 'sqlstate', 'unknown'))

        await asyncio.gather(*(attempt(i) for i in range(8)))
        print('concurrent inserts of one email:', sorted(outcomes))
        assert sorted(outcomes) == ['23505'] * 7 + ['committed']
        async with runtime.factory() as session:
            winner = await get_user_by_email(session, RACE)
            await session.delete(winner)
            await session.commit()
    finally:
        await runtime.close()


def observe(config):
    """An independent owner connection: what a database dump contains."""
    from sqlalchemy import text
    engine = owner_engine(config)
    try:
        with engine.connect() as connection:
            kind = connection.execute(text(
                "SELECT data_type FROM information_schema.columns WHERE table_schema = current_schema() "
                "AND table_name = 'users' AND column_name = 'email'")).scalar_one()
            value = connection.execute(text('SELECT email FROM users WHERE id = 8000000001')).scalar_one()
            indexes = connection.execute(text(
                "SELECT indexdef FROM pg_indexes WHERE schemaname = current_schema() AND tablename = 'users'")).scalars().all()
    finally:
        engine.dispose()
    stored = bytes(value) if not isinstance(value, str) else value.encode()
    print('users.email type:', kind, '| stored bytes:', len(stored), '| prefix:', stored[:8].hex())
    print('plaintext visible:', STORED.encode() in stored)
    print('indexes:', indexes)


def operate(config, action):
    _, registry = import_application(config)
    owner, operator = owner_engine(config), project(config, registry)
    try:
        if action == 'protect':
            print(operator.doctor(owner)['issues'])
            print(operator.protect(owner, runtime_role=role_name(config), writers_stopped=STOPPED,
                                   search_reviewed='Account emails are not enumerable; equality and frequency leakage are accepted.').phase)
        elif action in ('payload', 'search'):
            print(action, operator.rotate(owner, action, writers_stopped=STOPPED).phase)
        elif action == 'remove':
            print(operator.decrypt(owner, plaintext_role=role_name(config, 'plaintext'), writers_stopped=STOPPED,
                                   accept_plaintext=True, retained_backups='Disposable synthetic data; no backups.').phase)
            print(operator.remove(owner, writers_stopped=STOPPED, old_workers_stopped=True,
                                  application_verified='journey_search removed step restarts the original API.').phase)
    finally:
        owner.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('step', choices=('native', 'protect', 'protected', 'race', 'observe', 'payload', 'search', 'remove', 'removed'))
    args = parser.parse_args()
    config = load_config(args.config)
    if args.step in ('native', 'protected', 'removed'):
        asyncio.run(accounts(config, args.step))
    elif args.step == 'race':
        asyncio.run(race(config, 'protected'))
    elif args.step == 'observe':
        observe(config)
    else:
        operate(config, args.step)


if __name__ == '__main__':
    main()
