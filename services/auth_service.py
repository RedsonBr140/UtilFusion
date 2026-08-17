from argon2 import PasswordHasher

from database.models import User
from database.repositories.user_repository import UserRepository


class AuthService:

    def __init__(self, users: UserRepository):
        self.users = users
        self.passwords = PasswordHasher()


    def login(self, username: str, password: str) -> User:

        user = self.users.find_by_username(username)

        if not user:
            raise Exception(
                "Credenciais inválidas"
            )

        if not user.active:
            raise Exception("Usuário inativo")

        self.passwords.verify(
            user.password_hash,
            password
        )

        return user