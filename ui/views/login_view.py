# ui/views/login_view.py — Pantalla de Login personalizada con diseño médico profesional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QCheckBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont


class LoginView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("loginBackground")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget#loginBackground {
                background-color: #f8fafc;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ══════════════════════════════════════════════════════════
        # COLUMNA IZQUIERDA (Banner Institucional Clínico)
        # ══════════════════════════════════════════════════════════
        left_banner = QWidget()
        left_banner.setObjectName("leftBanner")
        left_banner.setStyleSheet("""
            QWidget#leftBanner {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f2b48,
                    stop:0.5 #163e65,
                    stop:1 #1e5282
                );
            }
        """)
        left_layout = QVBoxLayout(left_banner)
        left_layout.setContentsMargins(60, 50, 60, 50)
        left_layout.setSpacing(0)
        
        # Badge superior
        badge = QLabel("🏥  SISTEMA DE GESTIÓN MÉDICA INTEGRAL")
        badge.setStyleSheet("""
            background: rgba(255, 255, 255, 0.12);
            color: #93c5fd;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            padding: 6px 14px;
            border-radius: 14px;
            border: 1px solid rgba(147, 197, 253, 0.3);
        """)
        badge.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        left_layout.addWidget(badge)
        
        left_layout.addSpacing(30)
        
        # Logo / Icono + Título
        title_box = QVBoxLayout()
        title_box.setSpacing(6)
        
        banner_title = QLabel("Registro\nClínico Pro")
        banner_title.setStyleSheet("""
            color: #ffffff;
            font-size: 44px;
            font-weight: 800;
            line-height: 1.1;
        """)
        title_box.addWidget(banner_title)
        
        banner_sub = QLabel("Plataforma médica de historias, citas y prescripciones farmacológicas.")
        banner_sub.setWordWrap(True)
        banner_sub.setStyleSheet("""
            color: #cbd5e1;
            font-size: 15px;
            line-height: 1.4;
            margin-top: 6px;
        """)
        title_box.addWidget(banner_sub)
        left_layout.addLayout(title_box)
        
        left_layout.addSpacing(40)
        
        # ── Feature Cards (Indicadores destacados) ──
        features = [
            ("📋", "Expediente Digital 360°", "Ficha de identificación con formato cédula y control de antecedentes."),
            ("📅", "Agenda Médica Visual", "Calendario mensual interactivo con filtrado y estados codificados."),
            ("💊", "Recetario con Catálogo", "Catálogo integrado de ~80 fármacos, dosis usuales y exportación a PDF.")
        ]
        
        for icon, feat_title, feat_desc in features:
            f_card = QFrame()
            f_card.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.07);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    border-radius: 10px;
                    padding: 10px 14px;
                }
                QFrame:hover {
                    background: rgba(255, 255, 255, 0.11);
                    border-color: rgba(147, 197, 253, 0.4);
                }
            """)
            f_lay = QHBoxLayout(f_card)
            f_lay.setContentsMargins(8, 8, 8, 8)
            f_lay.setSpacing(12)
            
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 22px; background: transparent;")
            f_lay.addWidget(icon_lbl)
            
            t_box = QVBoxLayout()
            t_box.setSpacing(2)
            lbl_t = QLabel(feat_title)
            lbl_t.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 13px; background: transparent;")
            lbl_d = QLabel(feat_desc)
            lbl_d.setWordWrap(True)
            lbl_d.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent;")
            t_box.addWidget(lbl_t)
            t_box.addWidget(lbl_d)
            f_lay.addLayout(t_box)
            
            left_layout.addWidget(f_card)
            left_layout.addSpacing(10)
            
        left_layout.addStretch()
        
        # Footer izquierdo
        footer_lbl = QLabel("🔒 Conexión Segura Firebase Cloud • Versión 2.5 Pro")
        footer_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        left_layout.addWidget(footer_lbl)
        
        # ══════════════════════════════════════════════════════════
        # COLUMNA DERECHA (Formulario de Acceso)
        # ══════════════════════════════════════════════════════════
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_panel.setStyleSheet("""
            QWidget#rightPanel {
                background-color: #ffffff;
            }
        """)
        right_panel.setMinimumWidth(440)
        right_panel.setMaximumWidth(540)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 40, 50, 40)
        right_layout.setSpacing(14)
        
        right_layout.addStretch()
        
        # Título y Subtítulo
        title_label = QLabel("Bienvenido de nuevo")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("""
            color: #0f172a;
            font-size: 26px;
            font-weight: 700;
        """)
        right_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Ingresa tus credenciales para acceder a la clínica")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setStyleSheet("""
            color: #64748b;
            font-size: 13px;
            margin-bottom: 8px;
        """)
        right_layout.addWidget(subtitle_label)

        # ── Campos de Entrada ──
        lbl_email = QLabel("Correo Electrónico")
        lbl_email.setStyleSheet("color: #334155; font-size: 12px; font-weight: 600;")
        right_layout.addWidget(lbl_email)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("ejemplo@medico.com")
        self.email_input.setFixedHeight(44)
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1e293b;
                background: #f8fafc;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: #ffffff;
            }
        """)
        right_layout.addWidget(self.email_input)

        lbl_pass = QLabel("Contraseña")
        lbl_pass.setStyleSheet("color: #334155; font-size: 12px; font-weight: 600; margin-top: 6px;")
        right_layout.addWidget(lbl_pass)

        # Password layout
        password_layout = QHBoxLayout()
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(6)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(44)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: 1.5px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #1e293b;
                background: #f8fafc;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: #ffffff;
            }
        """)
        password_layout.addWidget(self.password_input)
        
        self.toggle_password_btn = QPushButton("👁")
        self.toggle_password_btn.setObjectName("togglePasswordBtn")
        self.toggle_password_btn.setCheckable(True)
        self.toggle_password_btn.setFixedSize(44, 44)
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                background: #f1f5f9;
                border: 1.5px solid #e2e8f0;
                border-radius: 8px;
                font-size: 15px;
            }
            QPushButton:hover { background: #e2e8f0; }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_btn)
        
        right_layout.addLayout(password_layout)

        # Opciones: Recordarme / Olvidé contraseña
        options_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("Recordarme")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #64748b;
                font-size: 12px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1.5px solid #cbd5e1;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
        """)
        options_layout.addWidget(self.remember_checkbox)
        options_layout.addStretch()
        
        self.forgot_password_btn = QPushButton("¿Olvidaste tu contraseña?")
        self.forgot_password_btn.setObjectName("forgotPasswordBtn")
        self.forgot_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forgot_password_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #2563eb;
                font-size: 12px;
                font-weight: 500;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        options_layout.addWidget(self.forgot_password_btn)
        right_layout.addLayout(options_layout)

        # Mensajes de Feedback
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("""
            QLabel#errorLabel {
                background: #fef2f2;
                color: #dc2626;
                border: 1px solid #fecaca;
                border-radius: 7px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        self.error_label.setVisible(False)
        right_layout.addWidget(self.error_label)
        
        self.success_label = QLabel("")
        self.success_label.setObjectName("successLabel")
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_label.setWordWrap(True)
        self.success_label.setStyleSheet("""
            QLabel#successLabel {
                background: #f0fdf4;
                color: #16a34a;
                border: 1px solid #bbf7d0;
                border-radius: 7px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        self.success_label.setVisible(False)
        right_layout.addWidget(self.success_label)
        
        self.countdown_label = QLabel("")
        self.countdown_label.setObjectName("countdownLabel")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet("""
            color: #d97706; font-size: 12px; font-weight: 600;
        """)
        self.countdown_label.setVisible(False)
        right_layout.addWidget(self.countdown_label)
        
        self.unlock_account_btn = QPushButton("Desbloquear cuenta ahora")
        self.unlock_account_btn.setObjectName("linkButton")
        self.unlock_account_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.unlock_account_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none; color: #dc2626;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        self.unlock_account_btn.setVisible(False)
        right_layout.addWidget(self.unlock_account_btn)

        # Botón Principal Iniciar Sesión
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setObjectName("primaryButton")
        self.login_button.setFixedHeight(46)
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton#primaryButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2563eb, stop:1 #1d4ed8);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton#primaryButton:hover {
                background: #1d4ed8;
            }
            QPushButton#primaryButton:pressed {
                background: #1e40af;
            }
            QPushButton#primaryButton:disabled {
                background: #94a3b8;
            }
        """)
        self.password_input.returnPressed.connect(self.login_button.click)
        right_layout.addWidget(self.login_button)
        
        # Divisor Visual
        divider_layout = QHBoxLayout()
        divider_layout.setContentsMargins(0, 4, 0, 4)
        line_left = QFrame()
        line_left.setFrameShape(QFrame.Shape.HLine)
        line_left.setStyleSheet("color: #e2e8f0; background: #e2e8f0; max-height: 1px; border: none;")
        divider_label = QLabel(" o continuar con ")
        divider_label.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 500;")
        line_right = QFrame()
        line_right.setFrameShape(QFrame.Shape.HLine)
        line_right.setStyleSheet("color: #e2e8f0; background: #e2e8f0; max-height: 1px; border: none;")
        divider_layout.addWidget(line_left)
        divider_layout.addWidget(divider_label)
        divider_layout.addWidget(line_right)
        right_layout.addLayout(divider_layout)
        
        # Botón de Google Sign-In
        self.google_button = QPushButton("  Continuar con Google")
        self.google_button.setObjectName("googleButton")
        self.google_button.setFixedHeight(44)
        self.google_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.google_button.setIcon(self._google_icon())
        self.google_button.setIconSize(self.google_button.sizeHint())
        self.google_button.setStyleSheet("""
            QPushButton#googleButton {
                background: #ffffff;
                color: #334155;
                border: 1.5px solid #cbd5e1;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#googleButton:hover {
                background: #f8fafc;
                border-color: #94a3b8;
            }
        """)
        right_layout.addWidget(self.google_button)

        right_layout.addSpacing(6)

        # Enlace a Registro
        self.go_register_button = QPushButton("¿Aún no tienes cuenta? Regístrate aquí")
        self.go_register_button.setObjectName("linkButton")
        self.go_register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.go_register_button.setStyleSheet("""
            QPushButton#linkButton {
                background: transparent;
                border: none;
                color: #2563eb;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#linkButton:hover {
                text-decoration: underline;
                color: #1d4ed8;
            }
        """)
        right_layout.addWidget(self.go_register_button)

        right_layout.addStretch()

        # Añadir al layout principal (55% banner, 45% form)
        main_layout.addWidget(left_banner, 11)
        main_layout.addWidget(right_panel, 9)

    def toggle_password_visibility(self, checked):
        if checked:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def show_error(self, message):
        self.success_label.setVisible(False)
        self.error_label.setText(message)
        self.error_label.setVisible(True)

    def show_success(self, message):
        self.error_label.setVisible(False)
        self.success_label.setText(message)
        self.success_label.setVisible(True)

    def clear_error(self):
        self.error_label.setText("")
        self.error_label.setVisible(False)
        self.success_label.setText("")
        self.success_label.setVisible(False)
        self.countdown_label.setVisible(False)

    def show_countdown(self, message):
        self.countdown_label.setText(message)
        self.countdown_label.setVisible(True)
        
    def set_ui_enabled(self, enabled):
        self.email_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.toggle_password_btn.setEnabled(enabled)
        self.remember_checkbox.setEnabled(enabled)
        self.login_button.setEnabled(enabled)
        self.google_button.setEnabled(enabled)
        self.go_register_button.setEnabled(enabled)

    def _google_icon(self):
        """Devuelve el ícono SVG oficial de Google como QIcon."""
        from PyQt6.QtGui import QIcon, QPixmap
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray
        from PyQt6.QtGui import QPainter

        svg = b"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="22" height="22">
          <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
          <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
          <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
          <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
        </svg>
        """
        renderer = QSvgRenderer(QByteArray(svg))
        pixmap = QPixmap(22, 22)
        pixmap.fill()
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
