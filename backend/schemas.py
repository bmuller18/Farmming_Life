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

	model_config = {"json_schema_extra": {"example": {"house_id": 1}}}


# ============================================================================
# CULTIVOS - SIEMBRA
# ============================================================================

class PlantCropRequest(BaseModel):
	crop_type_id: int = Field(..., gt=0, le=1000, description="Tipo de cultivo a plantar (1-1000)")

	model_config = {"json_schema_extra": {"example": {"crop_type_id": 1}}}


# ============================================================================
# COMPRA DE SEMILLAS
# ============================================================================

class BuySeedsRequest(BaseModel):
	crop_type_id: int = Field(..., gt=0, le=1000, description="Tipo de cultivo (1-1000)")
	quantity: int = Field(default=1, gt=0, le=1000, description="Cantidad de semillas (1-1000)")

	model_config = {"json_schema_extra": {"example": {"crop_type_id": 1, "quantity": 5}}}


# ============================================================================
# VENTA DE CULTIVOS
# ============================================================================

class SellCropsRequest(BaseModel):
	player_id: int = Field(..., gt=0, description="ID del jugador")
	crop_type_id: int = Field(..., gt=0, le=1000, description="Tipo de cultivo a vender")
	quantity: int = Field(default=1, gt=0, le=10000, description="Cantidad a vender (1-10000)")

	model_config = {"json_schema_extra": {"example": {"player_id": 1, "crop_type_id": 1, "quantity": 5}}}


class SellSingleCropRequest(BaseModel):
	player_id: int = Field(..., gt=0, description="ID del jugador")

	model_config = {"json_schema_extra": {"example": {"player_id": 1}}}


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
