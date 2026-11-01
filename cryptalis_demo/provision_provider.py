"""Provision isolated OpenBao custody for the local Cryptalis demonstration.

Requires hvac and cryptography. Reuses the reviewed local service setup from
the selected Cryptalis source checkout; application encryption still comes
from the normally installed wheel. This command never provisions PostgreSQL.
Keep the private work directory and its recovery keys outside Git.
"""

import argparse
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
from uuid import uuid4

import hvac
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


def helpers(checkout):
    source = checkout / 'scripts' / 'openbao_qualification.py'
    spec = importlib.util.spec_from_file_location('cryptalis_openbao_service', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def certificates(workdir):
    """Issue localhost TLS certificates accepted by Python 3.13 strict checks."""
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'Smolink preview local CA')])
    now = datetime.now(timezone.utc)
    ca_identifier = x509.SubjectKeyIdentifier.from_public_key(ca_key.public_key())
    ca = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
          .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now - timedelta(minutes=1)).not_valid_after(now + timedelta(days=2))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
              key_encipherment=False, data_encipherment=False, key_agreement=False,
              key_cert_sign=True, crl_sign=True, encipher_only=False, decipher_only=False), critical=True)
          .add_extension(ca_identifier, critical=False)
          .add_extension(x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(ca_identifier), critical=False)
          .sign(ca_key, hashes.SHA256()))
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf = (x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')]))
            .issuer_name(name).public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=1)).not_valid_after(now + timedelta(days=1))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
                key_encipherment=True, data_encipherment=False, key_agreement=False,
                key_cert_sign=False, crl_sign=False, encipher_only=False, decipher_only=False), critical=True)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .add_extension(x509.SubjectAlternativeName([
                x509.DNSName('localhost'), x509.IPAddress(ipaddress.ip_address('127.0.0.1'))]), critical=False)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_subject_key_identifier(ca_identifier), critical=False)
            .sign(ca_key, hashes.SHA256()))
    outputs = {'ca.pem': ca.public_bytes(serialization.Encoding.PEM),
               'server.pem': leaf.public_bytes(serialization.Encoding.PEM),
               'server.key': key.private_bytes(serialization.Encoding.PEM,
                   serialization.PrivateFormat.PKCS8, serialization.NoEncryption())}
    for filename, content in outputs.items():
        (workdir / filename).write_bytes(content)
        (workdir / filename).chmod(0o600)


def repair_tls(checkout, workdir):
    """Replace only TLS material on this retained local demonstration service."""
    service = helpers(checkout)
    report_path = workdir / 'service-receipt.json'
    report = json.loads(report_path.read_text())
    container = report['container']
    retained = workdir / 'tls-before-python313-repair'
    retained.mkdir(mode=0o700, exist_ok=False)
    before = {}
    for filename in ('ca.pem', 'server.pem', 'server.key'):
        content = (workdir / filename).read_bytes()
        service.write_private(retained / filename, content)
        before[filename] = hashlib.sha256(content).hexdigest()
    service.docker('stop', '--time', '15', container)
    certificates(workdir)
    service.docker('start', container)
    client = hvac.Client(url=report['endpoint'], verify=str(workdir / 'ca.pem'),
                         token='', allow_redirects=False, timeout=10)
    try:
        if not service.wait_available(client):
            raise RuntimeError('RetainedServiceNotInitialized')
        initialized = json.loads((workdir / 'initialization.json').read_text())
        client.sys.submit_unseal_key(initialized['keys'][0])
        service.wait_active(client)
        config = json.loads((workdir / 'provider-config.json').read_text())
        controls = [verify_provider(provider) for provider in config['providers']]
        repair = dict(status='PASS', prior_failure='Python 3.13 strict TLS: Missing Authority Key Identifier',
                      previous_tls_sha256=before, native_controls=controls,
                      changes='CA and leaf certificate extensions; same container, Raft, Transit keys and tokens')
        service.write_private(workdir / 'tls-repair-receipt.json', json.dumps(repair, indent=2).encode())
        return repair
    finally:
        client.session.close()


