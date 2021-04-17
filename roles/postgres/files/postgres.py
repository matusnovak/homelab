import sys
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def command_query(connection, args: dict):
    try:
        cursor = connection.cursor()
        assert cursor is not None

        cursor.execute(args['query'])
        results = cursor.fetchall()

        return dict(msg='Success', changed=False, results=results)

    except psycopg2.OperationalError as e:
        return dict(failed=True, msg=str(e))


def command_create(connection, args: dict):
    try:
        cursor = connection.cursor()
        assert cursor is not None

        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        changed = False

        if args['create']['database'] is not None:
            database_name = args['create']['database']['name']

            cursor.execute(
                f'SELECT * FROM pg_catalog.pg_database WHERE datname = \'{database_name}\';')
            results = cursor.fetchall()

            if len(results) == 0:
                query = f'CREATE DATABASE {database_name};'
                cursor.execute(query)
                changed = True

        if args['create']['user'] is not None:
            user_name = args['create']['user']['name']
            user_password = args['create']['user']['password']
            user_database = args['create']['user']['database']

            cursor.execute(
                f'SELECT * FROM pg_catalog.pg_roles WHERE rolname = \'{user_name}\';')
            results = cursor.fetchall()

            if len(results) == 0:
                query = f'CREATE ROLE {user_name};'
                query += f'ALTER ROLE {user_name} WITH PASSWORD \'{user_password}\';'
                query += f'ALTER ROLE {user_name} WITH LOGIN;'
                query += f'GRANT ALL PRIVILEGES ON DATABASE {user_database} TO {user_name};'
                cursor.execute(query)
                changed = True

        return dict(msg='Success', changed=changed)

    except psycopg2.OperationalError as e:
        return dict(failed=True, msg=str(e))


def main():
    command = sys.argv[1]
    args = json.loads(sys.argv[2])

    commands = {
        'query': command_query,
        'create': command_create
    }

    connection = psycopg2.connect(
        host=args['host'],
        user=args['user'],
        password=args['password'],
        dbname=args['database'],
        port=args['port']
    )

    return commands[command](connection, args)


if __name__ == '__main__':
    print(json.dumps(main()))
