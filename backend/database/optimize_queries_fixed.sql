-- ============================================================================
-- ÍNDICES OPTIMIZADOS PARA FARMING LIFE (Schema Real)
-- Ejecutar en Supabase SQL Editor UNO POR UNO
-- ============================================================================

-- 1. Player indexes
CREATE INDEX IF NOT EXISTS idx_player_email ON player(email);

-- 2. Houses indexes
CREATE INDEX IF NOT EXISTS idx_houses_player_id ON houses(player_id);
CREATE INDEX IF NOT EXISTS idx_houses_available ON houses(player_id) WHERE player_id IS NULL;

-- 3. Plots indexes
CREATE INDEX IF NOT EXISTS idx_plots_house_id ON plots(house_id);

-- 4. Crops indexes
CREATE INDEX IF NOT EXISTS idx_crops_plot_id ON crops(plot_id);
CREATE INDEX IF NOT EXISTS idx_crops_crop_type_id ON crops(crop_type_id);
CREATE INDEX IF NOT EXISTS idx_crops_harvested_at ON crops(harvested_at);

-- 5. Composite index para inventario (crops que se pueden vender)
CREATE INDEX IF NOT EXISTS idx_crops_inventory
ON crops(plot_id, crop_type_id, harvested_at, yield_amount);

-- 6. Index para ready crops (listos para cosechar)
CREATE INDEX IF NOT EXISTS idx_crops_ready
ON crops(ready_at) WHERE harvested_at IS NULL;

-- ============================================================================
-- VISTAS ÚTILES (Opcional pero recomendado)
-- ============================================================================

-- Vista: Inventario del jugador agrupado por tipo
CREATE OR REPLACE VIEW player_inventory_view AS
SELECT
    h.player_id,
    c.crop_type_id,
    COUNT(*) as crop_count,
    SUM(c.yield_amount) as total_yield,
    MAX(c.harvested_at) as last_harvest
FROM crops c
JOIN plots p ON c.plot_id = p.id
JOIN houses h ON p.house_id = h.id
WHERE c.harvested_at IS NOT NULL
  AND c.yield_amount > 0
GROUP BY h.player_id, c.crop_type_id;

-- Vista: Casas del jugador con info de plots
CREATE OR REPLACE VIEW player_houses_info AS
SELECT
    h.id,
    h.player_id,
    h.name,
    h.price,
    h.plot_count,
    COUNT(p.id) as actual_plots,
    COUNT(CASE WHEN EXISTS(
        SELECT 1 FROM crops c WHERE c.plot_id = p.id AND c.harvested_at IS NULL
    ) THEN 1 END) as occupied_plots
FROM houses h
LEFT JOIN plots p ON p.house_id = h.id
GROUP BY h.id, h.player_id, h.name, h.price, h.plot_count;

-- Vista: Cultivos listos para cosechar
CREATE OR REPLACE VIEW ready_to_harvest AS
SELECT
    c.id,
    c.plot_id,
    p.house_id,
    h.player_id,
    c.crop_type_id,
    c.ready_at,
    c.yield_amount
FROM crops c
JOIN plots p ON c.plot_id = p.id
JOIN houses h ON p.house_id = h.id
WHERE c.harvested_at IS NULL
  AND c.ready_at <= NOW();

-- ============================================================================
-- VERIFICACIÓN
-- ============================================================================

-- Ver todos los índices creados:
-- SELECT schemaname, tablename, indexname
-- FROM pg_indexes
-- WHERE schemaname = 'public'
-- ORDER BY tablename, indexname;

-- Ver estadísticas de uso:
-- SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read
-- FROM pg_stat_user_indexes
-- ORDER BY idx_scan DESC;
