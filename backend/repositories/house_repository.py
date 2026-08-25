from backend.supabase_client import get_supabase_client


def buy_house(player_id: int, house_id: int):
    supabase = get_supabase_client()

    response = supabase.rpc(
        "buy_house",
        {
            "p_player_id": player_id,
            "p_house_id": house_id,
        },
    ).execute()

    if not response.data:
        raise ValueError("House purchase failed")

    return response.data[0]


def get_houses_by_player(player_id: int):
    """Get all houses owned by a player."""

    supabase = get_supabase_client()

    response = (
        supabase
        .table("houses")
        .select("*")
        .eq("player_id", player_id)
        .order("id")
        .execute()
    )

    return response.data