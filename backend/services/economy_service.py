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
	"""Sell harvested crops by yield amount (not by individual crops)."""

	from backend.supabase_client import get_supabase_client

	supabase = get_supabase_client()

	# Asegurar que los parámetros son int
	crop_type_id = int(crop_type_id)
	quantity = int(quantity)

	# Get all crops
	crops_response = supabase.table("crops").select("*").execute()

	# Filter: crops that belong to this player's plots and are harvested
	from backend.repositories.plot_repository import get_plots_by_player
	player_plots = get_plots_by_player(player_id)
	plot_ids = [p["id"] for p in player_plots] if player_plots else []

	# Filter harvested crops of this type
	harvested_crops = []
	for c in crops_response.data:
		plot_id = c.get("plot_id")
		type_id = c.get("crop_type_id")
		harvested = c.get("harvested_at")

		if plot_id and plot_id in plot_ids and int(type_id) == crop_type_id and harvested:
			harvested_crops.append(c)

	# Calculate total available yield
	total_available_yield = sum(c.get("yield_amount", 0) for c in harvested_crops)

	if total_available_yield < quantity:
		raise ValueError(f"Solo {total_available_yield} unidades disponibles, solicitaste {quantity}")

	# Get crop price
	crop_price = get_crop_price(crop_type_id)

	# Sell crops by yield amount
	total_revenue = quantity * crop_price
	remaining_to_sell = quantity
	crops_to_delete = []

	for crop in harvested_crops:
		if remaining_to_sell <= 0:
			break

		yield_amount = crop.get("yield_amount", 0)

		if yield_amount <= remaining_to_sell:
			# Vender completamente este cultivo
			remaining_to_sell -= yield_amount
			crops_to_delete.append(crop["id"])
		else:
			# Vender solo parte y actualizar el cultivo
			new_yield = yield_amount - remaining_to_sell
			supabase.table("crops").update({"yield_amount": new_yield}).eq("id", crop["id"]).execute()
			remaining_to_sell = 0
			break

	# Eliminar cultivos vendidos completamente
	for crop_id in crops_to_delete:
		supabase.table("crops").delete().eq("id", crop_id).execute()

	# Add money to player
	player = price_repository.update_player_money(player_id, total_revenue)

	return {
		"sold_yield": quantity,
		"crop_type_id": crop_type_id,
		"crop_price": crop_price,
		"total_revenue": total_revenue,
		"new_balance": player["money"]
	}
