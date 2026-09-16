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

# ============================================================================
# AUTH ENDPOINTS
# ============================================================================

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new player."""
    try:
        from backend.services.auth_service import register_player
        data = request.get_json()
        email = data.get("email")
        name = data.get("name")
        password = data.get("password")

        if not email or not name or not password:
            return jsonify({"error": "email, name, and password are required"}), 400

        result = register_player(email, name, password)
        return jsonify(result), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login a player."""
    try:
        from backend.services.auth_service import login_player
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "email and password are required"}), 400

        result = login_player(email, password)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# PLAYER ENDPOINTS
# ============================================================================

@app.route("/api/player/<int:player_id>", methods=["GET"])
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
def get_player_houses(player_id):
    """Get all houses owned by a player."""
    try:
        houses = get_houses_by_player(player_id)
        return jsonify(houses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/houses/available/<int:player_id>", methods=["GET"])
def get_available_houses(player_id):
    """Get houses available for purchase (not owned by player)."""
    try:
        from backend.services.house_service import get_available_houses_for_purchase
        houses = get_available_houses_for_purchase(player_id)
        return jsonify(houses)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/buy-house", methods=["POST"])
def buy_house(player_id):
    """Purchase a house."""
    try:
        data = request.get_json()
        house_id = data.get("house_id")

        if not house_id:
            return jsonify({"error": "house_id is required"}), 400

        from backend.services.house_service import purchase_house
        result = purchase_house(player_id, house_id)
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
def plant_crop(plot_id):
    """Plant a crop in a plot."""
    try:
        data = request.get_json()
        crop_type_id = data.get("crop_type_id")

        if not crop_type_id:
            return jsonify({"error": "crop_type_id is required"}), 400

        crop = plant_crop_in_plot(plot_id, crop_type_id)
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
def get_inventory(player_id):
    """Get player's harvested crops (inventory)."""
    try:
        crops = get_harvested_crops(player_id)
        return jsonify(crops)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/crops/sell-batch", methods=["POST"])
def sell_batch():
    """Sell multiple crops of the same type at once."""
    try:
        data = request.get_json()
        player_id = data.get("player_id")
        crop_type_id = data.get("crop_type_id")
        quantity = data.get("quantity", 1)

        if not player_id or not crop_type_id:
            return jsonify({"error": "player_id and crop_type_id required"}), 400

        result = sell_crops_batch(player_id, crop_type_id, quantity)
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
def get_balance(player_id):
    """Get player's current money balance."""
    try:
        balance = get_player_balance(player_id)
        return jsonify({"player_id": player_id, "balance": balance})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/player/<int:player_id>/buy-seeds", methods=["POST"])
def buy_seeds_endpoint(player_id):
    """Buy seeds for planting."""
    try:
        data = request.get_json()
        crop_type_id = data.get("crop_type_id")
        quantity = data.get("quantity", 1)

        if not crop_type_id:
            return jsonify({"error": "crop_type_id is required"}), 400

        result = buy_seeds(player_id, crop_type_id, quantity)
        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/crop/<int:crop_id>/sell", methods=["POST"])
def sell_crop_endpoint(crop_id):
    """Sell a harvested crop."""
    try:
        data = request.get_json()
        player_id = data.get("player_id")

        if not player_id:
            return jsonify({"error": "player_id is required"}), 400

        result = sell_crops(crop_id, player_id)
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
