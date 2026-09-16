CREATE OR REPLACE FUNCTION buy_house_atomic(
    p_player_id INT,
    p_house_id INT
) RETURNS JSON AS $$
DECLARE
    v_house_price NUMERIC;
    v_player_money NUMERIC;
    v_result JSON;
BEGIN
    SELECT money INTO v_player_money
    FROM player
    WHERE id = p_player_id
    FOR UPDATE;

    IF v_player_money IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'Player not found', 'success', false);
    END IF;

    SELECT price INTO v_house_price
    FROM houses
    WHERE id = p_house_id AND player_id IS NULL
    FOR UPDATE;

    IF v_house_price IS NULL THEN
        RETURN JSON_BUILD_OBJECT('error', 'House not available or already owned', 'success', false);
    END IF;

    IF v_player_money < v_house_price THEN
        RETURN JSON_BUILD_OBJECT('error', 'Insufficient funds', 'success', false);
    END IF;

    UPDATE player
    SET money = money - v_house_price,
        updated_at = NOW()
    WHERE id = p_player_id;

    UPDATE houses
    SET player_id = p_player_id,
        updated_at = NOW()
    WHERE id = p_house_id;

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
