-- ============================================================================
-- FIX RLS POLICIES PARA INVENTORY_ITEMS
-- ============================================================================

-- Eliminar política anterior
DROP POLICY IF EXISTS "read_inventory_items" ON inventory_items;

-- Permitir lectura pública
CREATE POLICY "read_inventory_items" ON inventory_items
    FOR SELECT USING (true);

-- Permitir INSERT (backend-managed)
CREATE POLICY "insert_inventory_items" ON inventory_items
    FOR INSERT WITH CHECK (true);

-- Permitir UPDATE (backend-managed)
CREATE POLICY "update_inventory_items" ON inventory_items
    FOR UPDATE USING (true) WITH CHECK (true);

-- Permitir DELETE (backend-managed)
CREATE POLICY "delete_inventory_items" ON inventory_items
    FOR DELETE USING (true);
