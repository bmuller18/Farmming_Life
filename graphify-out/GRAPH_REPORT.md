# Graph Report - New Folder  (2026-09-17)

## Corpus Check
- Corpus is ~32,883 words - fits in a single context window. You may not need a graph.

## Summary
- 556 nodes · 991 edges · 40 communities (32 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 23 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- backend_repositories & house_service.py
- script.js & buyHouse()
- openapi_docs.py & AuthLogin
- Any & logging_config.py
- atexit & setup_stored_procedures_psycopg
- create_jwt_token() & Create a JWT token 
- Test 3: Obtener CSRF token & Test 4: Req
- crop_repository.py & get_active_crop_by_
- auth_middleware.py & extract_token_from_
- Retornar dashboard completo de SLOs & Re
- rate_limit.py & create_limiter()
- get_crop_types() & get_house_plots()
- player_repository.py & create_player()
- Gestiona sesiones activas y blacklist de
- plot_repository.py & create_starting_plo
- backend/app.py & get_available_houses()
- idempotency.py & cache_response()
- schemas.py & BuyHouseRequest
- sentry_config.py & capture_exception()
- get_csrf_token() & Obtener CSRF token pa
- session_manager.py & Session Manager - G
- buy_house() & Sell multiple crops of the
- harvest_crop() & plant_crop()
- correlation_id.py & get_correlation_id()
- house_repository.py & buy_house()
- buy_seeds_endpoint() & get_crop_type_pri
- transaction_repository.py & buy_house_at
- crop_type_repository.py & get_all_crop_t
- price_repository.py & get_all_prices()
- init_slo_monitoring() & after_request()
- dev.sh & dev.sh script
- get_balance() & Get player's current mon
- init_correlation_id() & after_request()
- init_request_logging() & after_request()
- get_harvested_crops_by_player() & Get al
- CropCard & ._harvest_click()

## God Nodes (most connected - your core abstractions)
1. `get_supabase_client()` - 47 edges
2. `fetchWithAuth()` - 15 edges
3. `require_player_match()` - 14 edges
4. `TestSecurityFeatures` - 14 edges
5. `SecurityTester` - 14 edges
6. `SLOMetrics` - 13 edges
7. `PlayerPage` - 13 edges
8. `require_csrf_protection()` - 11 edges
9. `require_auth()` - 10 edges
10. `SessionManager` - 10 edges

## Surprising Connections (you probably didn't know these)
- `register()` --uses--> `RegisterRequest`  [INFERRED]
  backend/app.py → backend/schemas.py
- `login()` --uses--> `LoginRequest`  [INFERRED]
  backend/app.py → backend/schemas.py
- `buy_house()` --uses--> `BuyHouseRequest`  [INFERRED]
  backend/app.py → backend/schemas.py
- `plant_crop()` --uses--> `PlantCropRequest`  [INFERRED]
  backend/app.py → backend/schemas.py
- `sell_batch()` --uses--> `SellCropsRequest`  [INFERRED]
  backend/app.py → backend/schemas.py

## Import Cycles
- None detected.

## Communities (40 total, 8 thin omitted)

### Community 0 - "backend_repositories & house_service.py"
Cohesion: 0.09
Nodes (19): backend_repositories, get_houses_by_player(), Get all houses owned by a player., get_player(), get_player_by_name(), Get a player by name., get_plots_by_house(), Get all plots belonging to a house. (+11 more)

### Community 1 - "script.js & buyHouse()"
Cohesion: 0.15
Nodes (28): buyHouse(), closePlantModal(), closeSellModal(), cropTypes, fetchCsrfToken(), fetchWithAuth(), handleLogin(), handleRegister() (+20 more)

### Community 2 - "openapi_docs.py & AuthLogin"
Cohesion: 0.10
Nodes (23): AuthLogin, AuthRegister, AvailableHouses, BuyHouse, PlayerInfo, route, OpenAPI/Swagger Documentation para Farming Life Documentación automática de…, Registro de nuevo jugador (+15 more)

### Community 3 - "Any & logging_config.py"
Cohesion: 0.08
Nodes (20): Any, get_logger(), log_buy_house(), log_error(), log_login(), log_sell_crops(), LogContext, Logging Estructurado para Farming Life Uso: from backend.logging_config import… (+12 more)

### Community 4 - "atexit & setup_stored_procedures_psycopg"
Cohesion: 0.10
Nodes (23): atexit, Script para crear Stored Procedures usando psycopg2 Esto conecta directamente a…, Crea los stored procedures en Supabase usando conexión directa, setup_stored_procedures(), Tests de Seguridad para Farming Life Ejecutar: pytest backend/tests_security.py…, Verificar configuración de seguridad Ejecutar: python backend/verify_config.py, Verifica que todas las variables de entorno requeridas estén configuradas, verify_config() (+15 more)

### Community 5 - "create_jwt_token() & Create a JWT token "
Cohesion: 0.11
Nodes (15): create_jwt_token(), Create a JWT token for a player., ❌ Email inválido debe retornar 400, ❌ Contraseña débil en registro debe retornar 400, ❌ house_id negativo debe retornar 400, Tests de seguridad para validar autenticación y protecciones, ⏱️ Rate limit en login debe prevenir múltiples intentos, 🔒 Comprar casa sin JWT debe retornar 401 (+7 more)

### Community 6 - "Test 3: Obtener CSRF token & Test 4: Req"
Cohesion: 0.14
Nodes (13): Test 3: Obtener CSRF token, Test 4: Request con cookie (sin CSRF), Test 5: POST sin CSRF token (debería fallar), Test 6: POST con CSRF token (debería aceptar), Test 7: Logout invalida token, Test 8: Token en blacklist tras logout, Imprimir resultado de test, Test 9: CSRF token inválido (+5 more)

### Community 7 - "crop_repository.py & get_active_crop_by_"
Cohesion: 0.11
Nodes (22): get_active_crop_by_plot(), get_crops_by_plot(), harvest_crop(), is_crop_ready(), plant_crop(), Check if a crop is ready to harvest., Get the currently active crop in a plot (not harvested)., Plant a new crop in a plot. (+14 more)

### Community 8 - "auth_middleware.py & extract_token_from_"
Cohesion: 0.13
Nodes (21): extract_token_from_header(), extract_token_from_request(), Autenticación con JWT - Middleware y decoradores, Extrae JWT de cookie HttpOnly o Authorization header, [DEPRECATED] Extrae JWT del header Authorization: Bearer <token> Mantener para…, Decorador para endpoints que requieren autenticación, Valida que el player_id en la URL coincida con el token JWT, require_auth() (+13 more)

### Community 9 - "Retornar dashboard completo de SLOs & Re"
Cohesion: 0.12
Nodes (11): Retornar dashboard completo de SLOs, Recopila métricas de SLO en tiempo real, Registrar una request completada, Registrar un período de downtime, Porcentaje de disponibilidad, Porcentaje de errores, Latencia p95 (95avo percentil), Latencia p99 (99avo percentil) (+3 more)

### Community 10 - "rate_limit.py & create_limiter()"
Cohesion: 0.11
Nodes (16): create_limiter(), rate_limit_moderate(), rate_limit_permissive(), rate_limit_strict(), decorator(), Rate Limiting - Protección contra DDoS, Crea y configura Flask-Limiter, Configura límites específicos por endpoint (+8 more)

### Community 11 - "get_crop_types() & get_house_plots()"
Cohesion: 0.12
Nodes (17): get_crop_types(), get_house_plots(), get_inventory(), get_player_endpoint(), get_player_houses(), get_plot_crop(), health_check(), logout() (+9 more)

### Community 12 - "player_repository.py & create_player()"
Cohesion: 0.18
Nodes (13): create_player(), get_player_by_id(), get_player_by_name(), Get a player by name., create_new_player(), Create a new player with default starting values., Script para crear Stored Procedures en Supabase Ejecutar: python…, Crea los stored procedures en Supabase (+5 more)

### Community 13 - "Gestiona sesiones activas y blacklist de"
Cohesion: 0.12
Nodes (9): Gestiona sesiones activas y blacklist de tokens, Registrar sesión activa (para auditoría), Agregar token a blacklist (logout), Verificar si token está en blacklist, Logout de jugador - invalidar token, Obtener sesiones activas del jugador, Limpiar tokens expirados de la blacklist, Estadísticas de sesiones (+1 more)

### Community 14 - "plot_repository.py & create_starting_plo"
Cohesion: 0.17
Nodes (14): create_starting_plots(), get_plots_by_house(), get_plots_by_player(), Get all plots belonging to a player (through houses)., Get all plots belonging to a house., Create the default number of plots for a house based on its plot_count., Add or subtract money from a player., update_player_money() (+6 more)

### Community 15 - "backend/app.py & get_available_houses()"
Cohesion: 0.17
Nodes (14): get_available_houses(), get_prices(), internal_error(), login(), not_found(), Farm RPG - REST API Backend, Get houses available for purchase (not owned by player)., backend_middleware (+6 more)

### Community 16 - "idempotency.py & cache_response()"
Cohesion: 0.16
Nodes (14): cache_response(), generate_idempotency_key(), get_cached_response(), get_idempotency_key(), Idempotency Keys - Prevenir duplicados en operaciones Uso:…, Extrae Idempotency-Key del header, Cachea respuesta de operación idempotente, Obtiene respuesta cacheada si existe (+6 more)

### Community 17 - "schemas.py & BuyHouseRequest"
Cohesion: 0.25
Nodes (13): BuyHouseRequest, BuySeedsRequest, Config, ErrorResponse, LoginRequest, PlantCropRequest, Validación de datos con Pydantic, RegisterRequest (+5 more)

### Community 18 - "sentry_config.py & capture_exception()"
Cohesion: 0.15
Nodes (12): capture_exception(), capture_message(), init_sentry(), Sentry Integration para Error Tracking centralizado Captura, agrupa y rastrea…, Inicializar Sentry para captura de errores, Configurar contexto del usuario para errores posteriores Útil para…, Capturar excepción manualmente Uso: try: risky_operation() except Exception as…, Capturar mensaje personalizado Niveles: debug, info, warning, error, fatal Uso:… (+4 more)

### Community 19 - "get_csrf_token() & Obtener CSRF token pa"
Cohesion: 0.20
Nodes (8): get_csrf_token(), Obtener CSRF token para operaciones POST/PUT/DELETE, CSRFTokenManager, Genera y valida CSRF tokens, Generar nuevo CSRF token, Limpiar tokens expirados (llamar periódicamente), Obtener CSRF token del request (header o form), decorated_function()

### Community 20 - "session_manager.py & Session Manager - G"
Cohesion: 0.20
Nodes (8): Session Manager - Gestión de sesiones y logout Token blacklist para invalidar…, SLO Monitoring - Objetivos de Nivel de Servicio Rastrea disponibilidad,…, collections, datetime, json, requests, Test Suite para Sprint 1 - Seguridad Crítica Valida: HttpOnly cookies, CSRF,…, time

### Community 21 - "buy_house() & Sell multiple crops of the"
Cohesion: 0.18
Nodes (11): buy_house(), Sell multiple crops of the same type at once., Sell a harvested crop., Register a new player., register(), sell_batch(), sell_crop_endpoint(), SellSingleCropRequest (+3 more)

### Community 22 - "harvest_crop() & plant_crop()"
Cohesion: 0.22
Nodes (8): harvest_crop(), plant_crop(), Plant a crop in a plot., CSRF Token Management - Protección contra Cross-Site Request Forgery, Decorator para requerir CSRF token en POST/PUT/DELETE, require_csrf_protection(), Security modules for Farming Life, secrets

### Community 23 - "correlation_id.py & get_correlation_id()"
Cohesion: 0.24
Nodes (8): get_correlation_id(), log_with_correlation(), Correlation IDs - Rastreo de requests a través del sistema Permite seguir una…, Obtener Correlation ID actual, Helper para loguear con Correlation ID automático, Request Logging Middleware Mide duración de requests y asigna IDs únicos, flask, uuid

### Community 24 - "house_repository.py & buy_house()"
Cohesion: 0.25
Nodes (8): buy_house(), get_available_houses_for_purchase(), get_houses_by_player(), purchase_house(), Purchase a house using the RPC function., Purchase a house by updating its owner., Get all houses owned by a player., Get houses available for purchase (not owned by this player).

### Community 25 - "buy_seeds_endpoint() & get_crop_type_pri"
Cohesion: 0.25
Nodes (8): buy_seeds_endpoint(), get_crop_type_price(), Get price for a specific crop type., Buy seeds for planting., buy_seeds(), get_seed_price(), Buy seeds for a crop type., Get the price of seeds for a crop type.

### Community 26 - "transaction_repository.py & buy_house_at"
Cohesion: 0.25
Nodes (7): buy_house_atomic(), buy_seeds_atomic(), Transacciones atómicas usando Stored Procedures en Supabase, Vender múltiples crops de forma ATÓMICA. Previene race conditions en dinero y…, Comprar semillas de forma ATÓMICA. Previene race conditions en dinero., Comprar casa de forma ATÓMICA usando stored procedure. Previene race conditions…, sell_crops_batch_atomic()

### Community 27 - "crop_type_repository.py & get_all_crop_t"
Cohesion: 0.29
Nodes (6): get_all_crop_types(), get_crop_type_by_id(), get_crop_type_by_name(), Get a crop type by ID., Get a crop type by name., Get all available crop types.

### Community 28 - "price_repository.py & get_all_prices()"
Cohesion: 0.33
Nodes (5): get_all_prices(), get_player_money(), get_price_by_crop_type(), Get price information for a crop type., Get player's current money.

### Community 30 - "dev.sh & dev.sh script"
Cohesion: 0.40
Nodes (3): dev.sh script, env_bin_activate, start.sh script

### Community 31 - "get_balance() & Get player's current mon"
Cohesion: 0.50
Nodes (4): get_balance(), Get player's current money balance., get_player_balance(), Get player's current money balance.

### Community 34 - "get_harvested_crops_by_player() & Get al"
Cohesion: 0.50
Nodes (4): get_harvested_crops_by_player(), Get all harvested crops (inventory) for a player., get_harvested_crops(), Get all harvested crops (inventory) for a player.

## Knowledge Gaps
- **5 isolated node(s):** `dev.sh script`, `cropTypes`, `prices`, `harvestingCrops`, `start.sh script`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 245 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_supabase_client()` connect `player_repository.py & create_player()` to `get_harvested_crops_by_player() & Get al`, `crop_repository.py & get_active_crop_by_`, `auth_middleware.py & extract_token_from_`, `plot_repository.py & create_starting_plo`, `backend/app.py & get_available_houses()`, `house_repository.py & buy_house()`, `transaction_repository.py & buy_house_at`, `crop_type_repository.py & get_all_crop_t`, `price_repository.py & get_all_prices()`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `SecurityTester` connect `Test 3: Obtener CSRF token & Test 4: Req` to `session_manager.py & Session Manager - G`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `SLOMetrics` connect `Retornar dashboard completo de SLOs & Re` to `session_manager.py & Session Manager - G`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **What connects `dev.sh script`, `cropTypes`, `prices` to the rest of the system?**
  _5 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `backend_repositories & house_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08527131782945736 - nodes in this community are weakly interconnected._
- **Should `openapi_docs.py & AuthLogin` be split into smaller, more focused modules?**
  _Cohesion score 0.09655172413793103 - nodes in this community are weakly interconnected._
- **Should `Any & logging_config.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07936507936507936 - nodes in this community are weakly interconnected._