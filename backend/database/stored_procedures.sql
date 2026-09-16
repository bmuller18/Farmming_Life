-- ============================================================================
-- Stored Procedures para Transacciones Atómicas en Supabase
-- Ejecutar estos queries en Supabase SQL Editor
-- ============================================================================

-- 1. COMPRAR CASA (Atómico)
CREATE OR REPLACE FUNCTION buy_house_atomic(
    p_player_id INT,
    p_house_id INT
) RETURNS JSON AS $$
DECLARE
    v_house_price NUMERIC;
    v_player_money NUMERIC;
    v_result JSON;
BEGIN
    -- Bloquear player para evitar race conditions
    SELECT money INTO v_player_money
    FROM player
    WHERE id = p_player_id
    FOR UPDATE;

    IF v_player_money IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Player not found', 'success', false);
    END IF;

    -- Obtener precio de la casa con bloqueo
    SELECT price INTO v_house_price
    FROM houses
    WHERE id = p_house_id AND player_id IS NULL
    FOR UPDATE;

    IF v_house_price IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'House not available or already owned', 'success', false);
    END IF;

    -- Verificar fondos
    IF v_player_money < v_house_price THEN
        RETURN JSON_BUILD_OBJECT('error', 'Insufficient funds', 'success', false);
    END IF;

    -- Deducir dinero (ATOMIC)
    UPDATE player
    SET money = money - v_house_price,
        updated_at = NOW()
    WHERE id = p_player_id;

    -- Asignar casa al jugador (ATOMIC)
    UPDATE houses
    SET player_id = p_player_id,
        updated_at = NOW()
    WHERE id = p_house_id;

    -- Crear plots automáticamente para la casa
    INSERT INTO plots (house_id, status, created_at, updated_at)
    SELECT p_house_id, 'empty', NOW(), NOW()
    FROM generate_series(1,
        (SELECT plot_count FROM houses WHERE id = p_house_id)
    );

    RETURN JSON_BUILD_OBJECT(
        'success', true,
        'message', 'House purchased successfully',
        'house_id', p_house_id,
        'money_spent', v_house_price
    );

EXCEPTION WHEN OTHERS THEN
    RETURN JSON_BUILD_OBJECT('error', SQLERRM, 'success', false);
END;
$$ LANGUAGE plpgsql;

-- 2. VENDER CROPS EN BATCH (Atómico)
CREATE OR REPLACE FUNCTION sell_crops_batch_atomic(
    p_player_id INT,
    p_crop_type_id INT,
    p_quantity INT
) RETURNS JSON AS $$
DECLARE
    v_crop_price NUMERIC;
    v_available_yield INT;
    v_total_earnings NUMERIC;
    v_crops_array INT[];
    v_row RECORD;
BEGIN
    -- Bloquear player para evitar race conditions
    SELECT money INTO v_crop_price
    FROM player
    WHERE id = p_player_id
    FOR UPDATE;

    IF v_crop_price IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Player not found', 'success', false);
    END IF;

    -- Obtener precio del crop
    SELECT price INTO v_crop_price
    FROM crop_type
    WHERE id = p_crop_type_id;

    IF v_crop_price IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Crop type not found', 'success', false);
    END IF;

    -- Contar yield disponible
    SELECT COALESCE(SUM(yield_amount), 0) INTO v_available_yield
    FROM crops
    WHERE player_id = p_player_id
    AND crop_type_id = p_crop_type_id
    AND harvested_at IS NOT NULL
    AND yield_amount > 0;

    IF v_available_yield < p_quantity THEN
        RETURN JSON_BUILD_OBJECT(
            'error', 'Insufficient crops to sell',
            'available', v_available_yield,
            'requested', p_quantity,
            'success', false
        );
    END IF;

    -- Calcular ganancias
    v_total_earnings := v_crop_price * p_quantity;

    -- Actualizar dinero del jugador (ATOMIC)
    UPDATE player
    SET money = money + v_total_earnings,
        updated_at = NOW()
    WHERE id = p_player_id;

    -- Reducir yield de crops (ATOMIC)
    -- Usar un loop para restar de crops uno por uno
    FOR v_row IN
        SELECT id, yield_amount
        FROM crops
        WHERE player_id = p_player_id
        AND crop_type_id = p_crop_type_id
        AND harvested_at IS NOT NULL
        AND yield_amount > 0
        ORDER BY harvested_at ASC
    LOOP
        IF p_quantity <= 0 THEN EXIT; END IF;

        IF v_row.yield_amount <= p_quantity THEN
            -- Usar todo el yield de este crop
            UPDATE crops
            SET yield_amount = 0,
                updated_at = NOW()
            WHERE id = v_row.id;

            p_quantity := p_quantity - v_row.yield_amount;
        ELSE
            -- Usar solo parte del yield
            UPDATE crops
            SET yield_amount = yield_amount - p_quantity,
                updated_at = NOW()
            WHERE id = v_row.id;

            p_quantity := 0;
        END IF;
    END LOOP;

    RETURN JSON_BUILD_OBJECT(
        'success', true,
        'message', 'Crops sold successfully',
        'crop_type_id', p_crop_type_id,
        'quantity_sold', p_quantity,
        'earnings', v_total_earnings
    );

EXCEPTION WHEN OTHERS THEN
    RETURN JSON_BUILD_OBJECT('error', SQLERRM, 'success', false);
END;
$$ LANGUAGE plpgsql;

-- 3. COMPRAR SEEDS (Atómico)
CREATE OR REPLACE FUNCTION buy_seeds_atomic(
    p_player_id INT,
    p_crop_type_id INT,
    p_quantity INT
) RETURNS JSON AS $$
DECLARE
    v_seed_price NUMERIC;
    v_player_money NUMERIC;
    v_total_cost NUMERIC;
BEGIN
    -- Bloquear player
    SELECT money INTO v_player_money
    FROM player
    WHERE id = p_player_id
    FOR UPDATE;

    IF v_player_money IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Player not found', 'success', false);
    END IF;

    -- Obtener precio de semillas
    SELECT seed_price INTO v_seed_price
    FROM crop_type
    WHERE id = p_crop_type_id;

    IF v_seed_price IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Crop type not found', 'success', false);
    END IF;

    -- Calcular costo total
    v_total_cost := v_seed_price * p_quantity;

    -- Verificar fondos
    IF v_player_money < v_total_cost THEN
        RETURN JSON_BUILD_OBJECT(
            'error', 'Insufficient funds',
            'required', v_total_cost,
            'available', v_player_money,
            'success', false
        );
    END IF;

    -- Deducir dinero (ATOMIC)
    UPDATE player
    SET money = money - v_total_cost,
        updated_at = NOW()
    WHERE id = p_player_id;

    RETURN JSON_BUILD_OBJECT(
        'success', true,
        'message', 'Seeds purchased successfully',
        'crop_type_id', p_crop_type_id,
        'quantity', p_quantity,
        'total_cost', v_total_cost
    );

EXCEPTION WHEN OTHERS THEN
    RETURN JSON_BUILD_OBJECT('error', SQLERRM, 'success', false);
END;
$$ LANGUAGE plpgsql;
