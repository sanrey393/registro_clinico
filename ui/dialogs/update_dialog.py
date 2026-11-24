import os
import sys
import time
import zipfile
import urllib.request
import tempfile
import subprocess
from PyQt6.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox, QTextEdit
)
from core.app_paths import app_dir as get_app_root


class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, url: str, parent=None):
        super().__init__(parent)
        self.url = url
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def _cleanup_file(self, path: str):
        if path and os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    def run(self):
        dest_file = ""
        try:
            self.status.emit("Conectando con el servidor...")
            temp_dir = tempfile.gettempdir()
            is_exe = self.url.split("?")[0].lower().endswith(".exe")
            ext = ".exe" if is_exe else ".zip"
            dest_file = os.path.join(temp_dir, f"update_{int(time.time())}{ext}")

            req = urllib.request.Request(
                self.url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) RegistroClinico-Updater"}
            )

            with urllib.request.urlopen(req, timeout=30) as response, open(dest_file, "wb") as out_file:
                total_length = response.getheader('content-length')
                if total_length:
                    total_length = int(total_length)

                downloaded = 0
                block_size = 8192
                self.status.emit("Descargando actualización...")

                while True:
                    if self._cancelled or self.isInterruptionRequested():
                        out_file.close()
                        self._cleanup_file(dest_file)
                        self.cancelled.emit()
                        return

                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    downloaded += len(buffer)
                    out_file.write(buffer)

                    if total_length:
                        percent = int((downloaded / total_length) * 100)
                        self.progress.emit(percent)
                        self.status.emit(f"Descargando: {downloaded // 1024} KB / {total_length // 1024} KB ({percent}%)")
                    else:
                        self.status.emit(f"Descargando: {downloaded // 1024} KB...")

            if self._cancelled or self.isInterruptionRequested():
                self._cleanup_file(dest_file)
                self.cancelled.emit()
                return

            self.status.emit("Descarga completada. Verificando archivo...")
            if is_exe:
                with open(dest_file, "rb") as f:
                    if f.read(2) != b"MZ":
                        raise ValueError("El archivo descargado no es un instalador .exe válido.")
            else:
                if not zipfile.is_zipfile(dest_file):
                    raise ValueError("El archivo descargado no es un paquete ZIP válido.")

            self.finished.emit(dest_file)

        except Exception as e:
            self._cleanup_file(dest_file)
            if not self._cancelled:
                self.error.emit(str(e))


