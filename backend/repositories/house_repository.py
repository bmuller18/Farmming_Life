from backend.supabase_client import get_supabase_client


def buy_house(player_id: int, house_id: int):
    """Purchase a house by updating its owner."""
    from backend.repositories import price_repository
    from datetime import datetime, timezone

    supabase = get_supabase_client()

    # Get the house to check price
    house_response = (
        supabase
        .table("houses")
        .select("id, price, player_id")
        .eq("id", house_id)
        .single()
        .execute()
    )

    if not house_response.data:
        raise ValueError(f"House {house_id} not found")

    house = house_response.data

    if house["player_id"] is not None:
        raise ValueError("House is already owned")

    house_price = house["price"]

    # Get player's current money
    player_response = (
        supabase
        .table("player")
        .select("money")
        .eq("id", player_id)
        .single()
        .execute()
    )

    if not player_response.data:
        raise ValueError(f"Player {player_id} not found")

    player_money = player_response.data["money"]

    if player_money < house_price:
        raise ValueError(f"Insufficient funds. Need ${house_price}, have ${player_money}")

    # Deduct money from player
    new_balance = player_money - house_price
    price_repository.update_player_money(player_id, -house_price)

    # Update house owner
    update_response = (
        supabase
        .table("houses")
        .update({
            "player_id": player_id,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        .eq("id", house_id)
        .execute()
    )

    if not update_response.data:
        raise ValueError("Failed to update house ownership")

    return {
        "house_id": house_id,
        "house_name": update_response.data[0].get("name", "House"),
        "price": house_price,
        "new_balance": new_balance
    }


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


def get_available_houses_for_purchase(player_id: int):
    """Get houses available for purchase (not owned by this player)."""

    supabase = get_supabase_client()

    response = (
        supabase
        .table("houses")
        .select("*")
        .neq("player_id", player_id)
        .order("price")
        .execute()
    )

    return response.data


def purchase_house(player_id: int, house_id: int):
    """Purchase a house using the RPC function."""
    return buy_house(player_id, house_id)