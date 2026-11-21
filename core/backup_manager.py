# core/backup_manager.py
# Módulo integral para creación, restauración y automatización de respaldos del sistema clínico

import os
import sys
import json
import sqlite3
import shutil
import zipfile
import datetime
from PyQt6.QtCore import QSettings
from core.app_paths import app_dir
from database.local_cache import LocalCache


def get_default_backup_dir() -> str:
    """Ruta predeterminada para guardar respaldos (Documentos/Respaldos_Clinicos)."""
    user_docs = os.path.join(os.path.expanduser("~"), "Documents", "Respaldos_Clinicos")
    if not os.path.exists(user_docs):
        try:
            os.makedirs(user_docs, exist_ok=True)
        except Exception:
            user_docs = app_dir()
    return user_docs


class BackupManager:
    """Manejador central de respaldos manuales, automáticos y exportación de datos."""

    @staticmethod
    def get_backup_config() -> dict:
        """Obtiene la configuración de respaldos automáticos guardada en QSettings."""
        s = QSettings("MiAppClinica", "BackupSettings")
        return {
            "auto_backup_enabled": s.value("auto_backup_enabled", False, type=bool),
            "frequency": s.value("frequency", "on_close"),  # "on_close", "daily", "weekly"
            "backup_dir": s.value("backup_dir", get_default_backup_dir()),
            "max_backups_retained": s.value("max_backups_retained", 10, type=int),
            "last_backup_date": s.value("last_backup_date", "")
        }

    @staticmethod
    def save_backup_config(config: dict):
        """Guarda la configuración de respaldos automáticos en QSettings."""
        s = QSettings("MiAppClinica", "BackupSettings")
        s.setValue("auto_backup_enabled", config.get("auto_backup_enabled", False))
        s.setValue("frequency", config.get("frequency", "on_close"))
        s.setValue("backup_dir", config.get("backup_dir", get_default_backup_dir()))
        s.setValue("max_backups_retained", config.get("max_backups_retained", 10))
        if "last_backup_date" in config:
            s.setValue("last_backup_date", config.get("last_backup_date"))

    @staticmethod
    def crear_respaldo(destino_archivo: str = None) -> tuple[bool, str, dict]:
        """
        Crea un paquete de respaldo seguro comprimido (.clinicabak / .zip).
        Contiene:
        1. Base de datos SQLite local (local_storage.db)
        2. Volcado estructurado en JSON de todos los registros clínicos
        3. Llave de cifrado de bóveda (.vault.key) si existe
        4. Manifiesto del respaldo (metadatos, fecha, conteos)
        
        Returns:
            (success: bool, mensaje_o_ruta: str, estadisticas: dict)
        """
        root = app_dir()
        db_path = os.path.join(root, "local_storage.db")

        if not os.path.exists(db_path):
            return False, "No se encontró la base de datos local para respaldar.", {}

        now_dt = datetime.datetime.now()
        timestamp_str = now_dt.strftime("%Y-%m-%d_%H%M%S")

        if not destino_archivo:
            default_dir = BackupManager.get_backup_config()["backup_dir"]
            os.makedirs(default_dir, exist_ok=True)
            destino_archivo = os.path.join(default_dir, f"Respaldo_Clinico_{timestamp_str}.clinicabak")

        # Asegurar extensión .clinicabak o .zip
        if not (destino_archivo.endswith(".clinicabak") or destino_archivo.endswith(".zip")):
            destino_archivo += ".clinicabak"

        # Extraer registros locales para incluirlos también en JSON legible
        cache = LocalCache()
        stats = {
            "fecha": now_dt.strftime("%d/%m/%Y %H:%M:%S"),
            "timestamp": now_dt.isoformat(),
            "pacientes": 0,
            "citas": 0,
            "sesiones": 0,
            "facturas": 0,
            "total_registros": 0
        }

        json_dump = {}
        try:
            with cache._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT collection_name, record_id, data_json, updated_at FROM local_records WHERE is_deleted = 0")
                rows = cursor.fetchall()
                for r in rows:
                    col = r["collection_name"]
                    if col not in json_dump:
                        json_dump[col] = []
                    try:
                        record_dict = json.loads(r["data_json"])
                    except Exception:
                        record_dict = {"raw": r["data_json"]}
                    record_dict["_id"] = r["record_id"]
                    record_dict["_updated_at"] = r["updated_at"]
                    json_dump[col].append(record_dict)

                stats["pacientes"] = len(json_dump.get("pacientes", []))
                stats["citas"] = len(json_dump.get("citas", []))
                stats["sesiones"] = len(json_dump.get("sesiones_clinicas", []))
                stats["facturas"] = len(json_dump.get("facturas", []))
                stats["total_registros"] = len(rows)
        except Exception as e:
            print(f"[WARN] No se pudo volcar JSON en respaldo: {e}")

        # Empaquetar todo en archivo ZIP (.clinicabak)
        temp_manifest = json.dumps(stats, indent=2, ensure_ascii=False)
        temp_json = json.dumps(json_dump, indent=2, ensure_ascii=False)

        try:
            with zipfile.ZipFile(destino_archivo, "w", zipfile.ZIP_DEFLATED) as zf:
                # 1. Base de datos SQLite
                zf.write(db_path, arcname="local_storage.db")
                # 2. JSON estructurado
                zf.writestr("datos_clinicos.json", temp_json)
                # 3. Manifiesto
                zf.writestr("manifest.json", temp_manifest)
                # 4. Llave de cifrado si existe
                vault_key = os.path.join(root, ".vault.key")
                if os.path.exists(vault_key):
                    zf.write(vault_key, arcname=".vault.key")
                # 5. Catálogo de fármacos registrados
                farmacos_json = os.path.join(root, "data", "farmacos_registrados.json")
                if os.path.exists(farmacos_json):
                    zf.write(farmacos_json, arcname="farmacos_registrados.json")

            # Actualizar última fecha de respaldo en config
            config = BackupManager.get_backup_config()
            config["last_backup_date"] = now_dt.strftime("%Y-%m-%d %H:%M:%S")
            BackupManager.save_backup_config(config)

            return True, destino_archivo, stats
        except Exception as e:
            return False, f"Error al escribir archivo de respaldo: {e}", stats

    @staticmethod
    def restaurar_respaldo(archivo_respaldo: str) -> tuple[bool, str]:
        """
        Restaura la base de datos local y archivos clínicos desde un archivo de respaldo.
        Crea una copia de seguridad preventiva automática de la base actual antes de restaurar.
        """
        if not os.path.exists(archivo_respaldo):
            return False, "El archivo de respaldo seleccionado no existe."

        if not zipfile.is_zipfile(archivo_respaldo):
            return False, "El archivo seleccionado no es un archivo de respaldo válido (.clinicabak o .zip)."

        root = app_dir()
        db_path = os.path.join(root, "local_storage.db")

        # 1. Crear copia de seguridad preventiva antes de sobreescribir
        if os.path.exists(db_path):
            pre_restore_bak = os.path.join(root, f"local_storage_prerestore_{int(datetime.datetime.now().timestamp())}.db")
            try:
                shutil.copy2(db_path, pre_restore_bak)
            except Exception as e:
                print(f"[WARN] No se pudo crear copia preventiva pre-restore: {e}")

        # 2. Extraer y restaurar componentes
        try:
            with zipfile.ZipFile(archivo_respaldo, "r") as zf:
                file_list = zf.namelist()

                if "local_storage.db" not in file_list:
                    return False, "El archivo de respaldo no contiene la base de datos local_storage.db."

                # Extraer local_storage.db
                zf.extract("local_storage.db", root)

                # Extraer .vault.key si está incluida
                if ".vault.key" in file_list:
                    zf.extract(".vault.key", root)

                # Extraer fármacos registrados si están incluidos
                if "farmacos_registrados.json" in file_list:
                    data_dir = os.path.join(root, "data")
                    os.makedirs(data_dir, exist_ok=True)
                    zf.extract("farmacos_registrados.json", data_dir)

            # Re-inicializar singleton de LocalCache para apuntar a la nueva base
            LocalCache._instance = None
            LocalCache()

            return True, "Base de datos y archivos clínicos restaurados exitosamente."
        except Exception as e:
            return False, f"Ocurrió un error al restaurar el respaldo: {e}"

    @staticmethod
    def rotar_respaldos_antiguos(backup_dir: str, max_retained: int = 10):
        """Elimina los respaldos automáticos más antiguos si exceden max_retained."""
        if not os.path.exists(backup_dir) or max_retained <= 0:
            return

        try:
            archivos = []
            for f in os.listdir(backup_dir):
                if f.startswith("Respaldo_") and (f.endswith(".clinicabak") or f.endswith(".zip")):
                    full = os.path.join(backup_dir, f)
                    archivos.append((os.path.getmtime(full), full))

            # Ordenar del más antiguo al más nuevo
            archivos.sort(key=lambda x: x[0])

            # Si exceden el límite, borrar los más viejos
            while len(archivos) > max_retained:
                antiguo = archivos.pop(0)
                try:
                    os.remove(antiguo[1])
                    print(f"[INFO] Respaldo antiguo rotado/eliminado: {antiguo[1]}")
                except Exception:
                    pass
        except Exception as e:
            print(f"[WARN] Error al rotar respaldos: {e}")

    @staticmethod
    def verificar_y_ejecutar_auto_backup() -> tuple[bool, str]:
        """
        Ejecuta el respaldo automático si está habilitado según la frecuencia configurada.
        """
        cfg = BackupManager.get_backup_config()
        if not cfg["auto_backup_enabled"]:
            return False, "Respaldo automático desactivado."

        freq = cfg["frequency"]
        last_str = cfg.get("last_backup_date", "")

        debe_ejecutar = False
        if not last_str or freq == "on_close":
            debe_ejecutar = True
        else:
            try:
                last_dt = datetime.datetime.strptime(last_str, "%Y-%m-%d %H:%M:%S")
                delta = datetime.datetime.now() - last_dt
                if freq == "daily" and delta.total_seconds() >= 86400:
                    debe_ejecutar = True
                elif freq == "weekly" and delta.total_seconds() >= 604800:
                    debe_ejecutar = True
            except Exception:
                debe_ejecutar = True

        if debe_ejecutar:
            dest_dir = cfg["backup_dir"]
            os.makedirs(dest_dir, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = os.path.join(dest_dir, f"Respaldo_Auto_{ts}.clinicabak")
            
            ok, msg, stats = BackupManager.crear_respaldo(filename)
            if ok:
                BackupManager.rotar_respaldos_antiguos(dest_dir, cfg["max_backups_retained"])
                return True, f"Respaldo automático creado en {filename}"
            return False, msg

        return False, "Aún no vence el intervalo para respaldo automático."

    @staticmethod
    def exportar_datos_completos(directorio_destino: str, formato: str = "csv") -> tuple[bool, str, list]:
        """
        Exporta los datos clínicos completos a archivos CSV individuales o a un solo JSON maestro.
        """
        if not os.path.exists(directorio_destino):
            try:
                os.makedirs(directorio_destino, exist_ok=True)
            except Exception as e:
                return False, f"No se pudo crear la carpeta de destino: {e}", []

        cache = LocalCache()
        colecciones = ["pacientes", "citas", "sesiones_clinicas", "facturas"]
        archivos_generados = []

        try:
            with cache._get_connection() as conn:
                cursor = conn.cursor()

                for col in colecciones:
                    cursor.execute("""
                        SELECT record_id, data_json, updated_at 
                        FROM local_records 
                        WHERE collection_name = ? AND is_deleted = 0
                    """, (col,))
                    rows = cursor.fetchall()
                    if not rows:
                        continue

                    records = []
                    all_keys = set(["_id", "_updated_at"])
                    for r in rows:
                        try:
                            d = json.loads(r["data_json"])
                        except Exception:
                            d = {"valor": r["data_json"]}
                        d["_id"] = r["record_id"]
                        d["_updated_at"] = r["updated_at"]
                        records.append(d)
                        all_keys.update(d.keys())

                    if formato == "json":
                        out_file = os.path.join(directorio_destino, f"export_{col}.json")
                        with open(out_file, "w", encoding="utf-8") as f:
                            json.dump(records, f, indent=2, ensure_ascii=False)
                        archivos_generados.append(out_file)
                    else:
                        # CSV
                        import csv
                        out_file = os.path.join(directorio_destino, f"export_{col}.csv")
                        headers = sorted(list(all_keys))
                        with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
                            writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
                            writer.writeheader()
                            for rec in records:
                                writer.writerow(rec)
                        archivos_generados.append(out_file)

            return True, f"Se exportaron {len(archivos_generados)} archivo(s) correctamente.", archivos_generados
        except Exception as e:
            return False, f"Error durante la exportación de datos: {e}", archivos_generados
