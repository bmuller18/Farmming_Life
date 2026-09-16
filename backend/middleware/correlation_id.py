"""
Correlation IDs - Rastreo de requests a través del sistema
Permite seguir una solicitud desde inicio a fin en los logs
"""
import uuid
from flask import request, g
from backend.logging_config import api_logger


def init_correlation_id(app):
    """Inicializa middleware de Correlation ID"""

    @app.before_request
    def before_request():
        """Generar o extraer Correlation ID antes de cada request"""
        # Intentar extraer ID de cliente (si viene en header)
        correlation_id = request.headers.get("X-Correlation-ID")

        # Si no viene, generar uno nuevo
        if not correlation_id:
            correlation_id = str(uuid.uuid4())[:8]

        # Guardar en contexto global (g)
        g.correlation_id = correlation_id
        g.request_id = correlation_id  # Alias para compatibilidad

        # Log del inicio del request
        api_logger.info(
            f"[{correlation_id}] {request.method} {request.path} iniciado",
            extra={
                "correlation_id": correlation_id,
                "method": request.method,
                "path": request.path,
                "remote_addr": request.remote_addr
            }
        )

    @app.after_request
    def after_request(response):
        """Agregar Correlation ID al response header"""
        correlation_id = g.get("correlation_id", "unknown")

        # Agregar ID al response header para que cliente lo sepa
        response.headers["X-Correlation-ID"] = correlation_id

        return response


def get_correlation_id():
    """Obtener Correlation ID actual"""
    return g.get("correlation_id", "unknown")


def log_with_correlation(logger, level, message, **kwargs):
    """Helper para loguear con Correlation ID automático"""
    correlation_id = get_correlation_id()
    enriched_message = f"[{correlation_id}] {message}"

    extra = {
        "correlation_id": correlation_id,
        **kwargs
    }

    getattr(logger, level)(enriched_message, extra=extra)


# ============================================================================
# EJEMPLOS DE USO EN CÓDIGO
# ============================================================================

"""
En cualquier función del backend:

from backend.middleware.correlation_id import get_correlation_id, log_with_correlation
from backend.logging_config import crop_logger

def harvest_crop(crop_id):
    correlation_id = get_correlation_id()

    # Opción 1: Loguear con helper
    log_with_correlation(crop_logger, "info",
        f"Cosechando crop {crop_id}",
        crop_id=crop_id,
        yield_amount=10
    )

    # Opción 2: Loguear manualmente
    crop_logger.info(
        f"Cosecha exitosa",
        extra={
            "correlation_id": correlation_id,
            "crop_id": crop_id,
            "yield_amount": 10
        }
    )

# Resultado en logs:
# {"timestamp": "2026-09-16T...", "correlation_id": "a1b2c3d4", "crop_id": 5, "yield_amount": 10, ...}
"""
