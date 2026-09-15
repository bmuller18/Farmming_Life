from backend.repositories import crop_repository, crop_type_repository


def get_all_crop_types():
	"""Get all available crop types to plant."""
	return crop_type_repository.get_all_crop_types()


def get_crops_in_plot(plot_id: int):
	"""Get all crops (past and current) in a plot."""
	return crop_repository.get_crops_by_plot(plot_id)


def get_active_crop(plot_id: int):
	"""Get the currently growing crop in a plot."""
	return crop_repository.get_active_crop_by_plot(plot_id)


def plant_crop_in_plot(plot_id: int, crop_type_id: int):
	"""Plant a new crop in a plot."""

	# Check if plot has an active crop
	active_crop = crop_repository.get_active_crop_by_plot(plot_id)

	if active_crop:
		raise ValueError("Plot already has an active crop. Harvest it first.")

	# Plant the crop
	crop = crop_repository.plant_crop(plot_id, crop_type_id)

	return crop


def harvest_crop_from_plot(crop_id: int):
	"""Harvest a crop if it's ready."""

	# Get crop to verify it hasn't been harvested already
	from backend.supabase_client import get_supabase_client
	supabase = get_supabase_client()

	response = (
		supabase
		.table("crops")
		.select("harvested_at")
		.eq("id", crop_id)
		.single()
		.execute()
	)

	if not response.data:
		raise ValueError(f"Crop {crop_id} not found")

	crop_data = response.data
	if crop_data["harvested_at"]:
		raise ValueError("Crop has already been harvested")

	# Harvest it (frontend already verified readiness with ready_at)
	crop = crop_repository.harvest_crop(crop_id)

	return crop


def get_crop_status(crop_id: int):
	"""Get the status of a crop (growing, ready, harvested)."""

	crop = crop_repository.get_crops_by_plot(None)  # This won't work, fix below

	# Better approach - get crop directly
	from backend.supabase_client import get_supabase_client
	from datetime import datetime

	supabase = get_supabase_client()

	response = (
		supabase
		.table("crops")
		.select("*, crop_types(*)")
		.eq("id", crop_id)
		.single()
		.execute()
	)

	if not response.data:
		return None

	crop = response.data

	if crop["harvested_at"]:
		return {
			"status": "harvested",
			"yield": crop["yield_amount"],
			"harvested_at": crop["harvested_at"],
		}

	ready_at = datetime.fromisoformat(crop["ready_at"].replace("Z", "+00:00"))

	if datetime.utcnow() >= ready_at:
		return {
			"status": "ready",
			"crop_type": crop["crop_types"]["name"],
			"ready_at": crop["ready_at"],
		}

	return {
		"status": "growing",
		"crop_type": crop["crop_types"]["name"],
		"planted_at": crop["planted_at"],
		"ready_at": crop["ready_at"],
	}
