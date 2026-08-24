from backend.supabase_client import get_supabase_client


def create_starting_plots(player_id):
    supabase = get_supabase_client()

    plots = [
        {
            "player_id": player_id,
            "plot_number": 1,
            "price": 0,
            "purchased": True,
            "status": "empty",
        },
        {
            "player_id": player_id,
            "plot_number": 2,
            "price": 0,
            "purchased": True,
            "status": "empty",
        },
        {
            "player_id": player_id,
            "plot_number": 3,
            "price": 0,
            "purchased": True,
            "status": "empty",
        },
    ]

    response = (
        supabase
        .table("plots")
        .insert(plots)
        .execute()
    )

    return response.data