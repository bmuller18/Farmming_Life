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