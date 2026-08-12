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