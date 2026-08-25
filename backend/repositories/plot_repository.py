from backend.supabase_client import get_supabase_client


def get_plots_by_house(house_id: int):
    """Get all plots belonging to a house."""

    supabase = get_supabase_client()

    response = (
        supabase
        .table("plots")
        .select("*")
        .eq("house_id", house_id)
        .order("id")
        .execute()
    )

    return response.data