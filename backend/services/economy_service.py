from backend.repositories import price_repository, crop_repository, plot_repository
from backend.services.crop_service import get_active_crop


def get_seed_price(crop_type_id: int):
	"""Get the price of seeds for a crop type."""

	price_info = price_repository.get_price_by_crop_type(crop_type_id)

	if not price_info:
		raise ValueError(f"Price information not found for crop type {crop_type_id}")

	return price_info["seed_price"]


def get_crop_price(crop_type_id: int):
	"""Get the selling price of a harvested crop."""

	price_info = price_repository.get_price_by_crop_type(crop_type_id)

	if not price_info:
		raise ValueError(f"Price information not found for crop type {crop_type_id}")

	return price_info["crop_price"]


def buy_seeds(player_id: int, crop_type_id: int, quantity: int = 1):
	"""Buy seeds for a crop type."""

	seed_price = get_seed_price(crop_type_id)
	total_cost = seed_price * quantity

	# Deduct money from player
	player = price_repository.update_player_money(player_id, -total_cost)

	return {
		"player_id": player_id,
		"crop_type_id": crop_type_id,
		"quantity": quantity,
		"seed_price": seed_price,
		"total_cost": total_cost,
		"new_balance": player["money"]
	}


def sell_crops(crop_id: int, player_id: int):
	"""Sell a harvested crop and add money to player."""

	# Get crop info
	from backend.supabase_client import get_supabase_client

	supabase = get_supabase_client()

	crop_response = (
		supabase
		.table("crops")
		.select("*, crop_types(id)")
		.eq("id", crop_id)
		.single()
		.execute()
	)

	if not crop_response.data:
		raise ValueError(f"Crop {crop_id} not found")

	crop = crop_response.data

	# Check if harvested
	if not crop["harvested_at"]:
		raise ValueError("Crop must be harvested before selling")

	if crop["yield_amount"] is None:
		raise ValueError("Crop has no yield amount")

	# Get crop price
	crop_type_id = crop["crop_types"]["id"]
	crop_price = get_crop_price(crop_type_id)

	# Calculate total revenue
	total_revenue = crop["yield_amount"] * crop_price

	# Add money to player
	player = price_repository.update_player_money(player_id, total_revenue)

	return {
		"crop_id": crop_id,
		"crop_type_id": crop_type_id,
		"yield_amount": crop["yield_amount"],
		"crop_price": crop_price,
		"total_revenue": total_revenue,
		"new_balance": player["money"]
	}


def get_all_prices():
	"""Get all crop prices."""
	return price_repository.get_all_prices()


def get_player_balance(player_id: int):
	"""Get player's current money balance."""
	return price_repository.get_player_money(player_id)


def sell_crops_batch(player_id: int, crop_type_id: int, quantity: int):
	"""Sell multiple harvested crops of the same type (by quantity of harvested crops, not yield)."""

	from backend.supabase_client import get_supabase_client

	supabase = get_supabase_client()

	# Get all crops
	crops_response = supabase.table("crops").select("*").execute()

	# Filter: crops that belong to this player's plots and are harvested
	from backend.repositories.plot_repository import get_plots_by_player
	player_plots = get_plots_by_player(player_id)
	plot_ids = [p["id"] for p in player_plots] if player_plots else []

	harvested_crops = [
		c for c in crops_response.data
		if c.get("plot_id") in plot_ids
		and c.get("crop_type_id") == crop_type_id
		and c.get("harvested_at") is not None
	]

	if len(harvested_crops) < quantity:
		raise ValueError(f"Solo {len(harvested_crops)} cultivos disponibles, solicitaste {quantity}")

	# Get crop price
	crop_price = get_crop_price(crop_type_id)

	# Sell first N crops
	total_revenue = 0
	sold_count = 0

	for crop in harvested_crops[:quantity]:
		yield_amount = crop.get("yield_amount", 0)
		revenue = yield_amount * crop_price
		total_revenue += revenue
		sold_count += 1

		# Delete the crop
		supabase.table("crops").delete().eq("id", crop["id"]).execute()

	# Add money to player
	player = price_repository.update_player_money(player_id, total_revenue)

	return {
		"sold_count": sold_count,
		"crop_type_id": crop_type_id,
		"crop_price": crop_price,
		"total_revenue": total_revenue,
		"new_balance": player["money"]
	}
