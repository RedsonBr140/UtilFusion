from database.models import Concorrente

CONCORRENTE_TIPOS = (
    "generico",
)


class ConcorrenteRepository:
    def __init__(self, database):
        self.database = database
        self._ensure_table()

    def _ensure_table(self):
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS concorrentes (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    id_erp INTEGER NOT NULL UNIQUE,
                    tipo VARCHAR(50) NOT NULL,
                    active BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        conn.commit()

    def find_all(self, only_active: bool = False) -> list[Concorrente]:
        conn = self.database.connection()
        with conn.cursor() as cur:
            sql = """
                SELECT id, nome, id_erp, tipo, active, created_at
                FROM concorrentes
            """
            if only_active:
                sql += " WHERE active = TRUE"
            sql += " ORDER BY nome"
            cur.execute(sql)
            return [self._row_to_model(row) for row in cur.fetchall()]

    def search(self, term: str, only_active: bool = False) -> list[Concorrente]:
        conn = self.database.connection()
        with conn.cursor() as cur:
            sql = """
                SELECT id, nome, id_erp, tipo, active, created_at
                FROM concorrentes
                WHERE nome ILIKE %s
            """
            if only_active:
                sql += " AND active = TRUE"
            sql += " ORDER BY nome"
            cur.execute(sql, (f"%{term}%",))
            return [self._row_to_model(row) for row in cur.fetchall()]

    def find_by_id(self, concorrente_id: int) -> Concorrente | None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, nome, id_erp, tipo, active, created_at
                FROM concorrentes
                WHERE id = %s
                """,
                (concorrente_id,),
            )
            row = cur.fetchone()
            return self._row_to_model(row) if row else None

    def create(self, nome: str, id_erp: int, tipo: str, active: bool = True) -> Concorrente:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO concorrentes (nome, id_erp, tipo, active)
                VALUES (%s, %s, %s, %s)
                RETURNING id, nome, id_erp, tipo, active, created_at
                """,
                (nome, id_erp, tipo, active),
            )
            row = cur.fetchone()
        conn.commit()
        return self._row_to_model(row)

    def update(
        self,
        concorrente_id: int,
        nome: str,
        id_erp: int,
        tipo: str,
        active: bool,
    ) -> Concorrente | None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE concorrentes
                SET nome = %s,
                    id_erp = %s,
                    tipo = %s,
                    active = %s
                WHERE id = %s
                RETURNING id, nome, id_erp, tipo, active, created_at
                """,
                (nome, id_erp, tipo, active, concorrente_id),
            )
            row = cur.fetchone()
        conn.commit()
        return self._row_to_model(row) if row else None

    def delete(self, concorrente_id: int) -> bool:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM concorrentes WHERE id = %s",
                (concorrente_id,),
            )
            deleted = cur.rowcount > 0
        conn.commit()
        return deleted

    @staticmethod
    def _row_to_model(row) -> Concorrente:
        return Concorrente(
            id=row[0],
            nome=row[1],
            id_erp=row[2],
            tipo=row[3],
            active=row[4],
            created_at=row[5],
        )
