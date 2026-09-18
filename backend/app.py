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
CORS(app)

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
    """Get player's harvested crops (inventory)."""
    try:
        crops = get_harvested_crops(player_id)
        return jsonify(crops)
    except Exception as e:
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
