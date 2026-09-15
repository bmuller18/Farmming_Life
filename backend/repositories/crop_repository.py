from backend.supabase_client import get_supabase_client
from datetime import datetime, timedelta, timezone


def get_crops_by_plot(plot_id: int):
	"""Get all crops for a specific plot."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("crops")
		.select("*, crop_types(*)")
		.eq("plot_id", plot_id)
		.order("planted_at", desc=True)
		.execute()
	)

	return response.data


def get_active_crop_by_plot(plot_id: int):
	"""Get the currently active crop in a plot (not harvested)."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("crops")
		.select("*, crop_types(*)")
		.eq("plot_id", plot_id)
		.is_("harvested_at", "null")
		.order("planted_at", desc=True)
		.limit(1)
		.execute()
	)

	return response.data[0] if response.data else None


def plant_crop(plot_id: int, crop_type_id: int):
	"""Plant a new crop in a plot."""

	supabase = get_supabase_client()

	# Get crop type to know growth time
	crop_type_response = (
		supabase
		.table("crop_types")
		.select("growth_time")
		.eq("id", crop_type_id)
		.single()
		.execute()
	)

	if not crop_type_response.data:
		raise ValueError(f"Crop type {crop_type_id} not found")

	growth_time_seconds = crop_type_response.data["growth_time"]
	ready_at = datetime.utcnow() + timedelta(seconds=growth_time_seconds)

	crop_data = {
		"plot_id": plot_id,
		"crop_type_id": crop_type_id,
		"planted_at": datetime.utcnow().isoformat(),
		"ready_at": ready_at.isoformat(),
	}

	response = (
		supabase
		.table("crops")
		.insert(crop_data)
		.execute()
	)

	if response.data:
		return response.data[0]

	raise RuntimeError("Failed to plant crop")


def harvest_crop(crop_id: int):
	"""Harvest a crop."""

	supabase = get_supabase_client()

	# Get crop with crop type info
	crop_response = (
		supabase
		.table("crops")
		.select("*, crop_types(base_yield)")
		.eq("id", crop_id)
		.single()
		.execute()
	)

	if not crop_response.data:
		raise ValueError(f"Crop {crop_id} not found")

	crop = crop_response.data

	# Calculate yield (base yield from crop type)
	base_yield = crop["crop_types"]["base_yield"]

	# Update crop with harvest info
	update_data = {
		"harvested_at": datetime.utcnow().isoformat(),
		"yield_amount": base_yield,
		"updated_at": datetime.utcnow().isoformat(),
	}

	response = (
		supabase
		.table("crops")
		.update(update_data)
		.eq("id", crop_id)
		.execute()
	)

	if response.data:
		return response.data[0]

	raise RuntimeError("Failed to harvest crop")


def get_harvested_crops_by_player(player_id: int):
	"""Get all harvested crops (inventory) for a player."""

	supabase = get_supabase_client()

	try:
		# Get all houses for the player
		houses_response = (
			supabase
			.table("houses")
			.select("id")
			.eq("player_id", player_id)
			.execute()
		)

		if not houses_response.data:
			return []

		house_ids = [house["id"] for house in houses_response.data]

		# Get all plots for those houses
		plots_response = (
			supabase
			.table("plots")
			.select("id")
		)

		for house_id in house_ids:
			plots_response = plots_response.or_(f"house_id.eq.{house_id}")

		plots_response = plots_response.execute()

		if not plots_response.data:
			return []

		plot_ids = [plot["id"] for plot in plots_response.data]

		# Get harvested crops for those plots
		crops_response = (
			supabase
			.table("crops")
			.select("*, crop_types(*)")
		)

		for plot_id in plot_ids:
			crops_response = crops_response.or_(f"plot_id.eq.{plot_id}")

		crops_response = (
			crops_response
			.not_("harvested_at", "is", None)
			.order("harvested_at", desc=True)
			.execute()
		)

		return crops_response.data
	except Exception as e:
		print(f"[INVENTORY ERROR] {str(e)}")
		import traceback
		traceback.print_exc()
		return []


def is_crop_ready(crop_id: int) -> bool:
	"""Check if a crop is ready to harvest."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("crops")
		.select("ready_at, harvested_at")
		.eq("id", crop_id)
		.single()
		.execute()
	)

	if not response.data:
		return False

	crop = response.data

	# If already harvested, it's not ready
	if crop["harvested_at"]:
		return False

	# Parse ready_at - handle both with and without timezone
	ready_at_str = crop["ready_at"]

	# Try parsing with timezone first, then strip it
	try:
		# Replace Z with +00:00 for fromisoformat compatibility
		normalized = ready_at_str.replace("Z", "+00:00")
		ready_at = datetime.fromisoformat(normalized)

		# If it has timezone info, convert to naive UTC
		if ready_at.tzinfo is not None:
			# Convert to UTC and remove timezone
			ready_at_utc = ready_at.astimezone(timezone.utc)
			ready_at = ready_at_utc.replace(tzinfo=None)
	except:
		# If parsing fails, assume it's naive UTC
		ready_at = datetime.fromisoformat(ready_at_str)

	# Use naive UTC now for comparison (with 5 second tolerance)
	now = datetime.utcnow()
	tolerance = timedelta(seconds=5)
	is_ready = now >= (ready_at - tolerance)

	print(f"[CROP {crop_id}] ready_at={ready_at}, now={now}, is_ready={is_ready}, diff={now - ready_at}")

	return is_ready
