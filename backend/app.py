"""
Farm RPG - REST API Backend
"""
import sys
import os

# Agregar la raíz del proyecto al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from pydantic import ValidationError

from backend.middleware import require_auth, require_player_match
from backend.middleware.rate_limit import create_limiter, setup_rate_limit_error_handler
from backend.middleware.request_logging import init_request_logging
from backend.schemas import (
    RegisterRequest, LoginRequest, BuyHouseRequest, PlantCropRequest,
    BuySeedsRequest, SellCropsRequest, SellSingleCropRequest
)
from backend.logging_config import api_logger
from backend.services.player_service import get_player, get_player_by_name
from backend.services.house_service import get_houses_by_player
from backend.services.plot_service import get_plots_by_house
from backend.services.crop_service import (
    get_all_crop_types,
    get_active_crop,
    plant_crop_in_plot,
    harvest_crop_from_plot,
    get_harvested_crops,
)
from backend.services.economy_service import (
    get_seed_price,
    get_crop_price,
    buy_seeds,
    sell_crops,
    sell_crops_batch,
    get_all_prices,
    get_player_balance,
)

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8000", "http://localhost:5000", "http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

# Configurar Rate Limiting
limiter = create_limiter(app)
setup_rate_limit_error_handler(app)

# Configurar Request Logging
init_request_logging(app)

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.route("/api/auth/register", methods=["POST"])
@limiter.limit("3 per minute")
def register():
    """Register a new player."""
    try:
        from backend.services.auth_service import register_player
        data = request.get_json()

        # Validar con Pydantic
        try:
            validated = RegisterRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        result = register_player(validated.email, validated.name, validated.password)
        return jsonify(result), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Login a player."""
    try:
        from backend.services.auth_service import login_player
        data = request.get_json()

        # Validar con Pydantic
        try:
            validated = LoginRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        result = login_player(validated.email, validated.password)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PLAYER ENDPOINTS
# ============================================================================

@app.route("/api/player/<int:player_id>", methods=["GET"])
@require_player_match
def get_player_endpoint(player_id):
    """Get player information."""
    try:
        player = get_player(player_id)
        if not player:
            return jsonify({"error": "Player not found"}), 404
        return jsonify(player)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# HOUSE ENDPOINTS
# ============================================================================

@app.route("/api/player/<int:player_id>/houses", methods=["GET"])
@require_player_match
def get_player_houses(player_id):
    """Get all houses owned by a player."""
    try:
        api_logger.info(f"[GET_HOUSES] Obteniendo casas para player {player_id}")
        houses = get_houses_by_player(player_id)
        api_logger.info(f"[GET_HOUSES] Encontradas {len(houses)} casas")
        return jsonify(houses)
    except Exception as e:
        api_logger.error(f"[GET_HOUSES] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/houses/available/<int:player_id>", methods=["GET"])
@require_player_match
def get_available_houses(player_id):
    """Get houses available for purchase (not owned by player)."""
    try:
        from backend.services.house_service import get_available_houses_for_purchase
        houses = get_available_houses_for_purchase(player_id)
        return jsonify(houses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/buy-house", methods=["POST"])
@limiter.limit("10 per hour")
@require_player_match
def buy_house(player_id):
    """Purchase a house."""
    try:
        data = request.get_json()

        # Validar con Pydantic
        try:
            validated = BuyHouseRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        from backend.services.house_service import purchase_house
        result = purchase_house(player_id, validated.house_id)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/sell-house", methods=["POST"])
@limiter.limit("10 per hour")
@require_player_match
def sell_house(player_id):
    """Sell a house."""
    try:
        data = request.get_json()

        # Validar con Pydantic
        try:
            validated = BuyHouseRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        from backend.services.house_service import sell_house
        result = sell_house(player_id, validated.house_id)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PLOT ENDPOINTS
# ============================================================================

@app.route("/api/house/<int:house_id>/plots", methods=["GET"])
def get_house_plots(house_id):
    """Get all plots in a house."""
    try:
        plots = get_plots_by_house(house_id)
        return jsonify(plots)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/house/<int:house_id>/crops", methods=["GET"])
def get_house_crops(house_id):
    """Get all crops for all plots in a house (single optimized query)."""
    try:
        from backend.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        # Get all plots for this house first
        plots_response = (
            supabase
            .table("plots")
            .select("id")
            .eq("house_id", house_id)
            .execute()
        )

        if not plots_response.data:
            return jsonify({})

        plot_ids = [p['id'] for p in plots_response.data]

        # Single query to get all active crops for these plots
        crops_response = (
            supabase
            .table("crops")
            .select("*, crop_types(*)")
            .in_("plot_id", plot_ids)
            .is_("harvested_at", "null")
            .execute()
        )

        # Convert to dict by plot_id for fast lookup
        result = {}
        if crops_response.data:
            for crop in crops_response.data:
                result[crop['plot_id']] = crop

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CROP TYPE ENDPOINTS
# ============================================================================

@app.route("/api/crop-types", methods=["GET"])
def get_crop_types():
    """Get all available crop types."""
    try:
        crop_types = get_all_crop_types()
        return jsonify(crop_types)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# CROP ENDPOINTS
# ============================================================================

@app.route("/api/plot/<int:plot_id>/crop", methods=["GET"])
def get_plot_crop(plot_id):
    """Get active crop in a plot."""
    try:
        crop = get_active_crop(plot_id)
        if not crop:
            return jsonify({"crop": None})
        return jsonify({"crop": crop})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/plot/<int:plot_id>/plant", methods=["POST"])
@require_auth
def plant_crop(plot_id):
    """Plant a crop in a plot."""
    try:
        data = request.get_json()

        # Validar con Pydantic
        try:
            validated = PlantCropRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        crop = plant_crop_in_plot(plot_id, validated.crop_type_id)
        return jsonify(crop), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/crop/<int:crop_id>/harvest", methods=["POST"])
def harvest_crop(crop_id):
    """Harvest a crop."""
    try:
        crop = harvest_crop_from_plot(crop_id)
        return jsonify(crop)
    except ValueError as e:
        print(f"ValueError in harvest: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Exception in harvest: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/inventory", methods=["GET"])
@require_player_match
def get_inventory(player_id):
    """Get player's complete inventory (crops, seeds, items)."""
    try:
        from backend.supabase_client import get_supabase_client
        from backend.logging_config import api_logger

        api_logger.info(f"[GET_INVENTORY] Obteniendo inventario para player {player_id}")

        supabase = get_supabase_client()

        # Obtener cultivos cosechados
        harvested_crops = get_harvested_crops(player_id)
        api_logger.info(f"[GET_INVENTORY] Cultivos cosechados: {len(harvested_crops) if harvested_crops else 0}")

        # Obtener player
        player_response = (
            supabase
            .table("player")
            .select("*")
            .eq("id", player_id)
            .single()
            .execute()
        )
        player = player_response.data or {}

        # Agrupar cultivos por tipo
        crops_by_type = {}
        if harvested_crops:
            for crop in harvested_crops:
                crop_type_id = crop.get('crop_type_id')
                crop_type_name = crop.get('crop_types', {}).get('name', 'Unknown')
                # Usar total_yield que es lo que devuelve get_harvested_crops_by_player
                yield_amount = crop.get('total_yield', crop.get('yield_amount', 0))

                if crop_type_id not in crops_by_type:
                    crops_by_type[crop_type_id] = {
                        'crop_type_id': crop_type_id,
                        'name': crop_type_name,
                        'quantity': 0,
                        'price': 0
                    }
                crops_by_type[crop_type_id]['quantity'] += yield_amount

        # Obtener precios (puede ser None)
        try:
            prices_response = get_all_prices()
            prices_map = {}
            if prices_response:
                for p in prices_response:
                    prices_map[p.get('crop_type_id')] = p.get('crop_price', 0)
        except:
            prices_map = {}

        # Agregar precios a los cultivos y filtrar los que tienen cantidad > 0
        crops_with_quantity = []
        for crop_type_id in crops_by_type:
            crop = crops_by_type[crop_type_id]
            crop['price'] = prices_map.get(crop_type_id, 0)
            # Solo incluir cultivos con cantidad > 0
            if crop['quantity'] > 0:
                crops_with_quantity.append(crop)

        # Obtener items del inventario
        from backend.repositories import inventory_repository
        inventory_items = inventory_repository.get_player_inventory_items(player_id)

        items_formatted = []
        if inventory_items:
            for item in inventory_items:
                item_data = item.get('npc_shop_items', {})
                items_formatted.append({
                    'id': item.get('id'),
                    'item_id': item.get('npc_shop_item_id'),
                    'name': item_data.get('name', 'Unknown'),
                    'category': item_data.get('category', ''),
                    'quantity': item.get('quantity', 0),
                    'price': item_data.get('price', 0),
                    'acquired_from': item.get('acquired_from')
                })

        result = {
            'player': {
                'id': player.get('id'),
                'name': player.get('name'),
                'money': player.get('money'),
                'level': player.get('level')
            },
            'crops': crops_with_quantity,
            'items': items_formatted,
            'total_value': sum(
                c['quantity'] * c['price'] for c in crops_by_type.values()
            )
        }

        api_logger.info(f"[GET_INVENTORY] Retornando {len(result['crops'])} tipos de cultivos y {len(items_formatted)} items")
        return jsonify(result)

    except Exception as e:
        api_logger.error(f"[GET_INVENTORY] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/crops/sell-batch", methods=["POST"])
