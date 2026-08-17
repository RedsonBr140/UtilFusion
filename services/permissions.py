from __future__ import annotations

# Rotinas do programa. A chave identifica a permissao no banco e o valor e o
# rotulo mostrado na interface. Manter a ordem estavel (aparece nas janelas).
ROUTINES: dict[str, str] = {
    "config": "Configurações",
    "filiais": "Filiais",
    "concorrentes": "Concorrentes",
    "usuarios": "Usuários",
    "consulta_menor_preco": "Atualizar via Menor Preço",
    "cotar_site_concorrente": "Cotar no site do concorrente",
    "consulta_pedido_fusion": "Consulta Pedido Fusion",
    "relatorio_concorrencia": "Relatório de Concorrência",
}


def all_granted() -> dict[str, bool]:
    return {key: True for key in ROUTINES}


def all_denied() -> dict[str, bool]:
    return {key: False for key in ROUTINES}


def user_permissions(context) -> dict[str, bool]:
    """Permissoes do usuario logado. A conta 'test' (bypass) e qualquer falha
    de configuracao retornam tudo liberado para nao travar o programa."""
    username = getattr(context, "current_username", None)
    if not username or username == "test":
        return all_granted()

    users = getattr(context, "users", None)
    db_user = users.find_by_username(username) if users else None
    if db_user is None:
        return all_granted()

    repo = getattr(context, "user_permissions", None)
    if repo is None:
        return all_granted()
    return repo.get(db_user.id)


def can(context, routine: str) -> bool:
    return bool(user_permissions(context).get(routine, False))