# 🔒 Roadmap de Seguridad - Farming Life

## Semana 1: Seguridad Crítica ✅ En Progreso

### ✅ 1. Middleware JWT Validation - COMPLETADO

**Cambios realizados:**
- ✅ Creado `backend/middleware/auth_middleware.py` con decoradores:
  - `@require_auth`: Valida JWT en cualquier endpoint
  - `@require_player_match`: Valida JWT + que player_id coincida con token
- ✅ Protegidos 8 endpoints críticos:
  - `GET /api/player/<player_id>` ✅
  - `GET /api/player/<player_id>/houses` ✅
  - `GET /api/houses/available/<player_id>` ✅
  - `POST /api/player/<player_id>/buy-house` ✅
  - `GET /api/player/<player_id>/inventory` ✅
  - `POST /api/crops/sell-batch` ✅
  - `POST /api/crop/<crop_id>/sell` ✅
  - `GET /api/player/<player_id>/balance` ✅
  - `POST /api/player/<player_id>/buy-seeds` ✅

**Cómo usan el middleware:**
```javascript
// Frontend debe enviar JWT en cada request:
fetch('/api/player/1', {
  headers: {
    'Authorization': 'Bearer <jwt_token>'
  }
})
```

---

### ⏳ 2. Transacciones SQL Atómicas - EN PROGRESO

**Problema resuelto:**
- ❌ ANTES: Race condition en dinero (3 queries separadas sin transacción)
- ✅ AHORA: Stored Procedures con bloqueos (FOR UPDATE)

**Stored Procedures creados:**
- `buy_house_atomic()` - Compra de casa ATÓMICA
- `sell_crops_batch_atomic()` - Venta de crops ATÓMICA
- `buy_seeds_atomic()` - Compra de semillas ATÓMICA

**⚠️ PRÓXIMO PASO - Ejecutar en Supabase:**

1. Ve a: https://app.supabase.com → Tu proyecto
2. SQL Editor → New Query
3. Copia el contenido de `backend/database/stored_procedures.sql`
4. Ejecuta cada función por separado (⚠️ IMPORTANTE: ejecutar una por una)
5. Verifica que no hay errores en la consola

**Después de crear los Stored Procedures:**
```bash
# Las funciones estarán disponibles para usar:
- SELECT buy_house_atomic(player_id, house_id)
- SELECT sell_crops_batch_atomic(player_id, crop_type_id, quantity)
- SELECT buy_seeds_atomic(player_id, crop_type_id, quantity)
```

---

### ⏳ 3. Validación Pydantic - Próximamente

Validar tipos de datos en todos los endpoints:
- Rangos: `quantity` debe ser > 0
- Tipos: `player_id` debe ser INT positivo
- Valores válidos: `crop_type_id` debe existir

---

### ⏳ 4. Rate Limiting - Próximamente

Proteger contra DDoS:
```bash
pip install Flask-Limiter
```

---

### ⏳ 5. Verificar SECRET_KEY - Próximamente

Asegurar que `.env` tiene:
```
SECRET_KEY=tu-super-secret-key-aqui-minimo-32-caracteres
```

---

## Testing de Seguridad

### Prueba 1: JWT Validation
```bash
# Sin JWT → Debe retornar 401
curl -X GET http://localhost:5000/api/player/1

# Con JWT inválido → Debe retornar 401
curl -X GET http://localhost:5000/api/player/1 \
  -H "Authorization: Bearer invalid_token"

# Con JWT válido → OK
curl -X GET http://localhost:5000/api/player/1 \
  -H "Authorization: Bearer <token_válido>"
```

### Prueba 2: Player Match Validation
```bash
# Intentar acceder a otro jugador → Debe retornar 403
# Token de player 1, pero intentando acceder a player 2
curl -X GET http://localhost:5000/api/player/2 \
  -H "Authorization: Bearer <token_player_1>"
# Respuesta: 403 Forbidden "Cannot access other player's data"
```

### Prueba 3: Race Conditions (después de Stored Procedures)
```bash
# El dinero ahora es ATÓMICO
# No puede ocurrir: player compra 2 casas con $1000 si cada casa cuesta $600
```

---

## Arquitectura de Seguridad

```
Request
  ↓
Frontend (index.html)
  ├─ Obtiene JWT en login
  ├─ Almacena en localStorage
  ├─ Envía en cada request: Authorization: Bearer <jwt>
  ↓
Backend (app.py)
  ├─ Extrae JWT del header
  ├─ Valida con middleware @require_auth o @require_player_match
  │  ├─ Si inválido → 401 Unauthorized
  │  ├─ Si válido pero player_id no coincide → 403 Forbidden
  │  └─ Si válido → continúa
  ├─ Llama a Stored Procedure (si es operación de dinero)
  │  └─ Stored Procedure garantiza ACID con FOR UPDATE bloqueos
  ↓
Supabase (PostgreSQL)
  ├─ Row Level Security (RLS) - adicional
  ├─ Índices en campos críticos
  └─ Logs de auditoría
```

---

## Status por Endpoint

| Endpoint | JWT Validation | Player Match | Atomic | Rate Limit |
|----------|----------------|--------------|--------|-----------|
| GET /api/player/{id} | ✅ | ✅ | N/A | ⏳ |
| GET /api/player/{id}/houses | ✅ | ✅ | N/A | ⏳ |
| POST /api/player/{id}/buy-house | ✅ | ✅ | ⏳* | ⏳ |
| GET /api/player/{id}/inventory | ✅ | ✅ | N/A | ⏳ |
| POST /api/crops/sell-batch | ✅ | ⚠️ | ⏳* | ⏳ |
| POST /api/player/{id}/buy-seeds | ✅ | ✅ | ⏳* | ⏳ |

\* = Requiere ejecutar Stored Procedures en Supabase

---

## Próximos Pasos

1. **Inmediato**: Ejecutar Stored Procedures en Supabase
2. **Esta semana**: Implementar Validación Pydantic
3. **Próxima semana**: Rate Limiting + verificar SECRET_KEY
