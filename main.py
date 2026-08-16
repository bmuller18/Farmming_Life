from backend.supabase_client import get_player_by_id

player = get_player_by_id(1)

if player:
    print(f"ID: {player['id']}")
    print(f"Name: {player['name']}")
    print(f"Money: {player['money']}")
    print(f"Level: {player['level']}")
else:
    print("Player not found")