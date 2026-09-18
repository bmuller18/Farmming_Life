from backend.supabase_client import get_supabase_client
from datetime import datetime, timezone


def get_npc_shop_items():
    """Obtener todos los items disponibles en la tienda NPC."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("npc_shop_items")
        .select("*")
        .order("category")
        .execute()
    )

    return response.data


def get_npc_item(item_id: int):
    """Obtener un item específico de la tienda NPC."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("npc_shop_items")
        .select("*")
        .eq("id", item_id)
        .single()
        .execute()
    )

    return response.data


def create_market_listing(seller_id: int, crop_type_id: int, quantity: int, price_per_unit: float):
    """Crear una nueva oferta en el mercado de jugadores."""
    supabase = get_supabase_client()

    total_price = quantity * price_per_unit
    commission = int(total_price * 0.05)  # 5% comisión

    listing_data = {
        "seller_id": seller_id,
        "crop_type_id": crop_type_id,
        "quantity": quantity,
        "price_per_unit": price_per_unit,
        "total_price": total_price,
        "commission": commission,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": None
    }

    response = (
        supabase
        .table("market_listings")
        .insert(listing_data)
        .execute()
    )

    return response.data


def get_market_listings(crop_type_id: int = None, limit: int = 50):
    """Obtener ofertas activas del mercado."""
    supabase = get_supabase_client()

    query = (
        supabase
        .table("market_listings")
        .select("*, crop_types(*), player!market_listings_seller_id_fkey(name)")
        .eq("status", "active")
        .order("created_at", desc=True)
        .limit(limit)
    )

    if crop_type_id:
        query = query.eq("crop_type_id", crop_type_id)

    response = query.execute()

    return response.data


def get_listing_by_id(listing_id: int):
    """Obtener una oferta específica."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("market_listings")
        .select("*, crop_types(*), player!market_listings_seller_id_fkey(name)")
        .eq("id", listing_id)
        .single()
        .execute()
    )

    return response.data


def get_player_listings(player_id: int):
    """Obtener mis ofertas en el mercado."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("market_listings")
        .select("*, crop_types(*)")
        .eq("seller_id", player_id)
        .eq("status", "active")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data


def accept_listing(listing_id: int, buyer_id: int):
    """Aceptar una oferta (comprar cultivo)."""
    supabase = get_supabase_client()

    # Actualizar estado de la oferta
    update_response = (
        supabase
        .table("market_listings")
        .update({
            "status": "sold",
            "buyer_id": buyer_id,
            "sold_at": datetime.now(timezone.utc).isoformat()
        })
        .eq("id", listing_id)
        .execute()
    )

    return update_response.data


def cancel_listing(listing_id: int):
    """Cancelar una oferta."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("market_listings")
        .update({"status": "cancelled"})
        .eq("id", listing_id)
        .execute()
    )

    return response.data


def add_market_history(seller_id: int, buyer_id: int, crop_type_id: int,
                       quantity: int, price_per_unit: float, commission: int):
    """Agregar transacción al historial."""
    supabase = get_supabase_client()

    history_data = {
        "seller_id": seller_id,
        "buyer_id": buyer_id,
        "crop_type_id": crop_type_id,
        "quantity": quantity,
        "price_per_unit": price_per_unit,
        "total_price": quantity * price_per_unit,
        "commission": commission,
        "transaction_date": datetime.now(timezone.utc).isoformat()
    }

    response = (
        supabase
        .table("market_history")
        .insert(history_data)
        .execute()
    )

    return response.data


def get_price_history(crop_type_id: int, days: int = 30):
    """Obtener histórico de precios."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("market_history")
        .select("price_per_unit, transaction_date")
        .eq("crop_type_id", crop_type_id)
        .order("transaction_date", desc=True)
        .limit(days * 10)  # Aproximado: 10 transacciones por día
        .execute()
    )

    return response.data


def get_global_prices():
    """Obtener precios actuales del mercado global."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("market_prices")
        .select("*")
        .order("crop_type_id")
        .execute()
    )

    return response.data


def update_global_price(crop_type_id: int, current_price: float, trend: str):
    """Actualizar precio del mercado global."""
    supabase = get_supabase_client()

    response = (
        supabase
        .table("market_prices")
        .update({
            "current_price": current_price,
            "trend": trend,
            "updated_at": datetime.now(timezone.utc).isoformat()
        })
        .eq("crop_type_id", crop_type_id)
        .execute()
    )

    return response.data
