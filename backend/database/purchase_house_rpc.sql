-- Función RPC para comprar casa de forma segura
CREATE OR REPLACE FUNCTION purchase_house(
  p_player_id BIGINT,
  p_house_id INT
)
RETURNS JSON AS $$
DECLARE
  v_house_price DECIMAL;
  v_player_money DECIMAL;
  v_house_name TEXT;
  v_new_balance DECIMAL;
BEGIN
  -- Obtener precio y nombre de la casa
  SELECT price, name INTO v_house_price, v_house_name
  FROM houses WHERE id = p_house_id AND player_id IS NULL;

  IF v_house_price IS NULL THEN
    RETURN json_build_object('error', 'House not found or already owned');
  END IF;

  -- Obtener dinero del jugador
  SELECT money INTO v_player_money FROM player WHERE id = p_player_id;

  IF v_player_money IS NULL THEN
    RETURN json_build_object('error', 'Player not found');
  END IF;

  IF v_player_money < v_house_price THEN
    RETURN json_build_object('error', 'Insufficient funds');
  END IF;

  -- Calcular nuevo balance
  v_new_balance := v_player_money - v_house_price;

  -- Actualizar casa
  UPDATE houses
  SET player_id = p_player_id, updated_at = NOW()
  WHERE id = p_house_id;

  -- Restar dinero
  UPDATE player
  SET money = v_new_balance, updated_at = NOW()
  WHERE id = p_player_id;

  RETURN json_build_object(
    'house_id', p_house_id,
    'house_name', v_house_name,
    'price', v_house_price,
    'new_balance', v_new_balance
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Crear política RLS para permitir llamar la función
CREATE POLICY "Anyone can call purchase_house function"
ON houses FOR ALL
USING (TRUE)
WITH CHECK (TRUE);
