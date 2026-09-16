"""
OpenAPI/Swagger Documentation para Farming Life
Documentación automática de endpoints
"""
from flask_restx import Api, Namespace, fields

# Namespaces para organizar endpoints
auth_ns = Namespace('auth', description='Autenticación y registro')
player_ns = Namespace('player', description='Información del jugador')
houses_ns = Namespace('houses', description='Gestión de casas')
plots_ns = Namespace('plots', description='Gestión de parcelas')
crops_ns = Namespace('crops', description='Gestión de cultivos')
economy_ns = Namespace('economy', description='Sistema económico')

# ============================================================================
# MODELOS PARA DOCUMENTACIÓN
# ============================================================================

# Modelos de Autenticación
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='Email del jugador'),
    'password': fields.String(required=True, description='Contraseña'),
})

register_model = auth_ns.model('Register', {
    'name': fields.String(required=True, description='Nombre del jugador'),
    'email': fields.String(required=True, description='Email único'),
    'password': fields.String(required=True, description='Contraseña (mín 8 caracteres)'),
})

auth_response_model = auth_ns.model('AuthResponse', {
    'player_id': fields.Integer(description='ID del jugador'),
    'name': fields.String(description='Nombre del jugador'),
    'email': fields.String(description='Email del jugador'),
    'token': fields.String(description='JWT token (válido 30 días)'),
    'message': fields.String(description='Mensaje de éxito'),
})

# Modelo de Jugador
player_model = player_ns.model('Player', {
    'id': fields.Integer(description='ID único del jugador'),
    'name': fields.String(description='Nombre del jugador'),
    'email': fields.String(description='Email del jugador'),
    'money': fields.Integer(description='Dinero disponible ($)'),
    'level': fields.Integer(description='Nivel actual'),
    'created_at': fields.DateTime(description='Fecha de creación'),
    'updated_at': fields.DateTime(description='Última actualización'),
})

# Modelo de Casa
house_model = houses_ns.model('House', {
    'id': fields.Integer(description='ID de la casa'),
    'name': fields.String(description='Nombre de la casa'),
    'price': fields.Integer(description='Precio de compra ($)'),
    'plot_count': fields.Integer(description='Número de parcelas'),
    'player_id': fields.Integer(description='ID del dueño (null si está disponible)'),
})

# Modelo de Parcela
plot_model = plots_ns.model('Plot', {
    'id': fields.Integer(description='ID de la parcela'),
    'house_id': fields.Integer(description='ID de la casa'),
    'name': fields.String(description='Nombre de la parcela'),
    'status': fields.String(description='Estado: empty, growing, ready'),
})

# Modelo de Cultivo
crop_model = crops_ns.model('Crop', {
    'id': fields.Integer(description='ID del cultivo'),
    'plot_id': fields.Integer(description='ID de la parcela'),
    'crop_type_id': fields.Integer(description='Tipo de cultivo'),
    'planted_at': fields.DateTime(description='Fecha de siembra'),
    'ready_at': fields.DateTime(description='Fecha de cosecha'),
    'harvested_at': fields.DateTime(description='Fecha de cosecha real (null si no cosechado)'),
    'yield_amount': fields.Integer(description='Cantidad cosechada'),
})

# Modelo de Precio
price_model = economy_ns.model('Price', {
    'crop_type_id': fields.Integer(description='ID del tipo de cultivo'),
    'crop_name': fields.String(description='Nombre del cultivo'),
    'seed_price': fields.Integer(description='Precio de semilla ($)'),
    'crop_price': fields.Integer(description='Precio de venta ($)'),
    'days_to_grow': fields.Integer(description='Días para crecer'),
})

# ============================================================================
# DOCUMENTACIÓN DE ENDPOINTS
# ============================================================================

@auth_ns.route('/login')
class AuthLogin:
    """Autenticación de jugador"""
    @auth_ns.doc('login')
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(auth_response_model)
    def post(self):
        """
        Iniciar sesión con email y contraseña

        Retorna JWT token válido por 30 días.
        Incluir token en header: Authorization: Bearer <token>
        """
        pass

@auth_ns.route('/register')
class AuthRegister:
    """Registro de nuevo jugador"""
    @auth_ns.doc('register')
    @auth_ns.expect(register_model)
    @auth_ns.marshal_with(auth_response_model)
    def post(self):
        """
        Registrar nuevo jugador

        Crea cuenta con email único.
        Retorna JWT token e información del jugador.
        Dinero inicial: $5,000
        Nivel inicial: 1
        """
        pass

@player_ns.route('/<int:player_id>')
class PlayerInfo:
    """Información del jugador"""
    @player_ns.doc('get_player', security='apiKey')
    @player_ns.marshal_with(player_model)
    def get(self, player_id):
        """
        Obtener información del jugador

        Requiere: JWT en Authorization header
        """
        pass

@houses_ns.route('/available/<int:player_id>')
class AvailableHouses:
    """Casas disponibles para compra"""
    @houses_ns.doc('get_available_houses', security='apiKey')
    def get(self, player_id):
        """
        Obtener casas disponibles para compra

        Requiere: JWT en Authorization header
        Retorna: Lista de casas no poseídas
        """
        pass

@houses_ns.route('/<int:player_id>/buy')
class BuyHouse:
    """Comprar casa"""
    @houses_ns.doc('buy_house', security='apiKey')
    def post(self, player_id):
        """
        Comprar una casa

        Requiere: JWT, funds suficientes
        Crea automáticamente parcelas
        """
        pass

@crops_ns.route('/sell-batch')
class SellBatch:
    """Vender múltiples cultivos"""
    @crops_ns.doc('sell_batch', security='apiKey')
    def post(self):
        """
        Vender cultivos en lote

        Requiere: JWT, cultivos disponibles
        Soporta venta de cantidad variable (1-N unidades)
        """
        pass

# ============================================================================
# DOCUMENTACIÓN DE SEGURIDAD
# ============================================================================

SECURITY_SCHEMES = {
    'apiKey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'JWT token: Bearer <token>'
    }
}

# ============================================================================
# INFO GENERAL DE API
# ============================================================================

API_INFO = {
    'title': '🌾 Farming Life API',
    'description': 'REST API para juego de agricultura con sistemas de cultivos, casas y economía',
    'version': '1.0.0',
    'contact': {
        'name': 'Farming Life Support',
        'email': 'support@farminglife.local'
    },
    'license': {
        'name': 'MIT'
    }
}

# ============================================================================
# CONFIGURACIÓN DE SWAGGER UI
# ============================================================================

SWAGGER_UI_CONFIG = {
    'title': '🌾 Farming Life - API Documentation',
    'uiversion': 3,
    'deepLinking': True,
    'presets': [
        'swaggerUIBundle.presets.apis',
        'swaggerUIBundle.SwaggerUIStandalonePreset'
    ],
    'layout': 'BaseLayout',
}
