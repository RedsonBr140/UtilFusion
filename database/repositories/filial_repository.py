from database.models import Filial


class FilialRepository:

    def __init__(self, database):
        self.database = database

    def find_all(self) -> list[Filial]:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome_fantasia,
                    endereco,
                    cidade,
                    estado,
                    telefone,
                    created_at
                FROM filiais
                ORDER BY nome_fantasia
                """
            )

            return [
                Filial(
                    id=row[0],
                    nome_fantasia=row[1],
                    endereco=row[2],
                    cidade=row[3],
                    estado=row[4],
                    telefone=row[5],
                    created_at=row[6],
                )
                for row in cur.fetchall()
            ]

    def search(self, term: str) -> list[Filial]:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome_fantasia,
                    endereco,
                    cidade,
                    estado,
                    telefone,
                    created_at
                FROM filiais
                WHERE nome_fantasia ILIKE %s
                ORDER BY nome_fantasia
                """,
                (f"%{term}%",)
            )

            return [
                Filial(
                    id=row[0],
                    nome_fantasia=row[1],
                    endereco=row[2],
                    cidade=row[3],
                    estado=row[4],
                    telefone=row[5],
                    created_at=row[6],
                )
                for row in cur.fetchall()
            ]

    def find_by_id(self, filial_id: int) -> Filial | None:
        conn = self.database.connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id,
                    nome_fantasia,
                    endereco,
                    cidade,
                    estado,
                    telefone,
                    created_at
                FROM filiais
                WHERE id = %s
                """,
                (filial_id,)
            )

            row = cur.fetchone()

            if not row:
                return None
            return Filial(
                id=row[0],
                nome_fantasia=row[1],
                endereco=row[2],
                cidade=row[3],
                estado=row[4],
                telefone=row[5],
                created_at=row[6],
            )
