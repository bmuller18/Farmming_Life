from backend.supabase_client import get_player_by_id, create_player

def get_or_create_player(player_id: int | None = None, name: str = "New Player", money: int = 0, level: int = 1):
    """
    Get a player by ID. If the player does not exist, create a new one with the given ID and optional defaults.

    Returns the player dictionary.
    """
    player = get_player_by_id(player_id)
    if player is None:
        player = create_player(name=name, money=money, level=level)
    return player

def show_player(player_id: int):
    """
    Fetch and display player information. If player does not exist, create it first.
    Prints player details to stdout.
    """
    player = get_or_create_player(player_id)
    if player:
        print(f"ID: {player['id']}")
        print(f"Name: {player['name']}")
        print(f"Money: {player['money']}")
        print(f"Level: {player['level']}")
    else:
        print("Failed to retrieve or create player.")