class UpdateDialog(QDialog):
    def __init__(self, parent, nueva_version: str, url: str, notas: str = "", auto_start: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Actualización de PSIQUE")
        self.setFixedSize(500, 340)
        self.url = url
        self.nueva_version = nueva_version
        self.notas = notas
        self.worker = None

        app = QApplication.instance()
        self._dark = (
            bool(parent._is_dark_mode)
            if (parent is not None and hasattr(parent, "_is_dark_mode"))
            else (app.palette().window().color().lightness() < 128 if app is not None else False)
        )

        self._build_ui()
        if auto_start:
            QTimer.singleShot(0, self._start_download)

    def _build_ui(self):
        if self._dark:
            bg_dlg = "#0f172a"
            title_col = "#f8fafc"
            label_col = "#e2e8f0"
            muted_col = "#94a3b8"
            notes_bg = "#1e293b"
            notes_border = "#334155"
            notes_text = "#f1f5f9"
            sec_btn_bg = "#1e293b"
            sec_btn_border = "#334155"
            sec_btn_text = "#e2e8f0"
            sec_btn_hover = "#334155"
            bar_bg = "#1e293b"
        else:
            bg_dlg = "#ffffff"
            title_col = "#0b2b2e"
            label_col = "#1e293b"
            muted_col = "#475569"
            notes_bg = "#f8fafc"
            notes_border = "#cbd5e1"
            notes_text = "#1e293b"
            sec_btn_bg = "#f1f5f9"
            sec_btn_border = "#cbd5e1"
            sec_btn_text = "#334155"
            sec_btn_hover = "#e2e8f0"
            bar_bg = "#e2e8f0"

        self.setObjectName("PsiqueUpdateDialog")
        self.setStyleSheet(f"""
            QDialog#PsiqueUpdateDialog {{
                background: {bg_dlg};
                font-family: "Segoe UI", "Inter", sans-serif;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)

        # Encabezado
        self.lbl_title = QLabel(f"Nueva versión v{self.nueva_version} disponible")
        self.lbl_title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {title_col}; background: transparent;"
        )
        layout.addWidget(self.lbl_title)

        # Notas de la versión
        lbl_notes_title = QLabel("Novedades y cambios:")
        lbl_notes_title.setStyleSheet(
            f"font-size: 12.5px; font-weight: 700; color: {label_col}; background: transparent;"
        )
        layout.addWidget(lbl_notes_title)

        self.txt_notes = QTextEdit()
        self.txt_notes.setReadOnly(True)
        self.txt_notes.setPlainText(self.notas if self.notas else "Mejoras de rendimiento y correcciones del sistema.")
        self.txt_notes.setStyleSheet(f"""
            QTextEdit {{
                background: {notes_bg};
                border: 1px solid {notes_border};
                border-radius: 8px;
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 12px;
                color: {notes_text};
                padding: 8px 10px;
            }}
        """)
        self.txt_notes.setFixedHeight(95)
        layout.addWidget(self.txt_notes)

        # Estado y progreso
        self.lbl_status = QLabel("Presiona 'Actualizar Ahora' para iniciar.")
        self.lbl_status.setStyleSheet(f"color: {muted_col}; font-size: 12px; background: transparent;")
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background: {bar_bg};
                border: 1px solid {notes_border};
                border-radius: 6px;
                text-align: center;
                color: {title_col};
                font-weight: 600;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background: #0f766e;
                border-radius: 5px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Recordar más tarde")
        self.btn_cancel.setStyleSheet(f"""
            QPushButton {{
                background: {sec_btn_bg};
                color: {sec_btn_text};
                border: 1px solid {sec_btn_border};
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 12.5px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {sec_btn_hover}; }}
        """)
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("Actualizar Ahora")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background: #0f766e;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 700;
                font-size: 12.5px;
            }
            QPushButton:hover { background: #14b8a6; }
        """)
        self.btn_start.clicked.connect(self._start_download)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def _start_download(self):
        if not self.url:
            QMessageBox.warning(self, "Aviso", "No se especificó la dirección de descarga para esta actualización.")
            return
        if self.worker and self.worker.isRunning():
            return

        self.btn_start.setEnabled(False)
        self.btn_cancel.setText("Cancelar")
        self.progress_bar.setVisible(True)
        self.lbl_status.setText("Iniciando descarga...")

        self.worker = DownloadWorker(self.url, parent=self)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self._on_download_complete)
        self.worker.error.connect(self._on_download_error)
        self.worker.cancelled.connect(self._on_download_cancelled)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.start()

    def _on_download_cancelled(self):
        self.btn_cancel.setText("Cerrar")
        self.btn_start.setEnabled(True)
        self.lbl_status.setText("Descarga cancelada.")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.worker.requestInterruption()
            self.worker.wait(3000)
        event.accept()

    def _on_download_complete(self, zip_path: str):
        self.lbl_status.setText("¡Descarga completada! Preparando reinicio...")
        self.btn_cancel.setEnabled(False)
        self._aplicar_actualizacion(zip_path)

    def _on_download_error(self, err_msg: str):
        self.btn_cancel.setText("Cerrar")
        self.btn_start.setEnabled(True)
        self.lbl_status.setText(f"<font color='red'>Error al descargar: {err_msg}</font>")
        QMessageBox.critical(
            self,
            "Error de actualización",
            f"No se pudo descargar la actualización:\n\n{err_msg}"
        )

    def _aplicar_actualizacion(self, zip_path: str):
        """
        Aplica la actualización descargada:
        - Si es un instalador .exe (InnoSetup), lo ejecuta directamente y cierra la app.
        - Si es un paquete .zip, crea un .bat auxiliar que respalda credenciales,
          descomprime sobre el directorio raíz, restaura credenciales y reinicia.
        """
        if zip_path.lower().endswith(".exe"):
            QMessageBox.information(
                self,
                "Instalador listo",
                "El instalador de la nueva versión se ha descargado correctamente.\n\n"
                "El sistema se cerrará ahora para ejecutar el instalador."
            )
            creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            subprocess.Popen([zip_path], creationflags=creationflags)
            self.accept()
            app = QApplication.instance()
            if app is not None:
                app.quit()
            return

        target_dir = get_app_root()
        temp_dir = tempfile.gettempdir()
        backup_dir = os.path.join(temp_dir, "clinic_backup_update")
        bat_path = os.path.join(temp_dir, "install_update.bat")

        is_frozen = getattr(sys, "frozen", False)
        exe_path = sys.executable

        if is_frozen:
            restart_line = f'start "" "{exe_path}"'
        else:
            main_script = os.path.join(target_dir, "main.py")
            restart_line = f'start "" "{exe_path}" "{main_script}"'

        bat_content = f"""@echo off
chcp 65001 > nul
title Actualizando Sistema Clínico...
echo ========================================================
echo       APLICANDO ACTUALIZACIÓN DEL SISTEMA CLÍNICO
echo ========================================================
echo Esperando a que el sistema se cierre por completo...
timeout /t 3 /nobreak > nul

:: 1. Respaldo preventivo de credenciales y datos locales
echo Protegiendo base de datos y licencias locales...
if not exist "{backup_dir}" mkdir "{backup_dir}"
if exist "{target_dir}\\.env" copy /y "{target_dir}\\.env" "{backup_dir}\\.env" > nul
if exist "{target_dir}\\firebase_service_account.json" copy /y "{target_dir}\\firebase_service_account.json" "{backup_dir}\\firebase_service_account.json" > nul
if exist "{target_dir}\\local_storage.db" copy /y "{target_dir}\\local_storage.db" "{backup_dir}\\local_storage.db" > nul
if exist "{target_dir}\\.license.dat" copy /y "{target_dir}\\.license.dat" "{backup_dir}\\.license.dat" > nul
if exist "{target_dir}\\.vault.key" copy /y "{target_dir}\\.vault.key" "{backup_dir}\\.vault.key" > nul

:: 2. Descomprimir archivos de la nueva versión
echo Descomprimiendo nueva versión en {target_dir}...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path '{zip_path}' -DestinationPath '{target_dir}' -Force"

:: 3. Restaurar credenciales y datos si fueron sobreescritos
echo Restaurando credenciales del usuario...
if exist "{backup_dir}\\.env" copy /y "{backup_dir}\\.env" "{target_dir}\\.env" > nul
if exist "{backup_dir}\\firebase_service_account.json" copy /y "{backup_dir}\\firebase_service_account.json" "{target_dir}\\firebase_service_account.json" > nul
if exist "{backup_dir}\\local_storage.db" copy /y "{backup_dir}\\local_storage.db" "{target_dir}\\local_storage.db" > nul
if exist "{backup_dir}\\.license.dat" copy /y "{backup_dir}\\.license.dat" "{target_dir}\\.license.dat" > nul
if exist "{backup_dir}\\.vault.key" copy /y "{backup_dir}\\.vault.key" "{target_dir}\\.vault.key" > nul
rmdir /s /q "{backup_dir}" > nul 2>&1

:: 4. Limpieza de temporales
del /f /q "{zip_path}" > nul 2>&1

:: 5. Reiniciar aplicación actualizada
echo Reiniciando el sistema...
{restart_line}

(goto) 2>nul & del "%~f0"
exit
"""
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

        QMessageBox.information(
            self,
            "Actualización lista",
            "La actualización se ha descargado correctamente.\n\n"
            "El sistema se cerrará en un momento, aplicará los cambios y se reiniciará automáticamente."
        )

        creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        subprocess.Popen(["cmd.exe", "/c", bat_path], creationflags=creationflags)
        self.accept()
        app = QApplication.instance()
        if app is not None:
            app.quit()
