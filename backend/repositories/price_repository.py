from backend.supabase_client import get_supabase_client


def get_price_by_crop_type(crop_type_id: int):
	"""Get price information for a crop type."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("prices")
		.select("*")
		.eq("crop_type_id", crop_type_id)
		.single()
		.execute()
	)

	return response.data if response.data else None


def get_all_prices():
	"""Get all prices."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("prices")
		.select("*")
		.execute()
	)

	return response.data


def update_player_money(player_id: int, amount: int):
	"""Add or subtract money from a player."""

	supabase = get_supabase_client()

	# Get current money
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

	current_money = player_response.data["money"]
	new_money = current_money + amount

	# Prevent negative money
	if new_money < 0:
		raise ValueError(f"Insufficient funds. Current: ${current_money}, Needed: ${abs(amount)}")

	# Update money
	response = (
		supabase
		.table("player")
		.update({"money": new_money})
		.eq("id", player_id)
		.execute()
	)

	if response.data:
		return response.data[0]

	raise RuntimeError("Failed to update player money")


def get_player_money(player_id: int):
	"""Get player's current money."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("player")
		.select("money")
		.eq("id", player_id)
		.single()
		.execute()
	)

	return response.data["money"] if response.data else 0
