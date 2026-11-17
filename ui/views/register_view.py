from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt

class RegisterView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Layout principal horizontal sin márgenes
        self.setObjectName("loginBackground")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- COLUMNA IZQUIERDA (Branding / Banner) ---
        left_banner = QWidget()
        left_banner.setObjectName("leftBanner")
        left_banner.setStyleSheet("""
            QWidget#leftBanner {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a2980, stop:1 #26d0ce);
            }
        """)
        left_layout = QVBoxLayout(left_banner)
        left_layout.setContentsMargins(50, 50, 50, 50)
        
        left_layout.addStretch()
        
        banner_title = QLabel("Únete a la\nPlataforma")
        banner_title.setStyleSheet("color: white; font-size: 48px; font-weight: bold; font-family: 'Segoe UI';")
        left_layout.addWidget(banner_title)
        
        banner_sub = QLabel("La forma más segura y moderna de\ngestionar tu trabajo clínico.")
        banner_sub.setStyleSheet("color: rgba(255, 255, 255, 0.8); font-size: 18px; margin-top: 10px;")
        left_layout.addWidget(banner_sub)
        
        left_layout.addStretch()
        
        # --- COLUMNA DERECHA (Formulario) ---
        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_panel.setStyleSheet("QWidget#rightPanel { background-color: #ffffff; }")
        right_panel.setMinimumWidth(450)
        right_panel.setMaximumWidth(550)
        
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 50, 50, 50)
        right_layout.setSpacing(20)
        
        right_layout.addStretch()
        
        # Título
        title_label = QLabel("Crear Nueva Cuenta")
        title_label.setObjectName("titleLabel")
        right_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Ingresa tus datos para registrarte")
        subtitle_label.setObjectName("subtitleLabel")
        right_layout.addWidget(subtitle_label)
        
        right_layout.addSpacing(20)

        # Cajas de Texto
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Correo Electrónico")
        self.email_input.setFixedHeight(45)
        right_layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña (mín. 6 caracteres)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(45)
        right_layout.addWidget(self.password_input)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar Contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setFixedHeight(45)
        right_layout.addWidget(self.confirm_password_input)
        
        # Medidor de fuerza de contraseña
        self.strength_bar = QLabel("")
        self.strength_bar.setFixedHeight(6)
        self.strength_bar.setStyleSheet("background-color: #e0e0e0; border-radius: 3px;")
        right_layout.addWidget(self.strength_bar)
        
        self.strength_label = QLabel("Fuerza de la contraseña: -")
        self.strength_label.setStyleSheet("font-size: 11px; color: #666;")
        right_layout.addWidget(self.strength_label)
        
        self.password_input.textChanged.connect(self._evaluate_password_strength)

        # Mensajes de Feedback
        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        right_layout.addWidget(self.error_label)
        
        self.success_label = QLabel("")
        self.success_label.setObjectName("successLabel")
        self.success_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.success_label.setWordWrap(True)
        self.success_label.setVisible(False)
        right_layout.addWidget(self.success_label)

        # Botón Principal
        self.register_button = QPushButton("Registrarse")
        self.register_button.setObjectName("primaryButton")
        self.register_button.setFixedHeight(48)
        right_layout.addWidget(self.register_button)
        
        right_layout.addSpacing(10)

        # Enlace a Login
        self.go_login_button = QPushButton("¿Ya tienes cuenta? Inicia Sesión")
        self.go_login_button.setObjectName("linkButton")
        self.go_login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        right_layout.addWidget(self.go_login_button)

        right_layout.addStretch()

        # Añadir al layout principal
        main_layout.addWidget(left_banner, 3)
        main_layout.addWidget(right_panel, 2)

    def show_error(self, message):
        self.success_label.setVisible(False)
        self.error_label.setText(message)
        self.error_label.setVisible(True)
        
    def show_success(self, message):
        self.error_label.setVisible(False)
        self.success_label.setText(message)
        self.success_label.setVisible(True)

    def clear_messages(self):
        self.error_label.setText("")
        self.error_label.setVisible(False)
        self.success_label.setText("")
        self.success_label.setVisible(False)
        
    def set_ui_enabled(self, enabled):
        self.email_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.confirm_password_input.setEnabled(enabled)
        self.register_button.setEnabled(enabled)
        self.go_login_button.setEnabled(enabled)

    def _evaluate_password_strength(self, text):
        if not text:
            self.strength_bar.setStyleSheet("background-color: #e0e0e0; border-radius: 3px;")
            self.strength_label.setText("Fuerza de la contraseña: -")
            return
            
        score = 0
        if len(text) >= 8: score += 1
        if any(c.islower() for c in text) and any(c.isupper() for c in text): score += 1
        if any(c.isdigit() for c in text): score += 1
        if any(not c.isalnum() for c in text): score += 1
        
        if score <= 1:
            color = "#dc3545" # Rojo (Débil)
            label = "Débil"
        elif score == 2:
            color = "#ffc107" # Amarillo (Regular)
            label = "Regular"
        elif score == 3:
            color = "#17a2b8" # Azul (Buena)
            label = "Buena"
        else:
            color = "#28a745" # Verde (Fuerte)
            label = "Fuerte"
            
        self.strength_bar.setStyleSheet(f"background-color: {color}; border-radius: 3px;")
        self.strength_label.setText(f"Fuerza de la contraseña: {label}")
