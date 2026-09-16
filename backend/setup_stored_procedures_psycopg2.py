"""
Script para crear Stored Procedures usando psycopg2
Esto conecta directamente a PostgreSQL en Supabase

Instalación:
  pip install psycopg2-binary

Uso:
  python backend/setup_stored_procedures_psycopg2.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

def setup_stored_procedures():
	"""Crea los stored procedures en Supabase usando conexión directa"""
	load_dotenv()

	try:
		import psycopg2
	except ImportError:
		print("❌ Error: psycopg2 no está instalado")
		print("Instala con: pip install psycopg2-binary")
		return False

	# Obtener credenciales de Supabase desde .env
	supabase_url = os.getenv("SUPABASE_URL")

	if not supabase_url:
		print("❌ Error: SUPABASE_URL no está en .env")
		return False

	# Extraer conexión info de la URL
	# Formato: https://xxxxx.supabase.co
	# Debemos usar las credenciales de PostgreSQL de Supabase directamente

	# Para usar psycopg2, necesitas las credenciales de PostgreSQL
	# que están en Supabase Settings → Database

	print("⚠️  Para usar psycopg2, necesitas:")
	print("  1. Ir a: https://app.supabase.com → Tu Proyecto")
	print("  2. Settings → Database → Connection String")
	print("  3. Copiar la conexión URI")
	print("  4. Poner en .env como: DATABASE_URL")
	print("\nEjemplo .env:")
	print('  DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres')

	database_url = os.getenv("DATABASE_URL")

	if not database_url:
		print("\n❌ DATABASE_URL no está en .env")
		print("\n💡 Alternativa: Ejecuta el SQL manualmente en Supabase")
		print("  1. Ve a: https://app.supabase.com → SQL Editor")
		print("  2. Abre: backend/database/stored_procedures.sql")
		print("  3. Copia-pega cada función")
		print("  4. Ejecuta")
		return False

	try:
		print("\n🔧 Conectando a PostgreSQL en Supabase...\n")
		conn = psycopg2.connect(database_url)
		cursor = conn.cursor()

		# Procedimiento 1: buy_house_atomic
		procedure_1 = """
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
		"""

		# Procedimiento 2: sell_crops_batch_atomic
		procedure_2 = """
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
		"""

		# Procedimiento 3: buy_seeds_atomic
		procedure_3 = """
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
		"""

		procedures = [
			("buy_house_atomic", procedure_1),
			("sell_crops_batch_atomic", procedure_2),
			("buy_seeds_atomic", procedure_3)
		]

		for proc_name, proc_sql in procedures:
			try:
				print(f"⏳ Creando {proc_name}...")
				cursor.execute(proc_sql)
				conn.commit()
				print(f"✅ {proc_name} - CREADO exitosamente\n")
			except Exception as e:
				print(f"❌ {proc_name} - ERROR: {str(e)}\n")
				conn.rollback()
				cursor.close()
				conn.close()
				return False

		cursor.close()
		conn.close()

		print("\n" + "="*60)
		print("✅ TODOS LOS STORED PROCEDURES CREADOS")
		print("="*60)
		print("\nAhora puedes usar:")
		print("- buy_house_atomic(player_id, house_id)")
		print("- sell_crops_batch_atomic(player_id, crop_type_id, quantity)")
		print("- buy_seeds_atomic(player_id, crop_type_id, quantity)")

		return True

	except Exception as e:
		print(f"❌ Error de conexión: {str(e)}")
		print("\n💡 Alternativa: Ejecuta el SQL manualmente en Supabase")
		print("  1. Ve a: https://app.supabase.com → SQL Editor")
		print("  2. Abre: backend/database/stored_procedures.sql")
		print("  3. Copia-pega cada función")
		print("  4. Ejecuta")
		return False


if __name__ == "__main__":
	success = setup_stored_procedures()
	sys.exit(0 if success else 1)
