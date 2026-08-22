from backend.supabase_client import get_supabase_client


def get_player_by_id(player_id: int):
    """Get a player by ID."""

    supabase = get_supabase_client()

    response = (
        supabase
        .table("player")
        .select("id, name, money, level")
        .eq("id", player_id)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def get_player_by_name(name: str):
    """Get a player by name."""

    supabase = get_supabase_client()

    response = (
        supabase
        .table("player")
        .select("id, name, money, level")
        .eq("name", name)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def create_player(
    name: str = "New Player",
    money: int = 0,
    level: int = 1,
    player_id: int | None = None,
):
    """Create a new player."""

    supabase = get_supabase_client()

    data = {
        "name": name,
        "money": money,
        "level": level,
    }

    if player_id is not None:
        data["id"] = player_id

    response = (
        supabase
        .table("player")
        .insert(data)
        .execute()
    )

    if response.data:
        return response.data[0]

    if player_id is not None:
        return get_player_by_id(player_id)

    raise RuntimeError(
        "No se pudo obtener el player recién creado."
    )