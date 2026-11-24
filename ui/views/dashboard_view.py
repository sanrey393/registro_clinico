from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QGridLayout, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor, QPainterPath
import urllib.request
from ui.widgets.app_icons import svg_icon, svg_pixmap


class DashboardView(QWidget):
    """
    Vista principal del sistema tras autenticarse.
    Muestra información del usuario y accesos directos a los módulos clínicos.
    """
    logout_requested = pyqtSignal()
    update_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._user_data = {}
        self._sidebar_collapsed = False
        self._sidebar_expanded_width = 240
        self._sidebar_collapsed_width = 68
        self._sidebar_anim = None
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
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(self._sidebar_expanded_width)
        self.sidebar.setMaximumWidth(self._sidebar_expanded_width)
        self.sidebar.setStyleSheet("""
            QFrame#sidebar {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 #132a2e, stop:1 #0d1f22);
                border-right: 1px solid #1e3a3f;
            }
        """)

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(0, 0, 0, 20)
        layout.setSpacing(0)

        # Logo / App name con icono SVG
        logo_area = QWidget()
        logo_area.setStyleSheet("background: transparent;")
        logo_layout = QHBoxLayout(logo_area)
        logo_layout.setContentsMargins(18, 22, 16, 18)
        logo_layout.setSpacing(10)

        self.app_logo_icon = QLabel()
        from core.app_paths import resource_path
        import os
        icon_png = resource_path(os.path.join("data", "app_icon.png"))
        if os.path.exists(icon_png):
            pix = QPixmap(icon_png).scaled(
                30, 30, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            self.app_logo_icon.setPixmap(pix)
            self.app_logo_icon.setStyleSheet(
                "background: #ffffff; border-radius: 7px; padding: 2px;"
            )
            self.app_logo_icon.setFixedSize(34, 34)
        else:
            self.app_logo_icon.setPixmap(svg_pixmap("heart-pulse", color="#2dd4bf", size=26))
            self.app_logo_icon.setStyleSheet("background: transparent;")
            self.app_logo_icon.setFixedSize(28, 28)

        self.app_label = QLabel("PSIQUE\nClínica")
        self.app_label.setStyleSheet("""
            color: #ffffff;
            font-size: 17px;
            font-weight: 700;
            line-height: 1.3;
            background: transparent;
        """)
        logo_layout.addWidget(self.app_logo_icon)
        logo_layout.addWidget(self.app_label, 1)
        layout.addWidget(logo_area)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #1e3a3f; max-height: 1px; margin: 0 14px;")
        layout.addWidget(sep)
        layout.addSpacing(12)

        # Nav items con iconos SVG vectoriales
        modules = [
            ("user-check", "Identificación"),  # index 0
            ("file-text", "Historias"),        # index 1
            ("calendar", "Agenda"),            # index 2
            ("bar-chart", "Bitácora"),         # index 3
            ("pill", "Fármacos"),              # index 4
        ]

        self._nav_items = modules
        self.nav_buttons = []
        for i, (icon_name, label) in enumerate(modules):
            btn = self._nav_button(icon_name, label, active=(i == 0))
            btn.setToolTip(label)
            btn.clicked.connect(lambda checked, idx=i: self._switch_tab(idx))
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background: #1e3a3f; max-height: 1px; margin: 0 14px;")
        layout.addWidget(sep2)
        layout.addSpacing(12)

        # User info box
        self.user_sidebar_widget = self._build_user_sidebar_box()
        layout.addWidget(self.user_sidebar_widget)

        return self.sidebar

    def toggle_sidebar(self):
        """Despliega o contrae suavemente la barra lateral para aprovechar el ancho."""
        self._sidebar_collapsed = not self._sidebar_collapsed
        start_w = self.sidebar.width()
        end_w = self._sidebar_collapsed_width if self._sidebar_collapsed else self._sidebar_expanded_width

        if self._sidebar_collapsed:
            self.app_label.setVisible(False)
            self.user_text_widget.setVisible(False)
            for btn in self.nav_buttons:
                btn.setText("")
        else:
            self.app_label.setVisible(True)
            self.user_text_widget.setVisible(True)
            for btn, (_icon_name, label) in zip(self.nav_buttons, self._nav_items):
                btn.setText(f"  {label}")

        current_idx = self.main_stack.currentIndex() if hasattr(self, "main_stack") else 0
        for i, btn in enumerate(self.nav_buttons):
            self._set_btn_active_style(btn, i == current_idx, i)

        if hasattr(self, "btn_toggle_sidebar"):
            self.btn_toggle_sidebar.setIcon(
                svg_icon("menu" if self._sidebar_collapsed else "chevron-left", color="#1e293b", size=18)
            )
            self.btn_toggle_sidebar.setToolTip(
                "Expandir menú lateral" if self._sidebar_collapsed else "Contraer menú lateral"
            )

        anim_min = QPropertyAnimation(self.sidebar, b"minimumWidth")
        anim_min.setDuration(180)
        anim_min.setStartValue(start_w)
        anim_min.setEndValue(end_w)
        anim_min.setEasingCurve(QEasingCurve.Type.InOutCubic)

        anim_max = QPropertyAnimation(self.sidebar, b"maximumWidth")
        anim_max.setDuration(180)
        anim_max.setStartValue(start_w)
        anim_max.setEndValue(end_w)
        anim_max.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._sidebar_anim = QParallelAnimationGroup(self)
        self._sidebar_anim.addAnimation(anim_min)
        self._sidebar_anim.addAnimation(anim_max)
        self._sidebar_anim.start()

    def _switch_tab(self, index: int):
        # Evitar errores de índice
        if index < self.main_stack.count():
            self.main_stack.setCurrentIndex(index)
        if index == 3 and hasattr(self, "sessions_view") and hasattr(self.sessions_view, "load_data"):
            try:
                self.sessions_view.load_data()
            except Exception as e:
                print(f"[WARN] Error refrescando bitácora: {e}")
        
        # Actualizar estilos visuales (active)
        for i, btn in enumerate(self.nav_buttons):
            self._set_btn_active_style(btn, i == index, i)

    def _set_btn_active_style(self, btn, active, index: int = -1):
        collapsed = getattr(self, "_sidebar_collapsed", False)
        align = "center" if collapsed else "left"
        pad = "0px" if collapsed else "18px"
        active_style = f"""
            QPushButton {{
                background: rgba(255,255,255,0.12);
                color: #ffffff;
                border: none;
                border-left: 3px solid #2dd4bf;
                text-align: {align};
                font-size: 13.5px;
                font-weight: 600;
                padding-left: {pad};
                border-radius: 0;
            }}
        """
        normal_style = f"""
            QPushButton {{
                background: transparent;
                color: #9bb5b8;
                border: none;
                border-left: 3px solid transparent;
                text-align: {align};
                font-size: 13.5px;
                font-weight: 500;
                padding-left: {pad};
                border-radius: 0;
            }}
            QPushButton:hover {{
                background: rgba(255,255,255,0.07);
                color: #e2f1f2;
            }}
        """
        btn.setStyleSheet(active_style if active else normal_style)
        if 0 <= index < len(getattr(self, "_nav_items", [])):
            icon_name = self._nav_items[index][0]
            btn.setIcon(svg_icon(icon_name, color="#ffffff" if active else "#9bb5b8", size=18))

    def _nav_button(self, icon_name: str, label: str, active: bool = False) -> QPushButton:
        btn = QPushButton(f"  {label}")
        btn.setIcon(svg_icon(icon_name, color="#ffffff" if active else "#9bb5b8", size=18))
        btn.setIconSize(QSize(18, 18))
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
        self.user_text_widget = QWidget()
        self.user_text_widget.setStyleSheet("background: transparent;")
        text_layout = QVBoxLayout(self.user_text_widget)
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
        layout.addWidget(self.user_text_widget, 1)

        return box

    # ── Main content ─────────────────────────────────────────────

    def _build_main(self) -> QWidget:
        from PyQt6.QtWidgets import QStackedWidget
        
        main = QWidget()
        main.setObjectName("dashboardMain")
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

        # Sincronización en vivo entre Identificación ↔ Historia Clínica ↔ Agenda
        self.identificacion_view.paciente_guardado.connect(self._on_paciente_sincronizado)
        self.identificacion_view.paciente_eliminado.connect(self._on_paciente_sincronizado)
        self.identificacion_view.abrir_historia_requested.connect(self._abrir_historia_de_paciente)
        self.identificacion_view.agendar_cita_requested.connect(
            lambda p: self._abrir_agenda_de_paciente_id(p.get("id", ""))
        )
        self.identificacion_view.farmacos_requested.connect(
            lambda p: self._abrir_farmacos_de_paciente_id(p.get("id", ""))
        )
        if hasattr(self.patients_view, "paciente_sincronizado"):
            self.patients_view.paciente_sincronizado.connect(self._on_historia_sincronizo_paciente)
        if hasattr(self.patients_view, "agendar_cita_requested"):
            self.patients_view.agendar_cita_requested.connect(self._abrir_agenda_de_paciente_id)
        if hasattr(self.patients_view, "farmacos_requested"):
            self.patients_view.farmacos_requested.connect(self._abrir_farmacos_de_paciente_id)
        if hasattr(self.appointments_view, "cita_actualizada"):
            self.appointments_view.cita_actualizada.connect(self._on_cita_actualizada)
        if hasattr(self.sessions_view, "abrir_historia_requested"):
            self.sessions_view.abrir_historia_requested.connect(
                lambda pid: self._abrir_historia_de_paciente({"id": pid})
            )
        if hasattr(self.sessions_view, "sesion_actualizada"):
            self.sessions_view.sesion_actualizada.connect(self.patients_view.load_data)
        if hasattr(self.patients_view, "visita_actualizada"):
            self.patients_view.visita_actualizada.connect(self.sessions_view.load_data)
        if hasattr(self.farmacos_view, "agendar_control_requested"):
            self.farmacos_view.agendar_control_requested.connect(self._abrir_agenda_de_paciente_id)
        if hasattr(self.farmacos_view, "receta_actualizada"):
            self.farmacos_view.receta_actualizada.connect(lambda _d: self.patients_view.load_data())

    def _abrir_farmacos_de_paciente_id(self, paciente_id: str):
        """Cambia a Fármacos y preselecciona al paciente."""
        self._switch_tab(4)
        if hasattr(self.farmacos_view, "load_data"):
            self.farmacos_view.load_data()
        if hasattr(self.farmacos_view, "seleccionar_paciente_por_id"):
            self.farmacos_view.seleccionar_paciente_por_id(paciente_id)

    def _abrir_agenda_de_paciente_id(self, paciente_id: str):
        """Cambia a Agenda y preselecciona al paciente."""
        self._switch_tab(2)
        if hasattr(self.appointments_view, "load_data"):
            self.appointments_view.load_data()
        if hasattr(self.appointments_view, "seleccionar_paciente_por_id"):
            self.appointments_view.seleccionar_paciente_por_id(paciente_id)

    def _on_cita_actualizada(self, cita_data: dict):
        """Sincroniza notas de citas completadas con Historia Clínica y recarga vistas."""
        try:
            if (
                not cita_data.get("deleted")
                and cita_data.get("estado") == "Completada"
                and cita_data.get("notas")
                and cita_data.get("paciente_id")
                and hasattr(self.patients_view, "db")
                and hasattr(self.patients_view.db, "crear_sesion")
            ):
                db = self.patients_view.db
                existentes = db.obtener_sesiones_por_paciente(cita_data["paciente_id"]) if hasattr(db, "obtener_sesiones_por_paciente") else []
                ya_existe = any(
                    s.get("fecha") == cita_data.get("fecha") and s.get("hora") == cita_data.get("hora")
                    for s in existentes
                )
                if not ya_existe:
                    db.crear_sesion({
                        "paciente_id": cita_data["paciente_id"],
                        "paciente_nombre": cita_data.get("paciente_nombre", ""),
                        "paciente_cedula": cita_data.get("paciente_cedula", ""),
                        "fecha": cita_data.get("fecha", ""),
                        "hora": cita_data.get("hora", ""),
                        "tipo": cita_data.get("tipo", "Sucesiva"),
                        "evolucion": cita_data.get("notas", ""),
                        "notas": cita_data.get("notas", ""),
                        "nota_recordatorio": "",
                    })
        except Exception as e:
            print(f"[WARN] Sincronizando nota de cita con Historia: {e}")

        for view_name in ("patients_view", "sessions_view"):
            view = getattr(self, view_name, None)
            if view and hasattr(view, "load_data"):
                try:
                    view.load_data()
                except Exception as e:
                    print(f"[WARN] Error sincronizando {view_name}: {e}")

    def _on_historia_sincronizo_paciente(self, *_args):
        """Recarga Identificación y módulos relacionados cuando Historia Clínica crea/actualiza un paciente."""
        if hasattr(self.identificacion_view, "_cargar_pacientes"):
            try:
                self.identificacion_view._cargar_pacientes()
            except Exception as e:
                print(f"[WARN] Error sincronizando identificacion_view: {e}")
        for view_name in ("appointments_view", "sessions_view"):
            view = getattr(self, view_name, None)
            if view and hasattr(view, "load_data"):
                try:
                    view.load_data()
                except Exception as e:
                    print(f"[WARN] Error sincronizando {view_name}: {e}")

    def _on_paciente_sincronizado(self, *_args):
        """Recarga la caché de pacientes en Historia Clínica y módulos relacionados."""
        for view_name in ("patients_view", "appointments_view", "sessions_view"):
            view = getattr(self, view_name, None)
            if view and hasattr(view, "load_data"):
                try:
                    view.load_data()
                except Exception as e:
                    print(f"[WARN] Error sincronizando {view_name}: {e}")

    def _abrir_historia_de_paciente(self, paciente: dict):
        """Cambia a Historia Clínica y selecciona automáticamente al paciente."""
        self._switch_tab(1)
        if hasattr(self.patients_view, "load_data"):
            self.patients_view.load_data()
        if hasattr(self.patients_view, "seleccionar_paciente_por_id"):
            self.patients_view.seleccionar_paciente_por_id(paciente.get("id", ""))

    def reload_all_data(self):
        """Recarga todas las vistas secundarias con los datos aislados del usuario actual."""
        print("[DEBUG] DashboardView: Recargando todos los módulos para el usuario activo...")
        if hasattr(self, "identificacion_view") and hasattr(self.identificacion_view, "_cargar_pacientes"):
            try:
                self.identificacion_view._cargar_pacientes()
            except Exception as e:
                print(f"[WARN] Error recargando identificacion_view: {e}")
        if hasattr(self, "patients_view") and hasattr(self.patients_view, "load_data"):
            try:
                self.patients_view.load_data()
            except Exception as e:
                print(f"[WARN] Error recargando patients_view: {e}")
        if hasattr(self, "appointments_view") and hasattr(self.appointments_view, "load_data"):
            try:
                self.appointments_view.load_data()
            except Exception as e:
                print(f"[WARN] Error recargando appointments_view: {e}")
        if hasattr(self, "sessions_view") and hasattr(self.sessions_view, "load_data"):
            try:
                self.sessions_view.load_data()
            except Exception as e:
                print(f"[WARN] Error recargando sessions_view: {e}")
        if hasattr(self, "billing_view") and hasattr(self.billing_view, "load_data"):
            try:
                self.billing_view.load_data()
            except Exception as e:
                print(f"[WARN] Error recargando billing_view: {e}")
        if hasattr(self, "farmacos_view") and hasattr(self.farmacos_view, "load_data"):
            try:
                self.farmacos_view.load_data()
            except Exception as e:
                print(f"[WARN] Error recargando farmacos_view: {e}")

    def clear_all_data(self):
        """Limpia todas las tablas y formularios en pantalla al cerrar sesión para evitar fuga de datos."""
        print("[DEBUG] DashboardView: Limpiando tablas de memoria por cierre de sesión.")
        if hasattr(self, "identificacion_view"):
            try:
                if hasattr(self.identificacion_view, "tabla_pacientes"):
                    self.identificacion_view.tabla_pacientes.setRowCount(0)
                if hasattr(self.identificacion_view, "_cancelar"):
                    self.identificacion_view._cancelar()
                self.identificacion_view._pacientes_cache = []
            except Exception:
                pass
        if hasattr(self, "patients_view"):
            try:
                if hasattr(self.patients_view, "table"):
                    self.patients_view.table.setRowCount(0)
                self.patients_view._historias_cache = []
            except Exception:
                pass
        if hasattr(self, "appointments_view"):
            try:
                if hasattr(self.appointments_view, "table"):
                    self.appointments_view.table.setRowCount(0)
                self.appointments_view._citas_cache = []
            except Exception:
                pass
        if hasattr(self, "sessions_view"):
            try:
                if hasattr(self.sessions_view, "table"):
                    self.sessions_view.table.setRowCount(0)
                self.sessions_view._sesiones_cache = []
            except Exception:
                pass
        if hasattr(self, "billing_view"):
            try:
                if hasattr(self.billing_view, "table"):
                    self.billing_view.table.setRowCount(0)
            except Exception:
                pass

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
        layout.setContentsMargins(16, 0, 24, 0)
        layout.setSpacing(12)

        self.btn_toggle_sidebar = QPushButton("")
        self.btn_toggle_sidebar.setObjectName("btnSecondary")
        self.btn_toggle_sidebar.setIcon(svg_icon("chevron-left", color="#475569", size=18))
        self.btn_toggle_sidebar.setIconSize(QSize(18, 18))
        self.btn_toggle_sidebar.setFixedSize(36, 36)
        self.btn_toggle_sidebar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_sidebar.setToolTip("Contraer menú lateral")
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        layout.addWidget(self.btn_toggle_sidebar)

        title = QLabel("PSIQUE — Sistema de Gestión Clínico Psicológica")
        title.setObjectName("topbarTitle")
        layout.addWidget(title)
        layout.addStretch()

        # ── Módulo de Actualización en la barra superior ──
        self.update_btn = QPushButton("🔄 Buscar Actualización")
        self.update_btn.setObjectName("updateBtn")
        self.update_btn.setToolTip("Comprobar si hay nuevas versiones del sistema disponibles")
        self.update_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_btn.setStyleSheet("""
            QPushButton#updateBtn {
                background: #f1f5f9;
                color: #334155;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 14px;
            }
            QPushButton#updateBtn:hover {
                background: #e2e8f0;
                color: #0f172a;
            }
        """)
        self.update_btn.clicked.connect(self._on_update_clicked)
        layout.addWidget(self.update_btn)

        # Botón Toggle Theme
        self.theme_btn = QPushButton(" Modo Oscuro")
        self.theme_btn.setObjectName("btnSecondary")
        self.theme_btn.setIcon(svg_icon("moon", color="#475569", size=15))
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self._on_theme_toggled)
        layout.addWidget(self.theme_btn)

        # Botón Logout
        self.logout_btn = QPushButton(" Cerrar sesión")
        self.logout_btn.setObjectName("logoutBtn")
        self.logout_btn.setIcon(svg_icon("log-out", color="#dc2626", size=15))
        self.logout_btn.clicked.connect(self.logout_requested.emit)
        layout.addWidget(self.logout_btn)

        self._is_dark = False
        return bar

    def set_theme_mode(self, is_dark: bool):
        """Sincroniza los iconos y etiquetas del topbar según el tema activo."""
        self._is_dark = bool(is_dark)
        if self._is_dark:
            self.theme_btn.setText(" Modo Claro")
            self.theme_btn.setIcon(svg_icon("sun", color="#fbbf24", size=15))
            if hasattr(self, "btn_toggle_sidebar"):
                self.btn_toggle_sidebar.setIcon(
                    svg_icon("menu" if self._sidebar_collapsed else "chevron-left", color="#e2e8f0", size=18)
                )
            if hasattr(self, "logout_btn"):
                self.logout_btn.setIcon(svg_icon("log-out", color="#fca5a5", size=15))
        else:
            self.theme_btn.setText(" Modo Oscuro")
            self.theme_btn.setIcon(svg_icon("moon", color="#475569", size=15))
            if hasattr(self, "btn_toggle_sidebar"):
                self.btn_toggle_sidebar.setIcon(
                    svg_icon("menu" if self._sidebar_collapsed else "chevron-left", color="#475569", size=18)
                )
            if hasattr(self, "logout_btn"):
                self.logout_btn.setIcon(svg_icon("log-out", color="#dc2626", size=15))

    def _on_update_clicked(self):
        self.update_requested.emit()

    def set_update_available(self, version: str, notes: str = ""):
        """Modifica el módulo superior para avisar de forma llamativa que hay una nueva versión."""
        self.update_btn.setText(f"✨ ¡Nueva versión v{version} disponible!")
        self.update_btn.setToolTip(f"Versión {version} lista para descargar e instalar.\nHaz clic para ver detalles.")
        self.update_btn.setStyleSheet("""
            QPushButton#updateBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
                color: #ffffff;
                border: 1px solid #047857;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 14px;
            }
            QPushButton#updateBtn:hover {
                background: #047857;
            }
        """)

    def set_system_up_to_date(self, current_version: str):
        """Muestra en el módulo superior que el sistema está al día."""
        self.update_btn.setText(f"✓ Sistema v{current_version}")
        self.update_btn.setToolTip(f"Tu sistema está actualizado con la versión más reciente (v{current_version}).\nHaz clic para verificar de nuevo.")
        self.update_btn.setStyleSheet("""
            QPushButton#updateBtn {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 14px;
            }
            QPushButton#updateBtn:hover {
                background: #e2e8f0;
                color: #1e293b;
            }
        """)
        
    def _on_theme_toggled(self):
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
