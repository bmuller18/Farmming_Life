from backend.services.house_service import buy_house


PLAYER_ID = 7
HOUSE_ID = 2


result = buy_house(
    player_id=3,
    house_id=1,
)

print("HOUSE PURCHASED:")
print(result)