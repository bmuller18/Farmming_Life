-- ============================================================================
-- Optimizaciones de PostgreSQL para Farming Life
-- Ejecutar en Supabase SQL Editor
-- ============================================================================

-- 1. ÍNDICES PARA QUERIES FRECUENTES
-- ============================================================================

-- Índice en player.email (usado en login)
CREATE INDEX IF NOT EXISTS idx_player_email ON player(email);

-- Índice en houses.player_id (buscar casas del jugador)
CREATE INDEX IF NOT EXISTS idx_houses_player_id ON houses(player_id);

-- Índice en plots.house_id (obtener plots de una casa)
CREATE INDEX IF NOT EXISTS idx_plots_house_id ON plots(house_id);

-- Índice en crops.player_id (obtener cultivos del jugador)
CREATE INDEX IF NOT EXISTS idx_crops_player_id ON crops(player_id);

-- Índice en crops.plot_id (obtener cultivo de un plot)
CREATE INDEX IF NOT EXISTS idx_crops_plot_id ON crops(plot_id);

-- Índice en crops.harvested_at (filtrar cosechados)
CREATE INDEX IF NOT EXISTS idx_crops_harvested_at ON crops(harvested_at);

-- Índice compuesto para queries de inventario
CREATE INDEX IF NOT EXISTS idx_crops_inventory
ON crops(player_id, crop_type_id, harvested_at, yield_amount);

-- Índice para queries de disponibilidad de casas
CREATE INDEX IF NOT EXISTS idx_houses_available
ON houses(player_id) WHERE player_id IS NULL;


-- 2. VISTAS PARA OPTIMIZAR QUERIES FRECUENTES
-- ============================================================================

-- Vista: Información de jugador con totales
CREATE OR REPLACE VIEW player_stats AS
SELECT
    p.id,
    p.name,
    p.email,
    p.money,
    p.level,
    p.created_at,
    COUNT(DISTINCT h.id) as house_count,
    COUNT(DISTINCT pl.id) as total_plots,
    COUNT(DISTINCT c.id) as total_crops
FROM player p
LEFT JOIN houses h ON h.player_id = p.id
LEFT JOIN plots pl ON pl.house_id = h.id
LEFT JOIN crops c ON c.player_id = p.id
GROUP BY p.id;


-- Vista: Inventario agrupado por tipo
CREATE OR REPLACE VIEW player_inventory AS
SELECT
    p.id as player_id,
    ct.id as crop_type_id,
    ct.name as crop_name,
    ct.price as crop_price,
    COUNT(*) as crop_count,
    SUM(c.yield_amount) as total_yield
FROM player p
JOIN crops c ON c.player_id = p.id AND c.harvested_at IS NOT NULL
JOIN crop_type ct ON ct.id = c.crop_type_id
WHERE c.yield_amount > 0
GROUP BY p.id, ct.id, ct.name, ct.price;


-- Vista: Casas del jugador con stats
CREATE OR REPLACE VIEW player_houses_view AS
SELECT
    h.id,
    h.name,
    h.price,
    h.plot_count,
    h.player_id,
    COUNT(pl.id) as available_plots,
    COUNT(c.id) as growing_crops
FROM houses h
LEFT JOIN plots pl ON pl.house_id = h.id AND pl.status = 'empty'
LEFT JOIN crops c ON c.plot_id IN (
    SELECT id FROM plots WHERE house_id = h.id
) AND c.harvested_at IS NULL
GROUP BY h.id, h.name, h.price, h.plot_count, h.player_id;


-- 3. ESTADÍSTICAS Y ANÁLISIS
-- ============================================================================

-- Analizar usage de índices
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
-- FROM pg_stat_user_indexes
-- ORDER BY idx_scan DESC;

-- Query lenta detection (requiere log_min_duration_statement)
-- SELECT query, calls, mean_exec_time, total_exec_time
-- FROM pg_stat_statements
-- ORDER BY mean_exec_time DESC
-- LIMIT 10;
