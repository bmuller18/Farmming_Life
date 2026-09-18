from backend.repositories import market_repository
from backend.repositories import player_repository
from backend.repositories import crop_repository


def buy_from_npc(player_id: int, item_id: int, quantity: int = 1):
    """Comprar items de la tienda NPC."""
    # Obtener item de la tienda
    item = market_repository.get_npc_item(item_id)

    if not item:
        raise ValueError(f"Item {item_id} not found in NPC shop")

    if quantity < 1:
        raise ValueError("Quantity must be at least 1")

    item_price = item["price"]
    total_price = item_price * quantity

    # Obtener dinero del jugador
    player = player_repository.get_player(player_id)

    if player["money"] < total_price:
        raise ValueError(f"Insufficient money. Need {total_price}, have {player['money']}")

    # Restar dinero del jugador
    new_balance = player["money"] - total_price
    player_repository.update_player_money(player_id, new_balance)

    return {
        "item_id": item_id,
        "item_name": item["name"],
        "quantity": quantity,
        "price_per_unit": item_price,
        "total_price": total_price,
        "new_balance": new_balance
    }


def create_market_offer(player_id: int, crop_type_id: int, quantity: int, price_per_unit: float):
    """Crear una oferta para vender cultivos."""
    # Validar que el jugador tenga suficientes cultivos
    player_crops = crop_repository.get_harvested_crops_by_player(player_id)

    crop_quantity = 0
    for crop in player_crops:
        if crop["crop_type_id"] == crop_type_id:
            crop_quantity = crop.get("total_yield", crop.get("yield_amount", 0))
            break

    if crop_quantity < quantity:
        raise ValueError(f"Insufficient crop quantity. Available: {crop_quantity}, Requested: {quantity}")

    # Crear la oferta
    listing = market_repository.create_market_listing(player_id, crop_type_id, quantity, price_per_unit)

    return listing


def accept_market_offer(buyer_id: int, listing_id: int):
    """Aceptar una oferta del mercado."""
    # Obtener oferta
    listing = market_repository.get_listing_by_id(listing_id)

    if not listing or listing["status"] != "active":
        raise ValueError("Listing not available")

    seller_id = listing["seller_id"]

    # Validar que no sea el mismo jugador
    if seller_id == buyer_id:
        raise ValueError("Cannot buy from yourself")

    # Obtener datos de transacción
    total_price = listing["total_price"]
    commission = listing["commission"]
    seller_receives = total_price - commission

    # Validar dinero del comprador
    buyer = player_repository.get_player(buyer_id)

    if buyer["money"] < total_price:
        raise ValueError("Insufficient money")

    # Obtener dinero del vendedor
    seller = player_repository.get_player(seller_id)

    # Actualizar dineros
    buyer_new_balance = buyer["money"] - total_price
    seller_new_balance = seller["money"] + seller_receives

    player_repository.update_player_money(buyer_id, buyer_new_balance)
    player_repository.update_player_money(seller_id, seller_new_balance)

    # Actualizar oferta
    market_repository.accept_listing(listing_id, buyer_id)

    # Agregar al historial
    market_repository.add_market_history(
        seller_id=seller_id,
        buyer_id=buyer_id,
        crop_type_id=listing["crop_type_id"],
        quantity=listing["quantity"],
        price_per_unit=listing["price_per_unit"],
        commission=commission
    )

    return {
        "listing_id": listing_id,
        "buyer_id": buyer_id,
        "seller_id": seller_id,
        "quantity": listing["quantity"],
        "price_per_unit": listing["price_per_unit"],
        "total_price": total_price,
        "commission": commission,
        "seller_receives": seller_receives,
        "buyer_new_balance": buyer_new_balance,
        "seller_new_balance": seller_new_balance
    }
