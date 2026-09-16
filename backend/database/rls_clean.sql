-- ENABLE RLS PRIMERO
ALTER TABLE player ENABLE ROW LEVEL SECURITY;
ALTER TABLE houses ENABLE ROW LEVEL SECURITY;
ALTER TABLE plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE crops ENABLE ROW LEVEL SECURITY;

-- PLAYER - Solo datos propios
CREATE POLICY "Players can view own profile"
ON player FOR SELECT
USING (id = auth.uid()::bigint);

CREATE POLICY "Players can update own profile"
ON player FOR UPDATE
USING (id = auth.uid()::bigint)
WITH CHECK (id = auth.uid()::bigint);

-- HOUSES - Ver propias o disponibles
CREATE POLICY "Anyone can view available houses"
ON houses FOR SELECT
USING (player_id IS NULL);

CREATE POLICY "Players can view own houses"
ON houses FOR SELECT
USING (player_id = auth.uid()::bigint);

CREATE POLICY "Players can purchase houses"
ON houses FOR UPDATE
USING (player_id IS NULL OR player_id = auth.uid()::bigint)
WITH CHECK (player_id = auth.uid()::bigint);

-- PLOTS - Solo plots de casas propias
CREATE POLICY "Players can view own plots"
ON plots FOR SELECT
USING (
    house_id IN (
        SELECT id FROM houses
        WHERE player_id = auth.uid()::bigint
    )
);

CREATE POLICY "Players can update own plots"
ON plots FOR UPDATE
USING (
    house_id IN (
        SELECT id FROM houses
        WHERE player_id = auth.uid()::bigint
    )
);

-- CROPS - Solo crops de plots propios
CREATE POLICY "Players can view own crops"
ON crops FOR SELECT
USING (
    plot_id IN (
        SELECT p.id FROM plots p
        JOIN houses h ON p.house_id = h.id
        WHERE h.player_id = auth.uid()::bigint
    )
);

CREATE POLICY "Players can update own crops"
ON crops FOR UPDATE
USING (
    plot_id IN (
        SELECT p.id FROM plots p
        JOIN houses h ON p.house_id = h.id
        WHERE h.player_id = auth.uid()::bigint
    )
);
