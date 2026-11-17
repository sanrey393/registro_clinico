# database/sync_manager.py
# Gestor de sincronización automática en segundo plano entre SQLite y Firebase Firestore

import time
import uuid
import socket
from datetime import datetime
from PyQt6.QtCore import QThread, pyqtSignal
from database.local_cache import LocalCache

def is_internet_available() -> bool:
    """Verifica si hay conexión a internet intentando resolver y conectar a un DNS público."""
    try:
        # Intenta conectar al DNS de Google (8.8.8.8) en el puerto 53
        socket.setdefaulttimeout(3)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("8.8.8.8", 53))
        s.close()
        return True
    except OSError:
        return False

class SyncWorker(QThread):
    sync_status = pyqtSignal(str, bool)  # mensaje, is_online

    def __init__(self, firebase_manager):
        super().__init__()
        self.firebase = firebase_manager
        self.cache = LocalCache()
        self._running = True

    def stop(self):
        self._running = False
        self.wait()

    def run(self):
        """Ciclo continuo que verifica conectividad cada 10 segundos y sincroniza."""
        while self._running:
            online = is_internet_available() and self.firebase.is_configured()
            
            if online:
                try:
                    self._sync_pending_records()
                    self._pull_latest_data()
                    self.sync_status.emit("En línea (Sincronizado)", True)
                except Exception as e:
                    print(f"[WARN] Error en ciclo de sincronización: {e}")
                    self.sync_status.emit("En línea (Error al sincronizar)", True)
            else:
                self.sync_status.emit("Modo Fuera de Línea (Offline)", False)

            # Esperar 15 segundos antes de la siguiente verificación
            for _ in range(15):
                if not self._running:
                    break
                time.sleep(1)

    def _sync_pending_records(self):
        """Sube a Firestore los registros que se crearon o modificaron sin internet."""
        pending = self.cache.get_pending_sync()
        if not pending:
            return

        print(f"[SYNC] Subiendo {len(pending)} registros pendientes a Firebase...")
        for item in pending:
            col = item["collection"]
            rec_id = item["record_id"]
            data = item["data"]
            is_del = item["is_deleted"]

            try:
                doc_ref = self.firebase._db.collection(col).document(rec_id)
                if is_del:
                    doc_ref.delete()
                    self.cache.mark_as_synced(col, rec_id, is_deleted=True)
                else:
                    # Limpiar campo id interno si existiese
                    upload_data = {k: v for k, v in data.items() if k != "id"}
                    upload_data["synced_at"] = datetime.now().isoformat()
                    doc_ref.set(upload_data, merge=True)
                    self.cache.mark_as_synced(col, rec_id, is_deleted=False)
                print(f"[SYNC] Registro sincronizado: {col}/{rec_id}")
            except Exception as e:
                print(f"[WARN] Falló sincronizar {col}/{rec_id}: {e}")

    def _pull_latest_data(self):
        """Descarga de Firestore las novedades a la base de datos local SQLite."""
        colecciones = [
            "pacientes", "historias_clinicas", "citas", 
            "sesiones_clinicas", "prescripciones", "facturas", "farmacos"
        ]
        
        for col in colecciones:
            try:
                # Traer documentos de Firestore
                docs = self.firebase._db.collection(col).limit(100).stream()
                for doc in docs:
                    d = doc.to_dict()
                    d["id"] = doc.id
                    # Guardar en SQLite marcado como ya sincronizado
                    self.cache.save_record(col, doc.id, d, is_synced=True)
            except Exception as e:
                pass

