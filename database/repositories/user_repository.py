from database.models import User


class UserRepository:

    def __init__(self, database):
        self.database = database

    def find_all(self) -> list[User]:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, password_hash, active, created_at
                FROM users
                ORDER BY username
                """
            )
            return [self._row_to_model(row) for row in cur.fetchall()]

    def search(self, term: str) -> list[User]:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, password_hash, active, created_at
                FROM users
                WHERE username ILIKE %s
                ORDER BY username
                """,
                (f"%{term}%",),
            )
            return [self._row_to_model(row) for row in cur.fetchall()]

    def find_by_username(self, username: str) -> User | None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, password_hash, active, created_at
                FROM users
                WHERE username = %s
                """,
                (username,),
            )
            row = cur.fetchone()
            return self._row_to_model(row) if row else None

    def find_by_id(self, user_id: int) -> User | None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, username, password_hash, active, created_at
                FROM users
                WHERE id = %s
                """,
                (user_id,),
            )
            row = cur.fetchone()
            return self._row_to_model(row) if row else None

    def create(self, username: str, password_hash: str, active: bool = True) -> User:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (username, password_hash, active)
                VALUES (%s, %s, %s)
                RETURNING id, username, password_hash, active, created_at
                """,
                (username, password_hash, active),
            )
            row = cur.fetchone()
        conn.commit()
        return self._row_to_model(row)

    def update(self, user_id: int, username: str, active: bool) -> User | None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET username = %s,
                    active = %s
                WHERE id = %s
                RETURNING id, username, password_hash, active, created_at
                """,
                (username, active, user_id),
            )
            row = cur.fetchone()
        conn.commit()
        return self._row_to_model(row) if row else None

    def update_password(self, user_id: int, password_hash: str) -> User | None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE users
                SET password_hash = %s
                WHERE id = %s
                RETURNING id, username, password_hash, active, created_at
                """,
                (password_hash, user_id),
            )
            row = cur.fetchone()
        conn.commit()
        return self._row_to_model(row) if row else None

    def delete(self, user_id: int) -> bool:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE id = %s",
                (user_id,),
            )
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted

    @staticmethod
    def _row_to_model(row) -> User:
        return User(
            id=row[0],
            username=row[1],
            password_hash=row[2],
            active=row[3],
            created_at=row[4],
        )
