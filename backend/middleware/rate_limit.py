"""
Rate Limiting - Protección contra DDoS
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request


def create_limiter(app):
	"""Crea y configura Flask-Limiter"""
	limiter = Limiter(
		app=app,
		key_func=get_remote_address,
		default_limits=["200 per day", "50 per hour"],
		storage_uri="memory://"  # En producción usar Redis
	)
	return limiter


def setup_rate_limits(limiter):
	"""Configura límites específicos por endpoint"""
	limits = {
		# Autenticación - muy restrictivo (prevenir fuerza bruta)
		"/api/auth/login": "5 per minute",
		"/api/auth/register": "3 per minute",

		# Operaciones de dinero - restrictivo
		"/api/player/*/buy-house": "10 per hour",
		"/api/player/*/buy-seeds": "30 per hour",
		"/api/crops/sell-batch": "30 per hour",
		"/api/crop/*/sell": "30 per hour",

		# Lectura - permisivo
		"/api/player/*": "100 per hour",
		"/api/player/*/houses": "100 per hour",
		"/api/player/*/inventory": "100 per hour",
		"/api/player/*/balance": "100 per hour",
		"/api/house/*": "100 per hour",
		"/api/plot/*": "100 per hour",
		"/api/crop-types": "100 per hour",

		# Información general
		"/api/prices": "100 per hour",
		"/health": "1000 per hour"
	}

	return limits


# ============================================================================
# DECORADORES PERSONALIZADOS
# ============================================================================

def rate_limit_strict(limiter):
	"""Decorador para endpoints críticos (login, transacciones)"""
	def decorator(f):
		return limiter.limit("5 per minute")(f)
	return decorator


def rate_limit_moderate(limiter):
	"""Decorador para operaciones normales"""
	def decorator(f):
		return limiter.limit("30 per hour")(f)
	return decorator


def rate_limit_permissive(limiter):
	"""Decorador para lecturas"""
	def decorator(f):
		return limiter.limit("100 per hour")(f)
	return decorator


# ============================================================================
# ERROR HANDLER
# ============================================================================

def setup_rate_limit_error_handler(app):
	"""Configura respuesta personalizada cuando se excede el límite"""
	@app.errorhandler(429)
	def ratelimit_handler(e):
		return {
			"error": "Rate limit exceeded",
			"message": "Has excedido el límite de requests. Intenta de nuevo más tarde.",
			"retry_after": e.description
		}, 429
