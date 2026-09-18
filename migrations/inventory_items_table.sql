-- ============================================================================
-- INVENTORY ITEMS TABLE
-- ============================================================================

-- Tabla para almacenar items en el inventario del jugador
CREATE TABLE IF NOT EXISTS public.inventory_items (
    id SERIAL PRIMARY KEY,
    player_id INTEGER NOT NULL REFERENCES public.player(id) ON DELETE CASCADE,
    npc_shop_item_id INTEGER NOT NULL REFERENCES public.npc_shop_items(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    acquired_from VARCHAR(50) NOT NULL,
    acquired_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_inventory_player ON inventory_items(player_id);
CREATE INDEX IF NOT EXISTS idx_inventory_item ON inventory_items(npc_shop_item_id);
CREATE INDEX IF NOT EXISTS idx_inventory_player_item ON inventory_items(player_id, npc_shop_item_id);

-- RLS: Lectura pública (backend-managed)
ALTER TABLE inventory_items ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "read_inventory_items" ON inventory_items;
CREATE POLICY "read_inventory_items" ON inventory_items
    FOR SELECT USING (true);
