from database.models import User


class UserRepository:

    def __init__(self, database):
        self.database = database

    def find_by_username(self, username: str) -> User | None:

        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    username,
                    password_hash,
                    active,
                    created_at
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            row = cur.fetchone()

            if not row:
                return None
            return User(
                id=row[0],
                username=row[1],
                password_hash=row[2],
                active=row[3],
                created_at=row[4]
            )