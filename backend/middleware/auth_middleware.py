"""
Autenticación con JWT - Middleware y decoradores
"""
from functools import wraps
from flask import request, jsonify
from backend.services.auth_service import verify_jwt_token


def extract_token_from_header():
	"""Extrae JWT del header Authorization: Bearer <token>"""
	auth_header = request.headers.get("Authorization")
	if not auth_header or not auth_header.startswith("Bearer "):
		return None
	return auth_header.split("Bearer ")[1]


def require_auth(f):
	"""Decorador para endpoints que requieren autenticación"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		token = extract_token_from_header()
		if not token:
			return jsonify({"error": "Missing or invalid Authorization header"}), 401

		try:
			payload = verify_jwt_token(token)
			request.player_id = payload["player_id"]
			return f(*args, **kwargs)
		except ValueError as e:
			return jsonify({"error": str(e)}), 401
		except Exception as e:
			return jsonify({"error": "Invalid token"}), 401

	return decorated_function


def require_player_match(f):
	"""Valida que el player_id en la URL coincida con el token JWT"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		token = extract_token_from_header()
		if not token:
			return jsonify({"error": "Missing or invalid Authorization header"}), 401

		try:
			payload = verify_jwt_token(token)
			request.player_id = payload["player_id"]

			# Validar que el player_id en URL coincida con el token
			url_player_id = kwargs.get("player_id")
			if url_player_id and int(url_player_id) != payload["player_id"]:
				return jsonify({"error": "Unauthorized: Cannot access other player's data"}), 403

			return f(*args, **kwargs)
		except ValueError as e:
			return jsonify({"error": str(e)}), 401
		except Exception as e:
			return jsonify({"error": "Invalid token"}), 401

	return decorated_function
