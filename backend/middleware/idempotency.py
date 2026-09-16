"""
Idempotency Keys - Prevenir duplicados en operaciones
Uso: @require_idempotency_key
"""
from flask import request, jsonify
from functools import wraps
import hashlib
import json


# En producción, usar Redis o base de datos
_idempotency_cache = {}


def get_idempotency_key():
	"""Extrae Idempotency-Key del header"""
	return request.headers.get("Idempotency-Key")


def cache_response(key: str, response: dict, status_code: int):
	"""Cachea respuesta de operación idempotente"""
	_idempotency_cache[key] = {
		"response": response,
		"status_code": status_code
	}


def get_cached_response(key: str):
	"""Obtiene respuesta cacheada si existe"""
	return _idempotency_cache.get(key)


def require_idempotency_key(f):
	"""
	Decorador para hacer endpoints idempotentes.
	Require header: Idempotency-Key

	Ejemplo de uso:
		@app.route("/api/crops/sell-batch", methods=["POST"])
		@require_idempotency_key
		def sell_batch():
			# ... endpoint code
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		idempotency_key = get_idempotency_key()

		# Validar que existe idempotency key
		if not idempotency_key:
			return jsonify({
				"error": "Idempotency-Key header requerido",
				"hint": "Incluye header: Idempotency-Key: <uuid>"
			}), 400

		# Validar formato (debe ser UUID o similar)
		if len(idempotency_key) < 10 or len(idempotency_key) > 100:
			return jsonify({
				"error": "Idempotency-Key inválido",
				"hint": "Debe ser único y de 10-100 caracteres"
			}), 400

		# Validar que no haya sido usado recientemente
		cached = get_cached_response(idempotency_key)
		if cached:
			# Retornar la misma respuesta
			return jsonify(cached["response"]), cached["status_code"]

		# Ejecutar endpoint
		try:
			result = f(*args, **kwargs)

			# Si es tupla (response, status_code), extraerlo
			if isinstance(result, tuple):
				response_data, status_code = result
			else:
				response_data = result
				status_code = 200

			# Cachear respuesta
			if isinstance(response_data, dict):
				cache_response(idempotency_key, response_data, status_code)

			return result

		except Exception as e:
			# No cachear errores
			raise

	return decorated_function


# ============================================================================
# HELPERS
# ============================================================================

def generate_idempotency_key(data: dict) -> str:
	"""Genera idempotency key a partir de datos"""
	payload = json.dumps(data, sort_keys=True)
	return hashlib.sha256(payload.encode()).hexdigest()[:16]
