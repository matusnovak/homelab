import kopf
import psycopg2
import os
import logging
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class Connection():
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB', 'postgres'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT', 5432),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.conn.autocommit = True
        self.cur = None

    def __enter__(self):
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, type, value, traceback):
        if self.cur:
            self.cur.close()
        self.conn.close()


def postgres_exec(query: str) -> list:
    with Connection() as c:
        c.execute(query)
        try:
            return c.fetchall()
        except psycopg2.ProgrammingError:
            return []


def postgres_create(spec):
    try:
        db_name = spec['name']
        db_role = spec['role']
        db_encoding = ' ENCODING \'{}\''.format(spec['encoding']) if 'encoding' in spec else ''
        db_collate = ' LC_COLLATE=\'{}\''.format(spec['collate']) if 'collate' in spec else ''
        db_ctype = ' LC_CTYPE=\'{}\''.format(spec['ctype']) if 'ctype' in spec else ''
        db_password = spec['password']
        db_superuser = spec['superuser'] if 'superuser' in spec else False

        db_extra = '{}{}{}'.format(db_encoding, db_collate, db_ctype)
        if db_extra:
            db_extra += 'template=template0'

        rows = postgres_exec(
            f'SELECT * FROM pg_catalog.pg_roles WHERE rolname = \'{db_role}\';')

        if not rows:
            queries = [
                f'CREATE ROLE {db_role};',
                f'ALTER ROLE {db_role} WITH PASSWORD \'{db_password}\';',
                f'ALTER ROLE {db_role} WITH LOGIN;',
            ]

            if db_superuser:
                queries += [f'ALTER ROLE {db_role} WITH SUPERUSER;']

            postgres_exec('\n'.join(queries))

            logging.info(f'Postgres role {db_role} created')
        else:
            logging.info(f'Postgres role {db_role} already exists')

        rows = postgres_exec(
            f'SELECT * FROM pg_catalog.pg_database WHERE datname = \'{db_name}\';')

        if not len(rows):
            queries = [
                f'CREATE DATABASE {db_name}{db_extra}',
                f'GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_role}'
            ]

            for q in queries:
                postgres_exec(q)

            logging.info(f'Postgres database {db_name} created')
        else:
            logging.info(f'Postgres database {db_name} already exists')
    except psycopg2.OperationalError as e:
        raise kopf.TemporaryError(str(e), delay=15)


@kopf.on.resume('postgresdatabases', timeout=60)
@kopf.on.create('postgresdatabases', timeout=60)
def create_database_fn(spec, name, meta, status, **kwargs):
    postgres_create(spec)


@kopf.on.update('postgresdatabases', timeout=60)
def update_database_fn(spec, old, new, diff, **kwargs):
    # TODO cleanup of old spec
    postgres_create(spec)
