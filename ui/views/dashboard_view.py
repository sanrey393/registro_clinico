from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPainterPath
import urllib.request


class DashboardView(QWidget):
    """
    Vista principal del sistema tras autenticarse.
    Muestra información del usuario y accesos directos a los módulos clínicos.
    """
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_data = {}
        self.setup_ui()

    # ── Construcción de UI ──────────────────────────────────────

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_main(), 1)

    # ── Sidebar ─────────────────────────────────────────────────

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame#sidebar {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #1a2744, stop:1 #0f1729);
                border-right: 1px solid #243054;
            }
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(0)

        # Logo / App name
        logo_area = QWidget()
        logo_area.setStyleSheet("background: transparent;")
        logo_layout = QVBoxLayout(logo_area)
        logo_layout.setContentsMargins(20, 28, 20, 24)

        app_label = QLabel("🏥 Registro\nClínico")
        app_label.setStyleSheet("""
            color: #ffffff;
            font-size: 18px;
            font-weight: bold;
            line-height: 1.4;
            background: transparent;
        """)
        logo_layout.addWidget(app_label)
        layout.addWidget(logo_area)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #243054; max-height: 1px; margin: 0 20px;")
        layout.addWidget(sep)
        layout.addSpacing(12)

        # Nav items
        modules = [
            ("👤", "Identificación"),  # index 0
            ("📋", "Historias"),       # index 1
            ("📅", "Agenda"),          # index 2
            ("🏥", "Sesiones"),        # index 3
            ("💊", "Fármacos"),        # index 4
            ("🧾", "Facturación"),     # index 5
            ("📁", "Documentos"),      # index 6 (Pendiente)
        ]
        
        self.nav_buttons = []
        for i, (icon, label) in enumerate(modules):
            btn = self._nav_button(icon, label, active=(i==0))
            # Usar un lambda captureando i
            btn.clicked.connect(lambda checked, idx=i: self._switch_tab(idx))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #243054; max-height: 1px; margin: 0 20px;")
        layout.addWidget(sep2)
        layout.addSpacing(12)

        # User info box
        self.user_sidebar_widget = self._build_user_sidebar_box()
        layout.addWidget(self.user_sidebar_widget)

        return sidebar

    def _switch_tab(self, index: int):
        # Evitar errores de índice
        if index < self.main_stack.count():
            self.main_stack.setCurrentIndex(index)
        
        # Actualizar estilos visuales (active)
        for i, btn in enumerate(self.nav_buttons):
            self._set_btn_active_style(btn, i == index)

    def _set_btn_active_style(self, btn, active):
        active_style = """
            QPushButton {
                background: rgba(255,255,255,0.12);
                color: #ffffff;
                border: none;
                border-left: 3px solid #4d9ef7;
                text-align: left;
                font-size: 14px;
                padding-left: 18px;
                border-radius: 0;
            }
        """
        normal_style = """
            QPushButton {
                background: transparent;
                color: #9baacf;
                border: none;
                border-left: 3px solid transparent;
                text-align: left;
                font-size: 14px;
                padding-left: 18px;
                border-radius: 0;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.07);
                color: #d0d9f0;
            }
        """
        btn.setStyleSheet(active_style if active else normal_style)

    def _nav_button(self, icon: str, label: str, active: bool = False) -> QPushButton:
        btn = QPushButton(f"  {icon}  {label}")
        btn.setFixedHeight(44)
        self._set_btn_active_style(btn, active)
        return btn

    def _build_user_sidebar_box(self) -> QWidget:
        box = QWidget()
        box.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(box)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(10)

        # Avatar circular
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(38, 38)
        self.avatar_label.setStyleSheet("""
            background: #4d9ef7;
            border-radius: 19px;
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setText("?")
        layout.addWidget(self.avatar_label)

        # Nombre + email
        text_widget = QWidget()
        text_widget.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        self.sidebar_name_label = QLabel("—")
        self.sidebar_name_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: bold; background: transparent;")
        self.sidebar_name_label.setWordWrap(False)

        self.sidebar_email_label = QLabel("—")
        self.sidebar_email_label.setStyleSheet("color: #7a8eb8; font-size: 11px; background: transparent;")
        self.sidebar_email_label.setWordWrap(False)

        text_layout.addWidget(self.sidebar_name_label)
        text_layout.addWidget(self.sidebar_email_label)
        layout.addWidget(text_widget, 1)

        return box

    # ── Main content ─────────────────────────────────────────────

    def _build_main(self) -> QWidget:
        from PyQt6.QtWidgets import QStackedWidget
        
        main = QWidget()
        main.setStyleSheet("background: #f0f3f8;")
        layout = QVBoxLayout(main)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_topbar())

        # Contenedor principal con scroll para la vista de inicio
        self.main_stack = QStackedWidget()
        layout.addWidget(self.main_stack, 1)

        # 0. Pantalla de Inicio: se añade en setup_modules (necesita db)
        # El placeholder se sustituye luego
        self._home_placeholder = QWidget()
        self._home_placeholder.setStyleSheet("background: #f0f3f8;")
        self.main_stack.addWidget(self._home_placeholder)

        return main

    def setup_modules(self, db_manager):
        """Inicializa las vistas de los módulos pasándoles el manejador de la base de datos."""
        from ui.views.identificacion_view import IdentificacionView
        from ui.views.patients_view import PatientsView
        from ui.views.appointments_view import AppointmentsView
        from ui.views.clinical_sessions_view import ClinicalSessionsView
        from ui.views.billing_view import BillingView
        from ui.views.farmacos_view import FarmacosView

        # Índice 0: Pantalla de Inicio → Identificación de Pacientes
        from PyQt6.QtWidgets import QScrollArea
        self.identificacion_view = IdentificacionView(db_manager)
        scroll = QScrollArea()
        scroll.setWidget(self.identificacion_view)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(scroll.Shape.NoFrame)
        scroll.setStyleSheet("background: #f0f3f8;")
        # Reemplazar el placeholder en índice 0
        self.main_stack.removeWidget(self._home_placeholder)
        self.main_stack.insertWidget(0, scroll)

        self.patients_view = PatientsView(db_manager)
        self.appointments_view = AppointmentsView(db_manager)
        self.sessions_view = ClinicalSessionsView(db_manager)
        self.billing_view = BillingView(db_manager)
        self.farmacos_view = FarmacosView(db_manager)
        self.prescriptions_view = self.farmacos_view

        self.main_stack.addWidget(self.patients_view)      # index 1
        self.main_stack.addWidget(self.appointments_view)  # index 2
        self.main_stack.addWidget(self.sessions_view)      # index 3
        self.main_stack.addWidget(self.farmacos_view)      # index 4
        self.main_stack.addWidget(self.billing_view)       # index 5

    theme_toggled = pyqtSignal()

    def _build_topbar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(60)
        bar.setObjectName("topbar")
        
        # Efecto de sombra para el topbar
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        bar.setGraphicsEffect(shadow)

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(15)

        title = QLabel("Sistema de Registro Clínico — Psicología")
        title.setObjectName("topbarTitle")
        layout.addWidget(title)
        layout.addStretch()

        # Botón Toggle Theme
        self.theme_btn = QPushButton("🌙 Modo Oscuro")
        self.theme_btn.setObjectName("themeBtn")
        self.theme_btn.setStyleSheet("""
            QPushButton#themeBtn {
                background: transparent;
                color: #4d9ef7;
                border: 1px solid #4d9ef7;
                border-radius: 6px;
                font-size: 13px;
                padding: 6px 12px;
            }
            QPushButton#themeBtn:hover {
                background: #4d9ef7;
                color: white;
            }
        """)
        self.theme_btn.clicked.connect(self._on_theme_toggled)
        layout.addWidget(self.theme_btn)

        # Botón Logout
        logout_btn = QPushButton("⬅  Cerrar sesión")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(logout_btn)

        self._is_dark = False
        return bar
        
    def _on_theme_toggled(self):
        self._is_dark = not self._is_dark
        if self._is_dark:
            self.theme_btn.setText("☀️ Modo Claro")
        else:
            self.theme_btn.setText("🌙 Modo Oscuro")
        self.theme_toggled.emit()

    def _build_module_cards(self) -> QWidget:
        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid = QGridLayout(grid_widget)
        grid.setSpacing(16)

        modules = [
            ("👥", "Pacientes",     "Gestiona el expediente de cada paciente.",      "#4d9ef7"),
            ("📅", "Citas",         "Programa y administra las consultas.",           "#6f42c1"),
            ("📋", "Sesiones",      "Registra notas de cada sesión clínica.",         "#20c997"),
            ("🧾", "Facturación",   "Control de cobros y pagos.",                     "#fd7e14"),
            ("💊", "Fármacos",      "Catálogo, indicaciones, dosis e interacciones.",  "#e83e8c"),
            ("📁", "Documentos",    "Archivos adjuntos del expediente.",               "#17a2b8"),
        ]

        for i, (icon, title, desc, color) in enumerate(modules):
            card = self._make_card(icon, title, desc, color)
            grid.addWidget(card, i // 3, i % 3)

        return grid_widget

    def _make_card(self, icon: str, title: str, desc: str, color: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e0e4ed;
            }}
            QFrame:hover {{
                border: 1px solid {color};
            }}
        """)
        card.setFixedHeight(130)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        icon_title = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"""
            font-size: 22px;
            background: {color}22;
            border-radius: 8px;
            padding: 4px 8px;
        """)
        icon_lbl.setFixedSize(42, 42)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_title.addWidget(icon_lbl)

        badge = QLabel("Próximamente")
        badge.setStyleSheet("""
            background: #e9ecef;
            color: #6c757d;
            border-radius: 4px;
            font-size: 10px;
            padding: 2px 8px;
        """)
        icon_title.addStretch()
        icon_title.addWidget(badge)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-size: 15px; font-weight: bold; color: #1a2744;")

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("font-size: 12px; color: #6c757d;")
        desc_lbl.setWordWrap(True)

        layout.addLayout(icon_title)
        layout.addWidget(title_lbl)
        layout.addWidget(desc_lbl)

        return card

    # ── Actualizar datos del usuario ─────────────────────────────

    def set_user(self, display_name: str, email: str, photo_url: str = ""):
        """Actualiza los labels del sidebar con la información del usuario autenticado."""
        first_letter = (display_name or email or "?")[0].upper()

        # Sidebar
        self.sidebar_name_label.setText(display_name or email)
        self.sidebar_email_label.setText(email)
        self.avatar_label.setText(first_letter)
