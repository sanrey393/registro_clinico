# ui/views/identificacion_view.py
# Vista principal de Identificación del Paciente

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QFrame, QMessageBox, QComboBox,
    QDateEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QFileDialog, QScrollArea,
    QGridLayout, QSpacerItem, QApplication, QSpinBox, QSplitter,
    QCompleter
)
from PyQt6.QtCore import Qt, QDate, QSize, QTimer, QRegularExpression, QStringListModel, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage, QFont, QColor, QIntValidator, QRegularExpressionValidator
from ui.widgets.smart_date_edit import SmartDateEdit
from ui.widgets.app_icons import svg_icon
from core.academic_catalog import (
    PNF_OPTIONS, ALL_TRAYECTOS, EMAIL_DOMAINS, get_trayectos_for_pnf,
    is_external_pnf, normalize_seccion, is_valid_seccion, validate_person_name,
    validate_cedula_num, validate_telefono_num
)


class IdentificacionView(QWidget):
    """
    Vista de inicio del sistema. Permite registrar, filtrar y gestionar pacientes.
    """

    paciente_guardado = pyqtSignal(dict)
    paciente_eliminado = pyqtSignal(str)
    abrir_historia_requested = pyqtSignal(dict)
    agendar_cita_requested = pyqtSignal(dict)
    farmacos_requested = pyqtSignal(dict)

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._foto_pixmap = None
        self._cache_busqueda_previa = []
        self._pacientes_cache = []
        self._paciente_id_actual = None
        self._setup_ui()
        if hasattr(self.db, "get_current_user_id") and self.db.get_current_user_id():
            self._cargar_pacientes()

    # ══════════════════════════════════════════════════════════════
    # UI Principal
    # ══════════════════════════════════════════════════════════════

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        # ── Contenedor superior: Formulario + Foto ──
        self.top_container = QWidget()
        self.top_container.setStyleSheet("background: transparent;")
        top_row = QHBoxLayout(self.top_container)
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(14)
        top_row.addWidget(self._build_form_panel(), 3)
        top_row.addWidget(self._build_photo_panel(), 1)

        # ── Splitter vertical para aprovechar la pantalla ──
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(6)
        self.splitter.setStyleSheet(
            "QSplitter::handle { background: #e2e8f0; border-radius: 3px; }"
            "QSplitter::handle:hover { background: #94a3b8; }"
        )
        self.splitter.addWidget(self.top_container)
        self.splitter.addWidget(self._build_listado_panel())
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        root.addWidget(self.splitter, 1)

    # ══════════════════════════════════════════════════════════════
    # Panel Formulario de Identificación
    # ══════════════════════════════════════════════════════════════

    def _build_form_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("rightPanel")

        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setOffset(0, 3)
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Título + indicador de modo
        title_row = QHBoxLayout()
        title = QLabel("Identificación del Paciente")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_row.addWidget(title)
        title_row.addStretch()

        self.lbl_modo_form = QLabel("🟢 Registrando nuevo paciente")
        self.lbl_modo_form.setStyleSheet(
            "font-size: 12px; font-weight: 600; color: #047857; "
            "background: #ecfdf5; border: 1px solid #a7f3d0; "
            "border-radius: 12px; padding: 3px 10px;"
        )
        title_row.addWidget(self.lbl_modo_form)
        layout.addLayout(title_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height:1px; border:none;")
        layout.addWidget(sep)

        # Grid de campos
        grid = QGridLayout()
        grid.setSpacing(8)
        grid.setColumnStretch(1, 2)
        grid.setColumnStretch(3, 1)

        row = 0

        # ── Fila 1: Nombre | Sexo ──────────────────────────────
        grid.addWidget(self._lbl("Nombre:"), row, 0)
        self.input_nombre = self._field(placeholder="Apellido y Nombre completo")
        self.input_nombre.setMaxLength(80)
        self.input_nombre.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü'\-\s]{0,80}$"))
        )
        self.input_nombre.setToolTip("Solo letras y espacios (Nombre y Apellido, máx. 80 caracteres).")
        grid.addWidget(self.input_nombre, row, 1)

        grid.addWidget(self._lbl("Sexo:"), row, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.combo_sexo = QComboBox()
        self.combo_sexo.addItems(["Masculino", "Femenino", "Otro"])
        self.combo_sexo.setStyleSheet(self._combo_style())
        grid.addWidget(self.combo_sexo, row, 3)
        row += 1

        # ── Fila 2: Fecha Nac | Edad | Estado Civil ────────────
        grid.addWidget(self._lbl("F. Nacimiento:"), row, 0)
        self.input_fnac = SmartDateEdit(QDate.currentDate().addYears(-25))
        self.input_fnac.dateChanged.connect(self._calcular_edad)
        grid.addWidget(self.input_fnac, row, 1)

        edad_civil_row = QHBoxLayout()
        edad_civil_row.setSpacing(8)

        self.lbl_edad = QLineEdit()
        self.lbl_edad.setReadOnly(True)
        self.lbl_edad.setPlaceholderText("Edad")
        self.lbl_edad.setMaximumWidth(70)

        self.combo_civil = QComboBox()
        self.combo_civil.addItems([
            "Soltero/a", "Casado/a", "Divorciado/a",
            "Viudo/a", "Unión estable"
        ])
        self.combo_civil.setStyleSheet(self._combo_style())

        edad_civil_row.addWidget(self._lbl("Edad:"))
        edad_civil_row.addWidget(self.lbl_edad)
        edad_civil_row.addWidget(self._lbl("Civil:"))
        edad_civil_row.addWidget(self.combo_civil, 1)

        edad_widget = QWidget()
        edad_widget.setStyleSheet("background: transparent;")
        edad_widget.setLayout(edad_civil_row)
        grid.addWidget(edad_widget, row, 2, 1, 2)
        row += 1

        # ── Fila 3: Cédula ─────────────────────────────────────
        grid.addWidget(self._lbl("Cédula:"), row, 0)
        cedula_row = QHBoxLayout()
        cedula_row.setSpacing(6)

        self.combo_tipo_cedula = QComboBox()
        self.combo_tipo_cedula.addItems(["V-", "E-", "P-", "J-"])
        self.combo_tipo_cedula.setMaximumWidth(60)
        self.combo_tipo_cedula.setStyleSheet(self._combo_style())

        self.input_cedula = QLineEdit()
        self.input_cedula.setPlaceholderText("Nº de cédula")
        self.input_cedula.setValidator(QIntValidator(0, 99999999))
        self.input_cedula.setStyleSheet(self._field_style())

        cedula_row.addWidget(self.combo_tipo_cedula)
        cedula_row.addWidget(self.input_cedula)

        cedula_widget = QWidget()
        cedula_widget.setStyleSheet("background: transparent;")
        cedula_widget.setLayout(cedula_row)
        grid.addWidget(cedula_widget, row, 1, 1, 3)
        row += 1

        # ── Fila 4: PNF | Trayecto | Sección | Año ──────────────
        grid.addWidget(self._lbl("PNF:"), row, 0)
        acad_row = QHBoxLayout()
        acad_row.setSpacing(8)

        self.combo_pnf = QComboBox()
        self.combo_pnf.addItems(PNF_OPTIONS)
        self.combo_pnf.setMinimumWidth(175)
        self.combo_pnf.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.combo_pnf.setStyleSheet(self._combo_style())
        self.combo_pnf.setToolTip("Seleccione el PNF del estudiante o 'No aplica / Externo' si es personal/externo.")
        self.combo_pnf.currentTextChanged.connect(self._on_pnf_changed)

        self.combo_trayecto = QComboBox()
        self.combo_trayecto.setMinimumWidth(130)
        self.combo_trayecto.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.combo_trayecto.setStyleSheet(self._combo_style())
        self.combo_trayecto.setToolTip("Trayecto cursado (Veterinaria tiene V trayectos; los demás IV).")

        self.input_seccion = QLineEdit()
        self.input_seccion.setPlaceholderText("Ej: 01")
        self.input_seccion.setMaxLength(2)
        self.input_seccion.setFixedWidth(72)
        self.input_seccion.setValidator(QRegularExpressionValidator(QRegularExpression(r"^\d{0,2}$")))
        self.input_seccion.setToolTip("Ingrese solo números de 2 dígitos (ej: 01, 02, 03).")
        self.input_seccion.setStyleSheet(self._field_style())
        self.input_seccion.editingFinished.connect(self._formatear_seccion)

        self.spin_anio = QSpinBox()
        self.spin_anio.setRange(2000, 2100)
        self.spin_anio.setValue(QDate.currentDate().year())
        self.spin_anio.setMinimumWidth(94)
        self.spin_anio.setMaximumWidth(110)
        self.spin_anio.setToolTip("Año académico en el que cursa el trayecto (ej: 2026).")

        acad_row.addWidget(self.combo_pnf, 2)
        acad_row.addWidget(self._lbl("Trayecto:"))
        acad_row.addWidget(self.combo_trayecto, 1)
        acad_row.addWidget(self._lbl("Secc.:"))
        acad_row.addWidget(self.input_seccion)
        acad_row.addWidget(self._lbl("Año:"))
        acad_row.addWidget(self.spin_anio)

        acad_widget = QWidget()
        acad_widget.setStyleSheet("background: transparent;")
        acad_widget.setLayout(acad_row)
        grid.addWidget(acad_widget, row, 1, 1, 3)
        row += 1

        # ── Fila 5: Aseguradora ────────────────────────────────
        grid.addWidget(self._lbl("Aseguradora:"), row, 0)
        self.input_aseguradora = self._field(placeholder="Nombre de la aseguradora")
        grid.addWidget(self.input_aseguradora, row, 1, 1, 3)
        row += 1

        # ── Fila 6: Email con autocompletado inteligente ───────
        grid.addWidget(self._lbl("Email:"), row, 0)
        email_row = QHBoxLayout()
        email_row.setSpacing(0)
        self.input_email = self._field(placeholder="correo@ejemplo.com (escribe @ para sugerencias)")
        self._email_model = QStringListModel([], self)
        self._email_completer = QCompleter(self._email_model, self)
        self._email_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._email_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.input_email.setCompleter(self._email_completer)
        self.input_email.textEdited.connect(self._actualizar_sugerencias_email)
        email_row.addWidget(self.input_email)
        email_widget = QWidget()
        email_widget.setStyleSheet("background: transparent;")
        email_widget.setLayout(email_row)
        grid.addWidget(email_widget, row, 1, 1, 3)
        row += 1

        # ── Fila 6: Domicilio ──────────────────────────────────
        grid.addWidget(self._lbl("Domicilio:"), row, 0)
        self.input_domicilio = self._field(placeholder="Dirección de habitación")
        grid.addWidget(self.input_domicilio, row, 1, 1, 3)
        row += 1

        # ── Fila 7: Teléfono con prefijo ───────────────────────
        grid.addWidget(self._lbl("Teléfono:"), row, 0)
        tel_row = QHBoxLayout()
        tel_row.setSpacing(6)

        self.combo_prefijo = QComboBox()
        self.combo_prefijo.addItems([
            "0412", "0414", "0416", "0424", "0426", "0422"
        ])
        self.combo_prefijo.setFixedWidth(85)
        self.combo_prefijo.setStyleSheet(self._combo_style() + " padding: 6px 4px;")

        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("Ej. 1234567 (7 dígitos)")
        self.input_telefono.setValidator(QIntValidator(0, 9999999))
        self.input_telefono.setMaxLength(7)
        self.input_telefono.setMinimumWidth(150)
        self.input_telefono.setStyleSheet(self._field_style() + " padding: 6px 10px;")

        tel_row.addWidget(self.combo_prefijo)
        tel_row.addWidget(self.input_telefono, 1)

        tel_widget = QWidget()
        tel_widget.setStyleSheet("background: transparent;")
        tel_widget.setLayout(tel_row)
        grid.addWidget(tel_widget, row, 1, 1, 3)
        row += 1

        # ── Fila 8: Otros datos ────────────────────────────────
        grid.addWidget(self._lbl("Otros datos:"), row, 0, Qt.AlignmentFlag.AlignTop)
        self.input_otros = QTextEdit()
        self.input_otros.setPlaceholderText("Alergias, antecedentes, observaciones...")
        self.input_otros.setMaximumHeight(60)
        grid.addWidget(self.input_otros, row, 1, 1, 3)
        row += 1

        layout.addLayout(grid)

        # ── Botones Guardar / Cancelar ──────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.btn_guardar = QPushButton(" Guardar")
        self.btn_guardar.setObjectName("btnPrimary")
        self.btn_guardar.setIcon(svg_icon("save", color="#ffffff", size=15))
        self.btn_guardar.clicked.connect(self._guardar)

        self.btn_imprimir = QPushButton(" Imprimir Expediente")
        self.btn_imprimir.setObjectName("btnSecondary")
        self.btn_imprimir.setIcon(svg_icon("printer", color="#475569", size=15))
        self.btn_imprimir.clicked.connect(self._imprimir_expediente)

        self.btn_historia = QPushButton(" Historia Clínica")
        self.btn_historia.setObjectName("btnSuccess")
        self.btn_historia.setIcon(svg_icon("file-text", color="#047857", size=15))
        self.btn_historia.setToolTip("Abrir o crear la Historia Clínica del paciente seleccionado")
        self.btn_historia.clicked.connect(self._ir_a_historia)

        self.btn_agendar = QPushButton(" Agendar Cita")
        self.btn_agendar.setObjectName("btnSecondary")
        self.btn_agendar.setIcon(svg_icon("calendar", color="#2a72de", size=15))
        self.btn_agendar.setToolTip("Ir a Agenda para programar una cita con este paciente")
        self.btn_agendar.clicked.connect(self._ir_a_agendar_cita)

        self.btn_farmacos = QPushButton(" Fármacos")
        self.btn_farmacos.setObjectName("btnSecondary")
        self.btn_farmacos.setIcon(svg_icon("pill", color="#7c3aed", size=15))
        self.btn_farmacos.setToolTip("Ir a Fármacos / Recetas con este paciente preseleccionado")
        self.btn_farmacos.clicked.connect(self._ir_a_farmacos)

        self.btn_cancelar = QPushButton(" Cancelar")
        self.btn_cancelar.setObjectName("btnSecondary")
        self.btn_cancelar.setIcon(svg_icon("x", color="#64748b", size=15))
        self.btn_cancelar.clicked.connect(self._cancelar)

        btn_row.addWidget(self.btn_guardar)
        btn_row.addWidget(self.btn_historia)
        btn_row.addWidget(self.btn_agendar)
        btn_row.addWidget(self.btn_farmacos)
        btn_row.addWidget(self.btn_imprimir)
        btn_row.addWidget(self.btn_cancelar)
        layout.addLayout(btn_row)

        # Inicializar estado académico y edad
        self._on_pnf_changed(self.combo_pnf.currentText())
        self._calcular_edad()

        return panel

    # ══════════════════════════════════════════════════════════════
    # Panel de Foto
    # ══════════════════════════════════════════════════════════════

    def _build_photo_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setMinimumWidth(190)
        panel.setMaximumWidth(230)

        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setOffset(0, 3)
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        lbl_title = QLabel("📷  Foto del Paciente")
        lbl_title.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1a2744; "
            "border: none; background: transparent;"
        )
        layout.addWidget(lbl_title)

        # Área de previsualización de foto
        self.foto_display = QLabel()
        self.foto_display.setFixedSize(160, 180)
        self.foto_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.foto_display.setStyleSheet("""
            QLabel {
                background: #f1f5f9;
                border: 2px dashed #cbd5e1;
                border-radius: 8px;
                color: #94a3b8;
                font-size: 12px;
            }
        """)
        self.foto_display.setText("👤\n\nSin foto")
        self.foto_display.setWordWrap(True)
        layout.addWidget(self.foto_display, alignment=Qt.AlignmentFlag.AlignCenter)

        # Botones de inserción
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height:1px; border:none;")
        layout.addWidget(sep)

        lbl_insertar = QLabel("Insertar foto:")
        lbl_insertar.setStyleSheet("font-size: 12px; color: #64748b; border:none; background:transparent;")
        layout.addWidget(lbl_insertar)

        btn_archivo = QPushButton("📁  Archivo")
        btn_archivo.setStyleSheet(self._photo_btn_style("#4d9ef7"))
        btn_archivo.clicked.connect(self._insertar_foto_archivo)
        layout.addWidget(btn_archivo)

        btn_portapapeles = QPushButton("📋  Portapapeles")
        btn_portapapeles.setStyleSheet(self._photo_btn_style("#6f42c1"))
        btn_portapapeles.clicked.connect(self._insertar_foto_portapapeles)
        layout.addWidget(btn_portapapeles)

        btn_quitar = QPushButton("🗑  Quitar foto")
        btn_quitar.setStyleSheet("""
            QPushButton {
                background: transparent; color: #ef4444;
                border: 1px solid #fecaca; border-radius: 6px;
                font-size: 12px; padding: 5px;
            }
            QPushButton:hover { background: #fef2f2; }
        """)
        btn_quitar.clicked.connect(self._quitar_foto)
        layout.addWidget(btn_quitar)

        layout.addStretch()
        return panel

    # ══════════════════════════════════════════════════════════════
    # Panel Listado de Pacientes
    # ══════════════════════════════════════════════════════════════

    def _build_listado_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("rightPanel")

        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setOffset(0, 3)
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Título + toggle formulario
        list_header = QHBoxLayout()
        title = QLabel("👥  Listado de Pacientes")
        title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #1a2744; "
            "border: none; background: transparent;"
        )
        list_header.addWidget(title)
        list_header.addStretch()

        self.btn_imprimir_lista = QPushButton("🖨  Imprimir Lista (PDF)")
        self.btn_imprimir_lista.setStyleSheet(
            "QPushButton { background: #0f766e; color: #ffffff; border: 1px solid #0d9488; "
            "border-radius: 6px; font-size: 12px; font-weight: 600; padding: 5px 12px; }"
            "QPushButton:hover { background: #0d9488; }"
        )
        self.btn_imprimir_lista.setToolTip("Exportar e imprimir en PDF el listado actual según los filtros aplicados")
        self.btn_imprimir_lista.clicked.connect(self._imprimir_lista_filtrada)
        list_header.addWidget(self.btn_imprimir_lista)

        self.btn_toggle_form = QPushButton("🔼  Ocultar formulario")
        self.btn_toggle_form.setStyleSheet(
            "QPushButton { background: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; "
            "border-radius: 6px; font-size: 12px; font-weight: 600; padding: 5px 12px; }"
            "QPushButton:hover { background: #e2e8f0; }"
        )
        self.btn_toggle_form.setToolTip("Ocultar o mostrar el formulario superior para ver la tabla a pantalla completa")
        self.btn_toggle_form.clicked.connect(self._toggle_form_panel)
        list_header.addWidget(self.btn_toggle_form)
        layout.addLayout(list_header)

        # ── Sección Búsqueda y Filtros Avanzados ────────────────
        busqueda_frame = QFrame()
        busqueda_frame.setObjectName("filterBox")
        busqueda_vbox = QVBoxLayout(busqueda_frame)
        busqueda_vbox.setContentsMargins(12, 8, 12, 8)
        busqueda_vbox.setSpacing(8)

        busqueda_layout = QHBoxLayout()
        busqueda_layout.setSpacing(8)

        lbl_busqueda = QLabel("🔍  Buscar:")
        lbl_busqueda.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1a2744; "
            "border: none; background: transparent;"
        )
        busqueda_layout.addWidget(lbl_busqueda)

        self.combo_busq_tipo = QComboBox()
        self.combo_busq_tipo.addItems(["Todos", "V-", "E-", "P-", "J-"])
        self.combo_busq_tipo.setMaximumWidth(75)
        self.combo_busq_tipo.setStyleSheet(self._combo_style())
        self.combo_busq_tipo.currentTextChanged.connect(self._aplicar_filtros)
        busqueda_layout.addWidget(self.combo_busq_tipo)

        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Cédula o nombre del paciente...")
        self.input_busqueda.setStyleSheet(
            "QLineEdit { border: 1.5px solid #e2e8f0; border-radius: 6px; "
            "padding: 6px 12px; font-size: 13px; background: white; min-width: 190px; }"
            "QLineEdit:focus { border-color: #4d9ef7; }"
        )
        self.input_busqueda.textChanged.connect(self._aplicar_filtros)
        self.input_busqueda.returnPressed.connect(self._buscar)
        busqueda_layout.addWidget(self.input_busqueda, 1)

        btn_buscar = QPushButton("🔍  Buscar")
        btn_buscar.setStyleSheet(self._action_btn_style("#2563eb"))
        btn_buscar.clicked.connect(self._buscar)
        busqueda_layout.addWidget(btn_buscar)

        self.btn_toggle_filtros = QPushButton("🎛  Filtros")
        self.btn_toggle_filtros.setCheckable(True)
        self.btn_toggle_filtros.setChecked(True)
        self.btn_toggle_filtros.setStyleSheet(
            "QPushButton { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; "
            "border-radius: 6px; font-size: 12px; font-weight: bold; padding: 6px 12px; }"
            "QPushButton:checked { background: #dbeafe; }"
            "QPushButton:hover { background: #dbeafe; }"
        )
        self.btn_toggle_filtros.toggled.connect(self._toggle_filtros)
        busqueda_layout.addWidget(self.btn_toggle_filtros)

        btn_ver_todo = QPushButton("📋  Ver Todo")
        btn_ver_todo.setStyleSheet(
            "QPushButton { background: #f8fafc; color: #334155; border: 1px solid #cbd5e1; "
            "border-radius: 6px; font-size: 12px; font-weight: 600; padding: 6px 12px; }"
            "QPushButton:hover { background: #e2e8f0; }"
        )
        btn_ver_todo.clicked.connect(self._ver_todo)
        busqueda_layout.addWidget(btn_ver_todo)

        btn_previa = QPushButton("⏮  Previa")
        btn_previa.setStyleSheet(
            "QPushButton { background: #f8fafc; color: #334155; border: 1px solid #cbd5e1; "
            "border-radius: 6px; font-size: 12px; font-weight: 600; padding: 6px 12px; }"
            "QPushButton:hover { background: #e2e8f0; }"
        )
        btn_previa.clicked.connect(self._restaurar_busqueda_previa)
        busqueda_layout.addWidget(btn_previa)

        btn_eliminar = QPushButton("🗑  Eliminar")
        btn_eliminar.setStyleSheet(
            "QPushButton { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; "
            "border-radius: 6px; font-size: 12px; font-weight: bold; padding: 6px 12px; }"
            "QPushButton:hover { background: #fecaca; }"
        )
        btn_eliminar.clicked.connect(self._eliminar_paciente)
        busqueda_layout.addWidget(btn_eliminar)

        self.lbl_resultado_busq = QLabel("")
        self.lbl_resultado_busq.setStyleSheet(
            "font-size: 12px; color: #6c757d; border: none; background: transparent;"
        )
        busqueda_layout.addWidget(self.lbl_resultado_busq)
        busqueda_vbox.addLayout(busqueda_layout)

        # Fila de filtros avanzados (colapsable)
        self.filtros_widget = QWidget()
        self.filtros_widget.setStyleSheet("background: transparent;")
        filtros_layout = QHBoxLayout(self.filtros_widget)
        filtros_layout.setContentsMargins(0, 0, 0, 0)
        filtros_layout.setSpacing(8)

        self.combo_filtro_pnf = QComboBox()
        self.combo_filtro_pnf.addItems(["Todos los PNF", "Sin asignar"] + PNF_OPTIONS)
        self.combo_filtro_pnf.setStyleSheet(self._combo_style())
        self.combo_filtro_pnf.currentTextChanged.connect(self._aplicar_filtros)

        self.combo_filtro_trayecto = QComboBox()
        self.combo_filtro_trayecto.addItems(["Todos los Trayectos", "Sin asignar"] + ALL_TRAYECTOS)
        self.combo_filtro_trayecto.setStyleSheet(self._combo_style())
        self.combo_filtro_trayecto.currentTextChanged.connect(self._aplicar_filtros)

        self.combo_filtro_seccion = QComboBox()
        self.combo_filtro_seccion.addItems(["Todas las Secciones", "Sin asignar"])
        self.combo_filtro_seccion.setStyleSheet(self._combo_style())
        self.combo_filtro_seccion.currentTextChanged.connect(self._aplicar_filtros)

        self.combo_filtro_anio = QComboBox()
        self.combo_filtro_anio.addItems(["Todos los Años", "Sin asignar"])
        self.combo_filtro_anio.setStyleSheet(self._combo_style())
        self.combo_filtro_anio.currentTextChanged.connect(self._aplicar_filtros)

        self.combo_filtro_sexo = QComboBox()
        self.combo_filtro_sexo.addItems(["Sexo: Todos", "Masculino", "Femenino", "Otro"])
        self.combo_filtro_sexo.setStyleSheet(self._combo_style())
        self.combo_filtro_sexo.currentTextChanged.connect(self._aplicar_filtros)

        btn_limpiar_filtros = QPushButton("🧹 Limpiar")
        btn_limpiar_filtros.setStyleSheet(self._action_btn_style("#64748b"))
        btn_limpiar_filtros.clicked.connect(self._limpiar_filtros)

        filtros_layout.addWidget(self.combo_filtro_pnf, 2)
        filtros_layout.addWidget(self.combo_filtro_trayecto, 1)
        filtros_layout.addWidget(self.combo_filtro_seccion, 1)
        filtros_layout.addWidget(self.combo_filtro_anio, 1)
        filtros_layout.addWidget(self.combo_filtro_sexo, 1)
        filtros_layout.addWidget(btn_limpiar_filtros)
        busqueda_vbox.addWidget(self.filtros_widget)

        layout.addWidget(busqueda_frame)

        # ── Tabla de Pacientes ──────────────────────────────────
        self.tabla_pacientes = QTableWidget(0, 8)
        self.tabla_pacientes.setHorizontalHeaderLabels([
            "Cédula", "Nombre Completo", "PNF", "Trayecto", "Sección", "Año", "Teléfono", "Edad"
        ])
        self.tabla_pacientes.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tabla_pacientes.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_pacientes.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.tabla_pacientes.setAlternatingRowColors(True)
        self.tabla_pacientes.verticalHeader().setVisible(False)
        self.tabla_pacientes.setMinimumHeight(160)
        self.tabla_pacientes.itemDoubleClicked.connect(self._cargar_paciente_en_form)
        layout.addWidget(self.tabla_pacientes)

        return panel

    # ══════════════════════════════════════════════════════════════
    # Lógica de negocio
    # ══════════════════════════════════════════════════════════════

    def _calcular_edad(self):
        """Calcula la edad a partir de la fecha de nacimiento."""
        fnac = self.input_fnac.date()
        hoy = QDate.currentDate()
        edad = hoy.year() - fnac.year()
        if (hoy.month(), hoy.day()) < (fnac.month(), fnac.day()):
            edad -= 1
        self.lbl_edad.setText(str(max(0, edad)))

    def _on_pnf_changed(self, pnf: str):
        """Actualiza los trayectos disponibles según el PNF seleccionado."""
        externo = is_external_pnf(pnf)
        self.combo_trayecto.blockSignals(True)
        self.combo_trayecto.clear()
        if externo:
            self.combo_trayecto.addItem("N/A")
            self.combo_trayecto.setEnabled(False)
            self.input_seccion.clear()
            self.input_seccion.setEnabled(False)
            self.spin_anio.setEnabled(False)
        else:
            trayectos = get_trayectos_for_pnf(pnf)
            self.combo_trayecto.addItems(trayectos)
            self.combo_trayecto.setEnabled(True)
            self.input_seccion.setEnabled(True)
            self.spin_anio.setEnabled(True)
        self.combo_trayecto.blockSignals(False)

    def _formatear_seccion(self):
        """Normaliza la sección a 2 dígitos ('1' -> '01') al terminar de editar."""
        txt = self.input_seccion.text().strip()
        if txt:
            self.input_seccion.setText(normalize_seccion(txt))

    def _actualizar_sugerencias_email(self, text: str):
        """Despliega sugerencias de dominio (@gmail.com, @hotmail.com, etc.) al escribir '@'."""
        if "@" not in text:
            self._email_model.setStringList([])
            return
        local, dom_prefix = text.split("@", 1)
        if not local.strip():
            self._email_model.setStringList([])
            return
        sugerencias = [
            f"{local}@{dom}"
            for dom in EMAIL_DOMAINS
            if dom.startswith(dom_prefix.strip().lower())
        ]
        self._email_model.setStringList(sugerencias)
        if sugerencias:
            self._email_completer.complete()

    def _guardar(self):
        """Valida y guarda el paciente en Firebase."""
        nombre = " ".join(self.input_nombre.text().strip().split())
        cedula_num = self.input_cedula.text().strip()
        email = self.input_email.text().strip()

        valido_nom, msg_nom = validate_person_name(nombre)
        if not valido_nom:
            QMessageBox.warning(self, "Nombre inválido", msg_nom)
            self.input_nombre.setFocus()
            return
        ok_ced, msg_ced = validate_cedula_num(cedula_num)
        if not ok_ced:
            QMessageBox.warning(self, "Cédula inválida", msg_ced)
            self.input_cedula.setFocus()
            return
        ok_tel, msg_tel = validate_telefono_num(self.input_telefono.text().strip())
        if not ok_tel:
            QMessageBox.warning(self, "Teléfono inválido", msg_tel)
            self.input_telefono.setFocus()
            return
        if email and "@" not in email:
            QMessageBox.warning(self, "Email inválido", "El email debe contener @.")
            self.input_email.setFocus()
            return

        pnf = self.combo_pnf.currentText()
        if is_external_pnf(pnf):
            trayecto = ""
            seccion = ""
            anio_academico = ""
        else:
            raw_sec = self.input_seccion.text().strip()
            if not is_valid_seccion(raw_sec):
                QMessageBox.warning(
                    self,
                    "Sección inválida",
                    "Ingresa una sección numérica válida de 2 dígitos (ejemplo: 01, 02, 03)."
                )
                self.input_seccion.setFocus()
                return
            seccion = normalize_seccion(raw_sec)
            self.input_seccion.setText(seccion)
            trayecto = self.combo_trayecto.currentText()
            anio_academico = str(self.spin_anio.value())

        telefono_completo = (
            f"{self.combo_prefijo.currentText()}-{self.input_telefono.text()}"
            if self.input_telefono.text() else ""
        )
        cedula_completa = f"{self.combo_tipo_cedula.currentText()}{cedula_num}"

        # Validar cédula duplicada
        duplicado = next(
            (
                p for p in self._pacientes_cache
                if p.get("cedula", "").strip().lower() == cedula_completa.lower()
                and p.get("id") != self._paciente_id_actual
            ),
            None,
        )
        if duplicado:
            QMessageBox.warning(
                self,
                "Cédula duplicada",
                f"Ya existe un paciente registrado con la cédula {cedula_completa}:\n"
                f"• {duplicado.get('nombre', '')}\n\n"
                "Búscalo en la tabla y haz doble clic para editarlo."
            )
            self.input_cedula.setFocus()
            return

        datos = {
            "nombre":       nombre,
            "cedula":       cedula_completa,
            "sexo":         self.combo_sexo.currentText(),
            "fecha_nac":    self.input_fnac.date().toString("dd/MM/yyyy"),
            "edad":         self.lbl_edad.text(),
            "estado_civil": self.combo_civil.currentText(),
            "aseguradora":  self.input_aseguradora.text().strip(),
            "email":        email,
            "domicilio":    self.input_domicilio.text().strip(),
            "telefono":     telefono_completo,
            "otros_datos":  self.input_otros.toPlainText().strip(),
            "pnf":          pnf,
            "trayecto":     trayecto,
            "seccion":      seccion,
            "anio_academico": anio_academico,
            # Mantener retrocompatibilidad con campos anteriores
            "motivo_consulta": self.input_otros.toPlainText().strip(),
        }

        try:
            paciente_id = self._paciente_id_actual
            if paciente_id:
                ok = self.db.actualizar_paciente(paciente_id, datos)
                if not ok:
                    raise RuntimeError("No se pudo actualizar el registro en Firestore.")
                # Sincronizar cambios demográficos/académicos hacia su Historia Clínica (si existe)
                if hasattr(self.db, "obtener_historia_por_paciente") and hasattr(self.db, "actualizar_historia_clinica"):
                    hist = self.db.obtener_historia_por_paciente(paciente_id)
                    if hist and hist.get("id"):
                        self.db.actualizar_historia_clinica(hist["id"], {
                            "paciente_id": paciente_id,
                            "nombre": datos["nombre"],
                            "cedula": datos["cedula"],
                            "sexo": datos["sexo"],
                            "fecha_nacimiento": datos["fecha_nac"],
                            "edad": datos["edad"],
                            "telefono": datos["telefono"],
                            "direccion": datos["domicilio"],
                            "pnf": datos["pnf"],
                            "trayecto": datos["trayecto"],
                            "seccion": datos["seccion"],
                            "anio_academico": datos["anio_academico"],
                        })
                QMessageBox.information(self, "✅ Éxito", "Paciente actualizado correctamente.")
            else:
                uid = self.db.get_current_user_id()
                if not uid:
                    try:
                        from core.auth_manager import AuthManager
                        uid = AuthManager().get_uid()
                    except Exception:
                        pass
                datos["user_id"] = uid or ""
                paciente_id = self.db.crear_paciente(datos)
                if not paciente_id:
                    raise RuntimeError("No se pudo registrar el paciente en Firestore.")
                QMessageBox.information(self, "✅ Éxito", "Paciente registrado correctamente.")

            self._cancelar()
            self._cargar_pacientes()
            self.paciente_guardado.emit(datos | {"id": paciente_id})

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    def _eliminar_paciente(self):
        """Archiva (borrado lógico) el paciente seleccionado en la tabla o formulario."""
        pid = self._paciente_id_actual
        nombre = self.input_nombre.text().strip()
        if not pid:
            rows = self.tabla_pacientes.selectionModel().selectedRows()
            if rows:
                r = rows[0].row()
                pid = self.tabla_pacientes.item(r, 0).data(Qt.ItemDataRole.UserRole)
                nombre = self.tabla_pacientes.item(r, 1).text() if self.tabla_pacientes.item(r, 1) else ""
        if not pid:
            QMessageBox.information(self, "Selección requerida", "Selecciona un paciente de la tabla para eliminar.")
            return

        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Deseas archivar al paciente '{nombre}'?\n"
            "Dejará de aparecer en los listados activos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.eliminar_paciente(pid, borrado_logico=True):
                self._cancelar()
                self._cargar_pacientes()
                self.paciente_eliminado.emit(pid)
                QMessageBox.information(self, "✅", "Paciente archivado correctamente.")
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar el paciente.")

    def _ir_a_historia(self):
        """Abre el módulo de Historia Clínica con el paciente seleccionado."""
        pid = self._paciente_id_actual
        if not pid:
            rows = self.tabla_pacientes.selectionModel().selectedRows()
            if rows:
                pid = self.tabla_pacientes.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        if not pid:
            QMessageBox.information(
                self,
                "Paciente no guardado",
                "Primero guarda el paciente o selecciona uno de la tabla (doble clic) para abrir su Historia Clínica."
            )
            return
        p = next((x for x in self._pacientes_cache if x.get("id") == pid), None)
        if p:
            self.abrir_historia_requested.emit(p)

    def _ir_a_agendar_cita(self):
        """Abre el módulo de Agenda con el paciente seleccionado."""
        pid = self._paciente_id_actual
        if not pid:
            rows = self.tabla_pacientes.selectionModel().selectedRows()
            if rows:
                pid = self.tabla_pacientes.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        if not pid:
            QMessageBox.information(
                self,
                "Paciente no guardado",
                "Primero guarda el paciente o selecciona uno de la tabla para agendarle una cita."
            )
            return
        p = next((x for x in self._pacientes_cache if x.get("id") == pid), None)
        if p:
            self.agendar_cita_requested.emit(p)

    def _ir_a_farmacos(self):
        """Abre el módulo de Fármacos / Recetas con el paciente seleccionado."""
        pid = self._paciente_id_actual
        if not pid:
            rows = self.tabla_pacientes.selectionModel().selectedRows()
            if rows:
                pid = self.tabla_pacientes.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        if not pid:
            QMessageBox.information(
                self,
                "Paciente no guardado",
                "Primero guarda el paciente o selecciona uno de la tabla para recetar fármacos."
            )
            return
        p = next((x for x in self._pacientes_cache if x.get("id") == pid), None)
        if p:
            self.farmacos_requested.emit(p)

    def _imprimir_expediente(self):
        """Exporta el expediente clínico del paciente actual a PDF."""
        nombre = self.input_nombre.text().strip()
        cedula_num = self.input_cedula.text().strip()
        if not nombre and not cedula_num:
            QMessageBox.warning(
                self, "Selección requerida",
                "Selecciona un paciente de la lista o completa sus datos antes de imprimir el expediente."
            )
            return

        try:
            from ui.dialogs.pdf_generator import generar_pdf_expediente
            cedula_completa = f"{self.combo_tipo_cedula.currentText()}{cedula_num}"
            telefono_completo = (
                f"{self.combo_prefijo.currentText()}-{self.input_telefono.text()}"
                if self.input_telefono.text() else ""
            )
            paciente_data = {
                "id": self._paciente_id_actual or "",
                "nombre": nombre,
                "cedula": cedula_completa,
                "sexo": self.combo_sexo.currentText(),
                "fecha_nacimiento": self.input_fnac.date().toString("dd/MM/yyyy"),
                "edad": self.lbl_edad.text(),
                "estado_civil": self.combo_civil.currentText(),
                "aseguradora": self.input_aseguradora.text().strip(),
                "telefono": telefono_completo,
                "email": self.input_email.text().strip(),
                "domicilio": self.input_domicilio.text().strip(),
                "otros_datos": self.input_otros.toPlainText().strip(),
                "pnf": self.combo_pnf.currentText(),
                "trayecto": "" if is_external_pnf(self.combo_pnf.currentText()) else self.combo_trayecto.currentText(),
                "seccion": normalize_seccion(self.input_seccion.text()) if not is_external_pnf(self.combo_pnf.currentText()) else "",
                "anio_academico": str(self.spin_anio.value()) if not is_external_pnf(self.combo_pnf.currentText()) else "",
            }

            # Consultar sesiones y recetas si hay ID o cédula
            sesiones = []
            recetas = []
            if hasattr(self.db, "_db"):
                try:
                    if self._paciente_id_actual:
                        s_docs = self.db._db.collection("sesiones").where("paciente_id", "==", self._paciente_id_actual).stream()
                    else:
                        s_docs = self.db._db.collection("sesiones").where("paciente_nombre", "==", nombre).stream()
                    sesiones = [d.to_dict() for d in s_docs]
                except Exception:
                    pass
                try:
                    if self._paciente_id_actual:
                        r_docs = self.db._db.collection("recetas").where("paciente_id", "==", self._paciente_id_actual).stream()
                    else:
                        r_docs = self.db._db.collection("recetas").where("paciente_nombre", "==", nombre).stream()
                    recetas = [d.to_dict() for d in r_docs]
                except Exception:
                    pass

            slug = nombre.replace(" ", "_") if nombre else "Expediente"
            default_name = f"Expediente_{slug}_{cedula_completa}.pdf"
            path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Expediente PDF", default_name, "PDF (*.pdf)"
            )
            if path:
                generar_pdf_expediente(path, paciente_data, sesiones, recetas)
                QMessageBox.information(self, "✅ PDF generado", f"Expediente guardado en:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", str(e))

    def _cancelar(self):
        """Limpia el formulario."""
        self._paciente_id_actual = None
        self.input_nombre.clear()
        self.combo_sexo.setCurrentIndex(0)
        self.input_fnac.setDate(QDate.currentDate().addYears(-25))
        self.combo_civil.setCurrentIndex(0)
        self.combo_tipo_cedula.setCurrentIndex(0)
        self.input_cedula.clear()
        self.input_aseguradora.clear()
        self.input_email.clear()
        self.input_domicilio.clear()
        self.combo_prefijo.setCurrentIndex(0)
        self.input_telefono.clear()
        self.input_otros.clear()
        self.combo_pnf.setCurrentIndex(0)
        self._on_pnf_changed(self.combo_pnf.currentText())
        self.input_seccion.clear()
        self.spin_anio.setValue(QDate.currentDate().year())
        self._quitar_foto()
        self.btn_guardar.setText("💾  Guardar")
        if hasattr(self, "lbl_modo_form"):
            self.lbl_modo_form.setText("🟢 Registrando nuevo paciente")
            self.lbl_modo_form.setStyleSheet(
                "font-size: 12px; font-weight: 600; color: #047857; "
                "background: #ecfdf5; border: 1px solid #a7f3d0; "
                "border-radius: 12px; padding: 3px 10px;"
            )
        self._calcular_edad()

    def _toggle_form_panel(self):
        """Muestra u oculta el formulario superior para aprovechar el ancho/alto de la tabla."""
        visible = not self.top_container.isVisible()
        self.top_container.setVisible(visible)
        self.btn_toggle_form.setText(
            "🔼  Ocultar formulario" if visible else "➕  Mostrar formulario"
        )

    def _toggle_filtros(self, checked: bool):
        """Muestra u oculta la barra de filtros avanzados."""
        self.filtros_widget.setVisible(checked)

    # ── Foto ─────────────────────────────────────────────────────

    def _insertar_foto_archivo(self):
        """Abre un diálogo para seleccionar imagen desde archivo."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar foto",
            "", "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )
        if path:
            self._mostrar_foto(path)

    def _insertar_foto_portapapeles(self):
        """Intenta obtener imagen del portapapeles."""
        clipboard = QApplication.clipboard()
        image = clipboard.image()
        if not image.isNull():
            pixmap = QPixmap.fromImage(image)
            self._foto_pixmap = pixmap
            self.foto_display.setPixmap(
                pixmap.scaled(160, 180,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation)
            )
            self.foto_display.setText("")
        else:
            QMessageBox.information(self, "Portapapeles",
                "No hay imagen en el portapapeles.\nCopia una imagen primero (Ctrl+C).")

    def _mostrar_foto(self, path: str):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Error", "No se pudo cargar la imagen.")
            return
        self._foto_pixmap = pixmap
        self.foto_display.setPixmap(
            pixmap.scaled(160, 180,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
        )
        self.foto_display.setText("")

    def _quitar_foto(self):
        self._foto_pixmap = None
        self.foto_display.setPixmap(QPixmap())
        self.foto_display.setText("👤\n\nSin foto")

    # ── Búsqueda y tabla ─────────────────────────────────────────

    def _cargar_pacientes(self):
        """Carga todos los pacientes desde Firebase."""
        try:
            self._pacientes_cache = self.db.obtener_pacientes()
        except Exception:
            self._pacientes_cache = []
        self._actualizar_opciones_filtros()
        self._aplicar_filtros()

    def _actualizar_opciones_filtros(self):
        """Actualiza dinámicamente las secciones y años disponibles en los combos de filtro."""
        secciones = sorted({
            normalize_seccion(p.get("seccion", ""))
            for p in self._pacientes_cache
            if p.get("seccion")
        })
        anios = sorted({
            str(p.get("anio_academico", "")).strip()
            for p in self._pacientes_cache
            if p.get("anio_academico")
        }, reverse=True)

        prev_sec = self.combo_filtro_seccion.currentText()
        self.combo_filtro_seccion.blockSignals(True)
        self.combo_filtro_seccion.clear()
        self.combo_filtro_seccion.addItems(["Todas las Secciones", "Sin asignar"] + secciones)
        idx_s = self.combo_filtro_seccion.findText(prev_sec)
        self.combo_filtro_seccion.setCurrentIndex(max(0, idx_s))
        self.combo_filtro_seccion.blockSignals(False)

        prev_anio = self.combo_filtro_anio.currentText()
        self.combo_filtro_anio.blockSignals(True)
        self.combo_filtro_anio.clear()
        self.combo_filtro_anio.addItems(["Todos los Años", "Sin asignar"] + anios)
        idx_a = self.combo_filtro_anio.findText(prev_anio)
        self.combo_filtro_anio.setCurrentIndex(max(0, idx_a))
        self.combo_filtro_anio.blockSignals(False)

    def _poblar_tabla(self, pacientes: list):
        """Rellena la tabla con la lista de pacientes."""
        self._pacientes_filtrados = list(pacientes)
        self.tabla_pacientes.setRowCount(0)
        for i, p in enumerate(pacientes):
            self.tabla_pacientes.insertRow(i)
            cedula   = p.get("cedula", p.get("id", ""))
            nombre   = p.get("nombre", "")
            pnf      = p.get("pnf", "") or "Sin asignar"
            trayecto = p.get("trayecto", "") or ("N/A" if is_external_pnf(p.get("pnf", "")) and p.get("pnf") else "—")
            seccion  = p.get("seccion", "") or "—"
            anio     = str(p.get("anio_academico", "") or "—")
            telefono = p.get("telefono", "")
            edad     = str(p.get("edad", ""))

            items = [cedula, nombre, pnf, trayecto, seccion, anio, telefono, edad]
            for j, val in enumerate(items):
                item = QTableWidgetItem(val)
                self.tabla_pacientes.setItem(i, j, item)

            # Guardar ID oculto
            self.tabla_pacientes.item(i, 0).setData(
                Qt.ItemDataRole.UserRole, p.get("id")
            )

        n = len(pacientes)
        total = len(self._pacientes_cache)
        if n == total:
            self.lbl_resultado_busq.setText(
                f"{n} paciente(s) registrado(s)" if n else "Sin resultados"
            )
        else:
            self.lbl_resultado_busq.setText(f"Mostrando {n} de {total} paciente(s)")

    def _aplicar_filtros(self):
        """Aplica búsqueda por texto + filtros avanzados (PNF, Trayecto, Sección, Año, Sexo)."""
        tipo = self.combo_busq_tipo.currentText()
        q = self.input_busqueda.text().strip().lower()
        f_pnf = self.combo_filtro_pnf.currentText()
        f_tray = self.combo_filtro_trayecto.currentText()
        f_sec = self.combo_filtro_seccion.currentText()
        f_anio = self.combo_filtro_anio.currentText()
        f_sexo = self.combo_filtro_sexo.currentText()

        filtrados = []
        for p in self._pacientes_cache:
            ced = p.get("cedula", "").lower()
            nom = p.get("nombre", "").lower()

            if tipo != "Todos" and not ced.startswith(tipo.lower()):
                continue
            if q and (q not in ced and q not in nom):
                continue

            pnf = p.get("pnf", "")
            if f_pnf == "Sin asignar":
                if pnf:
                    continue
            elif f_pnf != "Todos los PNF" and pnf != f_pnf:
                continue

            tray = p.get("trayecto", "")
            if f_tray == "Sin asignar":
                if tray:
                    continue
            elif f_tray != "Todos los Trayectos" and tray != f_tray:
                continue

            sec = normalize_seccion(p.get("seccion", ""))
            if f_sec == "Sin asignar":
                if sec:
                    continue
            elif f_sec != "Todas las Secciones" and sec != f_sec:
                continue

            anio = str(p.get("anio_academico", "")).strip()
            if f_anio == "Sin asignar":
                if anio:
                    continue
            elif f_anio != "Todos los Años" and anio != f_anio:
                continue

            if f_sexo != "Sexo: Todos" and p.get("sexo", "") != f_sexo:
                continue

            filtrados.append(p)

        self._poblar_tabla(filtrados)

    def _imprimir_lista_filtrada(self):
        """Exporta a PDF el listado actual de pacientes respetando los filtros activos."""
        pacientes = getattr(self, "_pacientes_filtrados", None)
        if pacientes is None:
            pacientes = list(getattr(self, "_pacientes_cache", []))
        if not pacientes:
            QMessageBox.warning(
                self, "Sin pacientes",
                "No hay pacientes en la lista actual para imprimir."
            )
            return

        filtros = {}
        q = self.input_busqueda.text().strip()
        if q:
            filtros["busqueda"] = q
        tipo = self.combo_busq_tipo.currentText()
        if tipo and tipo != "Todos":
            filtros["tipo_cedula"] = tipo
        pnf = self.combo_filtro_pnf.currentText()
        if pnf and pnf != "Todos los PNF":
            filtros["pnf"] = pnf
        tray = self.combo_filtro_trayecto.currentText()
        if tray and tray != "Todos los Trayectos":
            filtros["trayecto"] = tray
        sec = self.combo_filtro_seccion.currentText()
        if sec and sec != "Todas las Secciones":
            filtros["seccion"] = sec
        anio = self.combo_filtro_anio.currentText()
        if anio and anio != "Todos los Años":
            filtros["anio"] = anio
        sexo = self.combo_filtro_sexo.currentText()
        if sexo and sexo != "Sexo: Todos":
            filtros["sexo"] = sexo

        fecha_hoy = QDate.currentDate().toString("yyyyMMdd")
        default_name = f"Listado_Pacientes_PSIQUE_{fecha_hoy}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Listado de Pacientes en PDF", default_name, "Documento PDF (*.pdf)"
        )
        if not path:
            return
        try:
            from ui.dialogs.pdf_generator import generar_pdf_listado_pacientes
            generar_pdf_listado_pacientes(path, pacientes, filtros)
            QMessageBox.information(
                self, "✅ PDF Generado",
                f"Se exportaron {len(pacientes)} paciente(s) al PDF:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", f"No se pudo crear el PDF:\n{e}")

    def _buscar(self):
        """Guarda la búsqueda previa y aplica los filtros actuales."""
        self._cache_busqueda_previa = self._pacientes_cache.copy()
        self._aplicar_filtros()

    def _limpiar_filtros(self):
        """Restablece todos los filtros avanzados."""
        for w in (
            self.combo_busq_tipo, self.combo_filtro_pnf, self.combo_filtro_trayecto,
            self.combo_filtro_seccion, self.combo_filtro_anio, self.combo_filtro_sexo
        ):
            w.blockSignals(True)
            w.setCurrentIndex(0)
            w.blockSignals(False)
        self.input_busqueda.blockSignals(True)
        self.input_busqueda.clear()
        self.input_busqueda.blockSignals(False)
        self._aplicar_filtros()

    def _ver_todo(self):
        """Muestra todos los pacientes limpiando filtros."""
        self._limpiar_filtros()

    def _restaurar_busqueda_previa(self):
        """Restaura la última búsqueda realizada."""
        if self._cache_busqueda_previa:
            self._poblar_tabla(self._cache_busqueda_previa)
            self.lbl_resultado_busq.setText(
                f"⏮ Búsqueda previa: {len(self._cache_busqueda_previa)} resultado(s)"
            )
        else:
            self._ver_todo()

    def _cargar_paciente_en_form(self, item):
        """Doble-clic en fila: carga el paciente en el formulario."""
        row = item.row()
        paciente_id = self.tabla_pacientes.item(row, 0).data(
            Qt.ItemDataRole.UserRole
        )
        # Buscar datos completos en caché
        p = next(
            (x for x in self._pacientes_cache if x.get("id") == paciente_id),
            None
        )
        if not p:
            return

        self._paciente_id_actual = paciente_id

        # Rellenar formulario
        self.input_nombre.setText(p.get("nombre", ""))

        sexo = p.get("sexo", "Masculino")
        idx_sexo = self.combo_sexo.findText(sexo)
        self.combo_sexo.setCurrentIndex(max(0, idx_sexo))

        # Fecha nacimiento
        fnac_str = p.get("fecha_nac", "")
        if fnac_str:
            try:
                d = QDate.fromString(fnac_str, "dd/MM/yyyy")
                if d.isValid():
                    self.input_fnac.setDate(d)
            except Exception:
                pass

        civil = p.get("estado_civil", "")
        idx_civil = self.combo_civil.findText(civil)
        self.combo_civil.setCurrentIndex(max(0, idx_civil))

        # Cédula
        cedula = p.get("cedula", "")
        if len(cedula) >= 2 and cedula[0] in "VEJP" and cedula[1] == "-":
            tipo = cedula[:2]
            num  = cedula[2:]
            idx_t = self.combo_tipo_cedula.findText(tipo)
            self.combo_tipo_cedula.setCurrentIndex(max(0, idx_t))
            self.input_cedula.setText(num)
        else:
            self.input_cedula.setText(cedula)

        self.input_aseguradora.setText(p.get("aseguradora", ""))
        self.input_email.setText(p.get("email", ""))
        self.input_domicilio.setText(p.get("domicilio", ""))

        # Teléfono
        tel = p.get("telefono", "")
        if "-" in tel:
            partes = tel.split("-", 1)
            idx_pref = self.combo_prefijo.findText(partes[0])
            self.combo_prefijo.setCurrentIndex(max(0, idx_pref))
            self.input_telefono.setText(partes[1])
        else:
            self.input_telefono.setText(tel)

        self.input_otros.setPlainText(
            p.get("otros_datos", p.get("motivo_consulta", ""))
        )

        # Datos académicos (PNF, Trayecto, Sección, Año)
        pnf = p.get("pnf", "No aplica / Externo") or "No aplica / Externo"
        idx_pnf = self.combo_pnf.findText(pnf)
        self.combo_pnf.setCurrentIndex(max(0, idx_pnf))
        self._on_pnf_changed(self.combo_pnf.currentText())

        if not is_external_pnf(self.combo_pnf.currentText()):
            tray = p.get("trayecto", "")
            idx_tray = self.combo_trayecto.findText(tray)
            if idx_tray >= 0:
                self.combo_trayecto.setCurrentIndex(idx_tray)
            self.input_seccion.setText(normalize_seccion(p.get("seccion", "")))
            try:
                anio_val = int(p.get("anio_academico") or QDate.currentDate().year())
                self.spin_anio.setValue(anio_val)
            except (ValueError, TypeError):
                self.spin_anio.setValue(QDate.currentDate().year())

        self.btn_guardar.setText("✏️  Actualizar")
        if not self.top_container.isVisible():
            self._toggle_form_panel()
        if hasattr(self, "lbl_modo_form"):
            self.lbl_modo_form.setText(f"✏️ Editando: {p.get('nombre', '')} ({p.get('cedula', '')})")
            self.lbl_modo_form.setStyleSheet(
                "font-size: 12px; font-weight: 600; color: #1d4ed8; "
                "background: #eff6ff; border: 1px solid #bfdbfe; "
                "border-radius: 12px; padding: 3px 10px;"
            )
        self._calcular_edad()

    # ── Método público para resetear desde el menú ─────────────
    def focus_new_form(self):
        self._cancelar()
        self.input_nombre.setFocus()

    # ══════════════════════════════════════════════════════════════
    # Helpers de estilo
    # ══════════════════════════════════════════════════════════════

    def _lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("font-size: 13px; font-weight: 600;")
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return l

    def _field(self, placeholder: str = "") -> QLineEdit:
        f = QLineEdit()
        f.setPlaceholderText(placeholder)
        f.setStyleSheet(self._field_style())
        return f

    @staticmethod
    def _field_style() -> str:
        return ""

    @staticmethod
    def _combo_style() -> str:
        return ""

    @staticmethod
    def _photo_btn_style(color: str) -> str:
        return f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 6px;
                font-size: 12px; padding: 6px;
            }}
            QPushButton:hover {{ opacity: 0.85; }}
        """

    @staticmethod
    def _action_btn_style(color: str) -> str:
        return f"""
            QPushButton {{
                background: {color}; color: white;
                border: none; border-radius: 6px;
                font-size: 12px; font-weight: bold;
                padding: 6px 14px;
            }}
            QPushButton:hover {{ opacity: 0.9; }}
        """
