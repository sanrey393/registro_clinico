# core/license_manager.py
# Sistema de protección por Hardware ID (Machine Lock) y validación de licencias

import os
import sys
import json
import hashlib
import binascii
from datetime import datetime

class LicenseManager:
    _instance = None
    _SECRET_SALT = "AGY_CLINIC_SECURE_V1_2026_KEVIN"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.license_file = os.path.join(app_dir, ".license.dat")
        self.machine_id = self.get_machine_id()

    @classmethod
    def get_machine_id(cls) -> str:
        """
        Obtiene un identificador único del hardware físico y Windows (MachineGuid + CPU).
        No requiere privilegios de administrador ni comandos externos como wmic.
        """
        guid = "DEFAULT_SYSTEM_GUID"
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
                guid, _ = winreg.QueryValueEx(key, "MachineGuid")
                winreg.CloseKey(key)
            except Exception:
                guid = os.environ.get("COMPUTERNAME", "UNKNOWN_PC")

        cpu = os.environ.get("PROCESSOR_IDENTIFIER", "CPU_GENERIC")
        username = os.environ.get("USERNAME", "")

        raw_id = f"{guid}_{cpu}".encode("utf-8")
        digest = hashlib.sha256(raw_id).hexdigest().upper()[:16]
        # Formato limpio y legible: XXXX-XXXX-XXXX-XXXX
        return f"{digest[0:4]}-{digest[4:8]}-{digest[8:12]}-{digest[12:16]}"

    def check_cloud_activation(self, db_manager) -> tuple[bool, str]:
        """
        Consulta en Firebase si tú activaste este equipo en la nube con un solo clic.
        Si está activo en Firebase, guarda automáticamente el certificado local en la PC.
        """
        if not db_manager or not hasattr(db_manager, "is_configured") or not db_manager.is_configured():
            return False, "Sin conexión a la base de datos."

        try:
            doc_ref = db_manager._db.collection("licencias").document(self.machine_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                if data.get("activa", False):
                    cliente = data.get("cliente", "Licencia Autorizada")
                    # Activar en este equipo de forma silenciosa y permanente
                    self.activate_locally(cliente)
                    return True, f"Licencia activada remotamente para {cliente}."
                else:
                    return False, "La licencia figura como inactiva o pendiente de pago en el servidor."
            else:
                # Registrar el equipo como pendiente para que Kevin lo vea en su consola de Firebase
                doc_ref.set({
                    "machine_id": self.machine_id,
                    "activa": False,
                    "cliente": "Pendiente de activación",
                    "fecha_solicitud": datetime.now().isoformat()
                }, merge=True)
                return False, "Solicitud enviada a la nube. Actívala desde tu consola Firebase."
        except Exception as e:
            return False, f"Error al consultar Firebase: {e}"
        """Genera una firma criptográfica que solo es válida para ese Machine ID."""
        raw = f"{machine_id}::{client_name}::{expiry}::{self._SECRET_SALT}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest().upper()

    def _generate_signature(self, machine_id: str, client_name: str, expiry: str = "PERPETUAL") -> str:
        """Genera una firma criptográfica que solo es válida para ese Machine ID."""
        raw = f"{machine_id}::{client_name}::{expiry}::{self._SECRET_SALT}".encode("utf-8")
        return hashlib.sha256(raw).hexdigest().upper()

    def generate_activation_key(self, machine_id: str, client_name: str = "Clinica") -> str:
        """
        Función para que TÚ generes claves de activación válidas para tus clientes.
        Formato de clave: CLN-XXXX-XXXX-XXXX
        """
        raw = f"{machine_id}::{client_name}::{self._SECRET_SALT}".encode("utf-8")
        h = hashlib.sha256(raw).hexdigest().upper()[:12]
        return f"CLN-{h[0:4]}-{h[4:8]}-{h[8:12]}"

    def verify_activation_key(self, key_entered: str, machine_id: str = None) -> bool:
        """Comprueba si una clave introducida coincide con este equipo."""
        if not key_entered:
            return False
        mid = machine_id or self.machine_id
        expected_key = self.generate_activation_key(mid)
        # Comparación insensible a espacios y mayúsculas
        clean_entered = key_entered.strip().upper().replace(" ", "")
        return clean_entered == expected_key

    def activate_locally(self, client_name: str = "Licencia Autorizada") -> bool:
        """Guarda el certificado de activación firmado localmente para este equipo."""
        try:
            signature = self._generate_signature(self.machine_id, client_name)
            data = {
                "machine_id": self.machine_id,
                "client": client_name,
                "signature": signature,
                "activated_at": datetime.now().isoformat()
            }
            with open(self.license_file, "w", encoding="utf-8") as f:
                json.dump(data, f)

            if sys.platform == "win32":
                try:
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(self.license_file, 0x02) # Oculto
                except Exception:
                    pass
            return True
        except Exception as e:
            print(f"[ERROR] activate_locally: {e}")
            return False

    def is_license_valid(self, db_manager=None) -> tuple[bool, str]:
        """
        Valida si la computadora está autorizada.
        1. Comprueba el certificado local (Funciona 100% offline).
        2. Si hay conexión y db_manager, verifica si sigue activa en Firebase.
        """
        # 1. Comprobación local
        if not os.path.exists(self.license_file):
            return False, "Equipo no registrado. Se requiere activación."

        try:
            with open(self.license_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            saved_mid = data.get("machine_id")
            saved_client = data.get("client", "Clinica")
            saved_sig = data.get("signature")

            # Si copiaron el archivo a otra máquina, saved_mid != self.machine_id
            if saved_mid != self.machine_id:
                return False, "Copia no autorizada. El identificador del hardware no coincide."

            expected_sig = self._generate_signature(self.machine_id, saved_client)
            if saved_sig != expected_sig:
                return False, "Licencia alterada o inválida."

            # 2. Validación opcional en Firebase si hay internet
            if db_manager and hasattr(db_manager, "is_configured") and db_manager.is_configured():
                try:
                    doc = db_manager._db.collection("licencias").document(self.machine_id).get()
                    if doc.exists:
                        cloud_data = doc.to_dict()
                        if not cloud_data.get("activa", True):
                            return False, "Esta licencia ha sido suspendida por el administrador."
                except Exception:
                    # Si falla por falta de internet, se confía en la firma local válida
                    pass

            return True, "Licencia válida."

        except Exception as e:
            return False, f"Error leyendo licencia: {e}"

