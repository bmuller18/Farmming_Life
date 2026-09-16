"""
Validación de datos con Pydantic
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional


# ============================================================================
# AUTENTICACIÓN
# ============================================================================

class RegisterRequest(BaseModel):
	name: str = Field(..., min_length=3, max_length=50, description="Nombre del jugador")
	email: EmailStr = Field(..., description="Email único")
	password: str = Field(..., min_length=8, max_length=128, description="Contraseña mínimo 8 caracteres")

	class Config:
		json_schema_extra = {
			"example": {
				"name": "Muller29",
				"email": "player@example.com",
				"password": "securepass123"
			}
		}


class LoginRequest(BaseModel):
	email: EmailStr = Field(..., description="Email registrado")
	password: str = Field(..., min_length=1, description="Contraseña")

	class Config:
		json_schema_extra = {
			"example": {
				"email": "player@example.com",
				"password": "securepass123"
			}
		}


# ============================================================================
# CASAS
# ============================================================================

class BuyHouseRequest(BaseModel):
	house_id: int = Field(..., gt=0, description="ID de la casa a comprar")

	@validator("house_id")
	def validate_house_id(cls, v):
		if not isinstance(v, int) or v <= 0:
			raise ValueError("house_id debe ser un número positivo")
		return v

	class Config:
		json_schema_extra = {
			"example": {
				"house_id": 1
			}
		}


# ============================================================================
# CULTIVOS - SIEMBRA
# ============================================================================

class PlantCropRequest(BaseModel):
	crop_type_id: int = Field(..., gt=0, description="Tipo de cultivo a plantar")

	@validator("crop_type_id")
	def validate_crop_type(cls, v):
		if not isinstance(v, int) or v <= 0:
			raise ValueError("crop_type_id debe ser un número positivo")
		if v > 1000:  # Límite razonable
			raise ValueError("crop_type_id inválido")
		return v

	class Config:
		json_schema_extra = {
			"example": {
				"crop_type_id": 1
			}
		}


# ============================================================================
# COMPRA DE SEMILLAS
# ============================================================================

class BuySeedsRequest(BaseModel):
	crop_type_id: int = Field(..., gt=0, description="Tipo de cultivo")
	quantity: int = Field(default=1, gt=0, le=1000, description="Cantidad de semillas (1-1000)")

	@validator("crop_type_id", "quantity")
	def validate_positive_int(cls, v, field):
		if not isinstance(v, int) or v <= 0:
			raise ValueError(f"{field.name} debe ser un número positivo")
		if field.name == "quantity" and v > 1000:
			raise ValueError("No puedes comprar más de 1000 semillas a la vez")
		return v

	class Config:
		json_schema_extra = {
			"example": {
				"crop_type_id": 1,
				"quantity": 5
			}
		}


# ============================================================================
# VENTA DE CULTIVOS
# ============================================================================

class SellCropsRequest(BaseModel):
	player_id: int = Field(..., gt=0, description="ID del jugador")
	crop_type_id: int = Field(..., gt=0, description="Tipo de cultivo a vender")
	quantity: int = Field(default=1, gt=0, le=10000, description="Cantidad a vender")

	@validator("player_id", "crop_type_id", "quantity")
	def validate_positive_int(cls, v, field):
		if not isinstance(v, int) or v <= 0:
			raise ValueError(f"{field.name} debe ser un número positivo")
		if field.name == "quantity" and v > 10000:
			raise ValueError("No puedes vender más de 10000 cultivos a la vez")
		return v

	class Config:
		json_schema_extra = {
			"example": {
				"player_id": 1,
				"crop_type_id": 1,
				"quantity": 5
			}
		}


class SellSingleCropRequest(BaseModel):
	player_id: int = Field(..., gt=0, description="ID del jugador")

	@validator("player_id")
	def validate_player_id(cls, v):
		if not isinstance(v, int) or v <= 0:
			raise ValueError("player_id debe ser un número positivo")
		return v

	class Config:
		json_schema_extra = {
			"example": {
				"player_id": 1
			}
		}


# ============================================================================
# RESPUESTAS
# ============================================================================

class ErrorResponse(BaseModel):
	error: str = Field(..., description="Mensaje de error")
	success: bool = False

	class Config:
		json_schema_extra = {
			"example": {
				"error": "Insufficient funds",
				"success": False
			}
		}


class SuccessResponse(BaseModel):
	success: bool = True
	message: str = Field(..., description="Mensaje de éxito")

	class Config:
		json_schema_extra = {
			"example": {
				"success": True,
				"message": "Operation completed successfully"
			}
		}
