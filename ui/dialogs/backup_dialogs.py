# ui/dialogs/backup_dialogs.py
# Diálogos visuales para configuración de respaldo automático y exportación de datos

import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QCheckBox, QComboBox, QSpinBox, QLineEdit, QFileDialog, 
    QMessageBox, QFrame, QRadioButton, QButtonGroup
)
from core.backup_manager import BackupManager, get_default_backup_dir


class BackupConfigDialog(QDialog):
    """Diálogo para configurar el Respaldo Automático del sistema."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Respaldo Automático")
        self.setFixedSize(500, 380)
        self._cfg = BackupManager.get_backup_config()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Título
        title = QLabel("<b>💾 Configuración de Respaldo Automático</b>")
        title.setStyleSheet("font-size: 15px; color: #1e3a8a;")
        layout.addWidget(title)

        desc = QLabel("El sistema puede crear copias de seguridad automáticas de tus pacientes, historias clínicas y citas sin interrumpir tu trabajo.")
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 11.5px; color: #475569;")
        layout.addWidget(desc)

        # Marco de opciones
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        f_layout = QVBoxLayout(frame)
        f_layout.setSpacing(12)

        # Checkbox activar
        self.chk_enabled = QCheckBox("Activar respaldo automático periódico")
        self.chk_enabled.setChecked(self._cfg.get("auto_backup_enabled", False))
        self.chk_enabled.setStyleSheet("font-weight: bold; font-size: 12px; color: #0f172a;")
        self.chk_enabled.toggled.connect(self._toggle_options)
        f_layout.addWidget(self.chk_enabled)

        # Frecuencia
        freq_box = QHBoxLayout()
        lbl_freq = QLabel("Frecuencia:")
        lbl_freq.setStyleSheet("font-size: 12px; color: #334155;")
        self.cmb_freq = QComboBox()
        self.cmb_freq.addItem("Al cerrar el sistema (Recomendado)", "on_close")
        self.cmb_freq.addItem("Diario (cada 24 horas)", "daily")
        self.cmb_freq.addItem("Semanal (cada 7 días)", "weekly")

        current_freq = self._cfg.get("frequency", "on_close")
        idx = self.cmb_freq.findData(current_freq)
        if idx >= 0:
            self.cmb_freq.setCurrentIndex(idx)
        freq_box.addWidget(lbl_freq)
        freq_box.addWidget(self.cmb_freq, 1)
        f_layout.addLayout(freq_box)

        # Carpeta de destino
        lbl_dir = QLabel("Carpeta donde se guardarán los respaldos:")
        lbl_dir.setStyleSheet("font-size: 12px; color: #334155;")
        f_layout.addWidget(lbl_dir)

        dir_box = QHBoxLayout()
        self.txt_dir = QLineEdit(self._cfg.get("backup_dir", get_default_backup_dir()))
        self.txt_dir.setReadOnly(True)
        self.txt_dir.setStyleSheet("background: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 5px;")
        btn_browse = QPushButton("Examinar...")
        btn_browse.setStyleSheet("padding: 5px 12px;")
        btn_browse.clicked.connect(self._browse_dir)
        dir_box.addWidget(self.txt_dir, 1)
        dir_box.addWidget(btn_browse)
        f_layout.addLayout(dir_box)

        # Retención / Rotación
        ret_box = QHBoxLayout()
        lbl_ret = QLabel("Conservar como máximo:")
        lbl_ret.setStyleSheet("font-size: 12px; color: #334155;")
        self.spn_retained = QSpinBox()
        self.spn_retained.setRange(3, 50)
        self.spn_retained.setValue(self._cfg.get("max_backups_retained", 10))
        lbl_ret_post = QLabel("respaldos más recientes (los antiguos se rotan).")
        lbl_ret_post.setStyleSheet("font-size: 12px; color: #64748b;")
        ret_box.addWidget(lbl_ret)
        ret_box.addWidget(self.spn_retained)
        ret_box.addWidget(lbl_ret_post, 1)
        f_layout.addLayout(ret_box)

        layout.addWidget(frame)

        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        btn_save = QPushButton("💾 Guardar Configuración")
        btn_save.setStyleSheet("background: #2563eb; color: white; font-weight: bold; padding: 7px 16px; border-radius: 6px;")
        btn_save.clicked.connect(self._save)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)
        self._toggle_options(self.chk_enabled.isChecked())

    def _toggle_options(self, enabled: bool):
        self.cmb_freq.setEnabled(enabled)
        self.txt_dir.setEnabled(enabled)
        self.spn_retained.setEnabled(enabled)

    def _browse_dir(self):
        cur = self.txt_dir.text()
        d = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta para respaldos", cur)
        if d:
            self.txt_dir.setText(os.path.normpath(d))

    def _save(self):
        new_cfg = {
            "auto_backup_enabled": self.chk_enabled.isChecked(),
            "frequency": self.cmb_freq.currentData(),
            "backup_dir": self.txt_dir.text().strip(),
            "max_backups_retained": self.spn_retained.value()
        }
        BackupManager.save_backup_config(new_cfg)
        QMessageBox.information(
            self,
            "Configuración Guardada",
            "✅ La configuración de respaldo automático se ha guardado correctamente."
        )
        self.accept()


class ExportDataDialog(QDialog):
    """Diálogo para exportar todos los datos a Excel/CSV o JSON."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Exportar Datos Clínicos")
        self.setFixedSize(480, 260)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("<b>📊 Exportar Todos los Datos del Sistema</b>")
        title.setStyleSheet("font-size: 15px; color: #1e3a8a;")
        layout.addWidget(title)

        desc = QLabel("Exporta tus pacientes, citas, sesiones clínicas y facturación a formatos estándar abiertos.")
        desc.setWordWrap(True)
        desc.setStyleSheet("font-size: 11.5px; color: #475569;")
        layout.addWidget(desc)

        # Selección de formato
        fmt_box = QHBoxLayout()
        lbl_fmt = QLabel("<b>Formato:</b>")
        self.rad_csv = QRadioButton("CSV / Excel (.csv)")
        self.rad_csv.setChecked(True)
        self.rad_json = QRadioButton("JSON (.json)")
        fmt_box.addWidget(lbl_fmt)
        fmt_box.addWidget(self.rad_csv)
        fmt_box.addWidget(self.rad_json)
        fmt_box.addStretch()
        layout.addLayout(fmt_box)

        # Carpeta destino
        lbl_dir = QLabel("Carpeta donde se guardarán los archivos exportados:")
        layout.addWidget(lbl_dir)

        dir_box = QHBoxLayout()
        default_dir = os.path.join(os.path.expanduser("~"), "Documents", "Exportaciones_Clinicas")
        self.txt_dir = QLineEdit(default_dir)
        self.txt_dir.setReadOnly(True)
        btn_browse = QPushButton("Examinar...")
        btn_browse.clicked.connect(self._browse)
        dir_box.addWidget(self.txt_dir, 1)
        dir_box.addWidget(btn_browse)
        layout.addLayout(dir_box)

        # Botones
        btn_box = QHBoxLayout()
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_box.addWidget(btn_cancel)

        btn_export = QPushButton("🚀 Exportar Ahora")
        btn_export.setStyleSheet("background: #0284c7; color: white; font-weight: bold; padding: 7px 16px; border-radius: 6px;")
        btn_export.clicked.connect(self._do_export)
        btn_box.addWidget(btn_export)

        layout.addLayout(btn_box)

    def _browse(self):
        d = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta destino", self.txt_dir.text())
        if d:
            self.txt_dir.setText(os.path.normpath(d))

    def _do_export(self):
        target_dir = self.txt_dir.text().strip()
        fmt = "csv" if self.rad_csv.isChecked() else "json"

        ok, msg, files = BackupManager.exportar_datos_completos(target_dir, formato=fmt)
        if ok:
            archivos_str = "\n".join([f"• {os.path.basename(f)}" for f in files])
            QMessageBox.information(
                self,
                "Exportación Exitosa",
                f"✅ {msg}\n\n"
                f"Carpeta: {target_dir}\n\n"
                f"Archivos generados:\n{archivos_str}"
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Error de Exportación", msg)
