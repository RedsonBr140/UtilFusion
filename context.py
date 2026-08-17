from database.repositories.filial_repository import FilialRepository
from database.repositories.user_repository import UserRepository
from database.repositories.user_permission_repository import UserPermissionRepository
from database.repositories.cisspoder_config_repository import CisspoderConfigRepository
from database.repositories.concorrente_repository import ConcorrenteRepository
from fusion import FusionClient
from database.connection import Database
from services.auth_service import AuthService


class AppContext:
    def __init__(self):
        # Clients and Database connections
        self.database: Database | None = None
        self.FusionClient: FusionClient | None = None

        # Repositories
        self.users: UserRepository | None = None
        self.user_permissions: UserPermissionRepository | None = None
        self.filiais: FilialRepository | None = None
        self.cisspoder_config: CisspoderConfigRepository | None = None
        self.concorrentes: ConcorrenteRepository | None = None

        # Services
        self.auth: AuthService | None = None

        # Current logged in user (local app auth)
        self.current_username: str | None = None
