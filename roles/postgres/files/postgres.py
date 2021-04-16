import sys
import json
import psycopg2


def command_query(connection, args: dict):
    try:
        cursor = connection.cursor()
        assert cursor is not None

        cursor.execute(args['query'])
        results = cursor.fetchall()

        return dict(msg='Success', results=results)

    except psycopg2.OperationalError as e:
        return dict(failed=True, msg=str(e))


def main():
    command = sys.argv[1]
    args = json.loads(sys.argv[2])

    commands = {
        'query': command_query
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