def verify_provider(config):
    """Exercise native custody and denial controls without exposing tokens."""
    key = config['key_name']
    client = hvac.Client(url=config['endpoint'], verify=config['ca_cert'],
                         token=Path(config['token_file']).read_text(),
                         allow_redirects=False, timeout=10)
    encode = lambda value: base64.b64encode(value).decode('ascii')
    try:
        metadata = client.read(f'transit/keys/{key}')['data']
        assert metadata['type'] == 'aes256-gcm96'
        assert all(metadata[flag] is False for flag in
                   ('derived', 'exportable', 'allow_plaintext_backup', 'deletion_allowed'))
        marker, context = b'PUBLIC PREVIEW CUSTODY CONTROL', b'public-context-one'
        ciphertext = client.write(f'transit/encrypt/{key}', plaintext=encode(marker),
                                  associated_data=encode(context), key_version=1)['data']['ciphertext']
        recovered = client.write(f'transit/decrypt/{key}', ciphertext=ciphertext,
                                 associated_data=encode(context))['data']['plaintext']
        assert base64.b64decode(recovered, validate=True) == marker
        try:
            client.write(f'transit/decrypt/{key}', ciphertext=ciphertext,
                         associated_data=encode(b'wrong-public-context'))
        except hvac.exceptions.InvalidRequest:
            pass
        else:
            raise RuntimeError('WrongContextAccepted')
        for path, arguments in (
            (f'transit/keys/{key}/rotate', {}),
            ('transit/encrypt/unapproved-key', {'plaintext': encode(marker)}),
            ('auth/token/create', {'policies': ['root']}),
        ):
            try:
                client.write(path, **arguments)
            except hvac.exceptions.Forbidden:
                pass
            else:
                raise RuntimeError('UnauthorizedOperationAccepted')
        return dict(key_name=key, native_wrap_unwrap='PASS', context_mismatch='REFUSED',
                    key_rotation='DENIED', unapproved_key='DENIED', token_creation='DENIED')
    finally:
        client.session.close()


def provision(checkout, workdir):
    service = helpers(checkout)
    workdir.mkdir(mode=0o700, parents=False, exist_ok=False)
    container = 'cryptalis-bao-' + uuid4().hex
    created = False
    client = None
    try:
        service.service_files(workdir)
        certificates(workdir)
        endpoint = service.start_container(workdir, container)
        created = True
        service.write_private(workdir / 'container-name', container.encode())
        client = hvac.Client(url=endpoint, verify=str(workdir / 'ca.pem'),
                             token='', allow_redirects=False, timeout=10)
        if service.wait_available(client):
            raise RuntimeError('UnexpectedInitializedService')
        initialized = client.sys.initialize(secret_shares=1, secret_threshold=1)
        service.write_private(workdir / 'initialization.json', json.dumps(initialized).encode())
        client.sys.submit_unseal_key(initialized['keys'][0])
        service.wait_active(client)
        client.token = initialized['root_token']
        client.sys.enable_secrets_engine('transit', path='transit')
        providers = []
        for key_name in ('preview-v1', 'preview-v2'):
            client.write(f'transit/keys/{key_name}', type='aes256-gcm96', derived=False,
                         exportable=False, allow_plaintext_backup=False)
            policy = '\n'.join(
                f'path "transit/{operation}/{key_name}" {{ capabilities = ["{capability}"] }}'
                for operation, capability in [('keys', 'read'), ('encrypt', 'update'),
                                               ('decrypt', 'update')])
            client.sys.create_or_update_policy(key_name, policy)
            token = client.auth.token.create(policies=[key_name], no_default_policy=True,
                                             ttl='8h', explicit_max_ttl='8h')['auth']['client_token']
            token_file = workdir / (key_name + '-token')
            service.write_private(token_file, token.encode())
            providers.append(dict(endpoint=endpoint, ca_cert=str(workdir / 'ca.pem'),
                                  provider_id=str(uuid4()), key_name=key_name, key_version=1,
                                  token_file=str(token_file)))
        config = dict(providers=providers, active_provider=0)
        service.write_private(workdir / 'provider-config.json', json.dumps(config, indent=2).encode())
        controls = [verify_provider(provider) for provider in providers]
        report = dict(status='READY', image=service.IMAGE, version=client.sys.read_health_status(method='GET')['version'],
                      endpoint=endpoint, ca_cert=str(workdir / 'ca.pem'), container=container,
                      configuration=str(workdir / 'provider-config.json'),
                      native_controls=controls,
                      custody='single-node local TLS OpenBao; generated Transit keys; narrow 8-hour tokens',
                      limits='Local functional custody only. Production provider gate remains UNKNOWN.')
        service.write_private(workdir / 'service-receipt.json', json.dumps(report, indent=2).encode())
        return report
    except BaseException:
        if created:
            service.retire_container(workdir, container)
        raise
    finally:
        if client is not None:
            client.session.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cryptalis-source', type=Path, required=True)
    parser.add_argument('--workdir', type=Path, required=True)
    parser.add_argument('--repair-tls', action='store_true',
                        help='Replace local TLS certificates on an existing retained service; keep all custody data.')
    args = parser.parse_args()
    os.umask(0o077)
    try:
        operation = repair_tls if args.repair_tls else provision
        report = operation(args.cryptalis_source.resolve(), args.workdir.resolve())
    except Exception as error:
        # Provider errors and Docker logs can contain private service details.
        print(json.dumps(dict(status='FAIL', failure=type(error).__name__)))
        return 1
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
