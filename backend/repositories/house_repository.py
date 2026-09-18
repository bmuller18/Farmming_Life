from backend.supabase_client import get_supabase_client


def buy_house(player_id: int, house_id: int, jwt_token: str = None):
    """Purchase a house using RPC function."""
    from backend.logging_config import api_logger

    api_logger.info(f"[BUY_HOUSE_RPC] Iniciando compra: player={player_id}, house={house_id}")

    supabase = get_supabase_client()

    try:
        rpc_response = (
            supabase
            .rpc("purchase_house", {
                "p_player_id": player_id,
                "p_house_id": house_id
            })
            .execute()
        )

        api_logger.info(f"[BUY_HOUSE_RPC] Respuesta: {rpc_response.data}")

        if not rpc_response.data:
            raise ValueError("RPC returned no data")

        result = rpc_response.data

        if isinstance(result, dict) and "error" in result:
            raise ValueError(result["error"])

        return result

    except Exception as e:
        api_logger.error(f"[BUY_HOUSE_RPC] Error: {str(e)}", exc_info=True)
        raise


def get_houses_by_player(player_id: int):
    """Get all houses owned by a player."""
    from backend.logging_config import api_logger

    supabase = get_supabase_client()

    try:
        api_logger.info(f"[GET_HOUSES_REPO] Buscando casas para player {player_id}")
        response = (
            supabase
            .table("houses")
            .select("*")
            .eq("player_id", player_id)
            .order("id")
            .execute()
        )
        api_logger.info(f"[GET_HOUSES_REPO] Respuesta: {response.data}")
        return response.data
    except Exception as e:
        api_logger.error(f"[GET_HOUSES_REPO] Error: {str(e)}", exc_info=True)
        raise


def get_available_houses_for_purchase(player_id: int):
    """Get houses available for purchase (not owned by this player)."""

    supabase = get_supabase_client()

    # Obtener todas las casas y filtrar en Python
    # neq() en Supabase no incluye valores null, así que obtenemos todas y filtramos
    response = (
        supabase
        .table("houses")
        .select("*")
        .order("price")
        .execute()
    )

    # Filtrar: casas sin dueño (player_id = null) O dueño diferente
    available_houses = [
        house for house in response.data
        if house["player_id"] is None or house["player_id"] != player_id
    ]

    return available_houses


def purchase_house(player_id: int, house_id: int):
    """Purchase a house using the RPC function."""
    return buy_house(player_id, house_id)