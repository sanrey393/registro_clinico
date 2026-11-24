# ui/dialogs/update_prompt_dialog.py
# Notificación interactiva emergente para elegir si actualizar ahora o más adelante

import os
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QFrame
)
from core.app_paths import resource_path
from core.update_manager import CURRENT_VERSION
from ui.widgets.app_icons import svg_icon


def _is_dark_theme(parent) -> bool:
    if parent is not None and hasattr(parent, "_is_dark_mode"):
        return bool(parent._is_dark_mode)
    app = QApplication.instance()
    if app is not None:
        return app.palette().window().color().lightness() < 128
    return False


class UpdatePromptDialog(QDialog):
    """
    Notificación emergente en armonía con PSIQUE (Tema Claro y Oscuro) cuando se
    detecta una nueva versión en GitHub/servidor.
    """
    def __init__(self, parent, nueva_version: str, url: str, notas: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Actualización de PSIQUE")
        self.setFixedSize(520, 380)
        self.nueva_version = nueva_version
        self.url = url
        self.notas = notas
        self._dark = _is_dark_theme(parent)

        icon_png = resource_path(os.path.join("data", "app_icon.png"))
        if os.path.exists(icon_png):
            self.setWindowIcon(QIcon(icon_png))

        self._setup_ui()

    def _setup_ui(self):
        if self._dark:
            bg_dlg = "#0f172a"
            card_bg = "#132a2e"
            card_border = "#1e4e52"
            title_col = "#f8fafc"
            accent_col = "#2dd4bf"
            label_col = "#e2e8f0"
            muted_col = "#94a3b8"
            notes_bg = "#1e293b"
            notes_border = "#334155"
            notes_text = "#f1f5f9"
            sec_btn_bg = "#1e293b"
            sec_btn_border = "#334155"
            sec_btn_text = "#e2e8f0"
            sec_btn_hover = "#334155"
        else:
            bg_dlg = "#ffffff"
            card_bg = "#f0fdfa"
            card_border = "#99f6e4"
            title_col = "#0b2b2e"
            accent_col = "#0f766e"
            label_col = "#1e293b"
            muted_col = "#475569"
            notes_bg = "#f8fafc"
            notes_border = "#cbd5e1"
            notes_text = "#1e293b"
            sec_btn_bg = "#f1f5f9"
            sec_btn_border = "#cbd5e1"
            sec_btn_text = "#334155"
            sec_btn_hover = "#e2e8f0"

        self.setObjectName("PsiqueUpdatePrompt")
        self.setStyleSheet(f"""
            QDialog#PsiqueUpdatePrompt {{
                background: {bg_dlg};
                font-family: "Segoe UI", "Inter", sans-serif;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(14)

        # ── Encabezado PSIQUE (scoped por objectName para evitar herencia en QLabel) ──
        header_frame = QFrame()
        header_frame.setObjectName("UpdateHeaderCard")
        header_frame.setStyleSheet(f"""
            QFrame#UpdateHeaderCard {{
                background: {card_bg};
                border: 1px solid {card_border};
                border-left: 4px solid #0f766e;
                border-radius: 10px;
            }}
        """)
        h_layout = QHBoxLayout(header_frame)
        h_layout.setContentsMargins(14, 12, 14, 12)
        h_layout.setSpacing(14)

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(48, 48)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(
            "background: #ffffff; border: 1px solid #cbd5e1; border-radius: 10px; padding: 4px;"
        )
        icon_png = resource_path(os.path.join("data", "app_icon.png"))
        if os.path.exists(icon_png):
            icon_lbl.setPixmap(
                QPixmap(icon_png).scaled(
                    38, 38, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                )
            )
        h_layout.addWidget(icon_lbl)

        txt_box = QVBoxLayout()
        txt_box.setSpacing(4)
        title_lbl = QLabel(f"Nueva versión v{self.nueva_version} disponible")
        title_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {title_col}; background: transparent; border: none; padding: 0px;"
        )
        sub_lbl = QLabel(f"Versión instalada: v{CURRENT_VERSION}   →   Nueva: v{self.nueva_version}")
        sub_lbl.setStyleSheet(
            f"font-size: 12.5px; font-weight: 600; color: {accent_col}; background: transparent; border: none; padding: 0px;"
        )
        txt_box.addWidget(title_lbl)
        txt_box.addWidget(sub_lbl)
        h_layout.addLayout(txt_box, 1)

        layout.addWidget(header_frame)

        # ── Novedades ──
        lbl_notes = QLabel("Novedades y mejoras incluidas:")
        lbl_notes.setStyleSheet(
            f"font-size: 12.5px; font-weight: 700; color: {label_col}; background: transparent;"
        )
        layout.addWidget(lbl_notes)

        self.txt_notes = QTextEdit()
        self.txt_notes.setReadOnly(True)
        self.txt_notes.setPlainText(
            self.notas if self.notas else "Mejoras de rendimiento, estabilidad y nuevas funciones."
        )
        self.txt_notes.setStyleSheet(f"""
            QTextEdit {{
                background: {notes_bg};
                border: 1px solid {notes_border};
                border-radius: 8px;
                font-family: "Segoe UI", "Inter", sans-serif;
                font-size: 12px;
                color: {notes_text};
                padding: 10px 12px;
            }}
        """)
        self.txt_notes.setFixedHeight(105)
        layout.addWidget(self.txt_notes)

        # ── Pregunta ──
        lbl_question = QLabel("¿Deseas descargar e instalar esta actualización ahora?")
        lbl_question.setStyleSheet(
            f"font-size: 12.5px; font-weight: 600; color: {muted_col}; background: transparent;"
        )
        layout.addWidget(lbl_question)

        # ── Botones de decisión ──
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_later = QPushButton(" Más adelante")
        self.btn_later.setIcon(svg_icon("clock", color=sec_btn_text, size=15))
        self.btn_later.setIconSize(QSize(15, 15))
        self.btn_later.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_later.setToolTip(
            "Cerrar este aviso. Podrás actualizar en cualquier momento desde el botón superior."
        )
        self.btn_later.setStyleSheet(f"""
            QPushButton {{
                background: {sec_btn_bg};
                color: {sec_btn_text};
                border: 1px solid {sec_btn_border};
                border-radius: 8px;
                padding: 9px 18px;
                font-size: 12.5px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {sec_btn_hover};
            }}
        """)
        self.btn_later.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_later)

        btn_layout.addStretch()

        self.btn_now = QPushButton(" Actualizar Ahora")
        self.btn_now.setIcon(svg_icon("refresh", color="#ffffff", size=15))
        self.btn_now.setIconSize(QSize(15, 15))
        self.btn_now.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_now.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0f766e, stop:1 #0d9488);
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 9px 22px;
                font-size: 12.5px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #14b8a6;
            }
        """)
        self.btn_now.clicked.connect(self.accept)
        btn_layout.addWidget(self.btn_now)

        layout.addLayout(btn_layout)
