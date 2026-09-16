import bcrypt
import jwt
import os
from datetime import datetime, timedelta, timezone
from backend.supabase_client import get_supabase_client

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

def hash_password(password: str) -> str:
	"""Hash a password using bcrypt."""
	return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
	"""Verify a password against its hash."""
	return bcrypt.checkpw(password.encode(), hashed.encode())


def create_jwt_token(player_id: int) -> str:
	"""Create a JWT token for a player."""
	payload = {
		"player_id": player_id,
		"exp": datetime.now(timezone.utc) + timedelta(days=30),
		"iat": datetime.now(timezone.utc)
	}
	return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_jwt_token(token: str) -> dict:
	"""Verify and decode a JWT token."""
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
		return payload
	except jwt.ExpiredSignatureError:
		raise ValueError("Token has expired")
	except jwt.InvalidTokenError:
		raise ValueError("Invalid token")


def register_player(email: str, name: str, password: str):
	"""Register a new player."""
	supabase = get_supabase_client()

	# Check if email already exists
	existing = (
		supabase
		.table("player")
		.select("id")
		.eq("email", email)
		.execute()
	)

	if existing.data:
		raise ValueError("Email already registered")

	# Hash password
	password_hash = hash_password(password)

	# Create player
	player_data = {
		"email": email,
		"name": name,
		"password_hash": password_hash,
		"money": 5000,
		"level": 1,
		"created_at": datetime.now(timezone.utc).isoformat(),
		"updated_at": datetime.now(timezone.utc).isoformat()
	}

	response = supabase.table("player").insert(player_data).execute()

	if not response.data:
		raise ValueError("Failed to create player")

	player = response.data[0]
	token = create_jwt_token(player["id"])

	return {
		"player_id": player["id"],
		"name": player["name"],
		"email": player["email"],
		"token": token,
		"message": "Player registered successfully"
	}


def login_player(email: str, password: str):
	"""Login a player."""
	supabase = get_supabase_client()

	# Find player by email
	response = (
		supabase
		.table("player")
		.select("*")
		.eq("email", email)
		.execute()
	)

	if not response.data:
		raise ValueError("Invalid email or password")

	player = response.data[0]

	# Verify password
	if not verify_password(password, player["password_hash"]):
		raise ValueError("Invalid email or password")

	token = create_jwt_token(player["id"])

	return {
		"player_id": player["id"],
		"name": player["name"],
		"email": player["email"],
		"token": token,
		"message": "Login successful"
	}
