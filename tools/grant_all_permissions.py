"""Concede todas as rotinas a um usuario.

Uso:
    python tools/grant_all_permissions.py [username]

Se o username nao vier como argumento, sera perguntado.
Usa a mesma conexao de banco salva nas configuracoes do app.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import Database
from database.repositories.user_permission_repository import UserPermissionRepository
from database.repositories.user_repository import UserRepository
from services.permissions import ROUTINES
from settings import AppSettings


def main():
    settings = AppSettings()
    url = settings.getConnectionUrl()
    if not url:
        print("Conexao de banco nao configurada no app. Abra o programa e configure.")
        sys.exit(1)

    username = sys.argv[1].strip() if len(sys.argv) > 1 else input("Username: ").strip()
    if not username:
        print("Informe um username.")
        sys.exit(1)

    database = Database(url)
    users = UserRepository(database)
    permissions = UserPermissionRepository(database)

    user = users.find_by_username(username)
    if user is None:
        print(f"Usuario '{username}' nao encontrado.")
        sys.exit(1)

    permissions.set_all(user.id, {key: True for key in ROUTINES})
    print(f"Permissoes concedidas para '{username}' (id={user.id}): todas as rotinas.")


if __name__ == "__main__":
    main()
