from backend.supabase_client import get_supabase_client


def get_all_crop_types():
	"""Get all available crop types."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("crop_types")
		.select("*")
		.order("name")
		.execute()
	)

	return response.data


def get_crop_type_by_id(crop_type_id: int):
	"""Get a crop type by ID."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("crop_types")
		.select("*")
		.eq("id", crop_type_id)
		.single()
		.execute()
	)

	return response.data if response.data else None


def get_crop_type_by_name(name: str):
	"""Get a crop type by name."""

	supabase = get_supabase_client()

	response = (
		supabase
		.table("crop_types")
		.select("*")
		.eq("name", name)
		.single()
		.execute()
	)

	return response.data if response.data else None
