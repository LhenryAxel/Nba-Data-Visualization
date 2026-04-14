import os
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from dotenv import load_dotenv
from flask import request, jsonify

from app.models import Session, User

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET") or os.getenv("SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_HOURS = int(os.getenv("JWT_EXPIRES_HOURS", "24"))

if not JWT_SECRET:
    raise ValueError("JWT_SECRET or SECRET_KEY is missing in .env")


def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(stored_hash: str, password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )
    except Exception:
        return False


def create_token(user_id: int, role: str) -> str:
    """Generate a signed JWT."""
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": user_id,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRES_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """Validate and decode a JWT."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def register_user(username: str, password: str, role: str = "user") -> User | None:
    """Register a user in database."""
    session = Session()

    try:
        existing_user = session.query(User).filter_by(username=username).first()
        if existing_user:
            return None

        user = User(
            username=username,
            password_hash=hash_password(password),
            role=role
        )

        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def login_user(username: str, password: str) -> str | None:
    """Check credentials and return JWT."""
    session = Session()

    try:
        user = session.query(User).filter_by(username=username).first()
        if not user:
            return None

        if not verify_password(user.password_hash, password):
            return None

        return create_token(user.id, user.role)
    finally:
        session.close()


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()

        if not token:
            return jsonify({"error": "Token missing"}), 401

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "Non autorisé"}), 401

        return f(payload, *args, **kwargs)

    return decorated