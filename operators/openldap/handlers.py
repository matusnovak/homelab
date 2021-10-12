import kopf
import os
import ldap
import logging
from contextlib import contextmanager


@contextmanager
def connection():
    con = ldap.initialize(
        'ldap://{}:{}'.format(
            os.getenv('OPENLDAP_HOST'),
            os.getenv('OPENLDAP_PORT', '389')
        ), bytes_mode=False)
    con.simple_bind_s(
        os.getenv('OPENLDAP_USER'),
        os.getenv('OPENLDAP_PASSWORD')
    )

    try:
        yield con
    finally:
        con.unbind_s()


class LdapClient:
    def search(self, base: str, filter: str) -> list:
        with connection() as con:
            return con.search_s(base, ldap.SCOPE_SUBTREE, filter)

    def add(self, dn: str, entry) -> None:
        with connection() as con:
            con.add_s(dn, entry)


def ldap_create(spec: dict):
    try:
        dn = spec['dn']
        attributes = spec['attributes']

        tokens = dn.split(',')
        name = tokens[0]
        base = ','.join(tokens[1:])

        client = LdapClient()

        res = client.search(base, f'({name})')
        if not len(res):
            name_tokens = name.split('=')
            entry = [(name_tokens[0], [name_tokens[1].encode()])]

            attrs_group = {}
            for a in attributes:
                name = a['name']
                value = a['value']
                if name not in attrs_group:
                    attrs_group[name] = []
                attrs_group[name].append(value)

            for key, values in attrs_group.items():
                encoded = []
                for v in values:
                    encoded.append(str(v).encode())
                entry.append((key, encoded))

            client.add(dn, entry)
            logging.info(f'LDAP object {dn} created')
        else:
            logging.info(f'LDAP object {dn} already exists')

    except Exception as e:
        raise kopf.TemporaryError(str(e), delay=15)


@kopf.on.resume('ldapobjects', timeout=60)
@kopf.on.create('ldapobjects', timeout=60)
def create_database_fn(spec, name, meta, status, **kwargs):
    ldap_create(spec)


@kopf.on.update('ldapobjects', timeout=60)
def update_database_fn(spec, old, new, diff, **kwargs):
    # TODO cleanup of old spec
    ldap_create(spec)
