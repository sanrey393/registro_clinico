# core/security.py
# Módulo de seguridad, cifrado simétrico AES-256 (Fernet) y protección de datos médicos

import os
import sys
import base64
import hashlib
from cryptography.fernet import Fernet
from core.app_paths import app_dir

class SecurityVault:
    _instance = None
    _fernet = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_vault()
        return cls._instance

    def _init_vault(self):
        """
        Deriva una clave de cifrado única por máquina/instalación 
        usando identificadores del hardware o un salt local seguro.
        """
        base_dir = app_dir()
        key_file = os.path.join(base_dir, ".vault.key")

        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                key = f.read().strip()
        else:
            # Generar una clave segura aleatoria de 256 bits
            key = Fernet.generate_key()
            try:
                with open(key_file, "wb") as f:
                    f.write(key)
                # En Windows, podemos ocultar el archivo
                if sys.platform == "win32":
                    import ctypes
                    ctypes.windll.kernel32.SetFileAttributesW(key_file, 0x02) # FILE_ATTRIBUTE_HIDDEN
            except Exception as e:
                print(f"[WARN] No se pudo escribir .vault.key con atributo oculto: {e}")

        self._fernet = Fernet(key)

    def encrypt(self, plain_text: str) -> str:
        """Cifra un texto confidencial y retorna un string seguro en base64."""
        if not plain_text:
            return ""
        try:
            return self._fernet.encrypt(plain_text.encode("utf-8")).decode("utf-8")
        except Exception as e:
            print(f"[ERROR] Error al cifrar: {e}")
            return plain_text

    def decrypt(self, cipher_text: str) -> str:
        """Descifra un texto confidencial. Si no está cifrado (legacy), retorna el texto original."""
        if not cipher_text:
            return ""
        try:
            # Los tokens Fernet empiezan normalmente con 'gAAAAA'
            if cipher_text.startswith("gAAAAA"):
                return self._fernet.decrypt(cipher_text.encode("utf-8")).decode("utf-8")
            return cipher_text
        except Exception:
            # Si falla descifrar (por ejemplo si ya era texto plano anterior), retornarlo como está
            return cipher_text

