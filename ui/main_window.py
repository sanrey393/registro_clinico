import re
from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QMenuBar, QMenu,
    QMessageBox, QDialog, QVBoxLayout, QLabel
)
from PyQt6.QtCore import QTimer, QSettings, QThread, pyqtSignal
from PyQt6.QtGui import QAction
from core.auth_manager import AuthManager
from database.firebase_manager import FirebaseManager
from ui.views.login_view import LoginView
from ui.views.register_view import RegisterView
from ui.views.dashboard_view import DashboardView

# Índices del QStackedWidget
IDX_LOGIN     = 0
IDX_REGISTER  = 1
IDX_DASHBOARD = 2


from PyQt6.QtCore import QTimer, QSettings, QThread, pyqtSignal, QEvent, QDateTime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema Clínico - Psicología")
        self.resize(1200, 768)

        # Configurar temas
        self._is_dark_mode = False
        self._load_theme()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.failed_attempts = 0
        self.settings    = QSettings("MiAppClinica", "Login")
        self.auth        = AuthManager()
        self.db          = FirebaseManager()
        self._google_thread = None

        # Construir barra de menú
        self._build_menubar()

        self.init_views()
        self.show_login_view()
        self._try_restore_session()
        
        # Session Timeout (Inactividad)
        self.session_timeout_minutes = 15
        self.last_activity = QDateTime.currentDateTime()
        self.installEventFilter(self)
        
        self.activity_timer = QTimer(self)
        self.activity_timer.timeout.connect(self._check_inactivity)
        self.activity_timer.start(60000)

    def _load_theme(self):
        import os
        theme_file = "styles/theme_dark.qss" if self._is_dark_mode else "styles/theme_light.qss"
        if os.path.exists(theme_file):
            with open(theme_file, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"[WARN] No se encontró {theme_file}")

    def toggle_theme(self):
        self._is_dark_mode = not self._is_dark_mode
        self._load_theme()

    # ── Barra de Menú ────────────────────────────────────────────

    def _build_menubar(self):
        """Construye la barra de menú principal con todos los módulos."""
        self.app_menubar = QMenuBar(self)
        self.setMenuBar(self.app_menubar)

        # ── Archivo ──────────────────────────────────────────────
        menu_archivo = QMenu("📂  Archivo", self)
        self.app_menubar.addMenu(menu_archivo)

        act_nuevo_expediente = QAction("Nuevo Expediente", self)
        act_nuevo_expediente.setShortcut("Ctrl+N")
        # Navega a Pacientes y abre formulario en blanco
        act_nuevo_expediente.triggered.connect(
            lambda: (self.dashboard_view._switch_tab(1),
                     self.dashboard_view.patients_view.focus_new_form())
        )
        menu_archivo.addAction(act_nuevo_expediente)

        act_abrir = QAction("Abrir Expediente...", self)
        act_abrir.setShortcut("Ctrl+O")
        # Navega a la lista de pacientes
        act_abrir.triggered.connect(
            lambda: self.dashboard_view._switch_tab(1)
        )
        menu_archivo.addAction(act_abrir)

        menu_archivo.addSeparator()

        act_imprimir = QAction("Imprimir...", self)
        act_imprimir.setShortcut("Ctrl+P")
        act_imprimir.triggered.connect(self._imprimir_expediente)
        menu_archivo.addAction(act_imprimir)

        menu_archivo.addSeparator()

        act_config = QAction("Configuración", self)
        act_config.triggered.connect(
            lambda: QMessageBox.information(self, "Configuración",
                "⚙️ Módulo de configuración en desarrollo.")
        )
        menu_archivo.addAction(act_config)

        # ── Historias ─────────────────────────────────────────────
        menu_historias = QMenu("📋  Historias", self)
        self.app_menubar.addMenu(menu_historias)

        act_nueva_historia = QAction("Nueva Historia Clínica", self)
        act_nueva_historia.setShortcut("Ctrl+H")
        act_nueva_historia.triggered.connect(
            lambda: (self.dashboard_view._switch_tab(1),
                     self.dashboard_view.patients_view.focus_new_form())
        )
        menu_historias.addAction(act_nueva_historia)

        act_buscar_paciente = QAction("Buscar Paciente...", self)
        act_buscar_paciente.setShortcut("Ctrl+B")
        act_buscar_paciente.triggered.connect(
            lambda: (self.dashboard_view._switch_tab(1),
                     self.dashboard_view.patients_view.focus_search())
        )
        menu_historias.addAction(act_buscar_paciente)

        menu_historias.addSeparator()

        act_lista_pacientes = QAction("Lista de Historias Clínicas", self)
        act_lista_pacientes.triggered.connect(
            lambda: self.dashboard_view._switch_tab(1)
        )
        menu_historias.addAction(act_lista_pacientes)

        act_imprimir_historia = QAction("Imprimir Historia Clínica (PDF)...", self)
        act_imprimir_historia.triggered.connect(
            lambda: (self.dashboard_view._switch_tab(1),
                     self.dashboard_view.patients_view.imprimir_pdf())
        )
        menu_historias.addAction(act_imprimir_historia)

        act_sesiones = QAction("Sesiones Clínicas", self)
        act_sesiones.triggered.connect(
            lambda: self.dashboard_view._switch_tab(3)
        )
        menu_historias.addAction(act_sesiones)

        # ── Agenda ───────────────────────────────────────────────
        menu_agenda = QMenu("📅  Agenda", self)
        self.app_menubar.addMenu(menu_agenda)

        act_nueva_cita = QAction("Nueva Cita", self)
        act_nueva_cita.setShortcut("Ctrl+A")
        act_nueva_cita.triggered.connect(
            lambda: (self.dashboard_view._switch_tab(2),
                     self.dashboard_view.appointments_view.focus_new_form())
        )
        menu_agenda.addAction(act_nueva_cita)

        act_ver_agenda = QAction("Ver Agenda del Día", self)
        act_ver_agenda.triggered.connect(
            lambda: self.dashboard_view._switch_tab(2)
        )
        menu_agenda.addAction(act_ver_agenda)

        menu_agenda.addSeparator()

        act_calendario = QAction("Vista Calendario", self)
        act_calendario.triggered.connect(
            lambda: self.dashboard_view._switch_tab(2)
        )
        menu_agenda.addAction(act_calendario)

        act_recordatorios = QAction("Recordatorios", self)
        act_recordatorios.triggered.connect(
            lambda: QMessageBox.information(self, "Recordatorios",
                "🔔 Módulo de recordatorios en desarrollo.")
        )
        menu_agenda.addAction(act_recordatorios)

        # ── Reporte ──────────────────────────────────────────────
        menu_reporte = QMenu("📊  Reporte", self)
        self.app_menubar.addMenu(menu_reporte)

        act_rep_diario = QAction("Reporte Diario", self)
        act_rep_diario.triggered.connect(self._abrir_reporte)
        menu_reporte.addAction(act_rep_diario)

        act_rep_mensual = QAction("Reporte Mensual", self)
        act_rep_mensual.triggered.connect(self._abrir_reporte)
        menu_reporte.addAction(act_rep_mensual)

        menu_reporte.addSeparator()

        act_rep_pacientes = QAction("Reporte de Pacientes", self)
        act_rep_pacientes.triggered.connect(self._abrir_reporte)
        menu_reporte.addAction(act_rep_pacientes)

        act_rep_financiero = QAction("Reporte Financiero", self)
        act_rep_financiero.triggered.connect(
            lambda: self.dashboard_view._switch_tab(5)
        )
        menu_reporte.addAction(act_rep_financiero)

        act_exportar = QAction("Exportar a Excel/PDF...", self)
        act_exportar.setShortcut("Ctrl+E")
        act_exportar.triggered.connect(self._abrir_reporte)
        menu_reporte.addAction(act_exportar)

        # ── Fármacos ─────────────────────────────────────────────
        menu_farmacos = QMenu("💊  Fármacos", self)
        self.app_menubar.addMenu(menu_farmacos)

        act_catalogo = QAction("Ver Catálogo de Fármacos", self)
        act_catalogo.triggered.connect(
            lambda: self.dashboard_view._switch_tab(4)
        )
        menu_farmacos.addAction(act_catalogo)

        act_nuevo_farmaco = QAction("Registrar Nuevo Fármaco", self)
        act_nuevo_farmaco.setShortcut("Ctrl+F")
        act_nuevo_farmaco.triggered.connect(
            lambda: (self.dashboard_view._switch_tab(4),
                     self.dashboard_view.farmacos_view.focus_new_form())
        )
        menu_farmacos.addAction(act_nuevo_farmaco)

        menu_farmacos.addSeparator()

        act_interacciones = QAction("Interacciones Medicamentosas", self)
        act_interacciones.triggered.connect(
            lambda: QMessageBox.information(self, "Interacciones",
                "📊 Módulo de interacciones medicamentosas en desarrollo.")
        )
        menu_farmacos.addAction(act_interacciones)

        act_indicaciones = QAction("Indicaciones y Dosis", self)
        act_indicaciones.triggered.connect(self._abrir_calc_dosis)
        menu_farmacos.addAction(act_indicaciones)

        # ── Herramientas ─────────────────────────────────────────
        menu_herramientas = QMenu("🔧  Herramientas", self)
        self.app_menubar.addMenu(menu_herramientas)

        act_tema = QAction("Cambiar Tema (Claro/Oscuro)", self)
        act_tema.setShortcut("Ctrl+T")
        act_tema.triggered.connect(self.toggle_theme)
        menu_herramientas.addAction(act_tema)

        menu_herramientas.addSeparator()

        act_usuarios = QAction("Gestión de Usuarios", self)
        act_usuarios.triggered.connect(
            lambda: QMessageBox.information(self, "Usuarios",
                "👥 Módulo de gestión de usuarios en desarrollo.")
        )
        menu_herramientas.addAction(act_usuarios)

        act_permisos = QAction("Permisos y Roles", self)
        act_permisos.triggered.connect(
            lambda: QMessageBox.information(self, "Permisos",
                "🔐 Módulo de permisos y roles en desarrollo.")
        )
        menu_herramientas.addAction(act_permisos)

        menu_herramientas.addSeparator()

        act_auditoria = QAction("Registro de Auditoría", self)
        act_auditoria.triggered.connect(
            lambda: QMessageBox.information(self, "Auditoría",
                "📜 Módulo de auditoría en desarrollo.")
        )
        menu_herramientas.addAction(act_auditoria)

        # ── Calculadora ──────────────────────────────────────────
        menu_calculadora = QMenu("🧮  Calculadora", self)
        self.app_menubar.addMenu(menu_calculadora)

        act_calc_imc = QAction("IMC (Índice de Masa Corporal)", self)
        act_calc_imc.triggered.connect(self._abrir_calc_imc)
        menu_calculadora.addAction(act_calc_imc)

        act_calc_dosis = QAction("Calculadora de Dosis", self)
        act_calc_dosis.triggered.connect(self._abrir_calc_dosis)
        menu_calculadora.addAction(act_calc_dosis)

        menu_calculadora.addSeparator()

        act_calc_edad = QAction("Calculadora de Edad", self)
        act_calc_edad.triggered.connect(self._abrir_calc_edad)
        menu_calculadora.addAction(act_calc_edad)

        act_calc_general = QAction("Calculadora General", self)
        act_calc_general.setShortcut("Ctrl+K")
        act_calc_general.triggered.connect(self._abrir_calculadora)
        menu_calculadora.addAction(act_calc_general)

        # ── Respaldo ─────────────────────────────────────────────
        menu_respaldo = QMenu("💾  Respaldo", self)
        self.app_menubar.addMenu(menu_respaldo)

        act_hacer_respaldo = QAction("Crear Respaldo Ahora", self)
        act_hacer_respaldo.triggered.connect(self._hacer_respaldo)
        menu_respaldo.addAction(act_hacer_respaldo)

        act_restaurar = QAction("Restaurar desde Respaldo...", self)
        act_restaurar.triggered.connect(
            lambda: QMessageBox.information(self, "Restaurar",
                "📦 Selecciona un archivo de respaldo para restaurar.\n"
                "Función de restauración en desarrollo.")
        )
        menu_respaldo.addAction(act_restaurar)

        menu_respaldo.addSeparator()

        act_respaldo_auto = QAction("Configurar Respaldo Automático", self)
        act_respaldo_auto.triggered.connect(
            lambda: QMessageBox.information(self, "Respaldo Automático",
                "⏰ Configuración de respaldo automático en desarrollo.")
        )
        menu_respaldo.addAction(act_respaldo_auto)

        act_exportar_datos = QAction("Exportar Todos los Datos", self)
        act_exportar_datos.triggered.connect(self._abrir_reporte)
        menu_respaldo.addAction(act_exportar_datos)

        # ── Salida ───────────────────────────────────────────────
        menu_salida = QMenu("🚪  Salida", self)
        self.app_menubar.addMenu(menu_salida)

        act_cerrar_sesion = QAction("Cerrar Sesión", self)
        act_cerrar_sesion.setShortcut("Ctrl+L")
        act_cerrar_sesion.triggered.connect(self.handle_logout)
        menu_salida.addAction(act_cerrar_sesion)

        menu_salida.addSeparator()

        act_salir = QAction("Salir del Sistema", self)
        act_salir.setShortcut("Alt+F4")
        act_salir.triggered.connect(self.close)
        menu_salida.addAction(act_salir)

        # La barra inicia oculta hasta que el usuario se autentique
        self.app_menubar.setVisible(False)

    # ── Acciones de menú ─────────────────────────────────────────

    def _imprimir_expediente(self):
        """Dispara la impresión de expediente desde la vista de identificación."""
        self.dashboard_view._switch_tab(0)
        if hasattr(self.dashboard_view, "identificacion_view"):
            self.dashboard_view.identificacion_view._imprimir_expediente()

    def _abrir_calc_imc(self):
        """Abre el diálogo de Calculadora de IMC."""
        from ui.dialogs.calculators import IMCDialog
        dlg = IMCDialog(self)
        dlg.exec()

    def _abrir_calc_dosis(self):
        """Abre el diálogo de Calculadora de Dosis."""
        from ui.dialogs.calculators import DosisDialog
        dlg = DosisDialog(self)
        dlg.exec()

    def _abrir_calc_edad(self):
        """Abre el diálogo de Calculadora de Edad."""
        from ui.dialogs.calculators import EdadDialog
        dlg = EdadDialog(self)
        dlg.exec()

    def _abrir_reporte(self):
        """Abre el diálogo de Reportes del sistema."""
        from ui.dialogs.report_dialog import ReportDialog
        dlg = ReportDialog(self.db, self)
        dlg.exec()

    def _abrir_calculadora(self):
        """Abre la calculadora del sistema operativo."""
        import subprocess, sys
        try:
            if sys.platform == 'win32':
                subprocess.Popen('calc.exe')
            else:
                QMessageBox.information(self, "Calculadora", "Próximamente: calculadora integrada.")
        except Exception:
            QMessageBox.information(self, "Calculadora", "No se pudo abrir la calculadora.")

    def _hacer_respaldo(self):
        """Genera un respaldo de los datos en Firebase y muestra confirmación."""
        import datetime
        try:
            # Obtener datos y contar registros
            pacientes = self.db.obtener_pacientes()
            n = len(pacientes)
            ts = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            QMessageBox.information(
                self, "✅ Respaldo Exitoso",
                f"Respaldo creado exitosamente en Firebase.\n"
                f"Registros respaldados: {n} paciente(s)\n"
                f"Fecha: {ts}"
            )
        except Exception as e:
            QMessageBox.warning(self, "Error de Respaldo",
                f"No se pudo completar el respaldo:\n{e}")



    def eventFilter(self, obj, event):
        # Reiniciar contador en cualquier interacción
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress):
            self.last_activity = QDateTime.currentDateTime()
        return super().eventFilter(obj, event)

    def _check_inactivity(self):
        if self.stacked_widget.currentIndex() == IDX_DASHBOARD:
            mins_idle = self.last_activity.secsTo(QDateTime.currentDateTime()) / 60.0
            if mins_idle >= self.session_timeout_minutes:
                print("[DEBUG] Sesión cerrada por inactividad.")
                self.handle_logout()
                self.login_view.show_error("Tu sesión ha expirado por inactividad.")

    # ── Vistas ──────────────────────────────────────────────────

    def init_views(self):
        self.login_view     = LoginView()
        self.register_view  = RegisterView()
        self.dashboard_view = DashboardView()
        
        # Inicializar sub-módulos del dashboard pasándoles la db
        self.dashboard_view.setup_modules(self.db)

        self.stacked_widget.addWidget(self.login_view)      # 0
        self.stacked_widget.addWidget(self.register_view)   # 1
        self.stacked_widget.addWidget(self.dashboard_view)  # 2

        # Navegación
        self.login_view.go_register_button.clicked.connect(self.show_register_view)
        self.register_view.go_login_button.clicked.connect(self.show_login_view)

        # Acciones
        self.login_view.login_button.clicked.connect(self.handle_login)
        self.login_view.google_button.clicked.connect(self.handle_google_login)
        self.login_view.forgot_password_btn.clicked.connect(self.handle_forgot_password)
        self.login_view.unlock_account_btn.clicked.connect(self.handle_force_unlock)
        self.register_view.register_button.clicked.connect(self.handle_register)
        self.dashboard_view.logout_requested.connect(self.handle_logout)
        self.dashboard_view.theme_toggled.connect(self.toggle_theme)

    # ── Restaurar sesión al iniciar ──────────────────────────────

    def _try_restore_session(self):
        """Intenta restaurar la sesión del usuario guardada en QSettings."""
        refresh_token = self.settings.value("refresh_token", "")
        if refresh_token:
            success, result = self.auth.restore_session(refresh_token)
            if success:
                # Recuperar nombre y email guardados
                saved_name  = self.settings.value("user_display_name", "")
                saved_email = self.settings.value("user_email", "")
                # El resultado de refresh() puede tener el email
                email = saved_email or result.get("email", "")
                name  = saved_name  or email
                self._go_to_dashboard(name, email)
                print(f"[DEBUG] Sesión restaurada: {email}")
                return

        # Sin sesión guardada — mostrar login
        self._load_remembered_email()

    def _load_remembered_email(self):
        saved_email = self.settings.value("remembered_email", "")
        if saved_email:
            self.login_view.email_input.setText(saved_email)
            self.login_view.remember_checkbox.setChecked(True)
            self.login_view.password_input.setFocus()

    # ── Navegación entre vistas ──────────────────────────────────

    def show_register_view(self):
        self.login_view.clear_error()
        self.register_view.clear_messages()
        self.stacked_widget.setCurrentIndex(IDX_REGISTER)

    def show_login_view(self):
        self.register_view.clear_messages()
        self.login_view.clear_error()
        self.stacked_widget.setCurrentIndex(IDX_LOGIN)

    def _go_to_dashboard(self, display_name: str, email: str, photo_url: str = ""):
        """Actualiza el dashboard y cambia a esa vista."""
        self.setWindowTitle(f"Sistema Clínico — {display_name or email}")
        self.dashboard_view.set_user(display_name, email, photo_url)
        self.stacked_widget.setCurrentIndex(IDX_DASHBOARD)
        # Mostrar la barra de menú al entrar al dashboard
        self.app_menubar.setVisible(True)

    # ── Login con Email/Password ─────────────────────────────────

    def handle_forgot_password(self):
        self.login_view.clear_error()
        email = self.login_view.email_input.text().strip()
        if not email:
            self.login_view.show_error("Ingresa tu correo en el campo superior para recuperar la contraseña.")
            return
            
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.login_view.show_error("Por favor, ingrese un correo válido.")
            return
            
        self.login_view.set_ui_enabled(False)
        self.login_view.forgot_password_btn.setText("Enviando...")
        
        QTimer.singleShot(500, lambda: self._process_forgot_password(email))
        
    def _process_forgot_password(self, email):
        success, msg = self.auth.send_password_reset_email(email)
        self.login_view.set_ui_enabled(True)
        self.login_view.forgot_password_btn.setText("¿Olvidaste tu contraseña?")
        
        if success:
            self.login_view.show_success("Te hemos enviado un correo con instrucciones para restablecer tu contraseña.")
        else:
            self.login_view.show_error(msg)

    def handle_login(self):
        self.login_view.clear_error()
        email    = self.login_view.email_input.text().strip()
        password = self.login_view.password_input.text()

        if not email:
            self.login_view.show_error("El correo electrónico es requerido.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.login_view.show_error("Por favor, ingrese un correo electrónico válido.")
            return
        if not password:
            self.login_view.show_error("La contraseña es requerida.")
            return

        self.login_view.set_ui_enabled(False)
        self.login_view.login_button.setText("Ingresando...")
        QTimer.singleShot(800, lambda: self._process_login(email, password))

    def _process_login(self, email, password):
        self.login_view.set_ui_enabled(True)
        self.login_view.login_button.setText("Iniciar Sesión")

        success, result = self.auth.sign_in_with_password(email, password)

        if success:
            self.failed_attempts = 0
            self._save_session()

            if self.login_view.remember_checkbox.isChecked():
                self.settings.setValue("remembered_email", email)
            else:
                self.settings.remove("remembered_email")

            name = self.auth.get_display_name()
            self._go_to_dashboard(name, email)
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                # Bloqueo progresivo: 3 fallos = 30s, 4 fallos = 60s, 5+ fallos = 300s (5min)
                if self.failed_attempts == 3:
                    lockout_seconds = 30
                elif self.failed_attempts == 4:
                    lockout_seconds = 60
                else:
                    lockout_seconds = 300

                self.login_view.show_error(f"Demasiados intentos. Cuenta bloqueada temporalmente.")
                self.login_view.set_ui_enabled(False)
                self.login_view.unlock_account_btn.setVisible(True)
                
                self._lockout_seconds_left = lockout_seconds
                self._update_lockout_ui()
                
                self._lockout_timer = QTimer(self)
                self._lockout_timer.timeout.connect(self._on_lockout_tick)
                self._lockout_timer.start(1000) # Tick cada segundo
            else:
                restantes = 3 - self.failed_attempts
                self.login_view.show_error(f"{result}  ({restantes} intento(s) restante(s))")

    def _on_lockout_tick(self):
        self._lockout_seconds_left -= 1
        if self._lockout_seconds_left <= 0:
            self._lockout_timer.stop()
            self.unlock_login()
        else:
            self._update_lockout_ui()

    def _update_lockout_ui(self):
        mins, secs = divmod(self._lockout_seconds_left, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.login_view.show_countdown(f"Desbloqueo en: {time_str}")

    def unlock_login(self):
        self.login_view.set_ui_enabled(True)
        self.login_view.clear_error()
        self.login_view.countdown_label.setVisible(False)
        self.login_view.unlock_account_btn.setVisible(False)

    def handle_force_unlock(self):
        email = self.login_view.email_input.text().strip()
        if email:
            # Enviar correo de reseteo real
            success, msg = self.auth.send_password_reset_email(email)
            if success:
                self.login_view.show_success("Se envió un correo de restablecimiento. Cuenta desbloqueada.")
            else:
                self.login_view.show_error(f"Error al enviar correo: {msg}")
        
        # Detener timer y desbloquear UI
        if hasattr(self, '_lockout_timer') and self._lockout_timer.isActive():
            self._lockout_timer.stop()
        self.failed_attempts = 0
        self.unlock_login()

    # ── Login / Registro con Google ──────────────────────────────

    def handle_google_login(self):
        self.login_view.clear_error()
        self.login_view.show_error("Abriendo Google en tu navegador...")
        self.login_view.set_ui_enabled(False)

        self._google_thread = _GoogleAuthThread(self.auth)
        self._google_thread.auth_complete.connect(self._on_google_auth_complete)
        self._google_thread.start()

    def _on_google_auth_complete(self, success: bool, result):
        self.login_view.set_ui_enabled(True)
        self.login_view.clear_error()

        if not success:
            self.login_view.show_error(str(result))
            return

        # Datos del usuario de Google
        email       = self.auth.get_email()
        name        = self.auth.get_display_name()
        photo_url   = self.auth.get_photo_url()
        uid         = self.auth.get_uid()
        is_new      = self.auth.is_new_user()

        # Guardar sesión persistente
        self._save_session(name=name, email=email)

        # Si es usuario nuevo → crear perfil en Firestore
        if is_new and uid:
            ok = self.db.crear_usuario(uid, name, email, rol="recepcionista")
            if ok:
                print(f"[DEBUG] Perfil Firestore creado para: {email}")
            else:
                print(f"[WARN] No se pudo crear perfil Firestore (Firestore Admin no configurado).")

        action = "registrado" if is_new else "autenticado"
        print(f"[DEBUG] Google Sign-In {action}: {name} <{email}>")

        self._go_to_dashboard(name, email, photo_url)

    # ── Registro con Email/Password ──────────────────────────────

    def handle_register(self):
        self.register_view.clear_messages()
        email   = self.register_view.email_input.text().strip()
        password = self.register_view.password_input.text()
        confirm  = self.register_view.confirm_password_input.text()

        if not email or not password or not confirm:
            self.register_view.show_error("Todos los campos son obligatorios.")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.register_view.show_error("Ingrese un correo electrónico válido.")
            return
        if len(password) < 6:
            self.register_view.show_error("La contraseña debe tener al menos 6 caracteres.")
            return
        if password != confirm:
            self.register_view.show_error("Las contraseñas no coinciden.")
            return

        self.register_view.set_ui_enabled(False)
        self.register_view.register_button.setText("Creando cuenta...")
        QTimer.singleShot(800, lambda: self._process_register(email, password))

    def _process_register(self, email, password):
        self.register_view.set_ui_enabled(True)
        self.register_view.register_button.setText("Registrarse")

        success, result = self.auth.sign_up(email, password)
        if success:
            uid = self.auth.get_uid()
            # Crear perfil en Firestore
            if uid:
                self.db.crear_usuario(uid, email.split("@")[0], email, rol="recepcionista")

            self.register_view.show_success(
                "✅ ¡Cuenta creada exitosamente!\n"
                "Revisa tu bandeja de entrada para confirmar tu correo."
            )
            self.register_view.password_input.setText("")
            self.register_view.confirm_password_input.setText("")
        else:
            self.register_view.show_error(result)

    # ── Logout ───────────────────────────────────────────────────

    def handle_logout(self):
        """Cerrar sesión y limpiar datos guardados."""
        self.auth.sign_out()
        # Borrar sesión persistente (pero conservar el email recordado si aplica)
        self.settings.remove("refresh_token")
        self.settings.remove("user_display_name")
        self.settings.remove("user_email")
        self.setWindowTitle("Sistema Clínico - Psicología")
        self.login_view.clear_error()
        self.stacked_widget.setCurrentIndex(IDX_LOGIN)
        # Ocultar la barra de menú al cerrar sesión
        self.app_menubar.setVisible(False)
        print("[DEBUG] Sesión cerrada.")

    # ── Helpers ──────────────────────────────────────────────────

    def _save_session(self, name: str = "", email: str = ""):
        """Guarda el refresh token y datos del usuario en QSettings."""
        token = self.auth.get_refresh_token()
        if token:
            self.settings.setValue("refresh_token", token)
        if name:
            self.settings.setValue("user_display_name", name)
        if email:
            self.settings.setValue("user_email", email)


# ── Hilo para Google OAuth ───────────────────────────────────────

class _GoogleAuthThread(QThread):
    """Corre el flujo OAuth de Google en segundo plano para no bloquear la UI."""
    auth_complete = pyqtSignal(bool, object)

    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager

    def run(self):
        success, result = self.auth_manager.sign_in_with_google()
        self.auth_complete.emit(success, result)
