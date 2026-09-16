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
    SELECT money INTO v_crop_price
    FROM player
    WHERE id = p_player_id
    FOR UPDATE;

    IF v_crop_price IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Player not found', 'success', false);
    END IF;

    SELECT price INTO v_crop_price
    FROM crop_type
    WHERE id = p_crop_type_id;

    IF v_crop_price IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Crop type not found', 'success', false);
    END IF;

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

    v_total_earnings := v_crop_price * p_quantity;

    UPDATE player
    SET money = money + v_total_earnings,
        updated_at = NOW()
    WHERE id = p_player_id;

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
            UPDATE crops
            SET yield_amount = 0,
                updated_at = NOW()
            WHERE id = v_row.id;

            p_quantity := p_quantity - v_row.yield_amount;
        ELSE
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
