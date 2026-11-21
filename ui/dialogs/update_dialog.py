import os
import sys
import time
import zipfile
import urllib.request
import tempfile
import subprocess
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox, QTextEdit
)
from core.app_paths import app_dir as get_app_root


class DownloadWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            self.status.emit("Conectando con el servidor...")
            temp_dir = tempfile.gettempdir()
            dest_file = os.path.join(temp_dir, f"update_{int(time.time())}.zip")

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

            self.status.emit("Descarga completada. Verificando archivo...")
            # Verificar si es un ZIP válido
            if not zipfile.is_zipfile(dest_file):
                raise ValueError("El archivo descargado no es un paquete ZIP válido.")

            self.finished.emit(dest_file)

        except Exception as e:
            self.error.emit(str(e))


class UpdateDialog(QDialog):
    def __init__(self, parent, nueva_version: str, url: str, notas: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Actualización Disponible")
        self.setFixedSize(480, 320)
        self.url = url
        self.nueva_version = nueva_version
        self.notas = notas
        self.worker = None

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)

        # Encabezado
        self.lbl_title = QLabel(f"<b>✨ ¡Nueva versión {self.nueva_version} disponible!</b>")
        self.lbl_title.setStyleSheet("font-size: 15px; color: #1e3a8a;")
        layout.addWidget(self.lbl_title)

        # Notas de la versión
        lbl_notes_title = QLabel("Novedades y cambios:")
        lbl_notes_title.setStyleSheet("font-size: 12px; font-weight: bold; color: #475569;")
        layout.addWidget(lbl_notes_title)

        self.txt_notes = QTextEdit()
        self.txt_notes.setReadOnly(True)
        self.txt_notes.setPlainText(self.notas if self.notas else "Mejoras de rendimiento y correcciones del sistema.")
        self.txt_notes.setStyleSheet("""
            QTextEdit {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 11px;
                color: #334155;
                padding: 6px;
            }
        """)
        self.txt_notes.setFixedHeight(90)
        layout.addWidget(self.txt_notes)

        # Estado y progreso
        self.lbl_status = QLabel("Presiona 'Actualizar Ahora' para iniciar.")
        self.lbl_status.setStyleSheet("color: #64748b; font-size: 11px;")
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.btn_cancel = QPushButton("Recordar más tarde")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
            }
            QPushButton:hover { background: #e2e8f0; }
        """)
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        self.btn_start = QPushButton("🚀 Actualizar Ahora")
        self.btn_start.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        self.btn_start.clicked.connect(self._start_download)
        btn_layout.addWidget(self.btn_start)

        layout.addLayout(btn_layout)

    def _start_download(self):
        if not self.url:
            QMessageBox.warning(self, "Aviso", "No se especificó la dirección de descarga para esta actualización.")
            return

        self.btn_start.setEnabled(False)
        self.btn_cancel.setText("Cancelar")
        self.progress_bar.setVisible(True)
        self.lbl_status.setText("Iniciando descarga...")

        self.worker = DownloadWorker(self.url)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.lbl_status.setText)
        self.worker.finished.connect(self._on_download_complete)
        self.worker.error.connect(self._on_download_error)
        self.worker.start()

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
        Crea un script .bat auxiliar que:
        1. Espera a que la app actual termine de cerrarse por completo.
        2. Hace respaldo preventivo de .env, firebase_service_account.json, local_storage.db y .license.dat.
        3. Descomprime y sobreescribe los archivos en el directorio raíz del programa.
        4. Restaura los archivos de credenciales/licencia del usuario.
        5. Vuelve a iniciar la aplicación y se autoelimina.
        """
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

del "%~f0" > nul 2>&1
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

        subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True)
        sys.exit(0)
