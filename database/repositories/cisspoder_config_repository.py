from database.models import CisspoderConfig


class CisspoderConfigRepository:

    def __init__(self, database):
        self.database = database
        self._ensure_table()

    def _ensure_table(self):
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS cisspoder_config (
                    id SERIAL PRIMARY KEY,
                    host VARCHAR(255) NOT NULL DEFAULT '',
                    port VARCHAR(10) NOT NULL DEFAULT '',
                    database_name VARCHAR(255) NOT NULL DEFAULT '',
                    username VARCHAR(255) NOT NULL DEFAULT '',
                    password VARCHAR(255) NOT NULL DEFAULT ''
                )
                """
            )
            cur.execute(
                """
                INSERT INTO cisspoder_config (id)
                VALUES (1)
                ON CONFLICT (id) DO NOTHING
                """
            )
        conn.commit()

    def get(self) -> CisspoderConfig:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT host, port, database_name, username, password
                FROM cisspoder_config
                WHERE id = 1
                """
            )
            row = cur.fetchone()
            if not row:
                return CisspoderConfig("", "", "", "", "")
            return CisspoderConfig(
                host=row[0],
                port=row[1],
                database_name=row[2],
                username=row[3],
                password=row[4],
            )

    def save(self, config: CisspoderConfig):
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE cisspoder_config
                SET host = %s,
                    port = %s,
                    database_name = %s,
                    username = %s,
                    password = %s
                WHERE id = 1
                """,
                (
                    config.host,
                    config.port,
                    config.database_name,
                    config.username,
                    config.password,
                ),
            )
        conn.commit()
