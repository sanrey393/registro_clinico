import os
import sys
import time
import zipfile
import urllib.request
import tempfile
import subprocess
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QMessageBox
)

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
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
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
        self.setWindowTitle("Actualización del Sistema")
        self.setFixedSize(420, 220)
        self.url = url
        self.nueva_version = nueva_version

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.lbl_title = QLabel(f"<b>Actualizando a la versión {nueva_version}</b>")
        self.lbl_title.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.lbl_title)

        self.lbl_status = QLabel("Iniciando descarga...")
        self.lbl_status.setStyleSheet("color: #555;")
        layout.addWidget(self.lbl_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.close)
        layout.addWidget(self.btn_cancel)

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
        2. Descomprime y sobreescribe los archivos en el directorio del programa (excluyendo .env y firebase_service_account.json si ya existen).
        3. Vuelve a iniciar la aplicación y se autoelimina.
        """
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        temp_dir = tempfile.gettempdir()
        bat_path = os.path.join(temp_dir, "install_update.bat")
        python_exe = sys.executable

        # Script PowerShell embebido en el BAT para descompresión limpia y reinicio
        bat_content = f"""@echo off
chcp 65001 > nul
title Actualizando Sistema Clinico...
echo Esperando que el sistema se cierre...
timeout /t 2 /nobreak > nul

echo Descomprimiendo archivos de la nueva version...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Expand-Archive -Path '{zip_path}' -DestinationPath '{app_dir}' -Force"

echo Limpiando temporales...
del /f /q "{zip_path}" > nul 2>&1

echo Reiniciando el sistema actualizado...
start "" "{python_exe}" "{os.path.join(app_dir, 'main.py')}"

del "%~f0" > nul 2>&1
exit
"""
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

        # Avisar y ejecutar el batch
        QMessageBox.information(
            self,
            "Actualización lista",
            "La actualización se ha descargado correctamente.\n\n"
            "El sistema se cerrará ahora, aplicará los cambios y se reiniciará automáticamente."
        )

        subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True)
        # Cerrar toda la aplicación
        sys.exit(0)

