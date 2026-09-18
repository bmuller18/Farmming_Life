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
    """Purchase a house using the RPC function and create plots."""
    result = buy_house(player_id, house_id)

    # Crear plots para la casa comprada
    from backend.repositories import plot_repository
    try:
        plot_repository.create_starting_plots(house_id)
    except Exception as e:
        from backend.logging_config import api_logger
        api_logger.warning(f"[PURCHASE_HOUSE] Could not create plots: {str(e)}")

    return result


def sell_house(player_id: int, house_id: int):
    """Sell a house back to the system."""
    from backend.logging_config import api_logger

    api_logger.info(f"[SELL_HOUSE] Vendiendo casa {house_id} de player {player_id}")

    supabase = get_supabase_client()

    try:
        # Obtener datos de la casa
        house_response = (
            supabase
            .table("houses")
            .select("id, price, name, player_id")
            .eq("id", house_id)
            .single()
            .execute()
        )

        if not house_response.data:
            raise ValueError(f"House {house_id} not found")

        house = house_response.data

        if house["player_id"] != player_id:
            raise ValueError("You don't own this house")

        # Verificar si hay cultivos plantados en los plots de esta casa
        plots_response = (
            supabase
            .table("plots")
            .select("id")
            .eq("house_id", house_id)
            .execute()
        )

        if plots_response.data:
            plot_ids = [p["id"] for p in plots_response.data]

            # Buscar cultivos activos (no cosechados)
            crops_response = (
                supabase
                .table("crops")
                .select("id")
                .in_("plot_id", plot_ids)
                .is_("harvested_at", "null")
                .limit(1)
                .execute()
            )

            if crops_response.data:
                raise ValueError("Cannot sell house with active crops. Harvest all crops first.")

        house_price = house["price"]
        house_name = house["name"]

        # Devolver 80% del precio original
        refund_amount = int(house_price * 0.8)

        api_logger.info(f"[SELL_HOUSE] Precio: ${house_price}, Reembolso: ${refund_amount}")

        # Actualizar dinero del jugador
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

        player_money = player_response.data["money"]
        new_balance = player_money + refund_amount

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()

        # Actualizar casa (quitar dueño)
        house_update = supabase.table("houses").update({
            "player_id": None,
            "updated_at": now
        }).eq("id", house_id).execute()

        api_logger.info(f"[SELL_HOUSE] House update: {house_update.data}")

        # Actualizar dinero del jugador
        player_update = supabase.table("player").update({
            "money": new_balance,
            "updated_at": now
        }).eq("id", player_id).execute()

        api_logger.info(f"[SELL_HOUSE] Player update: {player_update.data}")

        api_logger.info(f"[SELL_HOUSE] Casa vendida exitosamente")

        return {
            "house_id": house_id,
            "house_name": house_name,
            "refund_amount": refund_amount,
            "new_balance": new_balance
        }

    except Exception as e:
        api_logger.error(f"[SELL_HOUSE] Error: {str(e)}", exc_info=True)
        raise