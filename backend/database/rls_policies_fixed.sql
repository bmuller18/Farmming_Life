-- ============================================================================
-- Row Level Security (RLS) - Schema Real
-- EJECUTAR EN SUPABASE (con autenticación habilitada)
-- ============================================================================

-- ENABLE RLS EN TABLAS CRÍTICAS
ALTER TABLE player ENABLE ROW LEVEL SECURITY;
ALTER TABLE houses ENABLE ROW LEVEL SECURITY;
ALTER TABLE plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE crops ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 1. PLAYER TABLE - Solo ver datos propios
-- ============================================================================

CREATE POLICY "Players can view own profile"
ON player FOR SELECT
USING (id = auth.uid()::bigint);

CREATE POLICY "Players can update own profile"
ON player FOR UPDATE
USING (id = auth.uid()::bigint)
WITH CHECK (id = auth.uid()::bigint);

-- ============================================================================
-- 2. HOUSES TABLE - Ver propias o disponibles
-- ============================================================================

-- Ver casas disponibles (sin owner)
CREATE POLICY "Anyone can view available houses"
ON houses FOR SELECT
USING (player_id IS NULL);

-- Ver casas propias
CREATE POLICY "Players can view own houses"
ON houses FOR SELECT
USING (player_id = auth.uid()::bigint);

-- Actualizar casas propias (compra)
CREATE POLICY "Players can purchase available houses"
ON houses FOR UPDATE
USING (player_id IS NULL OR player_id = auth.uid()::bigint)
WITH CHECK (player_id = auth.uid()::bigint);

-- ============================================================================
-- 3. PLOTS TABLE - Solo plots de casas propias
-- ============================================================================

-- Ver plots propios
CREATE POLICY "Players can view own plots"
ON plots FOR SELECT
USING (
    house_id IN (
        SELECT id FROM houses
        WHERE player_id = auth.uid()::bigint
    )
);

-- Actualizar plots propios
CREATE POLICY "Players can update own plots"
ON plots FOR UPDATE
USING (
    house_id IN (
        SELECT id FROM houses
        WHERE player_id = auth.uid()::bigint
    )
);

-- ============================================================================
-- 4. CROPS TABLE - Solo crops de plots propios
-- ============================================================================

-- Ver crops propios (a través de plots y houses)
CREATE POLICY "Players can view own crops"
ON crops FOR SELECT
USING (
    plot_id IN (
        SELECT p.id FROM plots p
        JOIN houses h ON p.house_id = h.id
        WHERE h.player_id = auth.uid()::bigint
    )
);

-- Actualizar crops propios
CREATE POLICY "Players can update own crops"
ON crops FOR UPDATE
USING (
    plot_id IN (
        SELECT p.id FROM plots p
        JOIN houses h ON p.house_id = h.id
        WHERE h.player_id = auth.uid()::bigint
    )
);

-- ============================================================================
-- VERIFICAR RLS
-- ============================================================================

-- Ver RLS habilitado:
-- SELECT tablename, rowsecurity FROM pg_tables
-- WHERE schemaname = 'public' AND tablename IN ('player', 'houses', 'plots', 'crops');

-- Ver policies:
-- SELECT schemaname, tablename, policyname, qual
-- FROM pg_policies
-- WHERE schemaname = 'public'
-- ORDER BY tablename;