@limiter.limit("30 per hour")
@require_auth
def sell_batch():
    """Sell multiple crops of the same type at once."""
    try:
        data = request.get_json()

        # Validar con Pydantic
        try:
            validated = SellCropsRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        # Validar que player_id coincida con el token
        if validated.player_id != request.player_id:
            return jsonify({"error": "Unauthorized: Cannot sell for other player"}), 403

        result = sell_crops_batch(validated.player_id, validated.crop_type_id, validated.quantity)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PLOTS ENDPOINTS
# ============================================================================

@app.route("/api/player/<int:player_id>/create-missing-plots", methods=["POST"])
@require_player_match
def create_missing_plots(player_id):
    """Create missing plots for all houses owned by player."""
    try:
        from backend.services.house_service import get_houses_by_player
        from backend.repositories import plot_repository
        from backend.logging_config import api_logger

        api_logger.info(f"[CREATE_MISSING_PLOTS] Creating plots for player {player_id}")

        houses = get_houses_by_player(player_id)
        created_count = 0

        for house in houses:
            # Obtener plots existentes
            existing_plots = get_plots_by_house(house["id"])
            # Usar plot_count de la casa, o default a 4
            house_plot_count = house.get("plot_count", 4)

            api_logger.info(f"[CREATE_MISSING_PLOTS] House {house['id']}: {len(existing_plots)} existing, need {house_plot_count}")

            # Si faltan plots, crearlos
            if len(existing_plots) < house_plot_count:
                plots_to_create = house_plot_count - len(existing_plots)
                for i in range(plots_to_create):
                    plot_number = len(existing_plots) + i + 1
                    try:
                        plot_repository.create_plot(house["id"], f"Plot {plot_number}")
                        api_logger.info(f"[CREATE_MISSING_PLOTS] Created Plot {plot_number} for house {house['id']}")
                        created_count += 1
                    except Exception as plot_error:
                        api_logger.error(f"[CREATE_MISSING_PLOTS] Error creating plot: {str(plot_error)}")

        api_logger.info(f"[CREATE_MISSING_PLOTS] Total created: {created_count}")

        return jsonify({
            "message": f"Created {created_count} missing plots",
            "created": created_count
        }), 200

    except Exception as e:
        api_logger.error(f"[CREATE_MISSING_PLOTS] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})


# ============================================================================
# ECONOMY ENDPOINTS
# ============================================================================

@app.route("/api/prices", methods=["GET"])
def get_prices():
    """Get all crop prices."""
    try:
        prices = get_all_prices()
        return jsonify(prices)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/crop-type/<int:crop_type_id>/price", methods=["GET"])
def get_crop_type_price(crop_type_id):
    """Get price for a specific crop type."""
    try:
        seed_price = get_seed_price(crop_type_id)
        crop_price = get_crop_price(crop_type_id)
        return jsonify({
            "crop_type_id": crop_type_id,
            "seed_price": seed_price,
            "crop_price": crop_price
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/balance", methods=["GET"])
@require_player_match
def get_balance(player_id):
    """Get player's current money balance."""
    try:
        balance = get_player_balance(player_id)
        return jsonify({"player_id": player_id, "balance": balance})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/buy-seeds", methods=["POST"])
@limiter.limit("30 per hour")
@require_player_match
def buy_seeds_endpoint(player_id):
    """Buy seeds for planting."""
    try:
        data = request.get_json()

        # Validar con Pydantic
        try:
            validated = BuySeedsRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        result = buy_seeds(player_id, validated.crop_type_id, validated.quantity)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/crop/<int:crop_id>/sell", methods=["POST"])
@limiter.limit("30 per hour")
@require_auth
def sell_crop_endpoint(crop_id):
    """Sell a harvested crop."""
    try:
        data = request.get_json()

        # Validar con Pydantic
        try:
            validated = SellSingleCropRequest(**data)
        except ValidationError as e:
            return jsonify({"error": "Validation error", "details": e.errors()}), 400

        # Validar que player_id coincida con el token
        if validated.player_id != request.player_id:
            return jsonify({"error": "Unauthorized: Cannot sell for other player"}), 403

        result = sell_crops(crop_id, validated.player_id)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# MARKET ENDPOINTS
# ============================================================================

@app.route("/api/market/npc-shop/items", methods=["GET"])
def get_npc_shop_items():
    """Get all items available in NPC shop."""
    try:
        from backend.repositories import market_repository
        items = market_repository.get_npc_shop_items()
        return jsonify(items), 200
    except Exception as e:
        api_logger.error(f"[GET_NPC_ITEMS] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/npc-shop/buy", methods=["POST"])
@limiter.limit("30 per hour")
@require_auth
def buy_from_npc():
    """Buy an item from NPC shop."""
    try:
        from backend.services.market_service import buy_from_npc
        data = request.get_json()

        item_id = data.get("item_id")
        quantity = data.get("quantity", 1)
        player_id = request.player_id

        if not item_id:
            return jsonify({"error": "item_id required"}), 400

        result = buy_from_npc(player_id, item_id, quantity)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        api_logger.error(f"[BUY_NPC] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/player/listings", methods=["GET"])
def get_market_listings():
    """Get active player market listings."""
    try:
        from backend.repositories import market_repository
        crop_type_id = request.args.get("crop_type_id", type=int)
        listings = market_repository.get_market_listings(crop_type_id)
        return jsonify(listings), 200
    except Exception as e:
        api_logger.error(f"[GET_LISTINGS] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/player/create-offer", methods=["POST"])
@limiter.limit("30 per hour")
@require_auth
def create_market_offer():
    """Create a player market listing (sell offer)."""
    try:
        from backend.services.market_service import create_market_offer
        data = request.get_json()

        crop_type_id = data.get("crop_type_id")
        quantity = data.get("quantity")
        price_per_unit = data.get("price_per_unit")
        player_id = request.player_id

        if not all([crop_type_id, quantity, price_per_unit]):
            return jsonify({"error": "crop_type_id, quantity, price_per_unit required"}), 400

        result = create_market_offer(player_id, crop_type_id, quantity, price_per_unit)
        return jsonify(result), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        api_logger.error(f"[CREATE_OFFER] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/player/my-offers", methods=["GET"])
@require_auth
def get_player_offers():
    """Get current player's active market listings."""
    try:
        from backend.repositories import market_repository
        player_id = request.player_id
        listings = market_repository.get_player_listings(player_id)
        return jsonify(listings), 200
    except Exception as e:
        api_logger.error(f"[GET_MY_OFFERS] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/player/accept-offer/<int:listing_id>", methods=["POST"])
@limiter.limit("30 per hour")
@require_auth
def accept_market_offer(listing_id):
    """Accept a player market listing (buy)."""
    try:
        from backend.services.market_service import accept_market_offer
        buyer_id = request.player_id

        result = accept_market_offer(buyer_id, listing_id)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        api_logger.error(f"[ACCEPT_OFFER] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/player/cancel-offer/<int:listing_id>", methods=["POST"])
@require_auth
def cancel_market_offer(listing_id):
    """Cancel a player's market listing."""
    try:
        from backend.repositories import market_repository
        player_id = request.player_id

        # Validar que el listing pertenezca al jugador
        listing = market_repository.get_listing_by_id(listing_id)
        if not listing or listing["seller_id"] != player_id:
            return jsonify({"error": "Unauthorized"}), 403

        market_repository.cancel_listing(listing_id)
        return jsonify({"message": "Listing cancelled"}), 200

    except Exception as e:
        api_logger.error(f"[CANCEL_OFFER] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/price-history/<int:crop_type_id>", methods=["GET"])
def get_price_history(crop_type_id):
    """Get price history for a crop type."""
    try:
        from backend.repositories import market_repository
        days = request.args.get("days", default=30, type=int)
        history = market_repository.get_price_history(crop_type_id, days)
        return jsonify(history), 200
    except Exception as e:
        api_logger.error(f"[GET_PRICE_HISTORY] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/market/global-prices", methods=["GET"])
def get_global_prices():
    """Get current global market prices."""
    try:
        from backend.repositories import market_repository
        prices = market_repository.get_global_prices()
        return jsonify(prices), 200
    except Exception as e:
        api_logger.error(f"[GET_GLOBAL_PRICES] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/inventory/items", methods=["GET"])
@require_player_match
def get_inventory_items(player_id):
    """Get player's inventory items."""
    try:
        from backend.repositories import inventory_repository
        items = inventory_repository.get_player_inventory_items(player_id)

        items_formatted = []
        if items:
            for item in items:
                item_data = item.get('npc_shop_items', {})
                items_formatted.append({
                    'id': item.get('id'),
                    'item_id': item.get('npc_shop_item_id'),
                    'name': item_data.get('name', 'Unknown'),
                    'category': item_data.get('category', ''),
                    'quantity': item.get('quantity', 0),
                    'price': item_data.get('price', 0),
                    'acquired_from': item.get('acquired_from')
                })

        return jsonify(items_formatted), 200
    except Exception as e:
        api_logger.error(f"[GET_INVENTORY_ITEMS] Error: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
