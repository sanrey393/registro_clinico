import os
import pyrebase
from core.app_paths import load_app_env
from core.google_auth_helper import GoogleAuthFlow
from database.local_cache import LocalCache

# Cargar variables de entorno desde el .env del programa (también si está instalado)
load_app_env()

# Configuración Firebase para el cliente (pyrebase4)
firebase_config = {
    "apiKey":            os.environ.get("FIREBASE_API_KEY"),
    "authDomain":        os.environ.get("FIREBASE_AUTH_DOMAIN"),
    "projectId":         os.environ.get("FIREBASE_PROJECT_ID"),
    "storageBucket":     os.environ.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.environ.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId":             os.environ.get("FIREBASE_APP_ID"),
    "databaseURL":       os.environ.get("FIREBASE_DATABASE_URL", ""),
}

# Nota: GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET se leen dinámicamente
# dentro de sign_in_with_google() para garantizar que el .env ya fue cargado.

class AuthManager:
    def __init__(self):
        self._firebase = None
        self._auth = None
        self._current_user = None  # Dict con todos los datos del usuario

        try:
            self._firebase = pyrebase.initialize_app(firebase_config)
            self._auth = self._firebase.auth()
            print("[DEBUG] Firebase Auth inicializado correctamente.")
        except Exception as e:
            print(f"[ERROR] No se pudo inicializar Firebase: {e}")
            
        self.local_cache = LocalCache()

    # ── Configuración ───────────────────────────────────────────

    def is_configured(self):
        """Devuelve True si Firebase está inicializado correctamente."""
        return self._auth is not None

    # ── Sesión actual ───────────────────────────────────────────

    def get_current_user(self):
        """Devuelve el dict completo del usuario autenticado."""
        return self._current_user

    def get_display_name(self):
        """Nombre a mostrar del usuario (displayName > email > 'Usuario')."""
        if not self._current_user:
            return "Usuario"
        return (
            self._current_user.get("displayName")
            or self._current_user.get("nombre_completo")
            or self._current_user.get("email", "Usuario")
        )

    def get_email(self):
        """Email del usuario autenticado."""
        if not self._current_user:
            return ""
        return self._current_user.get("email", "")

    def get_uid(self):
        """UID de Firebase del usuario autenticado."""
        if not self._current_user:
            return ""
        return self._current_user.get("localId", "")

    def get_photo_url(self):
        """URL de foto de perfil (solo disponible con Google Sign-In)."""
        if not self._current_user:
            return ""
        return self._current_user.get("photoUrl", "")

    def is_new_user(self):
        """True si el usuario se registró por primera vez en esta sesión."""
        if not self._current_user:
            return False
        return self._current_user.get("isNewUser", False)

    def get_refresh_token(self):
        """Refresh token para restaurar la sesión."""
        if not self._current_user:
            return ""
        return self._current_user.get("refreshToken", "")

    def sign_out(self):
        """Limpiar la sesión del usuario."""
        self._current_user = None

    # ── Autenticación con Email/Password ────────────────────────

    def sign_in_with_password(self, email, password):
        """Autenticar usuario con correo y contraseña. Soporta Online y Offline."""
        if not self.is_configured():
            # Si no hay configuración online, intentar directamente login offline
            return self.local_cache.verify_offline_credentials(email, password)

        try:
            user = self._auth.sign_in_with_email_and_password(email, password)
            self._current_user = user
            print(f"[DEBUG] Login online exitoso: {user.get('email')}")
            # Guardar credenciales en local_cache para futuros logins offline
            try:
                self.local_cache.save_user_credentials(email, password, user)
            except Exception as e_cache:
                print(f"[WARN] Error al guardar credenciales en local: {e_cache}")
            return True, user
        except Exception as e:
            error_msg = str(e)
            
            # Si el error es de conectividad / red (offline), intentar autenticar localmente
            is_network_error = any(term in error_msg.lower() for term in [
                "connection", "network", "timeout", "getaddrinfo", "offline", "unreachable", "name resolution"
            ])
            
            if is_network_error:
                print("[INFO] Sin conexión a internet detectada. Probando login offline...")
                ok, user_or_err = self.local_cache.verify_offline_credentials(email, password)
                if ok:
                    self._current_user = user_or_err
                    print(f"[DEBUG] Login offline exitoso: {email}")
                    return True, user_or_err
                else:
                    return False, f"Sin conexión a internet. {user_or_err}"

            # Si hay internet pero las credenciales son incorrectas
            if "INVALID_PASSWORD" in error_msg or "INVALID_LOGIN_CREDENTIALS" in error_msg:
                return False, "Correo o contraseña incorrectos."
            if "EMAIL_NOT_FOUND" in error_msg:
                return False, "No existe una cuenta con este correo."
            if "TOO_MANY_ATTEMPTS_TRY_LATER" in error_msg:
                return False, "Cuenta bloqueada temporalmente por múltiples intentos."
            if "USER_DISABLED" in error_msg:
                return False, "Esta cuenta ha sido deshabilitada."
            return False, "Error de autenticación. Intente nuevamente."

    def sign_up(self, email, password):
        """Registrar un nuevo usuario en Firebase Auth."""
        if not self.is_configured():
            return False, "Firebase no está configurado."

        try:
            user = self._auth.create_user_with_email_and_password(email, password)
            self._current_user = user
            print(f"[DEBUG] Usuario creado: {user.get('email')}")
            
            # Enviar correo de verificación
            try:
                self._auth.send_email_verification(user['idToken'])
                print("[DEBUG] Correo de verificación enviado.")
            except Exception as e:
                print(f"[WARN] No se pudo enviar correo de verificación: {e}")
                
            return True, user
        except Exception as e:
            error_msg = str(e)
            if "EMAIL_EXISTS" in error_msg:
                return False, "Este correo ya está registrado."
            if "WEAK_PASSWORD" in error_msg or "weak-password" in error_msg:
                return False, "La contraseña es muy débil (mínimo 6 caracteres)."
            if "INVALID_EMAIL" in error_msg:
                return False, "El correo electrónico no es válido."
            return False, "No se pudo crear la cuenta. Intente nuevamente."

    # ── Restaurar sesión con refresh token ──────────────────────

    def restore_session(self, refresh_token: str):
        """
        Restaurar la sesión usando un refresh token guardado.
        Returns: (success: bool, user_data | error_msg)
        """
        if not self.is_configured() or not refresh_token:
            return False, "Sin token de sesión."
        try:
            user = self._auth.refresh(refresh_token)
            # refresh() no devuelve displayName/photoUrl, los preservamos si los tenemos
            self._current_user = user
            return True, user
        except Exception as e:
            return False, f"Sesión expirada: {e}"

    # ── Recuperación de Contraseña ──────────────────────────────
    
    def send_password_reset_email(self, email: str) -> tuple:
        """
        Envía correo para restablecer la contraseña usando Firebase Auth
        y genera un enlace directo seguro de respaldo si Admin SDK está disponible.
        
        Returns:
            (success: bool, user_message: str, reset_link: str | None)
        """
        clean_email = email.strip().lower()
        if not clean_email:
            return False, "Por favor, ingresa un correo electrónico válido.", None

        # 1. Intentar generar enlace directo con Firebase Admin SDK como respaldo
        reset_link = None
        try:
            import firebase_admin
            from firebase_admin import auth as admin_auth
            if firebase_admin._apps:
                reset_link = admin_auth.generate_password_reset_link(clean_email)
                print(f"[DEBUG] Enlace directo de recuperación generado: {reset_link}")
        except Exception as ex_admin:
            print(f"[DEBUG] Firebase Admin no pudo generar link directo: {ex_admin}")

        # 2. Intentar enviar correo con Firebase Client SDK (Pyrebase)
        client_sent = False
        client_error = ""

        if self.is_configured():
            try:
                self._auth.send_password_reset_email(clean_email)
                client_sent = True
                print(f"[DEBUG] Solicitud de correo de recuperación enviada para: {clean_email}")
            except Exception as e:
                client_error = str(e)
                print(f"[WARN] Error al enviar correo vía Pyrebase: {client_error}")

        # 3. Determinar resultado y mensaje al usuario
        if client_sent or reset_link:
            msg = (
                "Se ha enviado la solicitud de restablecimiento.\n\n"
                "⚠️ REVISA TU CARPETA DE SPAM / CORREO NO DESEADO:\n"
                "Los correos automáticos de Firebase frecuentemente son clasificados como spam por Gmail, Outlook o Yahoo."
            )
            return True, msg, reset_link

        # Si ambos fallaron, interpretar el error
        err_upper = client_error.upper()
        if "EMAIL_NOT_FOUND" in err_upper:
            return False, "No existe ninguna cuenta registrada con este correo electrónico. Verifica si te registraste con otro email o mediante Google.", None
        if "INVALID_EMAIL" in err_upper:
            return False, "El formato del correo electrónico ingresado no es válido.", None
        if "TOO_MANY_ATTEMPTS" in err_upper:
            return False, "Demasiados intentos fallidos. Por seguridad, espera unos minutos antes de volver a intentar.", None

        return False, f"No se pudo enviar el correo de recuperación: {client_error or 'Sin conexión con el servicio de autenticación'}", None

    # ── Google Sign-In ──────────────────────────────────────────

    def sign_in_with_google(self) -> tuple:
        """
        Inicia el flujo OAuth 2.0 de Google Sign-In.
        Si es usuario nuevo, Firebase lo registra automáticamente.
        Returns: (success: bool, user_data | error_message)
        """
        # Leer credenciales en tiempo de ejecución (no al importar el módulo)
        # para asegurar que load_app_env() ya procesó el .env correctamente.
        google_client_id     = os.environ.get("GOOGLE_CLIENT_ID", "")
        google_client_secret = os.environ.get("GOOGLE_CLIENT_SECRET", "")

        if not google_client_id or not google_client_secret:
            return False, "Google OAuth no está configurado. Revisa el archivo .env"

        api_key = firebase_config.get("apiKey", "")
        flow = GoogleAuthFlow(google_client_id, google_client_secret, api_key)
        success, result = flow.sign_in()

        if success:
            self._current_user = result
            is_new = result.get("isNewUser", False)
            name   = result.get("displayName", result.get("email", "Usuario"))
            print(f"[DEBUG] Google Sign-In: {name} | nuevo={is_new}")

        return success, result
