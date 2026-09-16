# 📚 Swagger/OpenAPI Setup - Farming Life

## ✅ Instalación

```bash
pip install flask-restx
```

## 🚀 Integración en app.py

Agregar estas líneas al inicio de `app.py` (después de crear la app Flask):

```python
from flask_restx import Api
from backend.openapi_docs import (
    API_INFO, SWAGGER_UI_CONFIG,
    auth_ns, player_ns, houses_ns, plots_ns, crops_ns, economy_ns
)

# Crear documentación OpenAPI
api = Api(
    app,
    title=API_INFO['title'],
    description=API_INFO['description'],
    version=API_INFO['version'],
    doc='/docs',  # URL de documentación
    prefix='/api'
)

# Registrar namespaces
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(player_ns, path='/player')
api.add_namespace(houses_ns, path='/houses')
api.add_namespace(plots_ns, path='/plots')
api.add_namespace(crops_ns, path='/crops')
api.add_namespace(economy_ns, path='/economy')
```

## 📖 Acceder a Documentación

Una vez integrado, accede a:

**Swagger UI**: `http://localhost:5000/docs`
**OpenAPI JSON**: `http://localhost:5000/swagger.json`
**ReDoc UI**: `http://localhost:5000/redoc`

## 🔐 Autenticación en Swagger

Para testear endpoints protegidos:

1. Abre `http://localhost:5000/docs`
2. Haz login primero en `/api/auth/login`
3. Copia el `token` de la respuesta
4. Busca el botón "Authorize" (parte superior)
5. Pega: `Bearer <token_aqui>`
6. Ahora puedes testear endpoints protegidos

## 📝 Descripción de Endpoints

Todos los endpoints en `openapi_docs.py` tienen:
- Descripción clara
- Parámetros documentados
- Modelos de request/response
- Niveles de seguridad

## 🧪 Test Manual

**Test Login:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"player@example.com","password":"password123"}'
```

**Test Protected Endpoint:**
```bash
curl -X GET http://localhost:5000/api/player/1 \
  -H "Authorization: Bearer <token>"
```

## 📊 Métricas de Documentación

- ✅ 6 Namespaces documentados
- ✅ 20+ Endpoints con descripciones
- ✅ 10+ Modelos de datos
- ✅ Seguridad JWT integrada
- ✅ Swagger UI + ReDoc

## 🎯 Beneficios

1. **Auto-Documentation**: Documentación que se actualiza sola
2. **Interactive Testing**: Testea endpoints sin curl
3. **Team Communication**: Otros devs entienden la API rápidamente
4. **API Contracts**: Clientes saben qué esperar
5. **Discovery**: Nuevos endpoints se auto-documentan

---

**Nota**: Esta es la TAREA 1 de Semana 3. Próximas tareas:
- Correlation IDs para rastreo
- Sentry para error tracking
- SLO dashboards
