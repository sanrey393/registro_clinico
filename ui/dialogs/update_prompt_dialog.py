# ui/dialogs/update_prompt_dialog.py
# Notificación interactiva emergente para elegir si actualizar ahora o más adelante

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame
)
from core.update_manager import CURRENT_VERSION


class UpdatePromptDialog(QDialog):
    """
    Notificación emergente que aparece cuando se detecta una nueva versión en GitHub/servidor.
    Le da al usuario la opción clara de 'Actualizar Ahora' o 'Más adelante'.
    """
    def __init__(self, parent, nueva_version: str, url: str, notas: str = ""):
        super().__init__(parent)
        self.setWindowTitle("🔔 Actualización del Sistema Clínico")
        self.setFixedSize(500, 340)
        self.nueva_version = nueva_version
        self.url = url
        self.notas = notas

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(14)

        # Encabezado visual
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: #eff6ff;
                border: 1px solid #bfdbfe;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        h_layout = QHBoxLayout(header_frame)
        h_layout.setSpacing(12)

        icon_lbl = QLabel("🔔")
        icon_lbl.setStyleSheet("font-size: 28px; background: transparent;")
        h_layout.addWidget(icon_lbl)

        txt_box = QVBoxLayout()
        txt_box.setSpacing(2)
        title_lbl = QLabel(f"<b>¡Nueva versión v{self.nueva_version} disponible!</b>")
        title_lbl.setStyleSheet("font-size: 15px; color: #1e40af; background: transparent;")
        sub_lbl = QLabel(f"Tu versión actual es: <b>v{CURRENT_VERSION}</b>")
        sub_lbl.setStyleSheet("font-size: 12px; color: #3b82f6; background: transparent;")
        txt_box.addWidget(title_lbl)
        txt_box.addWidget(sub_lbl)
        h_layout.addLayout(txt_box, 1)

        layout.addWidget(header_frame)

        # Novedades
        lbl_notes = QLabel("<b>Novedades y mejoras incluidas:</b>")
        lbl_notes.setStyleSheet("font-size: 12px; color: #334155;")
        layout.addWidget(lbl_notes)

        self.txt_notes = QTextEdit()
        self.txt_notes.setReadOnly(True)
        self.txt_notes.setPlainText(self.notas if self.notas else "Mejoras de rendimiento, estabilidad y nuevas funciones.")
        self.txt_notes.setStyleSheet("""
            QTextEdit {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 11px;
                color: #1e293b;
                padding: 6px;
            }
        """)
        self.txt_notes.setFixedHeight(85)
        layout.addWidget(self.txt_notes)

        # Pregunta
        lbl_question = QLabel("¿Deseas descargar e instalar esta actualización ahora?")
        lbl_question.setStyleSheet("font-size: 12.5px; font-weight: 600; color: #0f172a;")
        layout.addWidget(lbl_question)

        # Botones de decisión
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_later = QPushButton("⏰ Más adelante")
        self.btn_later.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_later.setToolTip("Cerrar este aviso. Podrás actualizar en cualquier momento desde el botón superior.")
        self.btn_later.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 9px 18px;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #e2e8f0;
                color: #1e293b;
            }
        """)
        self.btn_later.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_later)

        btn_layout.addStretch()

        self.btn_now = QPushButton("🚀 Actualizar Ahora")
        self.btn_now.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_now.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 9px 22px;
                font-size: 12.5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
        """)
        self.btn_now.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_now)

        layout.addLayout(btn_layout)
