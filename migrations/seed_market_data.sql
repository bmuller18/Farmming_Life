-- ============================================================================
-- SEED DATA PARA MARKET
-- ============================================================================

-- Limpiar datos previos (opcional)
TRUNCATE TABLE npc_shop_items CASCADE;

-- Insertar items de la tienda NPC
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
('objeto', 'Semilla Dorada', 'Cultivo raro y valioso', 500, '/images/seed_golden.png');

-- Verificar que se insertaron
SELECT COUNT(*) as "Items NPC creados" FROM npc_shop_items;

-- Inicializar precios globales si crop_types existen
INSERT INTO market_prices (crop_type_id, base_price, current_price, trend)
SELECT id, 100.00, 100.00, 'stable' FROM crop_types
ON CONFLICT (crop_type_id) DO NOTHING;

-- Verificar precios
SELECT COUNT(*) as "Precios globales inicializados" FROM market_prices;
