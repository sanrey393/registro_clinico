import os
import sys
from pathlib import Path
from typing import Any
from datetime import datetime, date

import requests
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Ensure root project directory is importable
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.app_paths import load_app_env
from core.auth_manager import firebase_config
from database.firebase_manager import FirebaseManager

load_app_env()

security = HTTPBearer(auto_error=False)


def serialize_firestore(obj: Any) -> Any:
    """Recursively convert Firestore timestamps/dates to ISO strings for JSON."""
    if obj is None:
        return None
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if hasattr(obj, "isoformat"):
        try:
            return obj.isoformat()
        except Exception:
            return str(obj)
    if isinstance(obj, dict):
        return {k: serialize_firestore(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [serialize_firestore(v) for v in obj]
    return obj


def get_db() -> FirebaseManager:
    db = FirebaseManager()
    if not db.is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Base de datos Firebase no está configurada.",
        )
    return db


def _verify_token_via_rest(id_token: str) -> dict:
    """Fallback token verification using Firebase Identity Toolkit REST API."""
    api_key = firebase_config.get("apiKey") or os.environ.get("FIREBASE_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="FIREBASE_API_KEY no configurada.")
    resp = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}",
        json={"idToken": id_token},
        timeout=8,
    )
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sesión inválido o expirado.",
        )
    users = resp.json().get("users", [])
    if not users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado.",
        )
    u = users[0]
    return {
        "uid": u.get("localId", ""),
        "email": u.get("email", ""),
        "name": u.get("displayName", ""),
        "id_token": id_token,
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Verify Firebase ID token from Authorization: Bearer <token> header."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere iniciar sesión (Bearer token).",
        )
    token = credentials.credentials.strip()

    # Try Firebase Admin SDK first
    try:
        import firebase_admin
        from firebase_admin import auth as admin_auth

        if firebase_admin._apps:
            decoded = admin_auth.verify_id_token(token)
            return {
                "uid": decoded.get("uid", ""),
                "email": decoded.get("email", ""),
                "name": decoded.get("name", ""),
                "id_token": token,
            }
    except Exception as e:
        # If token explicitly expired or invalid, fail immediately
        msg = str(e).lower()
        if "expired" in msg or "revoked" in msg or "invalid" in msg:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Sesión expirada o token inválido.",
            )

    return _verify_token_via_rest(token)
