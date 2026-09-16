# 🚨 Sentry Setup - Farming Life

Sentry es una plataforma centralizada de error tracking que captura, agrupa y rastrea errores en tiempo real.

---

## 🚀 Instalación

```bash
# Ya está instalado con:
pip install sentry-sdk
```

---

## 📋 Crear Cuenta en Sentry

1. Ir a [sentry.io](https://sentry.io)
2. Crear cuenta gratis (o usar existente)
3. Crear nuevo proyecto:
   - **Plataforma**: Flask
   - **Nombre**: Farming Life
4. Copiar el **DSN** (Data Source Name)
   - Formato: `https://<key>@<host>/api/<project_id>`

---

## ⚙️ Configurar .env

Agregar a `.env`:

```env
SENTRY_DSN=https://<key>@<host>/api/<project_id>
ENVIRONMENT=development
RELEASE=1.0.0
```

**O para producción:**

```env
SENTRY_DSN=https://<key>@<host>/api/<project_id>
ENVIRONMENT=production
RELEASE=1.0.1
```

---

## 🔌 Integrar en app.py

```python
from backend.sentry_config import init_sentry

app = Flask(__name__)
init_sentry(app)  # ← Agregar aquí

# Resto del código...
```

**IMPORTANTE**: `init_sentry()` debe ser una de las primeras líneas después de crear `app`.

---

## 📊 Qué Captura Automáticamente

| Evento | Capturado | Beneficio |
|--------|-----------|-----------|
| Excepciones no manejadas | ✅ | Errores inesperados en endpoints |
| Errores de base de datos | ✅ | Fallos de consultas SQL |
| Errores de autenticación | ✅ | Problemas de JWT/tokens |
| Requests lentos (>1s) | ✅ | Performance issues |
| Errores 500 | ✅ | Server errors |

---

## 🛠️ Captura Manual en Código

### 1. Configurar contexto del usuario

```python
from backend.sentry_config import set_user_context

@app.route('/api/player/<int:player_id>')
@require_auth
def get_player(player_id):
    # Vincular errores a este usuario
    set_user_context(player_id=player_id, email="player@example.com")
    
    return {"name": "Juan", "money": 5000}
```

### 2. Capturar excepciones

```python
from backend.sentry_config import capture_exception

def harvest_crop(crop_id):
    try:
        # ... lógica de cosecha ...
        return {"status": "success"}
    except Exception as e:
        # Sentry captura automáticamente con contexto
        capture_exception(e, operation="harvest", crop_id=crop_id)
        return {"error": "Cosecha fallida"}, 500
```

### 3. Capturar mensajes personalizados

```python
from backend.sentry_config import capture_message

def sell_crops(quantity):
    # ... venta exitosa ...
    
    # Log en Sentry con contexto
    capture_message(
        "Venta completada exitosamente",
        level="info",
        quantity=quantity,
        revenue=quantity * 100
    )
```

---

## 📈 Dashboard de Sentry

**URL**: https://sentry.io/organizations/your-org/issues/

### Vistas principales:

| Vista | Información |
|------|-----------|
| **Issues** | Errores agrupados y rastreados |
| **Performance** | Requests lentos y cuellos de botella |
| **Releases** | Qué versión causó qué error |
| **Users** | Errores por usuario/jugador |
| **Stats** | Gráficos de errores en el tiempo |

---

## 🎯 Casos de Uso en Farming Life

### 1. Rastrear errores de cosecha
```python
try:
    harvest_result = harvest_crop(crop_id)
except CropNotReadyError as e:
    capture_exception(e, crop_id=crop_id, player_id=player_id)
```

### 2. Monitorear problemas de pago
```python
def process_house_purchase(house_id, player_id):
    set_user_context(player_id=player_id)
    try:
        purchase_house(house_id, player_id)
        capture_message(f"Casa comprada: {house_id}", level="info")
    except InsufficientFunds as e:
        capture_exception(e, house_id=house_id)
```

### 3. Alertas en tiempo real
```
Por defecto, Sentry alerta por email cuando:
- Hay > 10 errores nuevos en 1 hora
- Un error ocurre en múltiples sesiones
- Un error es crítico (status 500)
```

---

## 🔐 Privacidad y Seguridad

**Sentry NO captura:**
- Contraseñas ❌
- Tokens JWT (automáticamente filtrados) ❌
- Números de tarjeta de crédito ❌

**Sentry captura (con privacidad):**
- IDs de jugadores ✅
- Emails ✅
- Nombres de usuarios ✅
- Stack traces (código) ✅

---

## 🧪 Testear Sentry

```bash
# Hacer un request que cause error (si Sentry está configurado)
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"invalid","password":""}'

# Ir a Sentry dashboard → Issues
# Deberías ver el error capturado en segundos
```

---

## 📊 Próximos Pasos

- [x] Sentry SDK instalado
- [x] Configuración básica
- [ ] Integrar en app.py
- [ ] Configurar alertas por email
- [ ] SLO Dashboards (próxima tarea)

---

## 📝 Billing & Limits

**Plan Gratuito:**
- ✅ Captura de errores ilimitada
- ✅ 5,000 events/mes
- ✅ 90 días de retención

**Plan Pagado:**
- Errores/performance ilimitados
- Alertas avanzadas
- Retención de 90+ días

Para Farming Life en desarrollo, plan gratuito es suficiente.

---

**Nota**: Esta es TAREA 3 de Semana 3.
