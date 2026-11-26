from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from api.deps import get_current_user, get_db, serialize_firestore
from core.auth_manager import AuthManager
from database.firebase_manager import FirebaseManager

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    nombre_completo: str
    email: EmailStr
    password: str
    rol: str = "psicologo"


class RefreshRequest(BaseModel):
    refresh_token: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class GoogleLoginRequest(BaseModel):
    id_token: str
    refresh_token: str = ""
    display_name: str = ""
    email: str = ""


@router.post("/login")
def login(payload: LoginRequest, db: FirebaseManager = Depends(get_db)):
    auth = AuthManager()
    ok, result = auth.sign_in_with_password(payload.email, payload.password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result if isinstance(result, str) else "Credenciales inválidas.",
        )

    uid = result.get("localId") or result.get("uid") or ""
    profile = db.obtener_usuario(uid) if uid else None
    return {
        "uid": uid,
        "email": result.get("email", payload.email),
        "display_name": (
            (profile or {}).get("nombre_completo")
            or result.get("displayName")
            or payload.email
        ),
        "rol": (profile or {}).get("rol", "psicologo"),
        "id_token": result.get("idToken", ""),
        "refresh_token": result.get("refreshToken", ""),
        "expires_in": result.get("expiresIn", "3600"),
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: FirebaseManager = Depends(get_db)):
    if len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 6 caracteres.",
        )
    auth = AuthManager()
    ok, result = auth.sign_up(payload.email, payload.password)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result if isinstance(result, str) else "No se pudo crear la cuenta.",
        )

    uid = result.get("localId") or ""
    if uid:
        db.crear_usuario(uid, payload.nombre_completo.strip(), payload.email, payload.rol)

    return {
        "uid": uid,
        "email": result.get("email", payload.email),
        "display_name": payload.nombre_completo.strip(),
        "rol": payload.rol,
        "id_token": result.get("idToken", ""),
        "refresh_token": result.get("refreshToken", ""),
        "expires_in": result.get("expiresIn", "3600"),
    }


@router.post("/refresh")
def refresh_token(payload: RefreshRequest, db: FirebaseManager = Depends(get_db)):
    auth = AuthManager()
    ok, result = auth.restore_session(payload.refresh_token)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result if isinstance(result, str) else "No se pudo refrescar la sesión.",
        )
    uid = result.get("user_id") or result.get("localId") or ""
    profile = db.obtener_usuario(uid) if uid else None
    return {
        "uid": uid,
        "email": (profile or {}).get("email", ""),
        "display_name": (profile or {}).get("nombre_completo", "Profesional"),
        "rol": (profile or {}).get("rol", "psicologo"),
        "id_token": result.get("idToken", ""),
        "refresh_token": result.get("refreshToken", payload.refresh_token),
        "expires_in": result.get("expiresIn", "3600"),
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    auth = AuthManager()
    ok, msg, _ = auth.send_password_reset_email(payload.email)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
    return {"ok": True, "message": msg}


@router.post("/google")
def google_login(payload: GoogleLoginRequest, db: FirebaseManager = Depends(get_db)):
    from api.deps import _verify_token_via_rest

    verified = None
    try:
        import firebase_admin
        from firebase_admin import auth as admin_auth
        if firebase_admin._apps:
            decoded = admin_auth.verify_id_token(payload.id_token)
            verified = {
                "uid": decoded.get("uid", ""),
                "email": decoded.get("email", ""),
                "name": decoded.get("name", ""),
            }
    except Exception:
        pass

    if not verified:
        verified = _verify_token_via_rest(payload.id_token)

    uid = verified.get("uid", "")
    email = verified.get("email") or payload.email
    display_name = verified.get("name") or payload.display_name or email or "Profesional"

    profile = db.obtener_usuario(uid) if uid else None
    if uid and not profile:
        db.crear_usuario(uid, display_name, email, rol="psicologo")
        profile = {"nombre_completo": display_name, "rol": "psicologo"}

    return {
        "uid": uid,
        "email": email,
        "display_name": (profile or {}).get("nombre_completo") or display_name,
        "rol": (profile or {}).get("rol", "psicologo"),
        "id_token": payload.id_token,
        "refresh_token": payload.refresh_token,
        "expires_in": "3600",
    }


@router.get("/me")
def me(user: dict = Depends(get_current_user), db: FirebaseManager = Depends(get_db)):
    profile = db.obtener_usuario(user["uid"]) or {}
    return serialize_firestore(
        {
            "uid": user["uid"],
            "email": user.get("email") or profile.get("email", ""),
            "nombre_completo": profile.get("nombre_completo") or user.get("name") or "Profesional",
            "rol": profile.get("rol", "psicologo"),
            "activo": profile.get("activo", True),
        }
    )
