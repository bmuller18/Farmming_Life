import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


def get_supabase_client() -> Client:
    """Create and return a Supabase client instance."""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
        )

    return create_client(supabase_url, supabase_key)


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


def create_player(player_id: int, name: str = "New Player", money: int = 0, level: int = 1):
    """Create a new player with the given ID and optional default values."""
    supabase = get_supabase_client()

    data = {
        "id": player_id,
        "name": name,
        "money": money,
        "level": level
    }

    response = supabase.table("player").insert(data).execute()

    # Assuming insert returns list of inserted rows
    if response.data:
        return response.data[0]
    else:
        # If no data returned, fetch the newly created player to confirm
        return get_player_by_id(player_id)