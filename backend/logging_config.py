"""
Logging Estructurado para Farming Life
Uso: from backend.logging_config import get_logger
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
	"""Formatea logs como JSON para mejor análisis"""

	def format(self, record: logging.LogRecord) -> str:
		log_data = {
			"timestamp": datetime.utcnow().isoformat(),
			"level": record.levelname,
			"logger": record.name,
			"message": record.getMessage(),
			"module": record.module,
			"function": record.funcName,
			"line": record.lineno,
		}

		# Agregar contexto extra si existe
		if hasattr(record, "player_id"):
			log_data["player_id"] = record.player_id
		if hasattr(record, "request_id"):
			log_data["request_id"] = record.request_id
		if hasattr(record, "duration_ms"):
			log_data["duration_ms"] = record.duration_ms
		if hasattr(record, "status_code"):
			log_data["status_code"] = record.status_code

		# Agregar excepción si existe
		if record.exc_info:
			log_data["exception"] = self.formatException(record.exc_info)

		return json.dumps(log_data, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
	"""Obtiene logger estructurado"""
	logger = logging.getLogger(name)

	if not logger.handlers:
		handler = logging.StreamHandler()
		formatter = StructuredFormatter()
		handler.setFormatter(formatter)
		logger.addHandler(handler)
		logger.setLevel(logging.INFO)

	return logger


class LogContext:
	"""Context manager para agregar información a logs"""

	def __init__(self, logger: logging.Logger, **context):
		self.logger = logger
		self.context = context

	def __enter__(self):
		# Agregar contexto a logger
		for key, value in self.context.items():
			setattr(logging.LogRecord, key, value)
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		# Limpiar contexto
		for key in self.context.keys():
			if hasattr(logging.LogRecord, key):
				delattr(logging.LogRecord, key)


# Loggers por módulo
auth_logger = get_logger("farming_life.auth")
crop_logger = get_logger("farming_life.crop")
economy_logger = get_logger("farming_life.economy")
house_logger = get_logger("farming_life.house")
api_logger = get_logger("farming_life.api")


# ============================================================================
# LOG EVENTOS
# ============================================================================

def log_login(player_id: int, email: str, success: bool, error: str = None):
	"""Log de intento de login"""
	if success:
		auth_logger.info(
			f"Login exitoso",
			extra={"player_id": player_id, "email": email}
		)
	else:
		auth_logger.warning(
			f"Login fallido: {error}",
			extra={"email": email}
		)


def log_register(player_id: int, email: str, success: bool, error: str = None):
	"""Log de registro"""
	if success:
		auth_logger.info(
			f"Registro exitoso",
			extra={"player_id": player_id, "email": email}
		)
	else:
		auth_logger.warning(
			f"Registro fallido: {error}",
			extra={"email": email}
		)


def log_harvest(player_id: int, crop_id: int, yield_amount: int):
	"""Log de cosecha"""
	crop_logger.info(
		f"Cosecha exitosa: {yield_amount} unidades",
		extra={
			"player_id": player_id,
			"crop_id": crop_id,
			"yield_amount": yield_amount
		}
	)


def log_buy_house(player_id: int, house_id: int, price: float, success: bool):
	"""Log de compra de casa"""
	if success:
		house_logger.info(
			f"Casa comprada",
			extra={
				"player_id": player_id,
				"house_id": house_id,
				"price": price
			}
		)
	else:
		house_logger.warning(
			f"Compra de casa fallida",
			extra={
				"player_id": player_id,
				"house_id": house_id,
				"price": price
			}
		)


def log_sell_crops(player_id: int, crop_type_id: int, quantity: int, earnings: float):
	"""Log de venta de cultivos"""
	economy_logger.info(
		f"Venta exitosa: {quantity} cultivos = ${earnings}",
		extra={
			"player_id": player_id,
			"crop_type_id": crop_type_id,
			"quantity": quantity,
			"earnings": earnings
		}
	)


def log_api_request(method: str, path: str, status_code: int, duration_ms: float, player_id: int = None):
	"""Log de request HTTP"""
	api_logger.info(
		f"{method} {path} → {status_code}",
		extra={
			"method": method,
			"path": path,
			"status_code": status_code,
			"duration_ms": duration_ms,
			"player_id": player_id
		}
	)


def log_error(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None):
	"""Log de error con contexto"""
	context = context or {}
	logger.error(
		f"Error: {str(error)}",
		extra=context,
		exc_info=True
	)
