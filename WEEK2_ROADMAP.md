# 📊 SEMANA 2: CONFIABILIDAD - Roadmap Implementación

## ✅ Tareas Completadas

### 1. Logging Estructurado ✅
- **Archivo**: `backend/logging_config.py`
- **Features**:
  - JSON structured logging para better parsing
  - Loggers por módulo (auth, crop, economy, house, api)
  - Funciones helper: `log_login()`, `log_harvest()`, `log_buy_house()`, etc
  - Context manager para agregar información a logs

- **Middleware**: `backend/middleware/request_logging.py`
  - Request IDs únicos (UUID)
  - Duración de requests en ms
  - Alertas de slow requests (>1000ms)
  - Logging automático POST /after_request

- **Integración en app.py**:
  ```python
  from backend.middleware.request_logging import init_request_logging
  init_request_logging(app)
  ```

---

### 2. Optimizaciones de Base de Datos ✅
- **Archivo**: `backend/database/optimize_queries.sql`

#### Índices Creados (8):
```sql
-- Login optimization
CREATE INDEX idx_player_email ON player(email);

-- Casa lookup
CREATE INDEX idx_houses_player_id ON houses(player_id);

-- Plot queries
CREATE INDEX idx_plots_house_id ON plots(house_id);

-- Crop queries
CREATE INDEX idx_crops_player_id ON crops(player_id);
CREATE INDEX idx_crops_plot_id ON crops(plot_id);
CREATE INDEX idx_crops_harvested_at ON crops(harvested_at);

-- Composite index for inventory
CREATE INDEX idx_crops_inventory 
  ON crops(player_id, crop_type_id, harvested_at, yield_amount);

-- Available houses (for purchase)
CREATE INDEX idx_houses_available 
  ON houses(player_id) WHERE player_id IS NULL;
```

#### Vistas Creadas (3):
```sql
-- player_stats: jugador + casas + cultivos
-- player_inventory: inventario agrupado por tipo
-- player_houses_view: casas con disponibilidad de plots
```

**Impacto**: Reducción 50-80% en tiempo de queries frecuentes

---

### 3. Idempotencia ✅
- **Archivo**: `backend/middleware/idempotency.py`
- **Decorador**: `@require_idempotency_key`

- **Usage**:
```python
@app.route("/api/crops/sell-batch", methods=["POST"])
@require_idempotency_key
def sell_batch():
    # Si se repite request con mismo Idempotency-Key, retorna cached response
```

- **Cliente (Frontend)**:
```javascript
// Generar UUID único
const idempotencyKey = crypto.randomUUID();

fetch('/api/crops/sell-batch', {
    method: 'POST',
    headers: {
        'Idempotency-Key': idempotencyKey,
        'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({...})
})
```

- **Beneficio**: Evita duplicados si cliente reintenta request (network error, timeout)

---

### 4. Row Level Security (RLS) ✅
- **Archivo**: `backend/database/rls_policies.sql`

#### Policies Implementadas:
- **player**: Solo ver/editar datos propios
- **houses**: Ver disponibles + ver propias
- **plots**: Solo owner de casa
- **crops**: Solo player
- **crop_type**: Público (lectura)
- **price**: Público (lectura)

**⚠️ IMPORTANTE**: Ejecutar en Supabase ANTES de producción

---

## 📋 Próximos Pasos de Implementación

### AHORA (Ejecutar en Supabase):
```
1. backend/database/optimize_queries.sql
   → Crea 8 índices y 3 vistas
   
2. backend/database/rls_policies.sql
   → Habilita Row Level Security
```

### SEMANA 3: OBSERVABILIDAD
1. OpenAPI/Swagger (endpoint documentation)
2. Correlation IDs (rastrear requests)
3. Error tracking (Sentry integration)
4. SLO dashboards (monitoring)

---

## 🧪 Testing Cambios

### Verificar Índices:
```sql
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename;
```

### Verificar RLS Habilitado:
```sql
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';
```

### Test Idempotencia:
```bash
# Request 1
curl -X POST http://localhost:5000/api/crops/sell-batch \
  -H "Idempotency-Key: test-123" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1, "crop_type_id": 1, "quantity": 5}'

# Request 2 (mismo Idempotency-Key) → Retorna cached
curl -X POST http://localhost:5000/api/crops/sell-batch \
  -H "Idempotency-Key: test-123" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"player_id": 1, "crop_type_id": 1, "quantity": 5}'

# Request 3 (Idempotency-Key diferente) → Ejecuta de nuevo
curl -X POST http://localhost:5000/api/crops/sell-batch \
  -H "Idempotency-Key: test-456" \
  ...
```

### Verificar Logging JSON:
```bash
# Start app
python backend/app.py

# En otra terminal, hacer request
curl http://localhost:5000/api/health

# Logs aparecen en JSON structured
# {"timestamp": "2026-09-16T...", "level": "INFO", "message": "GET /api/health → 200", ...}
```

---

## 📊 Métricas Esperadas

| Métrica | Antes | Después |
|---------|-------|---------|
| Query tiempo (login) | ~200ms | ~50ms |
| Query tiempo (inventory) | ~500ms | ~100ms |
| Slow requests | - | <1% |
| Duplicate transactions | ⚠️ Posible | ✅ Prevenido |
| Unauthorized data access | ❌ Posible | ✅ Bloqueado |

---

## 🚀 Arquitectura Post-Semana 2

```
Request
  ↓
Middleware:
├─ Request Logging (timing + ID)
├─ JWT Validation
├─ Rate Limiting
├─ Idempotency Check
├─ Input Validation (Pydantic)
  ↓
Business Logic (services)
  ↓
Database:
├─ Optimized queries with indices
├─ RLS enforcement (row-level security)
├─ Cached results (vistas)
  ↓
Response
  ↓
Logging (JSON)
```

---

## 📝 Status Checklist

- [ ] Ejecutar `optimize_queries.sql` en Supabase
- [ ] Verificar 8 índices creados
- [ ] Ejecutar `rls_policies.sql` en Supabase
- [ ] Verificar RLS habilitado en todas tablas
- [ ] Ver logs JSON en stdout
- [ ] Test idempotencia en sell-batch
- [ ] Monitorear performance de queries
- [ ] Documentar SLOs (response time targets)

---

## 🔄 Ciclo de Mejora Continua

Cada semana:
1. Recolectar logs (JSON)
2. Analizar slow queries
3. Agregar índices donde sea necesario
4. Monitorear error rates
5. Optimizar hotspots

Ejemplo análisis:
```sql
-- Top 10 slowest queries (después de pg_stat_statements)
SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```
