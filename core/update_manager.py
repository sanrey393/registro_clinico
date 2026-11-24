# core/update_manager.py
# Gestor de comprobación de actualizaciones remotas en segundo plano

import json
import os
import urllib.request
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from core.app_paths import app_dir, resource_path

FALLBACK_VERSION = "2.0.0"
VERSION_JSON_URL = "https://raw.githubusercontent.com/sanrey393/registro_clinico/main/version.json"
GITHUB_RELEASES_API = "https://api.github.com/repos/sanrey393/registro_clinico/releases/latest"


def get_current_version() -> str:
    """Lee la versión actual desde version.json; usa FALLBACK_VERSION si no está disponible."""
    candidates = [
        os.path.join(app_dir(), "version.json"),
        resource_path("version.json"),
    ]
    for path in candidates:
        if path and os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                ver = str(data.get("version", "")).strip().lstrip("vV")
                if ver:
                    return ver
            except Exception as e:
                print(f"[WARN] No se pudo leer {path}: {e}")
    return FALLBACK_VERSION


CURRENT_VERSION = get_current_version()


def parse_version_tuple(v_str: str) -> tuple:
    """Convierte una cadena como 'v1.0.2' o '1.0.2' a una tupla de enteros (1, 0, 2)."""
    clean = v_str.strip().lstrip("vV")
    parts = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


def is_newer_version(remote_ver: str, current_ver: str = CURRENT_VERSION) -> bool:
    """Devuelve True si remote_ver es estrictamente superior a current_ver."""
    return parse_version_tuple(remote_ver) > parse_version_tuple(current_ver)


class CheckUpdateWorker(QThread):
    """Hilo secundario para comprobar si existen nuevas versiones sin congelar la interfaz."""
    update_available = pyqtSignal(str, str, str)  # (version, download_url, notes)
    up_to_date = pyqtSignal(str)                   # (current_version)
    check_error = pyqtSignal(str)                  # (error_message)

    def run(self):
        remote_version = None
        download_url = ""
        notes = ""

        # 1. Intentar consultar version.json en el repositorio oficial (rápido, sin límites de cuota)
        try:
            req = urllib.request.Request(
                VERSION_JSON_URL,
                headers={"User-Agent": "RegistroClinico-App"}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode("utf-8"))
                remote_version = data.get("version", "").strip()
                download_url = data.get("download_url", "")
                notes = data.get("notes", "Mejoras de rendimiento y correcciones del sistema.")
        except Exception as e_json:
            print(f"[DEBUG] No se pudo obtener version.json: {e_json}")

        # 2. Si falló version.json, intentar la API de GitHub Releases
        if not remote_version:
            try:
                req = urllib.request.Request(
                    GITHUB_RELEASES_API,
                    headers={"User-Agent": "RegistroClinico-App"}
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    rel_data = json.loads(response.read().decode("utf-8"))
                    remote_version = rel_data.get("tag_name", "").lstrip("vV").strip()
                    notes = rel_data.get("body", "Nueva versión disponible.")
                    # Buscar asset zip
                    assets = rel_data.get("assets", [])
                    for a in assets:
                        if a.get("name", "").endswith(".zip"):
                            download_url = a.get("browser_download_url", "")
                            break
                    if not download_url and assets:
                        download_url = assets[0].get("browser_download_url", "")
            except Exception as e_api:
                print(f"[DEBUG] No se pudo consultar GitHub Releases: {e_api}")

        # Si no se pudo obtener ninguna información
        if not remote_version:
            self.check_error.emit("No se pudo conectar con el servidor de actualizaciones. Verifique su conexión a internet.")
            return

        # Comparar versiones
        if is_newer_version(remote_version, CURRENT_VERSION):
            self.update_available.emit(remote_version, download_url, notes)
        else:
            self.up_to_date.emit(CURRENT_VERSION)


class UpdateManager(QObject):
    """Manejador global para disparar la verificación de actualizaciones."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None

    def _on_worker_finished(self):
        worker = self._worker
        self._worker = None
        if worker is not None:
            worker.deleteLater()

    def stop(self):
        """Detiene limpiamente el hilo de verificación si sigue activo al cerrar la app."""
        if self._worker and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.wait(3000)

    def check(self, on_update_available=None, on_up_to_date=None, on_error=None):
        """Inicia la comprobación asíncrona."""
        if self._worker and self._worker.isRunning():
            return

        self._worker = CheckUpdateWorker(parent=self)
        if on_update_available:
            self._worker.update_available.connect(on_update_available)
        if on_up_to_date:
            self._worker.up_to_date.connect(on_up_to_date)
        if on_error:
            self._worker.check_error.connect(on_error)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.start()
