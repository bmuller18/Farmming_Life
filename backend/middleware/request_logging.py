"""
Request Logging Middleware
Mide duración de requests y asigna IDs únicos
"""
import time
import uuid
from flask import request, g
from backend.logging_config import api_logger


def init_request_logging(app):
	"""Inicializa logging de requests en la app Flask"""

	@app.before_request
	def before_request():
		"""Antes de cada request"""
		g.request_id = str(uuid.uuid4())[:8]
		g.start_time = time.time()
		request.environ['LOGGER_REQUEST_ID'] = g.request_id


	@app.after_request
	def after_request(response):
		"""Después de cada request"""
		if hasattr(g, 'start_time'):
			duration_ms = (time.time() - g.start_time) * 1000

			# Obtener player_id del contexto si existe
			player_id = None
			if hasattr(request, 'player_id'):
				player_id = request.player_id

			# Log del request
			api_logger.info(
				f"{request.method} {request.path} → {response.status_code}",
				extra={
					"method": request.method,
					"path": request.path,
					"status_code": response.status_code,
					"duration_ms": round(duration_ms, 2),
					"player_id": player_id,
					"request_id": g.request_id
				}
			)

			# Alerta si request toma mucho tiempo
			if duration_ms > 1000:
				api_logger.warning(
					f"SLOW REQUEST: {request.method} {request.path} tomó {duration_ms:.0f}ms",
					extra={
						"method": request.method,
						"path": request.path,
						"duration_ms": round(duration_ms, 2)
					}
				)

		return response
