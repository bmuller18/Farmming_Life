# 🗺️ Roadmap Futuro - Farming Life

Documento de planeación para fases posteriores a Semana 3.

---

## 📅 SEMANA 3.5: Market (4 Pestañas)

### Objetivos
- Implementar sistema completo de mercado
- 4 mercados independientes con pestañas
- Sistema de oferta/demanda
- Monetización futura con dinero real

### Tareas

#### 1. **🏪 Tienda NPC**
Venta de items fijos por NPC

**Items disponibles:**
- Semillas (todas las variedades)
- Herramientas (pala, regadera, etc)
- Objetos especiales (fertilizante, insecticida, etc)

**Características:**
- Precios fijos por item (no varían)
- Stock ilimitado
- Compra instantánea
- Log de compras en actividad

**Backend:**
- Tabla `npc_shop_items` con precio fijo
- POST `/api/player/<id>/buy-from-npc` 
- GET `/api/npc-shop/items`
- Validación de dinero suficiente

**Frontend:**
- Grid de items con imagen/nombre/precio
- Botón "Comprar" por item
- Confirmación de compra
- Actualizar dinero del jugador

---

#### 2. **🤝 Mercado Jugador**
Compra/venta entre jugadores con sistema de ofertas

**Características:**
- Sistema de OFERTAS (no subastas)
- Comisión 5% en cada transacción
- Historial de precios último 30 días
- Búsqueda/filtros por tipo de cultivo
- Ofertas pendientes de aceptación

**Estructura de Ofertas:**
```
oferta {
  id, seller_id, crop_type_id, quantity, 
  price_per_unit, total_price, 
  comission (5%), status, created_at, expires_at
}
```

**Backend:**
- Tabla `market_listings` (ofertas activas)
- Tabla `market_history` (histórico de transacciones)
- POST `/api/market/create-offer` (vender)
- GET `/api/market/listings` (ofertas disponibles)
- POST `/api/market/accept-offer/<offer_id>` (comprar)
- GET `/api/market/my-offers` (mis ofertas)
- GET `/api/market/price-history/<crop_type_id>` (histórico)

**Frontend:**
- Tab con lista de ofertas activas
- Filtrar por tipo de cultivo
- Detalles: cantidad, precio unitario, precio total, comisión
- Botón "Comprar" para aceptar oferta
- Mi Tab de ofertas creadas (editar/cancelar)
- Gráfico de precios históricos (últimos 30 días)

**Monetización Futura:**
- Comisión 5% va a fondo especial
- Futura conversión a dinero real (premium currency)
- Sistema de billetera dual: dinero juego vs premium

---

#### 3. **📊 Mercado Global**
Precios dinámicos que evolucionan en el tiempo

**Características:**
- Precios base cambian según TIEMPO (no cantidad)
- Se actualiza cada hora o cada día (definir)
- Gráfico de evolución de precios
- Mostrar tendencia (sube/baja/estable)
- Predicción simple de precios futuros

**Sistema de Precios:**
- Base price (configuración)
- Multiplicador por hora/día del juego
- Ciclos de demanda (ej: trigo más caro lunes/viernes)
- Random variance pequeño (±10%)

**Backend:**
- Tabla `market_prices` con histórico
- Cálculo de precios cada hora (cron job)
- GET `/api/market/global-prices`
- GET `/api/market/price-trend/<crop_type_id>`
- GET `/api/market/price-prediction/<crop_type_id>`

**Frontend:**
- Tab con grid de todos los cultivos
- Mostrar: Precio base, precio actual, tendencia
- Gráfico de evolución (24h o 7 días)
- Indicador de tendencia (📈 sube, 📉 baja, ➡️ estable)
- Mejor hora para vender (predicción)

---

#### 4. **⏰ Detalles Técnicos Generales**

**Transacciones:**
- Validar dinero suficiente
- Transferir dinero entre jugadores
- Restar comisión
- Actualizar inventario inmediatamente
- Log en actividad del jugador

**UI/UX:**
- 4 pestañas limpias en la página Market
- Iconos claros para cada mercado
- Confirmaciones antes de comprar
- Animaciones suave de transacciones
- Notificaciones de éxito/error

