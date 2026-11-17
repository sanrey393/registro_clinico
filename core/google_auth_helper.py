import os
import webbrowser
import urllib.parse
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

REDIRECT_PORT = 8080
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"

# Página HTML que el navegador mostrará tras autenticarse
_SUCCESS_HTML = b"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Autenticado</title></head>
<body style="font-family:sans-serif;text-align:center;padding:80px;background:#f8f9fa">
  <div style="background:white;padding:40px;border-radius:12px;display:inline-block;box-shadow:0 4px 20px rgba(0,0,0,.1)">
    <div style="font-size:64px">&#10003;</div>
    <h2 style="color:#28a745;margin:10px 0">&#161;Autenticado correctamente!</h2>
    <p style="color:#666">Puedes cerrar esta ventana y volver a la aplicaci&#243;n.</p>
  </div>
</body>
</html>
"""

_ERROR_HTML = b"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Error</title></head>
<body style="font-family:sans-serif;text-align:center;padding:80px;background:#f8f9fa">
  <div style="background:white;padding:40px;border-radius:12px;display:inline-block;box-shadow:0 4px 20px rgba(0,0,0,.1)">
    <div style="font-size:64px">&#10007;</div>
    <h2 style="color:#dc3545">Error de autenticaci&#243;n</h2>
    <p style="color:#666">Cierra esta ventana e intenta de nuevo.</p>
  </div>
</body>
</html>
"""

class _OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Servidor local que captura el código de autorización de Google."""
    auth_code = None
    error = None

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            _OAuthCallbackHandler.auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_SUCCESS_HTML)
        else:
            _OAuthCallbackHandler.error = params.get("error", ["Error desconocido"])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(_ERROR_HTML)

    def log_message(self, format, *args):
        pass  # Silenciar logs del servidor HTTP


class GoogleAuthFlow:
    """
    Flujo OAuth 2.0 de Google para aplicación de escritorio.
    
    Pasos:
    1. Abre el navegador en la URL de autorización de Google.
    2. El usuario acepta permisos.
    3. Google redirige a localhost:8080 con el código de autorización.
    4. Se intercambia el código por un id_token.
    5. Se usa el id_token para autenticar en Firebase.
    """

    def __init__(self, client_id: str, client_secret: str, firebase_api_key: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.firebase_api_key = firebase_api_key

    def _build_auth_url(self) -> str:
        params = {
            "client_id":     self.client_id,
            "redirect_uri":  REDIRECT_URI,
            "response_type": "code",
            "scope":         "openid email profile",
            "access_type":   "offline",
            "prompt":        "select_account",
        }
        return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)

    def _exchange_code_for_tokens(self, auth_code: str) -> dict:
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code":          auth_code,
                "client_id":     self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri":  REDIRECT_URI,
                "grant_type":    "authorization_code",
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def _sign_in_firebase(self, id_token: str) -> dict:
        url = (
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp"
            f"?key={self.firebase_api_key}"
        )
        resp = requests.post(
            url,
            json={
                "postBody":           f"id_token={id_token}&providerId=google.com",
                "requestUri":         REDIRECT_URI,
                "returnIdpCredential": True,
                "returnSecureToken":   True,
            },
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()

    def sign_in(self) -> tuple:
        """
        Ejecuta el flujo completo de Google Sign-In.
        Returns: (success: bool, user_data | error_message)
        """
        _OAuthCallbackHandler.auth_code = None
        _OAuthCallbackHandler.error = None

        # Iniciar servidor local
        try:
            server = HTTPServer(("localhost", REDIRECT_PORT), _OAuthCallbackHandler)
        except OSError:
            return False, "El puerto 8080 ya está en uso. Cierra otras apps e intenta de nuevo."

        server.timeout = 120  # 2 minutos para que el usuario se autentique

        # Abrir navegador
        webbrowser.open(self._build_auth_url())

        # Esperar hasta recibir la respuesta del navegador
        server.handle_request()
        server.server_close()

        if _OAuthCallbackHandler.error:
            return False, f"Google rechazó el acceso: {_OAuthCallbackHandler.error}"

        if not _OAuthCallbackHandler.auth_code:
            return False, "No se recibió respuesta de Google. ¿Cerraste el navegador?"

        try:
            tokens   = self._exchange_code_for_tokens(_OAuthCallbackHandler.auth_code)
            id_token = tokens.get("id_token")
            if not id_token:
                return False, "No se obtuvo el token de Google."

            user_data = self._sign_in_firebase(id_token)
            return True, user_data

        except requests.HTTPError as e:
            try:
                detail = e.response.json().get("error", {}).get("message", str(e))
            except Exception:
                detail = str(e)
            return False, f"Error de Firebase: {detail}"
        except requests.Timeout:
            return False, "Tiempo de espera agotado. Verifica tu conexión."
        except Exception as e:
            return False, f"Error inesperado: {e}"
