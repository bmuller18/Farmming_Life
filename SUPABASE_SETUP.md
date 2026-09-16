# 🚀 Supabase Setup - Instrucciones Finales

## ✅ Paso 1: Ejecutar Stored Procedures

Abre Supabase SQL Editor y ejecuta **UNO POR UNO**:

### 1.1 buy_house_atomic
Archivo: `backend/database/stored_procedures_clean.sql`

```sql
CREATE OR REPLACE FUNCTION buy_house_atomic(
    p_player_id INT,
    p_house_id INT
) RETURNS JSON AS $$
...
```

### 1.2 sell_crops_batch_atomic
Archivo: `backend/database/function2_sell_crops.sql`

### 1.3 buy_seeds_atomic
Archivo: `backend/database/function3_buy_seeds.sql`

---

## ✅ Paso 2: Crear Índices (NUEVO SCHEMA)

Archivo: `backend/database/optimize_queries_fixed.sql`

Ejecuta **TODOS estos índices** (son rápidos):

```sql
-- Player
CREATE INDEX IF NOT EXISTS idx_player_email ON player(email);

-- Houses
CREATE INDEX IF NOT EXISTS idx_houses_player_id ON houses(player_id);
CREATE INDEX IF NOT EXISTS idx_houses_available ON houses(player_id) WHERE player_id IS NULL;

-- Plots
CREATE INDEX IF NOT EXISTS idx_plots_house_id ON plots(house_id);

-- Crops
CREATE INDEX IF NOT EXISTS idx_crops_plot_id ON crops(plot_id);
CREATE INDEX IF NOT EXISTS idx_crops_crop_type_id ON crops(crop_type_id);
CREATE INDEX IF NOT EXISTS idx_crops_harvested_at ON crops(harvested_at);
CREATE INDEX IF NOT EXISTS idx_crops_inventory ON crops(plot_id, crop_type_id, harvested_at, yield_amount);
CREATE INDEX IF NOT EXISTS idx_crops_ready ON crops(ready_at) WHERE harvested_at IS NULL;
```

---

## ✅ Paso 3: Crear Vistas

Mismo archivo (`optimize_queries_fixed.sql`):

```sql
CREATE OR REPLACE VIEW player_inventory_view AS ...
CREATE OR REPLACE VIEW player_houses_info AS ...
CREATE OR REPLACE VIEW ready_to_harvest AS ...
```

---

## ✅ Paso 4: Row Level Security (RLS)

Archivo: `backend/database/rls_policies_fixed.sql`

Ejecuta **UNO POR UNO** (o en bloque):

```sql
-- ENABLE RLS
ALTER TABLE player ENABLE ROW LEVEL SECURITY;
ALTER TABLE houses ENABLE ROW LEVEL SECURITY;
ALTER TABLE plots ENABLE ROW LEVEL SECURITY;
ALTER TABLE crops ENABLE ROW LEVEL SECURITY;

-- POLICIES
CREATE POLICY "Players can view own profile" ON player FOR SELECT ...
-- ... (más policies)
```

---

## 🧪 Verificación

### Verificar Índices:
```sql
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Debe mostrar 9 índices nuevos
```

### Verificar RLS:
```sql
SELECT tablename, rowsecurity FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename IN ('player', 'houses', 'plots', 'crops');

-- Debe mostrar rowsecurity = true para todas
```

### Verificar Vistas:
```sql
SELECT table_name FROM information_schema.views 
WHERE table_schema = 'public';

-- Debe mostrar 3 vistas nuevas
```

---

## 📋 Orden de Ejecución

1. ✅ Stored Procedures (3 funciones)
2. ✅ Índices (9 índices)
3. ✅ Vistas (3 vistas)
4. ✅ RLS Policies (7 policies)

**Total**: ~20 minutos

---

## ⚠️ Si algo falla

### Error: Column not found
- Verifica el esquema de tu tabla
- Ejecuta:
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'XXX';
```

### Error: Policy already exists
- Ejecuta primero:
```sql
DROP POLICY IF EXISTS "policy_name" ON table_name;
```

### Stored procedure no funciona
- Verifica que la función se creó:
```sql
SELECT routine_name FROM information_schema.routines 
WHERE routine_schema = 'public' AND routine_name LIKE '%atomic';
```

---

## 🎯 Próximos Pasos

Una vez completado:

```bash
# 1. Verificar config
python backend/verify_config.py

# 2. Ejecutar tests
python backend/tests_security.py

# 3. Iniciar servidor
python backend/app.py
```

---

## 📊 Schema Final

```
player (8 columnas)
├─ id, name, money, level
├─ email, password_hash
└─ created_at, updated_at

houses (7 columnas)
├─ id, player_id, name, price, plot_count
├─ created_at, updated_at
└─ INDEX: player_id, available

plots (5 columnas)
├─ id, house_id, name
├─ created_at, updated_at
└─ INDEX: house_id

crops (9 columnas)
├─ id, plot_id, crop_type_id
├─ planted_at, ready_at, harvested_at
├─ yield_amount
├─ created_at, updated_at
└─ INDEX: plot_id, crop_type_id, harvested_at, ready
```

---

✅ Ready to go! 🚀
