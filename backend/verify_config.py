"""
Verificar configuración de seguridad
Ejecutar: python backend/verify_config.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

def verify_config():
	"""Verifica que todas las variables de entorno requeridas estén configuradas"""
	load_dotenv()

	print("=" * 60)
	print("🔐 Verificación de Configuración de Seguridad")
	print("=" * 60)
	print()

	# Variables requeridas
	required_vars = {
		"SUPABASE_URL": "URL de Supabase",
		"SUPABASE_KEY": "Clave pública de Supabase",
		"SECRET_KEY": "Clave secreta para JWT"
	}

	all_ok = True

	for var_name, description in required_vars.items():
		value = os.getenv(var_name)

		if not value:
			print(f"❌ {var_name}: NO CONFIGURADO")
			print(f"   └─ {description}")
			all_ok = False
		else:
			# Verificar longitud mínima de SECRET_KEY
			if var_name == "SECRET_KEY":
				if len(value) < 32:
					print(f"⚠️  {var_name}: DÉBIL (menos de 32 caracteres)")
					print(f"   └─ Genera uno nuevo: python -c \"import secrets; print(secrets.token_hex(32))\"")
					all_ok = False
				else:
					# Mostrar hash parcial por seguridad
					masked = value[:8] + "..." + value[-8:]
					print(f"✅ {var_name}: CONFIGURADO ({masked})")
					print(f"   └─ {description}")
			else:
				# Mostrar hash parcial
				masked = value[:20] + "..." + value[-10:] if len(value) > 30 else value
				print(f"✅ {var_name}: CONFIGURADO ({masked})")
				print(f"   └─ {description}")

		print()

	# Verificar producción
	print("-" * 60)

	if os.getenv("FLASK_ENV") == "production":
		print("🚨 MODO PRODUCCIÓN - Verificaciones adicionales:")

		# En producción, algunas cosas son críticas
		if os.getenv("SECRET_KEY") and len(os.getenv("SECRET_KEY")) >= 32:
			print("✅ SECRET_KEY suficientemente fuerte")
		else:
			print("❌ SECRET_KEY debe tener al menos 32 caracteres en producción")
			all_ok = False
	else:
		print("💡 Modo Desarrollo - Asegúrate de cambiar SECRET_KEY antes de producción")

	print()
	print("=" * 60)

	if all_ok:
		print("✅ Configuración OK - El servidor puede iniciar")
		return True
	else:
		print("❌ Problemas encontrados - Corrige antes de iniciar")
		return False


if __name__ == "__main__":
	success = verify_config()
	sys.exit(0 if success else 1)
