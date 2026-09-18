import os

from dotenv import load_dotenv
from supabase import create_client, Client


load_dotenv()


def get_supabase_client(jwt_token: str = None) -> Client:
    """Create and return a Supabase client instance."""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
        )

    client = create_client(supabase_url, supabase_key)

    # Si hay token JWT, lo usamos para autenticación
    if jwt_token:
        client.auth.set_session(access_token=jwt_token, refresh_token="")

    return client