# ui/dialogs/license_dialog.py
# Ventana moderna para la activación de licencia del sistema

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QClipboard
from core.license_manager import LicenseManager

class LicenseDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Activación de Licencia - Sistema Clínico")
        self.setFixedSize(500, 380)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)
        self.db = db_manager
        self.mgr = LicenseManager()
        self.activated = False

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        # Encabezado
        title = QLabel("🔒 Activación de Licencia de Equipo")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e3a8a;")
        layout.addWidget(title)

        desc = QLabel(
            "Esta copia del Sistema Clínico no está activada para esta computadora.\n"
            "Para autorizar el uso en este dispositivo, proporciona el siguiente código al desarrollador:"
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #475569; font-size: 13px;")
        layout.addWidget(desc)

        # Caja de Machine ID con botón Copiar
        mid_box = QFrame()
        mid_box.setStyleSheet("background: #f1f5f9; border-radius: 8px; padding: 6px;")
        mid_lay = QHBoxLayout(mid_box)
        
        lbl_mid_title = QLabel("ID de este Equipo:")
        lbl_mid_title.setStyleSheet("font-weight: 600; color: #334155;")
        
        self.lbl_mid = QLabel(self.mgr.machine_id)
        self.lbl_mid.setStyleSheet("font-size: 15px; font-weight: bold; color: #2563eb; font-family: monospace;")
        
        btn_copy = QPushButton("📋 Copiar")
        btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_copy.setStyleSheet("background: #e2e8f0; border-radius: 6px; padding: 4px 10px; font-weight: 500;")
        btn_copy.clicked.connect(self._copiar_id)

        mid_lay.addWidget(lbl_mid_title)
        mid_lay.addWidget(self.lbl_mid)
        mid_lay.addStretch()
        mid_lay.addWidget(btn_copy)
        layout.addWidget(mid_box)

        # Botón para activar remotamente desde la nube
        self.btn_check_cloud = QPushButton("🔄 Comprobar activación en la nube")
        self.btn_check_cloud.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_check_cloud.setStyleSheet("""
            QPushButton {
                background: #0284c7;
                color: white;
                font-weight: 600;
                border-radius: 8px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background: #0369a1;
            }
        """)
        self.btn_check_cloud.clicked.connect(self._verificar_nube)
        layout.addWidget(self.btn_check_cloud)

        # O ingresar clave manual
        lbl_key = QLabel("O introduce una Clave de Activación directa:")
        lbl_key.setStyleSheet("font-weight: 600; color: #1e293b; margin-top: 4px;")
        layout.addWidget(lbl_key)

        self.input_key = QLineEdit()
        self.input_key.setPlaceholderText("Ej. CLN-XXXX-XXXX-XXXX")
        self.input_key.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-family: monospace;
                background: white;
            }
            QLineEdit:focus {
                border-color: #2563eb;
            }
        """)
        layout.addWidget(self.input_key)

        layout.addStretch()

        # Botones de Acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.btn_exit = QPushButton("Salir")
        self.btn_exit.setStyleSheet("""
            QPushButton {
                background: #f8fafc;
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: 600;
                color: #64748b;
            }
            QPushButton:hover {
                background: #e2e8f0;
            }
        """)
        self.btn_exit.clicked.connect(self.reject)

        self.btn_activate = QPushButton("Activar Sistema")
        self.btn_activate.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                border: none;
                border-radius: 8px;
                padding: 8px 22px;
                font-weight: bold;
                color: white;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """)
        self.btn_activate.clicked.connect(self._verificar_y_activar)

        btn_layout.addWidget(self.btn_exit)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_activate)

        layout.addLayout(btn_layout)

    def _verificar_nube(self):
        """Consulta en Firebase si Kevin activó el equipo con un solo clic."""
        self.btn_check_cloud.setText("Consultando servidor...")
        self.btn_check_cloud.setEnabled(False)
        QApplication.processEvents()

        ok, msg = self.mgr.check_cloud_activation(self.db)
        self.btn_check_cloud.setText("🔄 Comprobar activación en la nube")
        self.btn_check_cloud.setEnabled(True)

        if ok:
            QMessageBox.information(
                self,
                "✅ Activación Exitosa",
                "¡Tu equipo ha sido activado desde el servidor por el administrador!\n"
                "Ya puedes acceder al sistema."
            )
            self.activated = True
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Activación pendiente",
                f"{msg}\n\nSi ya le avisaste al desarrollador, espera unos segundos a que active tu ID y vuelve a presionar este botón."
            )

    def _copiar_id(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.mgr.machine_id)
        QMessageBox.information(self, "Copiado", f"El ID del equipo ha sido copiado al portapapeles:\n\n{self.mgr.machine_id}")

    def _verificar_y_activar(self):
        clave = self.input_key.text().strip()
        if not clave:
            QMessageBox.warning(self, "Clave requerida", "Por favor ingresa la clave de activación.")
            return

        if self.mgr.verify_activation_key(clave):
            # Guardar certificado local
            self.mgr.activate_locally("Doctora / Clinica")
            
            # Si hay Firebase disponible, registrarlo en la nube
            if self.db and hasattr(self.db, "is_configured") and self.db.is_configured():
                try:
                    self.db._db.collection("licencias").document(self.mgr.machine_id).set({
                        "machine_id": self.mgr.machine_id,
                        "activa": True,
                        "cliente": "Doctora / Clinica"
                    }, merge=True)
                except Exception:
                    pass

            QMessageBox.information(
                self,
                "✅ Activación Exitosa",
                "¡El sistema ha sido activado exitosamente para este equipo!\n"
                "Ya puedes utilizar el sistema con total normalidad."
            )
            self.activated = True
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Clave Inválida",
                "La clave de activación ingresada no es válida para este equipo.\n"
                "Verifica que no haya errores o contacta al desarrollador."
            )

