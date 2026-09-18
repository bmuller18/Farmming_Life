from backend.supabase_client import get_supabase_client
from datetime import datetime, timezone


def add_inventory_item(player_id: int, item_id: int, quantity: int = 1, acquired_from: str = "npc"):
    """Agregar item al inventario del jugador."""
    supabase = get_supabase_client()

    # Verificar si el jugador ya tiene este item
    response = (
        supabase
        .table("inventory_items")
        .select("id, quantity")
        .eq("player_id", player_id)
        .eq("npc_shop_item_id", item_id)
        .limit(1)
        .execute()
    )

    if response.data:
        # Actualizar cantidad existente
        existing_id = response.data[0]["id"]
        new_quantity = response.data[0]["quantity"] + quantity

        update_response = (
            supabase
            .table("inventory_items")
            .update({"quantity": new_quantity})
            .eq("id", existing_id)
            .execute()
        )
        return update_response.data
    else:
        # Crear nuevo registro
        insert_data = {
            "player_id": player_id,
            "npc_shop_item_id": item_id,
            "quantity": quantity,
            "acquired_from": acquired_from,
            "acquired_at": datetime.now(timezone.utc).isoformat()
        }

        insert_response = (
            supabase
            .table("inventory_items")
            .insert(insert_data)
            .execute()
        )
        return insert_response.data


def get_player_inventory_items(player_id: int):
    """Obtener todos los items del inventario del jugador."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("inventory_items")
        .select("*, npc_shop_items(*)")
        .eq("player_id", player_id)
        .gt("quantity", 0)
        .order("acquired_at", desc=True)
        .execute()
    )

    return response.data


def get_inventory_item(player_id: int, item_id: int):
    """Obtener un item específico del inventario."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("inventory_items")
        .select("*, npc_shop_items(*)")
        .eq("player_id", player_id)
        .eq("npc_shop_item_id", item_id)
        .single()
        .execute()
    )

    return response.data if response.data else None


def remove_inventory_item(player_id: int, item_id: int, quantity: int = 1):
    """Remover items del inventario."""
    supabase = get_supabase_client()

    # Obtener cantidad actual
    item = get_inventory_item(player_id, item_id)
    if not item:
        raise ValueError("Item not in inventory")

    new_quantity = item["quantity"] - quantity

    if new_quantity <= 0:
        # Eliminar el registro
        delete_response = (
            supabase
            .table("inventory_items")
            .delete()
            .eq("player_id", player_id)
            .eq("npc_shop_item_id", item_id)
            .execute()
        )
        return {"deleted": True}
    else:
        # Actualizar cantidad
        update_response = (
            supabase
            .table("inventory_items")
            .update({"quantity": new_quantity})
            .eq("player_id", player_id)
            .eq("npc_shop_item_id", item_id)
            .execute()
        )
        return update_response.data
