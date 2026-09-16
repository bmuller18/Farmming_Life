# 📊 SLO Dashboards - Farming Life

SLOs (Service Level Objectives) son objetivos de confiabilidad que definen qué tan bien debería funcionar tu servicio.

---

## ¿Qué es un SLO?

Un SLO es una promesa medible:
- "99.9% de requests completarán en < 200ms"
- "99.9% de disponibilidad"
- "< 0.1% de error rate"

Si cumples el SLO → ✅ SLI (Service Level Indicator)
Si no lo cumples → ❌ Se quema el error budget

---

## 📈 SLOs de Farming Life

| SLO | Target | Importancia |
|-----|--------|------------|
| **Disponibilidad** | 99.9% uptime | CRÍTICA |
| **Latencia p95** | < 200ms | ALTA |
| **Latencia p99** | < 500ms | ALTA |
| **Error Rate** | < 0.1% | CRÍTICA |
| **Rate Limiting** | < 5% rechazos | MEDIA |

---

## 🚀 Instalación

Ya está incluido en `backend/slo_monitoring.py`

---

## 🔌 Integrar en app.py

```python
from backend.slo_monitoring import init_slo_monitoring

app = Flask(__name__)
init_slo_monitoring(app)  # ← Agregar aquí

# Resto del código...
```

**Eso es todo**. El monitoreo ocurre automáticamente en cada request.

---

## 📊 Ver Dashboard

```bash
# Dashboard en tiempo real
curl http://localhost:5000/api/slo/dashboard | jq

# Resultado:
{
  "timestamp": "2026-09-16T10:30:00",
  "uptime": {
    "percentage": "99.95%",
    "requests_successful": 1995,
    "requests_total": 2000
  },
  "latency": {
    "average_ms": "45ms",
    "p95_ms": "120ms",
    "p99_ms": "350ms"
  },
  "errors": {
    "error_rate": "0.25%",
    "total_errors": 5,
    "rate_limited": 0
  },
  "slos": {
    "availability_target": "99.9% ✅",
    "latency_p95_target": "<200ms ✅",
    "latency_p99_target": "<500ms ✅",
    "error_rate_target": "<0.1% ❌",
    "rate_limit_target": "<5% ✅"
  }
}
```

---

## 📈 Métricas Explicadas

### Uptime (Disponibilidad)
- **% de requests exitosos** sin errores ni timeouts
- Target: 99.9% = ~43 minutos de downtime por mes
- Si < 99.9% → Error budget se quema 🔥

### Latency (Latencia)
- **p95**: 95% de requests más rápidos que esto
- **p99**: 99% de requests más rápidos que esto
- Target: p95 < 200ms, p99 < 500ms
- Si > target → Usuarios ven lentitud

### Error Rate (Tasa de Errores)
- **% de requests con error** (status 4xx/5xx)
- Target: < 0.1% = máximo 1 error por 1000 requests
- Si > target → Experiencia del usuario degradada

### Rate Limiting (Límite de Tasa)
- **% de requests rechazados** (status 429)
- Target: < 5% = máximo 50 rechazos por 1000 requests
- Si > target → Usuarios son bloqueados

---

## ⚠️ Error Budget

El error budget es cuánto puedes "fallar" antes de violar el SLO.

**Ejemplo: 99.9% uptime = 0.1% error budget**

```
Mes de 2,592,000 requests
0.1% = 2,592 requests permitidos fallar
Si tienes más de 2,592 errores → SLO se rompe
```

---

## 🎯 Cómo Usar en Desarrollo

### Durante desarrollo:
```python
# Ver SLOs después de cambios grandes
curl http://localhost:5000/api/slo/dashboard

# Si latency p95 sube mucho → Optimizar
# Si error_rate sube → Hay un bug
```

### Antes de deploy:
```bash
# Asegurarse de que todos los SLOs se cumplen
curl http://localhost:5000/api/slo/dashboard | jq '.slos'

# Resultado esperado:
# Todos los SLOs deben tener ✅
```

---

## 📊 Visualización Avanzada (Opcional)

Para dashboards en tiempo real, integrar con:

### Opción 1: Grafana + Prometheus
```yaml
# Exponer métricas en formato Prometheus
GET /metrics/prometheus

# Prometheus scrape cada 15 segundos
# Grafana visualiza en tiempo real
```

### Opción 2: Datadog
```python
from datadog import api

# Enviar SLOs a Datadog
api.ServiceLevelObjective.create(
    name="Farming Life - Latency",
    target=0.99,
    metric_query="avg:latency{service:farming-life}",
)
```

### Opción 3: CloudWatch (AWS)
```python
import boto3

cloudwatch = boto3.client('cloudwatch')
cloudwatch.put_metric_data(
    Namespace='FarmingLife',
    MetricData=[
        {'MetricName': 'Uptime', 'Value': 99.95},
        {'MetricName': 'LatencyP95', 'Value': 120},
    ]
)
```

---

## 🚨 Alertas

SLOs con ❌ = Alerta activa

### Cuándo alertar:
- Error rate > 0.1% → Página al oncall
- Latency p95 > 200ms → Slack alert
- Uptime < 99.9% → Email + Slack
- Rate limiting > 5% → Investigar tráfico

---

## 📊 Ejemplo: Problemas Comunes

### Error: "latency_p99_target: <500ms ❌"
**Significa**: 99% de requests son más lentos de 500ms

**Investigar**:
```bash
# Ver endpoints más lentos
curl http://localhost:5000/api/slo/dashboard | jq '.endpoints' | sort by .total_time

# Optimizar la BD
# Agregar índices
# Cachear respuestas
```

### Error: "error_rate_target: <0.1% ❌"
**Significa**: Hay muchos errores

**Investigar**:
```bash
# Ver endpoint con más errores
curl http://localhost:5000/api/slo/dashboard | jq '.endpoints'

# Revisar logs de Sentry
# Arreglar bugs
```

---

## 🎯 Próximos Pasos

- [x] Monitoring setup
- [x] SLO tracking
- [ ] Integrar con Sentry para alertas
- [ ] Dashboard en Grafana/Datadog
- [ ] Alertas automáticas

---

## 📝 Resumen

| Métrica | Target | Usar Para |
|---------|--------|-----------|
| Uptime | 99.9% | Disponibilidad general |
| Latency p95 | <200ms | Experiencia de usuario |
| Latency p99 | <500ms | Worst-case performance |
| Error Rate | <0.1% | Confiabilidad |
| Rate Limit | <5% | Health check |

**Regla de oro**: Si algún SLO tiene ❌, investiga y arregla antes de hacer deploy.

---

**Nota**: Esta es TAREA 4 de Semana 3.
