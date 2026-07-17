import psycopg


class Database:
    def __init__(self, connection_url: str):
        self._conn = psycopg.connect(
            connection_url
        )

    def connection(self):
        return self._conn

    @staticmethod
    def test_connection(host, port, database, username, password):
        with psycopg.connect(
            host=host,
            port=port,
            dbname=database,
            user=username,
            password=password,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")