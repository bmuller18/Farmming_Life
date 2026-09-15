from backend.services.player_service import get_player

player = get_player(1)

if player:
    print(f"ID: {player['id']}")
    print(f"Name: {player['name']}")
    print(f"Money: {player['money']}")
    print(f"Level: {player['level']}")
else:
    print("Player not found")