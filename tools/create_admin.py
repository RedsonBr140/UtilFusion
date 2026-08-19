"""Cria um usuario administrador.

Uso:
    python tools/create_admin.py [username] [--url postgresql://...]

Se o username nao vier como argumento, sera perguntado.
A conexao de banco vem das configuracoes salvas do app (QSettings),
ou pode ser informada via --url / variavel de ambiente DATABASE_URL.
"""

import argparse
import os
import sys
from getpass import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from argon2 import PasswordHasher

from database.connection import Database
from database.repositories.user_repository import UserRepository
from settings import AppSettings


def get_connection_url() -> str:
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        return url

    url = AppSettings().getConnectionUrl()
    if url:
        return url

    print(
        "Conexao de banco nao configurada.\n"
        "Configure no app (Arquivo > Configuracoes) ou informe "
        "DATABASE_URL / --url."
    )
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Cria um usuario no app.")
    parser.add_argument("username", nargs="?", help="Username do novo usuario")
    parser.add_argument("--url", help="URL de conexao postgresql://...")
    args = parser.parse_args()

    url = args.url.strip() if args.url else get_connection_url()

    username = args.username.strip() if args.username else input("Username: ").strip()
    if not username:
        print("Informe um username.")
        sys.exit(1)

    password = getpass("Password: ")
    if not password:
        print("Informe uma senha.")
        sys.exit(1)

    database = Database(url)
    users = UserRepository(database)

    if users.find_by_username(username) is not None:
        print(f"Usuario '{username}' ja existe.")
        sys.exit(1)

    password_hash = PasswordHasher().hash(password)
    user = users.create(username, password_hash, active=True)
    print(f"Usuario '{user.username}' criado (id={user.id}).")


if __name__ == "__main__":
    main()