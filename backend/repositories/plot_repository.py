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


def get_plots_by_player(player_id: int):
    """Get all plots belonging to a player (through houses)."""

    supabase = get_supabase_client()

    # First get all houses for this player
    houses_response = (
        supabase
        .table("houses")
        .select("id")
        .eq("player_id", player_id)
        .execute()
    )

    if not houses_response.data:
        return []

    house_ids = [h["id"] for h in houses_response.data]

    # Then get all plots from those houses
    plots_response = (
        supabase
        .table("plots")
        .select("*")
        .in_("house_id", house_ids)
        .execute()
    )

    return plots_response.data


def create_plot(house_id: int, name: str):
    """Create a single plot for a house."""
    supabase = get_supabase_client()

    plot_data = {
        "house_id": house_id,
        "name": name,
    }
    response = supabase.table("plots").insert(plot_data).execute()
    return response.data


def create_starting_plots(house_id: int):
    """Create the default number of plots for a house based on its plot_count."""
    supabase = get_supabase_client()

    # Get house details to know plot_count
    house_response = supabase.table("houses").select("plot_count").eq("id", house_id).single().execute()
    if not house_response.data:
        raise ValueError(f"House with id {house_id} not found")

    plot_count = house_response.data["plot_count"]

    # Create plots
    for i in range(1, plot_count + 1):
        plot_data = {
            "house_id": house_id,
            "name": f"Plot {i}",
        }
        supabase.table("plots").insert(plot_data).execute()