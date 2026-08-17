from services.permissions import ROUTINES


class UserPermissionRepository:

    def __init__(self, database):
        self.database = database
        self._ensure_table()

    def _ensure_table(self):
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_permissions (
                    user_id INTEGER NOT NULL,
                    routine VARCHAR(50) NOT NULL,
                    allowed BOOLEAN NOT NULL DEFAULT FALSE,
                    PRIMARY KEY (user_id, routine)
                )
                """
            )
        conn.commit()

    def get(self, user_id: int) -> dict[str, bool]:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT routine, allowed
                FROM user_permissions
                WHERE user_id = %s
                """,
                (user_id,),
            )
            rows = cur.fetchall()

        result = {key: False for key in ROUTINES}
        for routine, allowed in rows:
            result[routine] = bool(allowed)
        return result

    def set_all(self, user_id: int, permissions: dict[str, bool]) -> None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM user_permissions WHERE user_id = %s",
                (user_id,),
            )
            for routine in ROUTINES:
                cur.execute(
                    """
                    INSERT INTO user_permissions (user_id, routine, allowed)
                    VALUES (%s, %s, %s)
                    """,
                    (user_id, routine, bool(permissions.get(routine, False))),
                )
        conn.commit()

    def delete_all(self, user_id: int) -> None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM user_permissions WHERE user_id = %s",
                (user_id,),
            )
        conn.commit()