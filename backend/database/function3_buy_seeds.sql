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
    SELECT money INTO v_player_money
    FROM player
    WHERE id = p_player_id
    FOR UPDATE;

    IF v_player_money IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Player not found', 'success', false);
    END IF;

    SELECT seed_price INTO v_seed_price
    FROM crop_type
    WHERE id = p_crop_type_id;

    IF v_seed_price IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Crop type not found', 'success', false);
    END IF;

    v_total_cost := v_seed_price * p_quantity;

    IF v_player_money < v_total_cost THEN
        RETURN JSON_BUILD_OBJECT(
            'error', 'Insufficient funds',
            'required', v_total_cost,
            'available', v_player_money,
            'success', false
        );
    END IF;

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