**Testing:**
- Test de compra NPC
- Test de aceptar oferta (validar comisión)
- Test de histórico de precios
- Test de rechazo sin dinero suficiente

---

## 📅 SEMANA 4: Infraestructura

### Objetivos
- Containerizar la aplicación
- Implementar CI/CD automático
- Automated testing framework
- Preparar para producción

### Tareas
1. **Docker & Docker Compose**
   - Dockerfile para Flask backend
   - Dockerfile para frontend
   - docker-compose.yml para desarrollo
   - Multi-stage build para producción

2. **CI/CD Pipeline (GitHub Actions)**
   - Trigger en push a main
   - Linting automático (pylint/flake8)
   - Unit tests (pytest)
   - Security scanning (bandit)
   - Build Docker images
   - Deploy a staging

3. **Automated Testing**
   - Unit tests para servicios
   - Integration tests con Supabase
   - E2E tests para workflows críticos
   - Coverage reporting (>80%)

4. **Pre-deployment Checks**
   - Database migrations
   - Health checks
   - Readiness probes
   - Security validation

---

## 📅 SEMANA 5: Escalabilidad

### Objetivos
- Optimizar performance
- Reducir latencia
- Soportar más usuarios concurrentes
- Mejorar disponibilidad

### Tareas
1. **Redis Caching**
   - Cache de player data (5 min TTL)
   - Cache de crop prices (1 hora TTL)
   - Cache de house availability
   - Cache warming

2. **Database Optimization**
   - Connection pooling (pgbouncer)
   - Query optimization (EXPLAIN ANALYZE)
   - Read replicas si aplica
   - Backup automation

3. **Load Balancing**
   - Nginx reverse proxy
   - Multiple Flask instances
   - Session affinity si necesario
   - Health check endpoints

4. **Monitoring Avanzado**
   - Prometheus metrics
   - Grafana dashboards
   - Custom alerts (PagerDuty)
   - APM (Application Performance Monitoring)

---

## 📅 SEMANA 6: Analytics

### Objetivos
- Entender comportamiento de usuarios
- Identificar oportunidades de crecimiento
- Optimizar funnel de conversión
- Métricas de negocio

### Tareas
1. **User Behavior Tracking**
   - Event tracking (login, harvest, sell, etc)
   - Session tracking
   - User segmentation
   - Cohort analysis

2. **Funnel Analysis**
   - Registration funnel
   - Monetization funnel
   - Feature adoption funnel
   - Churn analysis

3. **A/B Testing Framework**
   - Feature flag system
   - Experiment tracking
   - Statistical significance testing
   - Results dashboard

4. **Business Metrics Dashboard**
   - DAU (Daily Active Users)
   - ARPU (Average Revenue Per User)
   - LTV (Lifetime Value)
   - Retention curves
   - Growth rate

---

## 📅 SEMANA 7+: Opcionales

### Semana 7: Mobile App
- React Native frontend
- Push notifications
- Offline support
- App store deployment

### Semana 8: Payment Integration
- Stripe/PayPal integration
- In-app purchases
- Subscription billing
- Revenue analytics

### Semana 9: Social Features
- Multiplayer farming
- Leaderboards
- Trading/marketplace
- Chat system

### Semana 10: AI/ML
- Recommendation engine
- Price prediction
- Crop optimization AI
- Chatbot support

---

## 🎯 Estimaciones

| Semana | Tarea | Esfuerzo | Impacto |
|--------|-------|----------|--------|
| 4 | Infraestructura | 40h | Crítico |
| 5 | Escalabilidad | 35h | Alto |
| 6 | Analytics | 30h | Medio |
| 7+ | Opcionales | Variable | Bajo-Alto |

---

## 🚀 Decisión Recomendada

**Start with Semana 4 (Infraestructura)**

Razón: Sin Docker + CI/CD, no puedes hacer deploy con confianza.

---

**Guardado el**: 2026-09-16
**Estado**: Ready para futuro
**Próximo paso**: Semana 4 cuando sea necesario
