-- ============================================================================
-- Row Level Security - Basado en EMAIL (Correcto para este schema)
-- ============================================================================

-- ENABLE RLS
ALTER TABLE player ENABLE ROW LEVEL SECURITY;
ALTER TABLE houses ENABLE ROW LEVEL SECURITY;
ALTER TABLE plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE crops ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PLAYER - Solo datos propios (por email)
-- ============================================================================

CREATE POLICY "Players can view own profile"
ON player FOR SELECT
USING (email = current_setting('request.jwt.claims', true)::jsonb->>'email');

CREATE POLICY "Players can update own profile"
ON player FOR UPDATE
USING (email = current_setting('request.jwt.claims', true)::jsonb->>'email')
WITH CHECK (email = current_setting('request.jwt.claims', true)::jsonb->>'email');

-- ============================================================================
-- HOUSES - Ver propias o disponibles
-- ============================================================================

-- Ver casas disponibles (sin owner)
CREATE POLICY "Anyone can view available houses"
ON houses FOR SELECT
USING (player_id IS NULL);

-- Ver casas propias
CREATE POLICY "Players can view own houses"
ON houses FOR SELECT
USING (player_id IN (
    SELECT id FROM player
    WHERE email = current_setting('request.jwt.claims', true)::jsonb->>'email'
));

-- Comprar casas
CREATE POLICY "Players can purchase houses"
ON houses FOR UPDATE
USING (player_id IS NULL OR player_id IN (
    SELECT id FROM player
    WHERE email = current_setting('request.jwt.claims', true)::jsonb->>'email'
))
WITH CHECK (player_id IN (
    SELECT id FROM player
    WHERE email = current_setting('request.jwt.claims', true)::jsonb->>'email'
));

-- ============================================================================
-- PLOTS - Solo plots de casas propias
-- ============================================================================

CREATE POLICY "Players can view own plots"
ON plots FOR SELECT
USING (house_id IN (
    SELECT h.id FROM houses h
    JOIN player p ON h.player_id = p.id
    WHERE p.email = current_setting('request.jwt.claims', true)::jsonb->>'email'
));

CREATE POLICY "Players can update own plots"
ON plots FOR UPDATE
USING (house_id IN (
    SELECT h.id FROM houses h
    JOIN player p ON h.player_id = p.id
    WHERE p.email = current_setting('request.jwt.claims', true)::jsonb->>'email'
));

-- ============================================================================
-- CROPS - Solo crops de plots propios
-- ============================================================================

CREATE POLICY "Players can view own crops"
ON crops FOR SELECT
USING (plot_id IN (
    SELECT p.id FROM plots p
    JOIN houses h ON p.house_id = h.id
    JOIN player pl ON h.player_id = pl.id
    WHERE pl.email = current_setting('request.jwt.claims', true)::jsonb->>'email'
));

CREATE POLICY "Players can update own crops"
ON crops FOR UPDATE
USING (plot_id IN (
    SELECT p.id FROM plots p
    JOIN houses h ON p.house_id = h.id
    JOIN player pl ON h.player_id = pl.id
    WHERE pl.email = current_setting('request.jwt.claims', true)::jsonb->>'email'
));
