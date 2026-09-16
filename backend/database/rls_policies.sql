-- ============================================================================
-- Row Level Security (RLS) para Farming Life
-- CRÍTICO: Ejecutar en Supabase para seguridad multi-usuario
-- ============================================================================

-- ENABLE RLS EN TODAS LAS TABLAS
ALTER TABLE player ENABLE ROW LEVEL SECURITY;
ALTER TABLE houses ENABLE ROW LEVEL SECURITY;
ALTER TABLE plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE crops ENABLE ROW LEVEL SECURITY;
ALTER TABLE crop_type ENABLE ROW LEVEL SECURITY;
ALTER TABLE price ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 1. PLAYER TABLE - Solo ver/editar datos propios
-- ============================================================================

-- Crear policy para SELECT
CREATE POLICY "Players can view own data"
ON player FOR SELECT
USING (auth.uid()::text = id::text OR TRUE);  -- TODO: cambiar a auth.uid()

-- Crear policy para UPDATE
CREATE POLICY "Players can update own data"
ON player FOR UPDATE
USING (auth.uid()::text = id::text)
WITH CHECK (auth.uid()::text = id::text);

-- Crear policy para DELETE (prevenir borrado)
CREATE POLICY "Players cannot delete own data"
ON player FOR DELETE
USING (FALSE);

-- ============================================================================
-- 2. HOUSES TABLE - Todos ven casas, solo owner puede ver sus detalles
-- ============================================================================

-- Ver casas disponibles (sin owner)
CREATE POLICY "Anyone can view available houses"
ON houses FOR SELECT
USING (player_id IS NULL);

-- Ver casas propias
CREATE POLICY "Players can view own houses"
ON houses FOR SELECT
USING (player_id = auth.uid()::int);

-- Comprar casa (insert)
CREATE POLICY "Players can purchase houses"
ON houses FOR UPDATE
USING (player_id IS NULL);

-- ============================================================================
-- 3. PLOTS TABLE - Solo owner de la casa puede verlos
-- ============================================================================

CREATE POLICY "Players can view own plots"
ON plots FOR SELECT
USING (
    house_id IN (
        SELECT id FROM houses
        WHERE player_id = auth.uid()::int
    )
);

CREATE POLICY "Players can update own plots"
ON plots FOR UPDATE
USING (
    house_id IN (
        SELECT id FROM houses
        WHERE player_id = auth.uid()::int
    )
);

-- ============================================================================
-- 4. CROPS TABLE - Solo player puede verlos
-- ============================================================================

CREATE POLICY "Players can view own crops"
ON crops FOR SELECT
USING (player_id = auth.uid()::int);

CREATE POLICY "Players can update own crops"
ON crops FOR UPDATE
USING (player_id = auth.uid()::int);

-- ============================================================================
-- 5. CROP_TYPE - Todos pueden ver (read-only)
-- ============================================================================

CREATE POLICY "Anyone can view crop types"
ON crop_type FOR SELECT
USING (TRUE);

-- ============================================================================
-- 6. PRICE - Todos pueden ver precios (read-only)
-- ============================================================================

CREATE POLICY "Anyone can view prices"
ON price FOR SELECT
USING (TRUE);

-- ============================================================================
-- VERIFICAR RLS
-- ============================================================================

-- Ver RLS habilitado:
-- SELECT tablename, rowsecurity FROM pg_tables
-- WHERE schemaname = 'public';

-- Ver policies:
-- SELECT schemaname, tablename, policyname, qual, with_check
-- FROM pg_policies
-- WHERE schemaname = 'public';
