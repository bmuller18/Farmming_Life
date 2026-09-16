"""
Transacciones atómicas usando Stored Procedures en Supabase
"""
from backend.supabase_client import get_supabase_client


def buy_house_atomic(player_id: int, house_id: int):
	"""
	Comprar casa de forma ATÓMICA usando stored procedure.
	Previene race conditions en dinero.
	"""
	supabase = get_supabase_client()

	result = supabase.rpc(
		"buy_house_atomic",
		{
			"p_player_id": player_id,
			"p_house_id": house_id
		}
	).execute()

	if not result.data:
		raise ValueError("Failed to execute buy_house_atomic")

	response = result.data

	# Si es un string, parsearlo como JSON (Supabase a veces retorna strings)
	if isinstance(response, str):
		import json
		response = json.loads(response)

	if isinstance(response, dict) and response.get("success"):
		return response
	elif isinstance(response, dict) and response.get("error"):
		raise ValueError(response["error"])
	else:
		raise ValueError("Invalid response from buy_house_atomic")


def sell_crops_batch_atomic(player_id: int, crop_type_id: int, quantity: int):
	"""
	Vender múltiples crops de forma ATÓMICA.
	Previene race conditions en dinero y yield.
	"""
	supabase = get_supabase_client()

	result = supabase.rpc(
		"sell_crops_batch_atomic",
		{
			"p_player_id": player_id,
			"p_crop_type_id": crop_type_id,
			"p_quantity": quantity
		}
	).execute()

	if not result.data:
		raise ValueError("Failed to execute sell_crops_batch_atomic")

	response = result.data

	if isinstance(response, str):
		import json
		response = json.loads(response)

	if isinstance(response, dict) and response.get("success"):
		return response
	elif isinstance(response, dict) and response.get("error"):
		raise ValueError(response["error"])
	else:
		raise ValueError("Invalid response from sell_crops_batch_atomic")


def buy_seeds_atomic(player_id: int, crop_type_id: int, quantity: int):
	"""
	Comprar semillas de forma ATÓMICA.
	Previene race conditions en dinero.
	"""
	supabase = get_supabase_client()

	result = supabase.rpc(
		"buy_seeds_atomic",
		{
			"p_player_id": player_id,
			"p_crop_type_id": crop_type_id,
			"p_quantity": quantity
		}
	).execute()

	if not result.data:
		raise ValueError("Failed to execute buy_seeds_atomic")

	response = result.data

	if isinstance(response, str):
		import json
		response = json.loads(response)

	if isinstance(response, dict) and response.get("success"):
		return response
	elif isinstance(response, dict) and response.get("error"):
		raise ValueError(response["error"])
	else:
		raise ValueError("Invalid response from buy_seeds_atomic")
