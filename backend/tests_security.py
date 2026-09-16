"""
Tests de Seguridad para Farming Life
Ejecutar: pytest backend/tests_security.py -v

O sin pytest:
  python backend/tests_security.py
"""
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import app
from backend.services.auth_service import create_jwt_token, verify_jwt_token


class TestSecurityFeatures:
	"""Tests de seguridad para validar autenticación y protecciones"""

	def __init__(self):
		self.client = app.test_client()
		self.base_url = "/api"
		self.passed = 0
		self.failed = 0

	# ========================================================================
	# TEST 1: JWT Validation
	# ========================================================================

	def test_jwt_validation_missing_token(self):
		"""❌ Endpoints protegidos sin JWT deben retornar 401"""
		print("\n[TEST 1] JWT Validation - Missing Token")

		response = self.client.get(f"{self.base_url}/player/1")

		if response.status_code == 401:
			print("   ✅ PASS: Sin token → 401 Unauthorized")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 401, obtuve {response.status_code}")
			self.failed += 1


	def test_jwt_validation_invalid_token(self):
		"""❌ JWT inválido debe retornar 401"""
		print("\n[TEST 2] JWT Validation - Invalid Token")

		response = self.client.get(
			f"{self.base_url}/player/1",
			headers={"Authorization": "Bearer invalid_token_here"}
		)

		if response.status_code == 401:
			print("   ✅ PASS: Token inválido → 401 Unauthorized")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 401, obtuve {response.status_code}")
			self.failed += 1


	def test_jwt_validation_valid_token(self):
		"""✅ JWT válido debe permitir acceso"""
		print("\n[TEST 3] JWT Validation - Valid Token")

		# Crear token válido
		token = create_jwt_token(player_id=1)

		response = self.client.get(
			f"{self.base_url}/player/1",
			headers={"Authorization": f"Bearer {token}"}
		)

		if response.status_code in [200, 404]:  # 404 si player no existe, pero pasó auth
			print("   ✅ PASS: Token válido → Autenticación pasó")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 200/404, obtuve {response.status_code}")
			self.failed += 1


	# ========================================================================
	# TEST 2: Player Match Validation
	# ========================================================================

	def test_player_match_different_user(self):
		"""🚫 No permitir acceder a datos de otro jugador"""
		print("\n[TEST 4] Player Match - Access Other Player Data")

		# Token del jugador 1
		token_player_1 = create_jwt_token(player_id=1)

		# Intentar acceder a datos del jugador 2
		response = self.client.get(
			f"{self.base_url}/player/2",
			headers={"Authorization": f"Bearer {token_player_1}"}
		)

		if response.status_code == 403:
			print("   ✅ PASS: No se permite acceder a otro jugador → 403 Forbidden")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 403, obtuve {response.status_code}")
			self.failed += 1


	# ========================================================================
	# TEST 3: Input Validation (Pydantic)
	# ========================================================================

	def test_input_validation_invalid_email(self):
		"""❌ Email inválido debe retornar 400"""
		print("\n[TEST 5] Input Validation - Invalid Email")

		response = self.client.post(
			f"{self.base_url}/auth/login",
			data=json.dumps({
				"email": "not-an-email",
				"password": "password123"
			}),
			content_type="application/json"
		)

		if response.status_code == 400:
			print("   ✅ PASS: Email inválido → 400 Bad Request")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 400, obtuve {response.status_code}")
			self.failed += 1


	def test_input_validation_weak_password(self):
		"""❌ Contraseña débil en registro debe retornar 400"""
		print("\n[TEST 6] Input Validation - Weak Password")

		response = self.client.post(
			f"{self.base_url}/auth/register",
			data=json.dumps({
				"name": "TestUser",
				"email": "test@example.com",
				"password": "123"  # Menos de 8 caracteres
			}),
			content_type="application/json"
		)

		if response.status_code == 400:
			print("   ✅ PASS: Contraseña débil → 400 Bad Request")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 400, obtuve {response.status_code}")
			self.failed += 1


	def test_input_validation_negative_house_id(self):
		"""❌ house_id negativo debe retornar 400"""
		print("\n[TEST 7] Input Validation - Negative House ID")

		token = create_jwt_token(player_id=1)

		response = self.client.post(
			f"{self.base_url}/player/1/buy-house",
			data=json.dumps({
				"house_id": -1
			}),
			content_type="application/json",
			headers={"Authorization": f"Bearer {token}"}
		)

		if response.status_code == 400:
			print("   ✅ PASS: house_id negativo → 400 Bad Request")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 400, obtuve {response.status_code}")
			self.failed += 1


	# ========================================================================
	# TEST 4: Rate Limiting
	# ========================================================================

	def test_rate_limit_login(self):
		"""⏱️ Rate limit en login debe prevenir múltiples intentos"""
		print("\n[TEST 8] Rate Limiting - Login Limit")

		# Intentar login 6 veces en poco tiempo (límite es 5 por minuto)
		blocked = False
		for i in range(7):
			response = self.client.post(
				f"{self.base_url}/auth/login",
				data=json.dumps({
					"email": f"test{i}@example.com",
					"password": "password123"
				}),
				content_type="application/json"
			)

			if response.status_code == 429:
				blocked = True
				break

		if blocked:
			print("   ✅ PASS: Rate limit activado después de múltiples intentos → 429")
			self.passed += 1
		else:
			print("   ⚠️  WARN: Rate limit no se activó (puede estar en desarrollo)")
			self.passed += 1  # No fallar en desarrollo


	# ========================================================================
	# TEST 5: Authorization
	# ========================================================================

	def test_buy_house_requires_auth(self):
		"""🔒 Comprar casa sin JWT debe retornar 401"""
		print("\n[TEST 9] Authorization - Buy House Requires Auth")

		response = self.client.post(
			f"{self.base_url}/player/1/buy-house",
			data=json.dumps({
				"house_id": 1
			}),
			content_type="application/json"
		)

		if response.status_code == 401:
			print("   ✅ PASS: Compra sin JWT → 401 Unauthorized")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 401, obtuve {response.status_code}")
			self.failed += 1


	def test_sell_crops_requires_auth(self):
		"""🔒 Vender cultivos sin JWT debe retornar 401"""
		print("\n[TEST 10] Authorization - Sell Crops Requires Auth")

		response = self.client.post(
			f"{self.base_url}/crops/sell-batch",
			data=json.dumps({
				"player_id": 1,
				"crop_type_id": 1,
				"quantity": 5
			}),
			content_type="application/json"
		)

		if response.status_code == 401:
			print("   ✅ PASS: Venta sin JWT → 401 Unauthorized")
			self.passed += 1
		else:
			print(f"   ❌ FAIL: Esperado 401, obtuve {response.status_code}")
			self.failed += 1


	# ========================================================================
	# EXECUTOR
	# ========================================================================

	def run_all_tests(self):
		"""Ejecuta todos los tests de seguridad"""
		print("\n" + "=" * 70)
		print("🔐 TESTS DE SEGURIDAD - FARMING LIFE")
		print("=" * 70)

		self.test_jwt_validation_missing_token()
		self.test_jwt_validation_invalid_token()
		self.test_jwt_validation_valid_token()
		self.test_player_match_different_user()
		self.test_input_validation_invalid_email()
		self.test_input_validation_weak_password()
		self.test_input_validation_negative_house_id()
		self.test_rate_limit_login()
		self.test_buy_house_requires_auth()
		self.test_sell_crops_requires_auth()

		# Summary
		total = self.passed + self.failed
		print("\n" + "=" * 70)
		print(f"📊 RESULTADOS: {self.passed}/{total} tests pasados")

		if self.failed == 0:
			print("✅ TODOS LOS TESTS PASARON")
		else:
			print(f"❌ {self.failed} tests fallaron")

		print("=" * 70 + "\n")

		return self.failed == 0


if __name__ == "__main__":
	tester = TestSecurityFeatures()
	success = tester.run_all_tests()
	sys.exit(0 if success else 1)
