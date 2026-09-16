"""
Sentry Integration para Error Tracking centralizado
Captura, agrupa y rastrea errores en tiempo real
"""
import os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration


def init_sentry(app):
    """Inicializar Sentry para captura de errores"""

    sentry_dsn = os.getenv("SENTRY_DSN")

    # Solo inicializar si hay DSN configurada
    if not sentry_dsn:
        print("⚠️  SENTRY_DSN no configurada. Error tracking deshabilitado.")
        return

    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
        ],
        # Qué porcentaje de requests capturar (0.1 = 10%)
        # En producción usar ~0.1 para no sobrecargar
        traces_sample_rate=0.1,

        # Qué porcentaje de transacciones capturar
        profiles_sample_rate=0.1,

        # Información de la aplicación
        environment=os.getenv("ENVIRONMENT", "development"),
        release=os.getenv("RELEASE", "1.0.0"),

        # Capturar contexto local en stack traces
        include_local_variables=True,

        # Máximo número de caracteres en string (para privacidad)
        max_value_length=1024,

        # Deshabilitar captura de sesiones (reducir datos)
        auto_session_tracking=False,
    )

    print("✅ Sentry inicializado para error tracking")


def set_user_context(player_id, email=None):
    """
    Configurar contexto del usuario para errores posteriores
    Útil para correlacionar errores con jugadores específicos

    Uso:
        set_user_context(player_id=23, email="player@example.com")
    """
    with sentry_sdk.Hub.current.client.push_scope() as scope:
        scope.set_user({
            "id": str(player_id),
            "email": email or "unknown"
        })


def capture_exception(error, **context):
    """
    Capturar excepción manualmente

    Uso:
        try:
            risky_operation()
        except Exception as e:
            capture_exception(e, operation="harvest", crop_id=5)
    """
    with sentry_sdk.Hub.current.client.push_scope() as scope:
        # Agregar contexto adicional
        for key, value in context.items():
            scope.set_tag(key, value)

        sentry_sdk.capture_exception(error)


def capture_message(message, level="info", **tags):
    """
    Capturar mensaje personalizado

    Niveles: debug, info, warning, error, fatal

    Uso:
        capture_message(
            "Cosecha completada exitosamente",
            level="info",
            crop_id=5,
            yield_amount=10
        )
    """
    with sentry_sdk.Hub.current.client.push_scope() as scope:
        # Agregar tags para filtrar en Sentry
        for key, value in tags.items():
            scope.set_tag(key, value)

        sentry_sdk.capture_message(message, level=level)


# ============================================================================
# EJEMPLOS DE USO EN CÓDIGO
# ============================================================================

"""
En app.py (después de crear Flask app):

from backend.sentry_config import init_sentry, set_user_context, capture_exception

app = Flask(__name__)
init_sentry(app)

En endpoints autenticados:

@app.route('/api/crops/harvest', methods=['POST'])
@require_auth
def harvest_crop():
    player_id = request.player_id

    # Configurar contexto del usuario para Sentry
    set_user_context(player_id=player_id)

    try:
        # ... lógica de cosecha ...
        return {"status": "success"}
    except Exception as e:
        # Capturar error con contexto automático
        capture_exception(e, operation="harvest", crop_id=crop_id)
        return {"error": "Cosecha fallida"}, 500

En try/except específicos:

def sell_crops_batch(crop_type_id, quantity):
    try:
        # ... lógica de venta ...
    except InsufficientCrops as e:
        capture_exception(e,
            operation="sell_batch",
            crop_type_id=crop_type_id,
            quantity=quantity
        )
        raise

Mensajes personalizados:

def complete_harvest():
    # ... cosecha exitosa ...
    capture_message(
        "Cosecha completada",
        level="info",
        crop_type="wheat",
        yield_amount=10
    )
"""
