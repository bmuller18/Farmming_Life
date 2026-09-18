-- ============================================================================
-- MARKET TABLES
-- ============================================================================

-- 1. NPC SHOP ITEMS TABLE
CREATE TABLE IF NOT EXISTS public.npc_shop_items (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price INTEGER NOT NULL,
    image_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_npc_shop_category ON npc_shop_items(category);

-- Insert sample NPC items
INSERT INTO npc_shop_items (category, name, description, price, image_url) VALUES
-- Semillas
('semilla', 'Trigo', 'Semilla de trigo', 50, '/images/seed_wheat.png'),
('semilla', 'Maíz', 'Semilla de maíz', 60, '/images/seed_corn.png'),
('semilla', 'Zanahoria', 'Semilla de zanahoria', 40, '/images/seed_carrot.png'),
('semilla', 'Fresa', 'Semilla de fresa', 75, '/images/seed_strawberry.png'),

-- Herramientas
('herramienta', 'Pala', 'Herramienta para cavar', 100, '/images/tool_shovel.png'),
('herramienta', 'Regadera', 'Herramienta para regar', 80, '/images/tool_watering_can.png'),
('herramienta', 'Azadón', 'Herramienta para preparar tierra', 120, '/images/tool_hoe.png'),

-- Objetos especiales
('objeto', 'Fertilizante', 'Aumenta la producción de cultivos', 150, '/images/fertilizer.png'),
('objeto', 'Insecticida', 'Protege contra plagas', 200, '/images/pesticide.png'),
('objeto', 'Semilla Dorada', 'Cultivo raro y valioso', 500, '/images/seed_golden.png')
ON CONFLICT DO NOTHING;


-- 2. MARKET LISTINGS TABLE
CREATE TABLE IF NOT EXISTS public.market_listings (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER NOT NULL REFERENCES public.player(id) ON DELETE CASCADE,
    buyer_id INTEGER REFERENCES public.player(id),
    crop_type_id INTEGER NOT NULL REFERENCES public.crop_types(id),
    quantity INTEGER NOT NULL,
    price_per_unit DECIMAL(10, 2) NOT NULL,
    total_price INTEGER NOT NULL,
    commission INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sold_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_market_listings_seller ON market_listings(seller_id);
CREATE INDEX IF NOT EXISTS idx_market_listings_buyer ON market_listings(buyer_id);
CREATE INDEX IF NOT EXISTS idx_market_listings_crop_type ON market_listings(crop_type_id);
CREATE INDEX IF NOT EXISTS idx_market_listings_status ON market_listings(status);
CREATE INDEX IF NOT EXISTS idx_market_listings_created_at ON market_listings(created_at DESC);


-- 3. MARKET HISTORY TABLE
CREATE TABLE IF NOT EXISTS public.market_history (
    id SERIAL PRIMARY KEY,
    seller_id INTEGER NOT NULL REFERENCES public.player(id),
    buyer_id INTEGER NOT NULL REFERENCES public.player(id),
    crop_type_id INTEGER NOT NULL REFERENCES public.crop_types(id),
    quantity INTEGER NOT NULL,
    price_per_unit DECIMAL(10, 2) NOT NULL,
    total_price INTEGER NOT NULL,
    commission INTEGER NOT NULL,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_market_history_seller ON market_history(seller_id);
CREATE INDEX IF NOT EXISTS idx_market_history_buyer ON market_history(buyer_id);
CREATE INDEX IF NOT EXISTS idx_market_history_crop_type ON market_history(crop_type_id);
CREATE INDEX IF NOT EXISTS idx_market_history_transaction_date ON market_history(transaction_date DESC);


-- 4. GLOBAL MARKET PRICES TABLE
CREATE TABLE IF NOT EXISTS public.market_prices (
    id SERIAL PRIMARY KEY,
    crop_type_id INTEGER NOT NULL UNIQUE REFERENCES public.crop_types(id),
    base_price DECIMAL(10, 2) NOT NULL,
    current_price DECIMAL(10, 2) NOT NULL,
    trend VARCHAR(20) DEFAULT 'stable',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_market_prices_crop_type ON market_prices(crop_type_id);

-- Initialize market prices for each crop type
INSERT INTO market_prices (crop_type_id, base_price, current_price, trend)
SELECT id, 100, 100, 'stable' FROM crop_types
ON CONFLICT (crop_type_id) DO NOTHING;


-- ============================================================================
-- ROW LEVEL SECURITY
-- ============================================================================

-- Enable RLS on market_listings
ALTER TABLE market_listings ENABLE ROW LEVEL SECURITY;

-- Players can read all active listings
CREATE POLICY "read_active_listings" ON market_listings
    FOR SELECT USING (status = 'active');

-- Players can create their own listings
CREATE POLICY "create_own_listings" ON market_listings
    FOR INSERT WITH CHECK (seller_id = auth.uid()::int);

-- Players can update their own listings
CREATE POLICY "update_own_listings" ON market_listings
    FOR UPDATE USING (seller_id = auth.uid()::int);

-- Enable RLS on market_history (read-only)
ALTER TABLE market_history ENABLE ROW LEVEL SECURITY;

-- Players can read market history
CREATE POLICY "read_market_history" ON market_history
    FOR SELECT USING (true);

-- Enable RLS on market_prices (read-only)
ALTER TABLE market_prices ENABLE ROW LEVEL SECURITY;

-- Players can read global prices
CREATE POLICY "read_global_prices" ON market_prices
    FOR SELECT USING (true);

-- Enable RLS on npc_shop_items (read-only)
ALTER TABLE npc_shop_items ENABLE ROW LEVEL SECURITY;

-- Everyone can read NPC shop items
CREATE POLICY "read_npc_items" ON npc_shop_items
    FOR SELECT USING (true);
