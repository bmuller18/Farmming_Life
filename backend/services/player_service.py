from backend.repositories import player_repository


def get_player(player_id: int):
    """Get a player."""

    return player_repository.get_player_by_id(player_id)


def create_new_player(
    name: str = "New Player",
    money: int = 0,
    level: int = 1,
):
    """Create a new player."""

    if not name or not name.strip():
        name = "New Player"

    if money < 0:
        raise ValueError("Money cannot be negative")

    if level < 1:
        raise ValueError("Level must be at least 1")

    return player_repository.create_player(
        name=name,
        money=money,
        level=level,
    )