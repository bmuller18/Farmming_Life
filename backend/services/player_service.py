from backend.repositories import player_repository


def get_player(player_id: int):
    """Get a player by ID."""
    return player_repository.get_player_by_id(player_id)


def get_player_by_name(name: str):
    """Get a player by name."""
    return player_repository.get_player_by_name(name)


def create_new_player(name: str = "New Player"):
    """Create a new player with default starting values."""

    if not name or not name.strip():
        name = "New Player"

    name = name.strip()

    # Check if the name already exists
    existing_player = player_repository.get_player_by_name(name)

    if existing_player:
        raise ValueError(f"Player name '{name}' already exists")

    return player_repository.create_player(
        name=name,
        money=100,
        level=1,
    )