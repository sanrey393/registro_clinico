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
    def crear_respaldo(destino_archivo: str = None, db=None) -> tuple[bool, str, dict]:
        """
        Crea un paquete de respaldo seguro comprimido (.clinicabak / .zip).
        Si `db` está conectado a Firestore, exporta primero todas las colecciones
        activas (pacientes, historias_clinicas, citas, sesiones_clinicas, recetas)
        y las sincroniza en local_storage.db antes de empaquetar.
        """
        root = app_dir()
        db_path = os.path.join(root, "local_storage.db")

        now_dt = datetime.datetime.now()
        timestamp_str = now_dt.strftime("%Y-%m-%d_%H%M%S")

        if not destino_archivo:
            default_dir = BackupManager.get_backup_config()["backup_dir"]
            os.makedirs(default_dir, exist_ok=True)
            destino_archivo = os.path.join(default_dir, f"Respaldo_Clinico_{timestamp_str}.clinicabak")

        if not (destino_archivo.endswith(".clinicabak") or destino_archivo.endswith(".zip")):
            destino_archivo += ".clinicabak"

        colecciones = [
            "pacientes",
            "historias_clinicas",
            "citas",
            "sesiones_clinicas",
            "recetas",
        ]

        cache = LocalCache()
        json_dump = {c: [] for c in colecciones}

        # 1. Si hay conexión a Firestore, extraer colecciones reales del usuario y volcarlas a SQLite
        uso_firestore = False
        if db is not None and hasattr(db, "is_configured") and db.is_configured():
            try:
                uid = db.get_current_user_id() if hasattr(db, "get_current_user_id") else ""
                with cache._get_connection() as conn:
                    cur = conn.cursor()
                    for col in colecciones:
                        query = db._db.collection(col)
                        if uid:
                            query = query.where("user_id", "==", uid)
                        for doc in query.stream():
                            rec = doc.to_dict() or {}
                            rec_id = doc.id
                            rec["_id"] = rec_id
                            rec["id"] = rec.get("id") or rec_id
                            json_dump[col].append(rec)
                            cur.execute(
                                """
                                INSERT OR REPLACE INTO local_records
                                (collection_name, record_id, data_json, is_synced, is_deleted, updated_at, user_id)
                                VALUES (?, ?, ?, 1, 0, ?, ?)
                                """,
                                (
                                    col,
                                    rec_id,
                                    json.dumps(rec, ensure_ascii=False, default=str),
                                    now_dt.isoformat(),
                                    uid or rec.get("user_id", ""),
                                ),
                            )
                    conn.commit()
                uso_firestore = True
            except Exception as e:
                print(f"[WARN] Error leyendo Firestore en respaldo (usando caché local): {e}")

        # 2. Fallback o complemento desde SQLite local_records
        if not uso_firestore:
            if not os.path.exists(db_path):
                return False, "No se encontró la base de datos local para respaldar.", {}
            try:
                with cache._get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT collection_name, record_id, data_json, updated_at "
                        "FROM local_records WHERE is_deleted = 0"
                    )
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
                        record_dict["id"] = record_dict.get("id") or r["record_id"]
                        record_dict["_updated_at"] = r["updated_at"]
                        json_dump[col].append(record_dict)
            except Exception as e:
                print(f"[WARN] No se pudo volcar JSON en respaldo: {e}")

        if not os.path.exists(db_path):
            return False, "No se encontró la base de datos local para respaldar.", {}

        total_reg = sum(len(v) for v in json_dump.values())
        stats = {
            "fecha": now_dt.strftime("%d/%m/%Y %H:%M:%S"),
            "timestamp": now_dt.isoformat(),
            "pacientes": len(json_dump.get("pacientes", [])),
            "historias_clinicas": len(json_dump.get("historias_clinicas", [])),
            "citas": len(json_dump.get("citas", [])),
            "sesiones": len(json_dump.get("sesiones_clinicas", [])),
            "recetas": len(json_dump.get("recetas", [])),
            "total_registros": total_reg,
        }

        temp_manifest = json.dumps(stats, indent=2, ensure_ascii=False)
        temp_json = json.dumps(json_dump, indent=2, ensure_ascii=False, default=str)

        try:
            with zipfile.ZipFile(destino_archivo, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(db_path, arcname="local_storage.db")
                zf.writestr("datos_clinicos.json", temp_json)
                zf.writestr("manifest.json", temp_manifest)
                vault_key = os.path.join(root, ".vault.key")
                if os.path.exists(vault_key):
                    zf.write(vault_key, arcname=".vault.key")
                farmacos_json = os.path.join(root, "data", "farmacos_registrados.json")
                if os.path.exists(farmacos_json):
                    zf.write(farmacos_json, arcname="farmacos_registrados.json")
                recetas_local = os.path.join(root, "recetas_guardadas.json")
                if os.path.exists(recetas_local):
                    zf.write(recetas_local, arcname="recetas_guardadas.json")

            config = BackupManager.get_backup_config()
            config["last_backup_date"] = now_dt.strftime("%Y-%m-%d %H:%M:%S")
            BackupManager.save_backup_config(config)

            return True, destino_archivo, stats
        except Exception as e:
            return False, f"Error al escribir archivo de respaldo: {e}", stats

    @staticmethod
    def restaurar_respaldo(archivo_respaldo: str, db=None) -> tuple[bool, str]:
        """
        Restaura la base de datos local, archivos clínicos y (si Firestore está activo)
        sincroniza los registros restaurados en la nube bajo el usuario actual.
        """
        if not os.path.exists(archivo_respaldo):
            return False, "El archivo de respaldo seleccionado no existe."

        es_db_directo = archivo_respaldo.lower().endswith(".db")
        if not es_db_directo and not zipfile.is_zipfile(archivo_respaldo):
            return False, "El archivo seleccionado no es un respaldo válido (.clinicabak, .zip o .db)."

        root = app_dir()
        db_path = os.path.join(root, "local_storage.db")

        # 1. Copia preventiva de la base actual
        if os.path.exists(db_path):
            pre_restore_bak = os.path.join(
                root, f"local_storage_prerestore_{int(datetime.datetime.now().timestamp())}.db"
            )
            try:
                shutil.copy2(db_path, pre_restore_bak)
            except Exception as e:
                print(f"[WARN] No se pudo crear copia preventiva pre-restore: {e}")

        json_dump = {}
        try:
            if es_db_directo:
                shutil.copy2(archivo_respaldo, db_path)
            else:
                with zipfile.ZipFile(archivo_respaldo, "r") as zf:
                    file_list = zf.namelist()
                    if "local_storage.db" not in file_list and "datos_clinicos.json" not in file_list:
                        return False, "El respaldo no contiene local_storage.db ni datos_clinicos.json."

                    if "local_storage.db" in file_list:
                        zf.extract("local_storage.db", root)
                    if ".vault.key" in file_list:
                        zf.extract(".vault.key", root)
                    if "farmacos_registrados.json" in file_list:
                        data_dir = os.path.join(root, "data")
                        os.makedirs(data_dir, exist_ok=True)
                        zf.extract("farmacos_registrados.json", data_dir)
                    if "recetas_guardadas.json" in file_list:
                        zf.extract("recetas_guardadas.json", root)
                    if "datos_clinicos.json" in file_list:
                        try:
                            json_dump = json.loads(zf.read("datos_clinicos.json").decode("utf-8"))
                        except Exception as e_json:
                            print(f"[WARN] No se pudo parsear datos_clinicos.json: {e_json}")

            # Re-inicializar LocalCache
            LocalCache._instance = None
            cache = LocalCache()

            uid = ""
            if db is not None and hasattr(db, "get_current_user_id"):
                uid = db.get_current_user_id() or ""

            # Si no venía datos_clinicos.json, leer desde local_records del SQLite restaurado
            if not json_dump and os.path.exists(db_path):
                with cache._get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT collection_name, record_id, data_json "
                        "FROM local_records WHERE is_deleted = 0"
                    )
                    for row in cur.fetchall():
                        col = row["collection_name"]
                        json_dump.setdefault(col, [])
                        try:
                            d = json.loads(row["data_json"])
                        except Exception:
                            continue
                        d["_id"] = row["record_id"]
                        d["id"] = d.get("id") or row["record_id"]
                        json_dump[col].append(d)

            # Reasignar user_id en local_records al usuario activo para que el modo offline funcione
            if uid and os.path.exists(db_path):
                try:
                    with cache._get_connection() as conn:
                        cur = conn.cursor()
                        cur.execute("UPDATE local_records SET user_id = ?", (uid,))
                        conn.commit()
                except Exception as e_uid:
                    print(f"[WARN] No se pudo reasignar user_id local: {e_uid}")

            # 3. Sincronizar registros restaurados hacia Firestore si está conectado
            subidos_nube = 0
            if db is not None and hasattr(db, "is_configured") and db.is_configured() and json_dump:
                now_iso = datetime.datetime.now().isoformat()
                batch = db._db.batch()
                ops_in_batch = 0
                for col, records in json_dump.items():
                    if not isinstance(records, list):
                        continue
                    for rec in records:
                        if not isinstance(rec, dict):
                            continue
                        rec_id = str(rec.get("_id") or rec.get("id") or "").strip()
                        if not rec_id:
                            continue
                        payload = {
                            k: v for k, v in rec.items()
                            if k not in ("_id", "_updated_at")
                        }
                        if uid:
                            payload["user_id"] = uid
                        doc_ref = db._db.collection(col).document(rec_id)
                        batch.set(doc_ref, payload, merge=True)
                        ops_in_batch += 1
                        subidos_nube += 1
                        if ops_in_batch >= 400:
                            batch.commit()
                            batch = db._db.batch()
                            ops_in_batch = 0
                if ops_in_batch > 0:
                    batch.commit()

                # Asegurar también caché local consistente
                with cache._get_connection() as conn:
                    cur = conn.cursor()
                    for col, records in json_dump.items():
                        if not isinstance(records, list):
                            continue
                        for rec in records:
                            if not isinstance(rec, dict):
                                continue
                            rec_id = str(rec.get("_id") or rec.get("id") or "").strip()
                            if not rec_id:
                                continue
                            cur.execute(
                                """
                                INSERT OR REPLACE INTO local_records
                                (collection_name, record_id, data_json, is_synced, is_deleted, updated_at, user_id)
                                VALUES (?, ?, ?, 1, 0, ?, ?)
                                """,
                                (col, rec_id, json.dumps(rec, ensure_ascii=False, default=str), now_iso, uid),
                            )
                    conn.commit()

            n_pac = len(json_dump.get("pacientes", []))
            n_his = len(json_dump.get("historias_clinicas", []))
            n_cit = len(json_dump.get("citas", []))
            n_ses = len(json_dump.get("sesiones_clinicas", []))
            n_rec = len(json_dump.get("recetas", []))
            detalle = (
                f"Pacientes: {n_pac} | Historias: {n_his} | Citas: {n_cit} | "
                f"Sesiones: {n_ses} | Recetas: {n_rec}"
            )
            if subidos_nube:
                return True, f"Respaldo restaurado y sincronizado en la nube.\n{detalle}"
            return True, f"Base de datos local restaurada.\n{detalle}"
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
