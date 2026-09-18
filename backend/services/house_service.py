from backend.repositories import house_repository


def get_houses_by_player(player_id: int):
    """Get all houses owned by a player."""
    return house_repository.get_houses_by_player(player_id)


def get_available_houses_for_purchase(player_id: int):
    """Get houses available for purchase (not owned by this player)."""
    return house_repository.get_available_houses_for_purchase(player_id)


def purchase_house(player_id: int, house_id: int, jwt_token: str = None):
    """Purchase a house for a player."""
    return house_repository.purchase_house(player_id, house_id, jwt_token)