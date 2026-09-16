# 🔍 Correlation IDs Setup - Farming Life

## ¿Qué son Correlation IDs?

Identificadores únicos que viajan con cada request a través del sistema, permitiendo rastrear:
- Dónde comienza un request
- Qué funciones ejecuta
- Cuánto tiempo tarda
- Qué errores ocurren

**Ejemplo de rastreo:**
```
Request llega → [a1b2c3d4] GET /api/player/23
  ↓
auth_middleware → [a1b2c3d4] JWT validation OK
  ↓
loadPlayer() → [a1b2c3d4] Loading player data
  ↓
database → [a1b2c3d4] Query: SELECT * FROM player WHERE id=23
  ↓
Response → [a1b2c3d4] Status: 200 (145ms)

Todos los logs tienen el ID a1b2c3d4, así sabes que pertenecen al mismo request.
```

---

## 🚀 Integración en app.py

Agregar después de crear la app Flask:

```python
from backend.middleware.correlation_id import init_correlation_id

# Inicializar Correlation ID middleware
init_correlation_id(app)
```

---

## 📖 Cómo Usarlo en el Código

### Opción 1: Helper automático (recomendado)

```python
from backend.middleware.correlation_id import log_with_correlation
from backend.logging_config import crop_logger

def harvest_crop(crop_id):
    # Loguea con Correlation ID automático
    log_with_correlation(crop_logger, "info",
        f"Cosechando crop {crop_id}",
        crop_id=crop_id,
        yield_amount=10
    )
```

### Opción 2: Obtener ID manualmente

```python
from backend.middleware.correlation_id import get_correlation_id
from backend.logging_config import crop_logger

def harvest_crop(crop_id):
    correlation_id = get_correlation_id()
    
    crop_logger.info(
        f"Cosechando crop",
        extra={
            "correlation_id": correlation_id,
            "crop_id": crop_id,
            "yield_amount": 10
        }
    )
```

---

## 🔄 Flujo Completo

### 1. Request llega desde Frontend

Frontend envía (opcional):
```javascript
fetch('/api/player/23', {
    headers: {
        'X-Correlation-ID': 'user-request-123'  // Opcional
    }
})
```

### 2. Middleware genera/extrae ID

```python
@app.before_request
def before_request():
    correlation_id = request.headers.get("X-Correlation-ID")
    if not correlation_id:
        correlation_id = str(uuid.uuid4())[:8]  # Generar nuevo
    
    g.correlation_id = correlation_id  # Guardar en contexto
```

### 3. Se usa en todos los logs

```json
{
  "timestamp": "2026-09-16T08:45:00.000",
  "level": "INFO",
  "correlation_id": "a1b2c3d4",
  "message": "Cosechando crop 5",
  "crop_id": 5,
  "yield_amount": 10
}
```

### 4. Response incluye el ID

```
X-Correlation-ID: a1b2c3d4
```

---

## 📊 Ventajas

| Ventaja | Beneficio |
|---------|-----------|
| **Rastreo de errores** | Sigue un error desde inicio a fin |
| **Performance debugging** | Identifica qué requests son lentos |
| **Multi-service tracing** | En futuro, rastrea entre microservicios |
| **Audit trail** | Sabe quién hizo qué y cuándo |
| **Log correlation** | Agrupa logs relacionados automáticamente |

---

## 🧪 Testing

### Ver Correlation ID en Response

```bash
curl -i http://localhost:5000/api/player/23 \
  -H "Authorization: Bearer <token>"

# Output incluye:
# X-Correlation-ID: a1b2c3d4
```

### Propios IDs desde Cliente

```bash
curl -i http://localhost:5000/api/player/23 \
  -H "X-Correlation-ID: my-custom-id" \
  -H "Authorization: Bearer <token>"

# Output:
# X-Correlation-ID: my-custom-id
```

---

## 📝 Logs con Correlation ID

**Antes** (sin correlation):
```json
{
  "timestamp": "2026-09-16T08:45:00.000",
  "level": "INFO",
  "message": "Player loaded"
}
```

**Después** (con correlation):
```json
{
  "timestamp": "2026-09-16T08:45:00.000",
  "level": "INFO",
  "correlation_id": "a1b2c3d4",
  "message": "[a1b2c3d4] Player loaded",
  "player_id": 23,
  "load_time_ms": 15
}
```

---

## 🎯 Próximos Pasos

- [x] Correlation ID middleware
- [ ] Integrar en app.py
- [ ] Sentry error tracking
- [ ] SLO dashboards

---

**Nota**: Esto es TAREA 2 de Semana 3.
