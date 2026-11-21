# database/local_cache.py
# Motor de persistencia local SQLite para funcionamiento Offline y Sincronización con Firebase

import os
import sys
import json
import sqlite3
import hashlib
import binascii
from datetime import datetime
from core.security import SecurityVault
from core.app_paths import app_dir

class LocalCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Guardar la base de datos local en la carpeta del usuario o de la app
        base_dir = app_dir()
        self.db_path = os.path.join(base_dir, "local_storage.db")
        self.vault = SecurityVault()
        self._init_db()
        self._initialized = True

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Crea las tablas necesarias para autenticación offline y sincronización."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Tabla de credenciales de usuarios en caché (hash seguro con salt)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS local_users (
                    email TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    uid TEXT,
                    display_name TEXT,
                    user_data TEXT,
                    last_online_login TEXT
                )
            """)

            # 2. Tabla para almacenar colecciones en local (pacientes, historias, citas, etc.)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS local_records (
                    collection_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    is_synced INTEGER DEFAULT 1,     -- 1 = sincronizado con nube, 0 = pendiente de subir
                    is_deleted INTEGER DEFAULT 0,    -- 1 = marcado para borrar en la nube
                    updated_at TEXT,
                    user_id TEXT DEFAULT '',
                    PRIMARY KEY (collection_name, record_id)
                )
            """)

            # Migración: verificar si la columna user_id existe
            cursor.execute("PRAGMA table_info(local_records)")
            cols = [c[1] for c in cursor.fetchall()]
            if "user_id" not in cols:
                try:
                    cursor.execute("ALTER TABLE local_records ADD COLUMN user_id TEXT DEFAULT ''")
                except Exception:
                    pass

            conn.commit()

    # ── MÓDULO DE AUTENTICACIÓN OFFLINE ──────────────────────────────────────────

    def _hash_password(self, password: str, salt: bytes = None) -> tuple[str, str]:
        """Genera hash seguro PBKDF2-HMAC-SHA256."""
        if salt is None:
            salt = os.urandom(16)
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return binascii.hexlify(pwd_hash).decode('ascii'), binascii.hexlify(salt).decode('ascii')

    def save_user_credentials(self, email: str, password: str, user_dict: dict):
        """Guarda en caché las credenciales válidas cuando el login online es exitoso."""
        email_clean = email.strip().lower()
        pwd_hash, salt = self._hash_password(password)
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO local_users 
                (email, password_hash, salt, uid, display_name, user_data, last_online_login)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                email_clean,
                pwd_hash,
                salt,
                user_dict.get("localId", ""),
                user_dict.get("displayName") or user_dict.get("email", ""),
                json.dumps(user_dict),
                now
            ))
            conn.commit()

    def verify_offline_credentials(self, email: str, password: str) -> tuple[bool, dict | str]:
        """Verifica si el usuario puede ingresar sin conexión con sus credenciales cacheadas."""
        email_clean = email.strip().lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM local_users WHERE email = ?", (email_clean,))
            row = cursor.fetchone()
            
            if not row:
                return False, "Sin conexión a internet. Para iniciar sesión por primera vez en este equipo se requiere internet."

            salt_bytes = binascii.unhexlify(row["salt"])
            computed_hash, _ = self._hash_password(password, salt_bytes)

            if computed_hash == row["password_hash"]:
                user_data = json.loads(row["user_data"])
                user_data["offline_mode"] = True
                return True, user_data
            else:
                return False, "Correo o contraseña incorrectos."

    # ── MÓDULO DE REGISTROS LOCALES (LOCAL-FIRST) ──────────────────────────────

    def save_record(self, collection: str, record_id: str, data: dict, is_synced: bool = False, user_id: str = ""):
        """Guarda o actualiza un documento en local vinculado al usuario, cifrando datos clínicos sensibles."""
        now = datetime.now().isoformat()
        
        # Determinar user_id
        doc_user_id = user_id or data.get("user_id", "")
        if not doc_user_id:
            try:
                from core.auth_manager import AuthManager
                doc_user_id = AuthManager().get_uid()
            except Exception:
                pass

        # Cifrar campos clínicos especialmente confidenciales si están presentes
        clean_data = dict(data)
        clean_data["user_id"] = doc_user_id
        campos_confidenciales = [
            "motivo_consulta", "enfermedad_actual", "antecedentes_personales",
            "antecedentes_familiares", "examen_mental", "diagnostico_principal",
            "diagnostico_dsm5", "plan_tratamiento", "notas_evolucion", "observaciones"
        ]
        for campo in campos_confidenciales:
            if campo in clean_data and isinstance(clean_data[campo], str) and clean_data[campo]:
                clean_data[campo] = self.vault.encrypt(clean_data[campo])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO local_records
                (collection_name, record_id, data_json, is_synced, is_deleted, updated_at, user_id)
                VALUES (?, ?, ?, ?, 0, ?, ?)
            """, (
                collection,
                str(record_id),
                json.dumps(clean_data),
                1 if is_synced else 0,
                now,
                doc_user_id or ""
            ))
            conn.commit()

    def mark_deleted(self, collection: str, record_id: str, is_synced: bool = False):
        """Marca un documento para eliminación."""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if is_synced:
                # Si ya se eliminó en la nube, borrarlo definitivamente de local
                cursor.execute("""
                    DELETE FROM local_records WHERE collection_name = ? AND record_id = ?
                """, (collection, str(record_id)))
            else:
                cursor.execute("""
                    UPDATE local_records SET is_deleted = 1, is_synced = 0, updated_at = ?
                    WHERE collection_name = ? AND record_id = ?
                """, (now, collection, str(record_id)))
            conn.commit()

    def get_records(self, collection: str, user_id: str = "") -> list[dict]:
        """Obtiene todos los registros activos del usuario especificado descifrando campos sensibles."""
        uid = user_id
        if not uid:
            try:
                from core.auth_manager import AuthManager
                uid = AuthManager().get_uid()
            except Exception:
                pass

        if not uid:
            return []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT record_id, data_json FROM local_records
                WHERE collection_name = ? AND is_deleted = 0 AND user_id = ?
            """, (collection, uid))
            rows = cursor.fetchall()
            result = []
            
            campos_confidenciales = [
                "motivo_consulta", "enfermedad_actual", "antecedentes_personales",
                "antecedentes_familiares", "examen_mental", "diagnostico_principal",
                "diagnostico_dsm5", "plan_tratamiento", "notas_evolucion", "observaciones"
            ]

            for r in rows:
                item = json.loads(r["data_json"])
                item["id"] = r["record_id"]
                # Filtro estricto de seguridad: el documento debe pertenecer al usuario
                if item.get("user_id") and item.get("user_id") != uid:
                    continue
                # Descifrar si vienen cifrados
                for campo in campos_confidenciales:
                    if campo in item and isinstance(item[campo], str) and item[campo]:
                        item[campo] = self.vault.decrypt(item[campo])
                result.append(item)
            return result

    def get_pending_sync(self) -> list[dict]:
        """Retorna todos los registros que cambiaron en modo offline y deben subirse a Firebase."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT collection_name, record_id, data_json, is_deleted FROM local_records
                WHERE is_synced = 0
            """)
            rows = cursor.fetchall()
            pending = []
            for r in rows:
                pending.append({
                    "collection": r["collection_name"],
                    "record_id": r["record_id"],
                    "data": json.loads(r["data_json"]),
                    "is_deleted": bool(r["is_deleted"])
                })
            return pending

    def mark_as_synced(self, collection: str, record_id: str, is_deleted: bool = False):
        """Marca un registro como sincronizado con la nube."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if is_deleted:
                cursor.execute("DELETE FROM local_records WHERE collection_name = ? AND record_id = ?", (collection, str(record_id)))
            else:
                cursor.execute("UPDATE local_records SET is_synced = 1 WHERE collection_name = ? AND record_id = ?", (collection, str(record_id)))
            conn.commit()

