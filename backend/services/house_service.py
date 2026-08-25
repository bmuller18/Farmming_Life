from backend.repositories import house_repository


def buy_house(player_id: int, house_id: int):
    """Purchase a house for a player."""
    return house_repository.buy_house(
        player_id=player_id,
        house_id=house_id,
    )


def get_houses_by_player(player_id: int):
    """Get all houses owned by a player."""

    return house_repository.get_houses_by_player(player_id)