-- ============================================================================
-- RLS POLICIES PARA MARKET
-- ============================================================================

-- 1. NPC SHOP ITEMS - Lectura pública (todos pueden ver)
ALTER TABLE npc_shop_items ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "read_npc_items" ON npc_shop_items;
CREATE POLICY "read_npc_items" ON npc_shop_items
    FOR SELECT USING (true);

-- 2. MARKET LISTINGS - Lectura pública (activas), escritura del propietario
ALTER TABLE market_listings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "read_active_listings" ON market_listings;
CREATE POLICY "read_active_listings" ON market_listings
    FOR SELECT USING (status = 'active');

-- 3. MARKET HISTORY - Lectura pública
ALTER TABLE market_history ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "read_market_history" ON market_history;
CREATE POLICY "read_market_history" ON market_history
    FOR SELECT USING (true);

-- 4. MARKET PRICES - Lectura pública
ALTER TABLE market_prices ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "read_global_prices" ON market_prices;
CREATE POLICY "read_global_prices" ON market_prices
    FOR SELECT USING (true);
