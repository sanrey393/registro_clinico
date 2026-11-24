# ui/views/historia_clinica_view.py
# Módulo completo y profesional de Historia Clínica (Psicología y Neurodesarrollo)

import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QTextEdit, QComboBox, QDateEdit, QTimeEdit,
    QGridLayout, QTabWidget, QSizePolicy, QCheckBox,
    QGraphicsDropShadowEffect, QScrollArea, QAbstractItemView,
    QFileDialog, QListView, QCompleter, QSplitter, QInputDialog
)
from PyQt6.QtCore import Qt, QDate, QTime, QRegularExpression, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QIntValidator, QRegularExpressionValidator
from ui.widgets.smart_date_edit import SmartDateEdit
from ui.widgets.app_icons import svg_icon
from core.academic_catalog import (
    PNF_OPTIONS, ALL_TRAYECTOS, DEFAULT_CONDICIONES_CLINICAS, normalize_seccion, validate_person_name,
    generar_codigo_historia, validate_num_historia, validate_cedula_num, validate_telefono_num
)

STYLE = """
QWidget {
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 13.5px;
}
QLabel {
    background: transparent;
    border: none;
    color: #334155;
}
QLineEdit, QComboBox, QDateEdit, QTimeEdit {
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    padding: 7px 12px;
    background: #ffffff;
    color: #0f172a;
    font-size: 13.5px;
    min-height: 24px;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
    border-color: #2563eb;
    background: #ffffff;
}
QTextEdit {
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    padding: 9px 12px;
    background: #ffffff;
    color: #0f172a;
    font-size: 13.5px;
    line-height: 1.45;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView,
QComboBox QListView {
    border: 1px solid #cbd5e1;
    background-color: #ffffff;
    background: #ffffff;
    color: #0f172a;
    selection-background-color: #e0f2fe;
    selection-color: #0369a1;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}
QComboBox QAbstractItemView::item,
QComboBox QListView::item {
    color: #0f172a;
    background-color: #ffffff;
    min-height: 24px;
    padding: 3px 6px;
}
QComboBox QAbstractItemView::item:hover,
QComboBox QAbstractItemView::item:selected,
QComboBox QListView::item:hover,
QComboBox QListView::item:selected {
    background-color: #e0f2fe;
    color: #0369a1;
}
QTableWidget {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    gridline-color: transparent;
    alternate-background-color: #f8fafc;
}
QHeaderView::section {
    background: #f1f5f9;
    color: #475569;
    font-weight: bold;
    border: none;
    padding: 9px 10px;
    border-bottom: 2px solid #cbd5e1;
}
QTableWidget::item {
    padding: 7px;
}
QTableWidget::item:selected {
    background: #dbeafe;
    color: #1e40af;
}
QFrame#card {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}
QFrame#subCard {
    background: #f8fafc;
    border-radius: 10px;
    border: 1.5px solid #e2e8f0;
    padding: 12px;
}
QPushButton#btnPrimary {
    background: #2563eb;
    color: white; border: none; border-radius: 8px;
    font-weight: bold; padding: 10px 22px; font-size: 13.5px;
}
QPushButton#btnPrimary:hover { background: #1d4ed8; }
QPushButton#btnPdf {
    background: #f8fafc;
    color: #334155; border: 1px solid #cbd5e1; border-radius: 8px;
    font-weight: 600; padding: 10px 20px; font-size: 13.5px;
}
QPushButton#btnPdf:hover { background: #e2e8f0; }
QPushButton#btnSuccess {
    background: #ecfdf5;
    color: #047857; border: 1px solid #a7f3d0; border-radius: 8px;
    font-weight: bold; padding: 8px 14px; font-size: 13px;
}
QPushButton#btnSuccess:hover { background: #d1fae5; }
QPushButton#btnDanger {
    background: #fee2e2; color: #dc2626;
    border: 1px solid #fecaca; border-radius: 8px;
    font-weight: bold; padding: 9px 18px; font-size: 13.5px;
}
QPushButton#btnDanger:hover { background: #fecaca; }
QPushButton#btnSecondary {
    background: #f1f5f9; color: #475569;
    border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 9px 18px; font-size: 13.5px;
}
QPushButton#btnSecondary:hover { background: #e2e8f0; color: #0f172a; }
QTabWidget::pane {
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    background: #ffffff;
    top: -1px;
}
QTabBar::tab {
    background: #f1f5f9;
    color: #64748b;
    padding: 10px 20px;
    margin-right: 3px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-weight: 600;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: #ffffff;
    color: #2563eb;
    border: 1.5px solid #e2e8f0;
    border-bottom: 2px solid #ffffff;
}
QTabBar::tab:hover:!selected {
    background: #e2e8f0;
    color: #0f172a;
}
QCheckBox {
    font-size: 13.5px;
    color: #0f172a;
    font-weight: 600;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 20px;
    height: 20px;
    border-radius: 5px;
    border: 1.5px solid #cbd5e1;
    background: #ffffff;
}
QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}
"""


class HistoriaClinicaView(QWidget):
    """
    Módulo completo de Historia Clínica Psicológica y Neurodesarrollo.
    Contiene:
      - Búsqueda y gestión de expedientes
      - Formulario exhaustivo en 5 pestañas temáticas
      - Campos independientes de edad y teléfono
      - Niveles de instrucción académica detallados
      - Áreas de texto amplias y cómodas
      - Exportación oficial en PDF con membrete clínico
    """

    historia_guardada = pyqtSignal(str)
    paciente_sincronizado = pyqtSignal(str)
    agendar_cita_requested = pyqtSignal(str)
    visita_actualizada = pyqtSignal()
    farmacos_requested = pyqtSignal(str)

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._historia_id = None
        self._paciente_id = None
        self._visita_id = None
        self._historias_cache = []
        self._pacientes_cache = []
        self._sesiones_cache = []
        self._citas_cache = []
        self._recetas_cache = []
        self._syncing_combo = False
        self.setup_ui()
        if hasattr(self.db, "get_current_user_id") and self.db.get_current_user_id():
            self.load_data()

    def focus_new_form(self):
        """Limpia el formulario, abre la pestaña de Expediente y enfoca el nombre."""
        self.clear_form()
        if hasattr(self, "main_tabs"):
            self.main_tabs.setCurrentIndex(1)
        self.input_nombre.setFocus()

    def focus_search(self):
        """Abre la pestaña de Listado y pone el foco en el buscador."""
        if hasattr(self, "main_tabs"):
            self.main_tabs.setCurrentIndex(0)
        self.search_input.setFocus()

    def _toggle_lista_panel(self):
        """Alterna entre la pestaña de Listado y la pestaña de Expediente."""
        if hasattr(self, "main_tabs"):
            idx = 0 if self.main_tabs.currentIndex() == 1 else 1
            self.main_tabs.setCurrentIndex(idx)

    # ══════════════════════════════════════════════════════════
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ══════════════════════════════════════════════════════════

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(0)

        self.left_panel = QWidget()
        self.left_panel.setLayout(self._build_left_panel())

        self.right_panel = self._build_right_panel()

        self.main_tabs = QTabWidget()
        self.main_tabs.addTab(self.left_panel, "📋 Historial Clínico (Listado)")
        self.main_tabs.addTab(self.right_panel, "📝 Expediente Clínico")
        root.addWidget(self.main_tabs, 1)

    # ── Panel Izquierdo (Búsqueda y Tabla) ─────────────────────
    def _build_left_panel(self) -> QVBoxLayout:
        lay = QVBoxLayout()
        lay.setSpacing(10)

        # Título
        header = QHBoxLayout()
        t = QLabel("📋 Historias Clínicas")
        t.setStyleSheet("font-size: 19px; font-weight: bold;")
        header.addWidget(t)
        header.addStretch()

        btn_nueva = QPushButton("➕ Nueva Historia")
        btn_nueva.setObjectName("btnSuccess")
        btn_nueva.clicked.connect(self.focus_new_form)
        header.addWidget(btn_nueva)
        lay.addLayout(header)

        # Buscador por cédula o nombre
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por N° Historia, Cédula o Nombre...")
        self.search_input.textChanged.connect(self._filtrar_tabla)
        search_row.addWidget(self.search_input)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setObjectName("btnSecondary")
        btn_refresh.setFixedWidth(38)
        btn_refresh.setToolTip("Recargar lista de historias y pacientes")
        btn_refresh.clicked.connect(self.load_data)
        search_row.addWidget(btn_refresh)

        self.btn_toggle_filtros = QPushButton("🎛")
        self.btn_toggle_filtros.setCheckable(True)
        self.btn_toggle_filtros.setChecked(True)
        self.btn_toggle_filtros.setObjectName("btnSecondary")
        self.btn_toggle_filtros.setFixedWidth(38)
        self.btn_toggle_filtros.setToolTip("Mostrar u ocultar filtros avanzados")
        self.btn_toggle_filtros.toggled.connect(lambda checked: self.filt_box.setVisible(checked))
        search_row.addWidget(self.btn_toggle_filtros)
        lay.addLayout(search_row)

        # Filtros avanzados en cuadrícula 2x2 (legible en cualquier ancho)
        self.filt_box = QFrame()
        self.filt_box.setObjectName("filterBox")
        filt_v = QVBoxLayout(self.filt_box)
        filt_v.setContentsMargins(8, 6, 8, 6)
        filt_v.setSpacing(6)

        f_grid = QGridLayout()
        f_grid.setSpacing(6)
        self.combo_filtro_pnf = QComboBox()
        self.combo_filtro_pnf.addItems(["Todos PNF", "Sin asignar"] + PNF_OPTIONS)
        self.combo_filtro_pnf.currentTextChanged.connect(self._filtrar_tabla)

        self.combo_filtro_tray = QComboBox()
        self.combo_filtro_tray.addItems(["Todos Tray.", "Sin asignar"] + ALL_TRAYECTOS)
        self.combo_filtro_tray.currentTextChanged.connect(self._filtrar_tabla)

        self.combo_filtro_sec = QComboBox()
        self.combo_filtro_sec.addItems(["Todas Secc.", "Sin asignar"])
        self.combo_filtro_sec.currentTextChanged.connect(self._filtrar_tabla)

        self.combo_filtro_anio = QComboBox()
        self.combo_filtro_anio.addItems(["Todos Años", "Sin asignar"])
        self.combo_filtro_anio.currentTextChanged.connect(self._filtrar_tabla)

        self.combo_filtro_patologia = QComboBox()
        self.combo_filtro_patologia.addItems(["Condición / IPX: Todas"] + DEFAULT_CONDICIONES_CLINICAS)
        self.combo_filtro_patologia.currentTextChanged.connect(self._filtrar_tabla)

        f_grid.addWidget(self.combo_filtro_pnf, 0, 0)
        f_grid.addWidget(self.combo_filtro_tray, 0, 1)
        f_grid.addWidget(self.combo_filtro_sec, 0, 2)
        f_grid.addWidget(self.combo_filtro_anio, 1, 0)
        f_grid.addWidget(self.combo_filtro_patologia, 1, 1, 1, 2)
        filt_v.addLayout(f_grid)

        f_row2 = QHBoxLayout()
        f_row2.setSpacing(6)
        self.combo_filtro_tipo = QComboBox()
        self.combo_filtro_tipo.addItems(["Consulta: Todas", "Primera vez", "Sucesiva"])
        self.combo_filtro_tipo.currentTextChanged.connect(self._filtrar_tabla)

        self.chk_filtro_fecha = QCheckBox("Fecha:")
        self.chk_filtro_fecha.toggled.connect(self._filtrar_tabla)

        self.date_filtro_desde = SmartDateEdit(QDate.currentDate().addMonths(-1))
        self.date_filtro_desde.dateChanged.connect(self._filtrar_tabla)

        self.date_filtro_hasta = SmartDateEdit(QDate.currentDate())
        self.date_filtro_hasta.dateChanged.connect(self._filtrar_tabla)

        btn_limpiar_filt = QPushButton("🧹")
        btn_limpiar_filt.setObjectName("btnSecondary")
        btn_limpiar_filt.setFixedWidth(36)
        btn_limpiar_filt.setToolTip("Limpiar todos los filtros")
        btn_limpiar_filt.clicked.connect(self._limpiar_filtros)

        f_row2.addWidget(self.combo_filtro_tipo, 2)
        f_row2.addWidget(self.chk_filtro_fecha)
        f_row2.addWidget(self.date_filtro_desde, 1)
        f_row2.addWidget(self.date_filtro_hasta, 1)
        f_row2.addWidget(btn_limpiar_filt)
        filt_v.addLayout(f_row2)

        lay.addWidget(self.filt_box)

        # Tabla de historias (ancho completo con datos académicos + condición IPX + seguimiento)
        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels([
            "N° Historia", "Cédula", "Paciente", "PNF", "Trayecto",
            "Sección", "Año", "Condición / IPX", "Visitas", "Última Visita", "Fecha", "ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(11, True)  # ID oculto
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(self._cargar_historia_click)
        lay.addWidget(self.table)

        # Contador y botones inferiores
        bottom_row = QHBoxLayout()
        self.lbl_count = QLabel("0 historia(s) registrada(s)")
        self.lbl_count.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        bottom_row.addWidget(self.lbl_count)
        bottom_row.addStretch()

        btn_abrir = QPushButton("✏️ Abrir / Editar")
        btn_abrir.setObjectName("btnPrimary")
        btn_abrir.clicked.connect(self._abrir_historia_seleccionada)
        bottom_row.addWidget(btn_abrir)

        btn_del = QPushButton("🗑 Eliminar")
        btn_del.setObjectName("btnDanger")
        btn_del.clicked.connect(self._eliminar_historia)
        bottom_row.addWidget(btn_del)
        lay.addLayout(bottom_row)

        return lay

    # ── Panel Derecho (Formulario con Tabs) ────────────────────
    def _build_right_panel(self) -> QWidget:
        card = QFrame()
        card.setObjectName("card")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(12)

        # ── Encabezado Principal de la Ficha ──
        title_bar = QHBoxLayout()
        title_bar.setSpacing(8)
        self.btn_toggle_lista = QPushButton("⬅ Volver al Listado")
        self.btn_toggle_lista.setObjectName("btnSecondary")
        self.btn_toggle_lista.setToolTip("Regresar a la pestaña de listado y filtros de historias")
        self.btn_toggle_lista.clicked.connect(lambda: self.main_tabs.setCurrentIndex(0))
        title_bar.addWidget(self.btn_toggle_lista)

        self.form_title = QLabel("Expediente de Historia Clínica")
        self.form_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_bar.addWidget(self.form_title, 1)
        lay.addLayout(title_bar)

        # ── Selector de Paciente Registrado (Sincronizado con Identificación) ──
        sel_frame = QFrame()
        sel_frame.setObjectName("infoBanner")
        sel_row = QHBoxLayout(sel_frame)
        sel_row.setContentsMargins(10, 6, 10, 6)
        sel_row.setSpacing(8)

        lbl_sel = QLabel("🔗 Paciente:")
        lbl_sel.setStyleSheet("font-weight: bold; color: #1e40af; font-size: 13px;")
        sel_row.addWidget(lbl_sel)

        self.input_buscar_pac_combo = QLineEdit()
        self.input_buscar_pac_combo.setPlaceholderText("🔍 Filtrar por cédula o nombre...")
        self.input_buscar_pac_combo.setMaximumWidth(210)
        self.input_buscar_pac_combo.textChanged.connect(self._filtrar_combo_pacientes)
        sel_row.addWidget(self.input_buscar_pac_combo)

        self.combo_paciente = QComboBox()
        self.combo_paciente.setView(QListView())
        self.combo_paciente.setEditable(False)
        self.combo_paciente.setToolTip("Haz clic para desplegar todos los pacientes registrados en Identificación")
        self.combo_paciente.currentIndexChanged.connect(self._on_paciente_seleccionado)
        sel_row.addWidget(self.combo_paciente, 2)

        self.lbl_paciente_acad = QLabel("Sin paciente vinculado")
        self.lbl_paciente_acad.setStyleSheet("color: #475569; font-size: 12px; font-weight: 500;")
        sel_row.addWidget(self.lbl_paciente_acad, 1)

        lay.addWidget(sel_frame)

        # Cabecera en filas flexibles (evita solapes del grid de 7 columnas)
        header = QVBoxLayout()
        header.setSpacing(10)

        # Fila 0: N° Historia (compacto + auto) | Fecha | Hora
        row0 = QHBoxLayout()
        row0.setSpacing(10)

        self.input_num_historia = QLineEdit()
        self.input_num_historia.setPlaceholderText("Ej: HC-INF-2026-12345678")
        self.input_num_historia.setMaxLength(28)
        self.input_num_historia.setMinimumWidth(185)
        self.input_num_historia.setMaximumWidth(235)
        self.input_num_historia.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^[A-Za-z0-9\-]{0,28}$"))
        )
        self.input_num_historia.setToolTip("Código único de historia clínica (letras, números y guiones).")

        btn_gen_codigo = QPushButton("✨")
        btn_gen_codigo.setObjectName("btnSecondary")
        btn_gen_codigo.setFixedSize(36, 36)
        btn_gen_codigo.setToolTip("Generar código único automático según PNF, año y cédula")
        btn_gen_codigo.clicked.connect(lambda: self._generar_codigo_historia_actual())

        num_wrap = QWidget()
        num_wrap.setStyleSheet("background: transparent;")
        num_inner = QHBoxLayout(num_wrap)
        num_inner.setContentsMargins(0, 0, 0, 0)
        num_inner.setSpacing(4)
        num_inner.addWidget(self.input_num_historia)
        num_inner.addWidget(btn_gen_codigo)
        row0.addWidget(self._labeled_field("N° Historia:", num_wrap), 0)

        self.input_fecha_elab = SmartDateEdit(QDate.currentDate())
        self.input_fecha_elab.setMinimumWidth(165)
        row0.addWidget(self._labeled_field("Fecha Elab.:", self.input_fecha_elab), 0)

        self.input_hora_elab = QTimeEdit(QTime.currentTime())
        self.input_hora_elab.setDisplayFormat("HH:mm")
        self.input_hora_elab.setMinimumWidth(105)
        row0.addWidget(self._labeled_field("Hora:", self.input_hora_elab), 0)
        row0.addStretch(1)
        header.addLayout(row0)

        # Fila 1: Nombre | Sexo
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombres y Apellidos completos del paciente")
        self.input_nombre.setMaxLength(80)
        self.input_nombre.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü'\-\s]{0,80}$"))
        )
        self.input_nombre.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        row1.addWidget(self._labeled_field("Nombre y Apellidos:", self.input_nombre), 1)

        self.combo_sexo = QComboBox()
        self.combo_sexo.setView(QListView())
        self.combo_sexo.addItems(["Masculino", "Femenino", "Otro"])
        self.combo_sexo.setMinimumContentsLength(10)
        self.combo_sexo.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.combo_sexo.setMaximumWidth(140)
        row1.addWidget(self._labeled_field("Sexo:", self.combo_sexo), 0)
        header.addLayout(row1)

        # Fila 2: Cédula | Checkbox primera vez
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.combo_tipo_cedula = QComboBox()
        self.combo_tipo_cedula.setView(QListView())
        self.combo_tipo_cedula.addItems(["V-", "E-", "J-", "P-"])
        self.combo_tipo_cedula.setFixedWidth(68)
        self.combo_tipo_cedula.setStyleSheet("padding: 5px 6px;")
        self.input_cedula = QLineEdit()
        self.input_cedula.setPlaceholderText("Número de cédula")
        self.input_cedula.setValidator(QIntValidator(0, 999999999))
        self.input_cedula.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        ced_wrap = QWidget()
        ced_wrap.setStyleSheet("background: transparent;")
        ced_inner = QHBoxLayout(ced_wrap)
        ced_inner.setContentsMargins(0, 0, 0, 0)
        ced_inner.setSpacing(4)
        ced_inner.addWidget(self.combo_tipo_cedula)
        ced_inner.addWidget(self.input_cedula, 1)
        row2.addWidget(self._labeled_field("Cédula / ID:", ced_wrap), 1)

        self.chk_primera_vez = QCheckBox("Consulta por primera vez")
        self.chk_primera_vez.setChecked(True)
        self.chk_primera_vez.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )
        row2.addWidget(self.chk_primera_vez, 0, Qt.AlignmentFlag.AlignVCenter)

        self.lbl_estado_visita = QLabel("🆕 Primera consulta")
        self.lbl_estado_visita.setStyleSheet(
            "font-size: 12px; font-weight: bold; color: #047857; "
            "background: #ecfdf5; border: 1px solid #a7f3d0; "
            "border-radius: 10px; padding: 3px 10px;"
        )
        row2.addWidget(self.lbl_estado_visita, 0, Qt.AlignmentFlag.AlignVCenter)
        header.addLayout(row2)

        lay.addLayout(header)
        lay.addWidget(self._sep())

        # ── Pestañas de la Historia Clínica ──
        self.tabs = QTabWidget()

        self.tab_filiacion = self._build_tab_filiacion()
        self.tab_antecedentes = self._build_tab_antecedentes()
        self.tab_representante = self._build_tab_representante()
        self.tab_emocional = self._build_tab_emocional()
        self.tab_neuro = self._build_tab_neuro()
        self.tab_evolucion = self._build_tab_evolucion()

        self.tabs.addTab(self.tab_filiacion, "1. 👤 Filiación / Ingreso")
        self.tabs.addTab(self.tab_antecedentes, "2. 🩺 Antecedentes")
        self.tabs.addTab(self.tab_representante, "3. 👨‍👩‍👧 Representante")
        self.tabs.addTab(self.tab_emocional, "4. 💭 Autoexploración")
        self.tabs.addTab(self.tab_neuro, "5. 🧠 Neurodesarrollo / IPX")
        self.tabs.addTab(self.tab_evolucion, "6. 📅 Evolución y Visitas")

        lay.addWidget(self.tabs, 1)

        # ── Botones de Acción Inferiores ──
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(12)

        self.btn_guardar = QPushButton(" Guardar Historia")
        self.btn_guardar.setObjectName("btnPrimary")
        self.btn_guardar.setIcon(svg_icon("save", color="#ffffff", size=15))
        self.btn_guardar.clicked.connect(self.save_data)

        self.btn_agendar_cita = QPushButton(" Agendar Cita")
        self.btn_agendar_cita.setObjectName("btnSuccess")
        self.btn_agendar_cita.setIcon(svg_icon("calendar", color="#047857", size=15))
        self.btn_agendar_cita.setToolTip("Abrir Agenda con este paciente preseleccionado")
        self.btn_agendar_cita.clicked.connect(self._ir_a_agendar_cita)

        self.btn_farmacos = QPushButton(" Fármacos")
        self.btn_farmacos.setObjectName("btnSecondary")
        self.btn_farmacos.setIcon(svg_icon("pill", color="#7c3aed", size=15))
        self.btn_farmacos.setToolTip("Abrir Fármacos / Recetas con este paciente preseleccionado")
        self.btn_farmacos.clicked.connect(self._ir_a_farmacos)

        self.btn_imprimir = QPushButton(" Imprimir Historia PDF")
        self.btn_imprimir.setObjectName("btnPdf")
        self.btn_imprimir.setIcon(svg_icon("printer", color="#475569", size=15))
        self.btn_imprimir.clicked.connect(self.imprimir_pdf)

        self.btn_limpiar = QPushButton(" Limpiar")
        self.btn_limpiar.setObjectName("btnSecondary")
        self.btn_limpiar.setIcon(svg_icon("x", color="#64748b", size=15))
        self.btn_limpiar.clicked.connect(self.clear_form)

        btn_bar.addWidget(self.btn_guardar)
        btn_bar.addWidget(self.btn_agendar_cita)
        btn_bar.addWidget(self.btn_farmacos)
        btn_bar.addWidget(self.btn_imprimir)
        btn_bar.addWidget(self.btn_limpiar)
        btn_bar.addStretch()

        lay.addLayout(btn_bar)

        return card

    # ── Pestaña 1: Filiación e Ingreso ─────────────────────────
    def _build_tab_filiacion(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        g = QGridLayout()
        g.setSpacing(12)

        # Fechas de ingreso y egreso
        g.addWidget(self._lbl("Fecha de Ingreso:"), 0, 0)
        self.input_fecha_ingreso = SmartDateEdit(QDate.currentDate())
        g.addWidget(self.input_fecha_ingreso, 0, 1)

        g.addWidget(self._lbl("Fecha de Egreso:"), 0, 2)
        self.input_fecha_egreso = SmartDateEdit(QDate.currentDate().addMonths(6))
        g.addWidget(self.input_fecha_egreso, 0, 3)

        # Lugar y fecha de nacimiento
        g.addWidget(self._lbl("Lugar de Nacimiento:"), 1, 0)
        self.input_lugar_nac = QLineEdit()
        self.input_lugar_nac.setPlaceholderText("Ciudad, Estado, País de nacimiento")
        g.addWidget(self.input_lugar_nac, 1, 1)

        g.addWidget(self._lbl("Fecha de Nacimiento:"), 1, 2)
        self.input_fecha_nac = SmartDateEdit(QDate.currentDate().addYears(-15))
        self.input_fecha_nac.setDisplayFormat("dd/MM/yyyy")
        self.input_fecha_nac.dateChanged.connect(self._actualizar_edad)
        g.addWidget(self.input_fecha_nac, 1, 3)

        # Edad independiente y Teléfono independiente
        g.addWidget(self._lbl("Edad:"), 2, 0)
        self.input_edad = QLineEdit()
        self.input_edad.setPlaceholderText("Edad en años")
        self.input_edad.setValidator(QIntValidator(0, 120))
        g.addWidget(self.input_edad, 2, 1)

        g.addWidget(self._lbl("Teléfono:"), 2, 2)
        tel_row = QHBoxLayout()
        tel_row.setSpacing(6)
        self.combo_prefijo_tel = QComboBox()
        self.combo_prefijo_tel.setView(QListView())
        self.combo_prefijo_tel.addItems(["0412", "0414", "0416", "0424", "0426", "0422"])
        self.combo_prefijo_tel.setFixedWidth(85)
        self.combo_prefijo_tel.setStyleSheet("padding: 7px 4px;")
        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("Ej. 1234567")
        self.input_telefono.setValidator(QIntValidator(0, 9999999))
        self.input_telefono.setMaxLength(7)
        self.input_telefono.setMinimumWidth(140)
        self.input_telefono.setStyleSheet("padding: 7px 10px;")
        tel_row.addWidget(self.combo_prefijo_tel)
        tel_row.addWidget(self.input_telefono, 1)
        g.addLayout(tel_row, 2, 3)

        # Dirección
        g.addWidget(self._lbl("Dirección / Domicilio:"), 3, 0)
        self.input_direccion = QLineEdit()
        self.input_direccion.setPlaceholderText("Dirección completa de habitación y sector")
        g.addWidget(self.input_direccion, 3, 1, 1, 3)

        # Nivel de Instrucción Académica y Ocupación
        g.addWidget(self._lbl("Nivel de Instrucción Académica:"), 4, 0)
        self.combo_instruccion = QComboBox()
        self.combo_instruccion.setView(QListView())
        self.combo_instruccion.addItems([
            "Sin instrucción", "Preescolar", "Primaria en curso", "Primaria completa",
            "Secundaria en curso", "Bachiller", "Técnico Medio / Superior",
            "Universitario en curso", "Universitario graduado", "Especialización / Postgrado", "Maestría / Doctorado"
        ])
        g.addWidget(self.combo_instruccion, 4, 1)

        g.addWidget(self._lbl("Ocupación:"), 4, 2)
        self.input_ocupacion = QLineEdit()
        self.input_ocupacion.setPlaceholderText("Estudiante, profesión, oficio o actividad actual")
        g.addWidget(self.input_ocupacion, 4, 3)

        # Creencias religiosas y Solicitante
        g.addWidget(self._lbl("Creencias Religiosas:"), 5, 0)
        self.input_religion = QLineEdit()
        self.input_religion.setPlaceholderText("Religión o práctica espiritual")
        g.addWidget(self.input_religion, 5, 1)

        g.addWidget(self._lbl("Referencias / Solicitante:"), 5, 2)
        self.input_referencias = QLineEdit()
        self.input_referencias.setPlaceholderText("Médico remitente, colegio o iniciativa propia")
        g.addWidget(self.input_referencias, 5, 3)

        lay.addLayout(g)

        # Entorno familiar
        lay.addWidget(self._lbl_bold("Entorno Familiar (¿Con quién vive? Integrantes del hogar y dinámica familiar):"))
        self.input_entorno_familiar = QTextEdit()
        self.input_entorno_familiar.setPlaceholderText("Describir personas que conviven en el hogar, parentesco, relaciones interpersonales, clima afectivo...")
        self.input_entorno_familiar.setMinimumHeight(85)
        lay.addWidget(self.input_entorno_familiar)

        lay.addStretch()
        scroll.setWidget(w)
        return scroll

    # ── Pestaña 6: Evolución, Visitas y Recordatorios ──────────
    def _build_tab_evolucion(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Tarjeta resumen inteligente (Última visita + Recordatorio + Próxima cita)
        resumen_card = QFrame()
        resumen_card.setObjectName("subCard")
        r_lay = QVBoxLayout(resumen_card)
        r_lay.setSpacing(6)

        top_info = QHBoxLayout()
        self.lbl_ultima_visita = QLabel("🕒 Última visita: Sin visitas registradas aún")
        self.lbl_ultima_visita.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px;")
        top_info.addWidget(self.lbl_ultima_visita, 1)

        self.lbl_proxima_cita = QLabel("📅 Próxima cita: Ninguna programada")
        self.lbl_proxima_cita.setStyleSheet("font-weight: 600; color: #047857; font-size: 13px;")
        top_info.addWidget(self.lbl_proxima_cita)
        r_lay.addLayout(top_info)

        self.lbl_recordatorio_pendiente = QLabel("📌 Recordatorio pendiente: Ninguno")
        self.lbl_recordatorio_pendiente.setWordWrap(True)
        self.lbl_recordatorio_pendiente.setStyleSheet(
            "background: #fefce8; border: 1px solid #fde047; border-radius: 6px; "
            "color: #854d0e; padding: 8px 10px; font-size: 13px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_recordatorio_pendiente)

        self.lbl_medicacion_activa = QLabel("💊 Medicación / Recetas activas: Sin medicación registrada")
        self.lbl_medicacion_activa.setWordWrap(True)
        self.lbl_medicacion_activa.setStyleSheet(
            "background: #faf5ff; border: 1px solid #ddd6fe; border-radius: 6px; "
            "color: #6d28d9; padding: 7px 10px; font-size: 12.5px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_medicacion_activa)
        lay.addWidget(resumen_card)

        # Formulario de nueva visita / nota adicional
        lay.addWidget(self._lbl_bold("Registrar Visita / Nota Adicional de Seguimiento:"))
        form_row = QHBoxLayout()
        form_row.setSpacing(10)

        self.visita_fecha = SmartDateEdit(QDate.currentDate())
        self.visita_fecha.setMinimumWidth(165)
        form_row.addWidget(self._labeled_field("Fecha:", self.visita_fecha), 0)

        self.visita_hora = QTimeEdit(QTime.currentTime())
        self.visita_hora.setDisplayFormat("HH:mm")
        self.visita_hora.setMinimumWidth(100)
        form_row.addWidget(self._labeled_field("Hora:", self.visita_hora), 0)

        self.visita_tipo = QComboBox()
        self.visita_tipo.addItems(["Primera vez", "Sucesiva", "Control", "Seguimiento"])
        form_row.addWidget(self._labeled_field("Tipo:", self.visita_tipo), 1)
        lay.addLayout(form_row)

        self.visita_evolucion = QTextEdit()
        self.visita_evolucion.setPlaceholderText(
            "Detalles de esta visita, evolución observada, temas tratados, avances o cambios..."
        )
        self.visita_evolucion.setMinimumHeight(80)
        self.visita_evolucion.setMaximumHeight(110)
        lay.addWidget(self.visita_evolucion)

        self.visita_recordatorio = QLineEdit()
        self.visita_recordatorio.setPlaceholderText(
            "📌 Nota adicional / Recordatorio para la próxima visita (ej: Traer informe, evaluar tarea...)"
        )
        self.visita_recordatorio.setMaxLength(200)
        lay.addWidget(self.visita_recordatorio)

        v_btns = QHBoxLayout()
        self.btn_guardar_visita = QPushButton("➕ Guardar Visita")
        self.btn_guardar_visita.setObjectName("btnSuccess")
        self.btn_guardar_visita.clicked.connect(self._guardar_visita)

        btn_nueva_visita = QPushButton("🧹 Limpiar Visita")
        btn_nueva_visita.setObjectName("btnSecondary")
        btn_nueva_visita.clicked.connect(self._limpiar_visita_form)

        btn_del_visita = QPushButton("🗑 Eliminar Visita")
        btn_del_visita.setObjectName("btnDanger")
        btn_del_visita.clicked.connect(self._eliminar_visita)

        v_btns.addWidget(self.btn_guardar_visita)
        v_btns.addWidget(btn_nueva_visita)
        v_btns.addWidget(btn_del_visita)
        v_btns.addStretch()
        lay.addLayout(v_btns)

        # Tabla cronológica de visitas del paciente
        lay.addWidget(self._lbl_bold("Historial Cronológico de Visitas y Notas:"))
        self.tabla_visitas = QTableWidget(0, 6)
        self.tabla_visitas.setHorizontalHeaderLabels([
            "Fecha", "Hora", "Tipo", "Evolución / Detalles", "Recordatorio", "ID"
        ])
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.setColumnHidden(5, True)
        self.tabla_visitas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_visitas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_visitas.setAlternatingRowColors(True)
        self.tabla_visitas.verticalHeader().setVisible(False)
        self.tabla_visitas.setMinimumHeight(160)
        self.tabla_visitas.itemDoubleClicked.connect(self._cargar_visita_click)
        lay.addWidget(self.tabla_visitas, 1)

        scroll.setWidget(w)
        return scroll

    # ── Pestaña 2: Antecedentes Médicos y Consulta ─────────────
    def _build_tab_antecedentes(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Motivo de Consulta
        lay.addWidget(self._lbl_bold("Motivo de Consulta (Razón principal referida por el paciente o acudiente):"))
        self.input_motivo = QTextEdit()
        self.input_motivo.setPlaceholderText("Describir detalladamente la sintomatología o motivo que origina la consulta...")
        self.input_motivo.setMinimumHeight(90)
        lay.addWidget(self.input_motivo)

        # Antecedentes Personales No Patológicos
        lay.addWidget(self._lbl_bold("Antecedentes Personales No Patológicos:"))
        self.input_ant_no_patologicos = QTextEdit()
        self.input_ant_no_patologicos.setPlaceholderText("Hábitos de sueño, alimentación, apetito, actividad física, rutinas diarias, higiene...")
        self.input_ant_no_patologicos.setMinimumHeight(85)
        lay.addWidget(self.input_ant_no_patologicos)

        # Antecedentes Personales Patológicos
        lay.addWidget(self._lbl_bold("Antecedentes Personales Patológicos (Hipertensión, diabetes, alergias, cirugías, traumatismos, etc.):"))
        self.input_ant_patologicos = QTextEdit()
        self.input_ant_patologicos.setPlaceholderText("Enfermedades crónicas o previas, medicación actual, hospitalizaciones, intervenciones quirúrgicas...")
        self.input_ant_patologicos.setMinimumHeight(85)
        lay.addWidget(self.input_ant_patologicos)

        # Antecedentes Heredo-Familiares de Trastornos Mentales
        lay.addWidget(self._lbl_bold("Antecedentes Patológicos Heredo-Familiares de Trastornos Mentales:"))
        self.input_ant_heredo_mentales = QTextEdit()
        self.input_ant_heredo_mentales.setPlaceholderText("Historia familiar de depresión, ansiedad, trastorno bipolar, esquizofrenia, consumo de sustancias, conductas autolíticas...")
        self.input_ant_heredo_mentales.setMinimumHeight(85)
        lay.addWidget(self.input_ant_heredo_mentales)

        # Gestas / Pérdidas y Atención Psicológica Previa
        g2 = QGridLayout()
        g2.setSpacing(12)

        g2.addWidget(self._lbl("N° de Gestas / Pérdidas:"), 0, 0)
        self.input_gestas_perdidas = QLineEdit()
        self.input_gestas_perdidas.setPlaceholderText("Ej: G:2, P:1, A:1 (si aplica)")
        g2.addWidget(self.input_gestas_perdidas, 0, 1)

        g2.addWidget(self._lbl("Atención Psicológica Previa:"), 0, 2)
        self.input_atencion_psic_previa = QLineEdit()
        self.input_atencion_psic_previa.setPlaceholderText("¿Ha recibido atención antes? Duración, motivos y resultados")
        g2.addWidget(self.input_atencion_psic_previa, 0, 3)

        lay.addLayout(g2)

        # Evaluaciones previas por otra especialidad
        lay.addWidget(self._lbl_bold("Evaluaciones Previas por otra Especialidad (Neurología, psicopedagogía, psiquiatría, foniatría, etc.):"))
        self.input_eval_especialidades = QTextEdit()
        self.input_eval_especialidades.setPlaceholderText("Informes previos de especialistas, estudios complementarios realizados (EEG, audiometría, etc.)...")
        self.input_eval_especialidades.setMinimumHeight(85)
        lay.addWidget(self.input_eval_especialidades)

        lay.addStretch()
        scroll.setWidget(w)
        return scroll

    # ── Pestaña 6: Evolución, Visitas y Recordatorios ──────────
    def _build_tab_evolucion(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Tarjeta resumen inteligente (Última visita + Recordatorio + Próxima cita)
        resumen_card = QFrame()
        resumen_card.setObjectName("subCard")
        r_lay = QVBoxLayout(resumen_card)
        r_lay.setSpacing(6)

        top_info = QHBoxLayout()
        self.lbl_ultima_visita = QLabel("🕒 Última visita: Sin visitas registradas aún")
        self.lbl_ultima_visita.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px;")
        top_info.addWidget(self.lbl_ultima_visita, 1)

        self.lbl_proxima_cita = QLabel("📅 Próxima cita: Ninguna programada")
        self.lbl_proxima_cita.setStyleSheet("font-weight: 600; color: #047857; font-size: 13px;")
        top_info.addWidget(self.lbl_proxima_cita)
        r_lay.addLayout(top_info)

        self.lbl_recordatorio_pendiente = QLabel("📌 Recordatorio pendiente: Ninguno")
        self.lbl_recordatorio_pendiente.setWordWrap(True)
        self.lbl_recordatorio_pendiente.setStyleSheet(
            "background: #fefce8; border: 1px solid #fde047; border-radius: 6px; "
            "color: #854d0e; padding: 8px 10px; font-size: 13px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_recordatorio_pendiente)

        self.lbl_medicacion_activa = QLabel("💊 Medicación / Recetas activas: Sin medicación registrada")
        self.lbl_medicacion_activa.setWordWrap(True)
        self.lbl_medicacion_activa.setStyleSheet(
            "background: #faf5ff; border: 1px solid #ddd6fe; border-radius: 6px; "
            "color: #6d28d9; padding: 7px 10px; font-size: 12.5px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_medicacion_activa)
        lay.addWidget(resumen_card)

        # Formulario de nueva visita / nota adicional
        lay.addWidget(self._lbl_bold("Registrar Visita / Nota Adicional de Seguimiento:"))
        form_row = QHBoxLayout()
        form_row.setSpacing(10)

        self.visita_fecha = SmartDateEdit(QDate.currentDate())
        self.visita_fecha.setMinimumWidth(165)
        form_row.addWidget(self._labeled_field("Fecha:", self.visita_fecha), 0)

        self.visita_hora = QTimeEdit(QTime.currentTime())
        self.visita_hora.setDisplayFormat("HH:mm")
        self.visita_hora.setMinimumWidth(100)
        form_row.addWidget(self._labeled_field("Hora:", self.visita_hora), 0)

        self.visita_tipo = QComboBox()
        self.visita_tipo.addItems(["Primera vez", "Sucesiva", "Control", "Seguimiento"])
        form_row.addWidget(self._labeled_field("Tipo:", self.visita_tipo), 1)
        lay.addLayout(form_row)

        self.visita_evolucion = QTextEdit()
        self.visita_evolucion.setPlaceholderText(
            "Detalles de esta visita, evolución observada, temas tratados, avances o cambios..."
        )
        self.visita_evolucion.setMinimumHeight(80)
        self.visita_evolucion.setMaximumHeight(110)
        lay.addWidget(self.visita_evolucion)

        self.visita_recordatorio = QLineEdit()
        self.visita_recordatorio.setPlaceholderText(
            "📌 Nota adicional / Recordatorio para la próxima visita (ej: Traer informe, evaluar tarea...)"
        )
        self.visita_recordatorio.setMaxLength(200)
        lay.addWidget(self.visita_recordatorio)

        v_btns = QHBoxLayout()
        self.btn_guardar_visita = QPushButton("➕ Guardar Visita")
        self.btn_guardar_visita.setObjectName("btnSuccess")
        self.btn_guardar_visita.clicked.connect(self._guardar_visita)

        btn_nueva_visita = QPushButton("🧹 Limpiar Visita")
        btn_nueva_visita.setObjectName("btnSecondary")
        btn_nueva_visita.clicked.connect(self._limpiar_visita_form)

        btn_del_visita = QPushButton("🗑 Eliminar Visita")
        btn_del_visita.setObjectName("btnDanger")
        btn_del_visita.clicked.connect(self._eliminar_visita)

        v_btns.addWidget(self.btn_guardar_visita)
        v_btns.addWidget(btn_nueva_visita)
        v_btns.addWidget(btn_del_visita)
        v_btns.addStretch()
        lay.addLayout(v_btns)

        # Tabla cronológica de visitas del paciente
        lay.addWidget(self._lbl_bold("Historial Cronológico de Visitas y Notas:"))
        self.tabla_visitas = QTableWidget(0, 6)
        self.tabla_visitas.setHorizontalHeaderLabels([
            "Fecha", "Hora", "Tipo", "Evolución / Detalles", "Recordatorio", "ID"
        ])
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.setColumnHidden(5, True)
        self.tabla_visitas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_visitas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_visitas.setAlternatingRowColors(True)
        self.tabla_visitas.verticalHeader().setVisible(False)
        self.tabla_visitas.setMinimumHeight(160)
        self.tabla_visitas.itemDoubleClicked.connect(self._cargar_visita_click)
        lay.addWidget(self.tabla_visitas, 1)

        scroll.setWidget(w)
        return scroll

    # ── Pestaña 3: Datos del Representante ──────────────────────
    def _build_tab_representante(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        box_rep = QFrame()
        box_rep.setObjectName("subCard")
        box_lay = QGridLayout(box_rep)
        box_lay.setSpacing(12)
        box_lay.setContentsMargins(14, 14, 14, 14)

        # Fila 0: Nombre y Cédula
        box_lay.addWidget(self._lbl("Nombre y Apellidos del Representante:"), 0, 0)
        self.input_rep_nombre = QLineEdit()
        self.input_rep_nombre.setPlaceholderText("Nombre completo del padre, madre o tutor legal")
        box_lay.addWidget(self.input_rep_nombre, 0, 1)

        box_lay.addWidget(self._lbl("Cédula:"), 0, 2)
        ced_rep_row = QHBoxLayout()
        ced_rep_row.setSpacing(4)
        self.combo_rep_tipo_cedula = QComboBox()
        self.combo_rep_tipo_cedula.setView(QListView())
        self.combo_rep_tipo_cedula.addItems(["V-", "E-", "J-", "P-"])
        self.combo_rep_tipo_cedula.setFixedWidth(68)
        self.combo_rep_tipo_cedula.setStyleSheet("padding: 5px 6px;")
        self.input_rep_cedula = QLineEdit()
        self.input_rep_cedula.setPlaceholderText("Nº Cédula")
        self.input_rep_cedula.setValidator(QIntValidator(0, 999999999))
        ced_rep_row.addWidget(self.combo_rep_tipo_cedula)
        ced_rep_row.addWidget(self.input_rep_cedula)
        box_lay.addLayout(ced_rep_row, 0, 3)

        # Fila 1: EDAD INDEPENDIENTE y TELÉFONO INDEPENDIENTE
        box_lay.addWidget(self._lbl("Edad:"), 1, 0)
        self.input_rep_edad = QLineEdit()
        self.input_rep_edad.setPlaceholderText("Edad en años")
        self.input_rep_edad.setValidator(QIntValidator(0, 120))
        box_lay.addWidget(self.input_rep_edad, 1, 1)

        box_lay.addWidget(self._lbl("Teléfono:"), 1, 2)
        tel_rep_row = QHBoxLayout()
        tel_rep_row.setSpacing(6)
        self.combo_rep_prefijo = QComboBox()
        self.combo_rep_prefijo.setView(QListView())
        self.combo_rep_prefijo.addItems(["0412", "0414", "0416", "0424", "0426", "0422"])
        self.combo_rep_prefijo.setFixedWidth(85)
        self.combo_rep_prefijo.setStyleSheet("padding: 7px 4px;")
        self.input_rep_telefono = QLineEdit()
        self.input_rep_telefono.setPlaceholderText("Ej. 1234567")
        self.input_rep_telefono.setValidator(QIntValidator(0, 9999999))
        self.input_rep_telefono.setMaxLength(7)
        self.input_rep_telefono.setMinimumWidth(140)
        self.input_rep_telefono.setStyleSheet("padding: 7px 10px;")
        tel_rep_row.addWidget(self.combo_rep_prefijo)
        tel_rep_row.addWidget(self.input_rep_telefono, 1)
        box_lay.addLayout(tel_rep_row, 1, 3)

        # Fila 2: NIVEL DE INSTRUCCIÓN ACADÉMICA y OCUPACIÓN
        box_lay.addWidget(self._lbl("Nivel de Instrucción Académica:"), 2, 0)
        self.combo_rep_instruccion = QComboBox()
        self.combo_rep_instruccion.setView(QListView())
        self.combo_rep_instruccion.addItems([
            "Sin instrucción", "Primaria incompleta", "Primaria completa",
            "Secundaria incompleta", "Bachiller", "Técnico Medio / Superior",
            "Universitario en curso", "Universitario graduado",
            "Especialización / Postgrado", "Maestría / Doctorado"
        ])
        box_lay.addWidget(self.combo_rep_instruccion, 2, 1)

        box_lay.addWidget(self._lbl("Ocupación:"), 2, 2)
        self.input_rep_ocupacion = QLineEdit()
        self.input_rep_ocupacion.setPlaceholderText("Profesión, empleo u ocupación actual")
        box_lay.addWidget(self.input_rep_ocupacion, 2, 3)

        lay.addWidget(box_rep)

        # Historia biográfica del Representante con campos amplios
        lay.addWidget(self._lbl_bold("Historia Biográfica del Representante:"))

        lay.addWidget(self._lbl("• Infancia (Ambiente familiar de origen, dinámica de crianza, eventos relevantes):"))
        self.input_rep_infancia = QTextEdit()
        self.input_rep_infancia.setPlaceholderText("Relación con sus padres, ambiente familiar de crianza, pérdidas o eventos significativos en la niñez...")
        self.input_rep_infancia.setMinimumHeight(90)
        lay.addWidget(self.input_rep_infancia)

        lay.addWidget(self._lbl("• Adultez (Trayectoria personal, estabilidad emocional, responsabilidades y desarrollo):"))
        self.input_rep_adultez = QTextEdit()
        self.input_rep_adultez.setPlaceholderText("Desarrollo en la etapa adulta, estabilidad laboral y económica, manejo de situaciones de estrés...")
        self.input_rep_adultez.setMinimumHeight(90)
        lay.addWidget(self.input_rep_adultez)

        lay.addWidget(self._lbl("• Etapa Amorosa (Relación de pareja, convivencia, conflictos, acuerdos de crianza):"))
        self.input_rep_etapa_amorosa = QTextEdit()
        self.input_rep_etapa_amorosa.setPlaceholderText("Historia afectiva y de pareja, tipo de relación actual, canales de comunicación y apoyo mutuo...")
        self.input_rep_etapa_amorosa.setMinimumHeight(90)
        lay.addWidget(self.input_rep_etapa_amorosa)

        lay.addStretch()
        scroll.setWidget(w)
        return scroll

    # ── Pestaña 6: Evolución, Visitas y Recordatorios ──────────
    def _build_tab_evolucion(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Tarjeta resumen inteligente (Última visita + Recordatorio + Próxima cita)
        resumen_card = QFrame()
        resumen_card.setObjectName("subCard")
        r_lay = QVBoxLayout(resumen_card)
        r_lay.setSpacing(6)

        top_info = QHBoxLayout()
        self.lbl_ultima_visita = QLabel("🕒 Última visita: Sin visitas registradas aún")
        self.lbl_ultima_visita.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px;")
        top_info.addWidget(self.lbl_ultima_visita, 1)

        self.lbl_proxima_cita = QLabel("📅 Próxima cita: Ninguna programada")
        self.lbl_proxima_cita.setStyleSheet("font-weight: 600; color: #047857; font-size: 13px;")
        top_info.addWidget(self.lbl_proxima_cita)
        r_lay.addLayout(top_info)

        self.lbl_recordatorio_pendiente = QLabel("📌 Recordatorio pendiente: Ninguno")
        self.lbl_recordatorio_pendiente.setWordWrap(True)
        self.lbl_recordatorio_pendiente.setStyleSheet(
            "background: #fefce8; border: 1px solid #fde047; border-radius: 6px; "
            "color: #854d0e; padding: 8px 10px; font-size: 13px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_recordatorio_pendiente)

        self.lbl_medicacion_activa = QLabel("💊 Medicación / Recetas activas: Sin medicación registrada")
        self.lbl_medicacion_activa.setWordWrap(True)
        self.lbl_medicacion_activa.setStyleSheet(
            "background: #faf5ff; border: 1px solid #ddd6fe; border-radius: 6px; "
            "color: #6d28d9; padding: 7px 10px; font-size: 12.5px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_medicacion_activa)
        lay.addWidget(resumen_card)

        # Formulario de nueva visita / nota adicional
        lay.addWidget(self._lbl_bold("Registrar Visita / Nota Adicional de Seguimiento:"))
        form_row = QHBoxLayout()
        form_row.setSpacing(10)

        self.visita_fecha = SmartDateEdit(QDate.currentDate())
        self.visita_fecha.setMinimumWidth(165)
        form_row.addWidget(self._labeled_field("Fecha:", self.visita_fecha), 0)

        self.visita_hora = QTimeEdit(QTime.currentTime())
        self.visita_hora.setDisplayFormat("HH:mm")
        self.visita_hora.setMinimumWidth(100)
        form_row.addWidget(self._labeled_field("Hora:", self.visita_hora), 0)

        self.visita_tipo = QComboBox()
        self.visita_tipo.addItems(["Primera vez", "Sucesiva", "Control", "Seguimiento"])
        form_row.addWidget(self._labeled_field("Tipo:", self.visita_tipo), 1)
        lay.addLayout(form_row)

        self.visita_evolucion = QTextEdit()
        self.visita_evolucion.setPlaceholderText(
            "Detalles de esta visita, evolución observada, temas tratados, avances o cambios..."
        )
        self.visita_evolucion.setMinimumHeight(80)
        self.visita_evolucion.setMaximumHeight(110)
        lay.addWidget(self.visita_evolucion)

        self.visita_recordatorio = QLineEdit()
        self.visita_recordatorio.setPlaceholderText(
            "📌 Nota adicional / Recordatorio para la próxima visita (ej: Traer informe, evaluar tarea...)"
        )
        self.visita_recordatorio.setMaxLength(200)
        lay.addWidget(self.visita_recordatorio)

        v_btns = QHBoxLayout()
        self.btn_guardar_visita = QPushButton("➕ Guardar Visita")
        self.btn_guardar_visita.setObjectName("btnSuccess")
        self.btn_guardar_visita.clicked.connect(self._guardar_visita)

        btn_nueva_visita = QPushButton("🧹 Limpiar Visita")
        btn_nueva_visita.setObjectName("btnSecondary")
        btn_nueva_visita.clicked.connect(self._limpiar_visita_form)

        btn_del_visita = QPushButton("🗑 Eliminar Visita")
        btn_del_visita.setObjectName("btnDanger")
        btn_del_visita.clicked.connect(self._eliminar_visita)

        v_btns.addWidget(self.btn_guardar_visita)
        v_btns.addWidget(btn_nueva_visita)
        v_btns.addWidget(btn_del_visita)
        v_btns.addStretch()
        lay.addLayout(v_btns)

        # Tabla cronológica de visitas del paciente
        lay.addWidget(self._lbl_bold("Historial Cronológico de Visitas y Notas:"))
        self.tabla_visitas = QTableWidget(0, 6)
        self.tabla_visitas.setHorizontalHeaderLabels([
            "Fecha", "Hora", "Tipo", "Evolución / Detalles", "Recordatorio", "ID"
        ])
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.setColumnHidden(5, True)
        self.tabla_visitas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_visitas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_visitas.setAlternatingRowColors(True)
        self.tabla_visitas.verticalHeader().setVisible(False)
        self.tabla_visitas.setMinimumHeight(160)
        self.tabla_visitas.itemDoubleClicked.connect(self._cargar_visita_click)
        lay.addWidget(self.tabla_visitas, 1)

        scroll.setWidget(w)
        return scroll

    # ── Pestaña 4: Autoexploración Emocional ────────────────────
    def _build_tab_emocional(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        intro = QLabel("💭 Preguntas de Autoexploración y Reflexión Emocional")
        intro.setStyleSheet("font-size: 16px; font-weight: bold; color: #1e3a8a;")
        lay.addWidget(intro)

        # Pregunta 1
        q1_box = QFrame()
        q1_box.setObjectName("subCard")
        q1_lay = QVBoxLayout(q1_box)
        q1_lay.addWidget(self._lbl_bold("1) ¿Eres feliz?"))
        self.input_pregunta_feliz = QTextEdit()
        self.input_pregunta_feliz.setPlaceholderText("Respuesta del evaluado, motivos de satisfacción o insatisfacción actual, percepción de bienestar emocional...")
        self.input_pregunta_feliz.setMinimumHeight(95)
        q1_lay.addWidget(self.input_pregunta_feliz)
        lay.addWidget(q1_box)

        # Pregunta 2
        q2_box = QFrame()
        q2_box.setObjectName("subCard")
        q2_lay = QVBoxLayout(q2_box)
        q2_lay.addWidget(self._lbl_bold("2) Si pudieras modificar algo en tu vida, ¿qué sería?"))
        self.input_pregunta_modificar = QTextEdit()
        self.input_pregunta_modificar.setPlaceholderText("Aspectos personales, familiares, de relaciones o decisiones pasadas que desearía transformar...")
        self.input_pregunta_modificar.setMinimumHeight(95)
        q2_lay.addWidget(self.input_pregunta_modificar)
        lay.addWidget(q2_box)

        # Pregunta 3
        q3_box = QFrame()
        q3_box.setObjectName("subCard")
        q3_lay = QVBoxLayout(q3_box)
        q3_lay.addWidget(self._lbl_bold("3) ¿Cómo te proyectas en el futuro?"))
        self.input_pregunta_futuro = QTextEdit()
        self.input_pregunta_futuro.setPlaceholderText("Metas, aspiraciones personales, proyectos académicos, laborales o familiares a mediano y largo plazo...")
        self.input_pregunta_futuro.setMinimumHeight(95)
        q3_lay.addWidget(self.input_pregunta_futuro)
        lay.addWidget(q3_box)

        lay.addStretch()
        scroll.setWidget(w)
        return scroll

    # ── Pestaña 6: Evolución, Visitas y Recordatorios ──────────
    def _build_tab_evolucion(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Tarjeta resumen inteligente (Última visita + Recordatorio + Próxima cita)
        resumen_card = QFrame()
        resumen_card.setObjectName("subCard")
        r_lay = QVBoxLayout(resumen_card)
        r_lay.setSpacing(6)

        top_info = QHBoxLayout()
        self.lbl_ultima_visita = QLabel("🕒 Última visita: Sin visitas registradas aún")
        self.lbl_ultima_visita.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px;")
        top_info.addWidget(self.lbl_ultima_visita, 1)

        self.lbl_proxima_cita = QLabel("📅 Próxima cita: Ninguna programada")
        self.lbl_proxima_cita.setStyleSheet("font-weight: 600; color: #047857; font-size: 13px;")
        top_info.addWidget(self.lbl_proxima_cita)
        r_lay.addLayout(top_info)

        self.lbl_recordatorio_pendiente = QLabel("📌 Recordatorio pendiente: Ninguno")
        self.lbl_recordatorio_pendiente.setWordWrap(True)
        self.lbl_recordatorio_pendiente.setStyleSheet(
            "background: #fefce8; border: 1px solid #fde047; border-radius: 6px; "
            "color: #854d0e; padding: 8px 10px; font-size: 13px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_recordatorio_pendiente)

        self.lbl_medicacion_activa = QLabel("💊 Medicación / Recetas activas: Sin medicación registrada")
        self.lbl_medicacion_activa.setWordWrap(True)
        self.lbl_medicacion_activa.setStyleSheet(
            "background: #faf5ff; border: 1px solid #ddd6fe; border-radius: 6px; "
            "color: #6d28d9; padding: 7px 10px; font-size: 12.5px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_medicacion_activa)
        lay.addWidget(resumen_card)

        # Formulario de nueva visita / nota adicional
        lay.addWidget(self._lbl_bold("Registrar Visita / Nota Adicional de Seguimiento:"))
        form_row = QHBoxLayout()
        form_row.setSpacing(10)

        self.visita_fecha = SmartDateEdit(QDate.currentDate())
        self.visita_fecha.setMinimumWidth(165)
        form_row.addWidget(self._labeled_field("Fecha:", self.visita_fecha), 0)

        self.visita_hora = QTimeEdit(QTime.currentTime())
        self.visita_hora.setDisplayFormat("HH:mm")
        self.visita_hora.setMinimumWidth(100)
        form_row.addWidget(self._labeled_field("Hora:", self.visita_hora), 0)

        self.visita_tipo = QComboBox()
        self.visita_tipo.addItems(["Primera vez", "Sucesiva", "Control", "Seguimiento"])
        form_row.addWidget(self._labeled_field("Tipo:", self.visita_tipo), 1)
        lay.addLayout(form_row)

        self.visita_evolucion = QTextEdit()
        self.visita_evolucion.setPlaceholderText(
            "Detalles de esta visita, evolución observada, temas tratados, avances o cambios..."
        )
        self.visita_evolucion.setMinimumHeight(80)
        self.visita_evolucion.setMaximumHeight(110)
        lay.addWidget(self.visita_evolucion)

        self.visita_recordatorio = QLineEdit()
        self.visita_recordatorio.setPlaceholderText(
            "📌 Nota adicional / Recordatorio para la próxima visita (ej: Traer informe, evaluar tarea...)"
        )
        self.visita_recordatorio.setMaxLength(200)
        lay.addWidget(self.visita_recordatorio)

        v_btns = QHBoxLayout()
        self.btn_guardar_visita = QPushButton("➕ Guardar Visita")
        self.btn_guardar_visita.setObjectName("btnSuccess")
        self.btn_guardar_visita.clicked.connect(self._guardar_visita)

        btn_nueva_visita = QPushButton("🧹 Limpiar Visita")
        btn_nueva_visita.setObjectName("btnSecondary")
        btn_nueva_visita.clicked.connect(self._limpiar_visita_form)

        btn_del_visita = QPushButton("🗑 Eliminar Visita")
        btn_del_visita.setObjectName("btnDanger")
        btn_del_visita.clicked.connect(self._eliminar_visita)

        v_btns.addWidget(self.btn_guardar_visita)
        v_btns.addWidget(btn_nueva_visita)
        v_btns.addWidget(btn_del_visita)
        v_btns.addStretch()
        lay.addLayout(v_btns)

        # Tabla cronológica de visitas del paciente
        lay.addWidget(self._lbl_bold("Historial Cronológico de Visitas y Notas:"))
        self.tabla_visitas = QTableWidget(0, 6)
        self.tabla_visitas.setHorizontalHeaderLabels([
            "Fecha", "Hora", "Tipo", "Evolución / Detalles", "Recordatorio", "ID"
        ])
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.setColumnHidden(5, True)
        self.tabla_visitas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_visitas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_visitas.setAlternatingRowColors(True)
        self.tabla_visitas.verticalHeader().setVisible(False)
        self.tabla_visitas.setMinimumHeight(160)
        self.tabla_visitas.itemDoubleClicked.connect(self._cargar_visita_click)
        lay.addWidget(self.tabla_visitas, 1)

        scroll.setWidget(w)
        return scroll

    # ── Pestaña 5: Neurodesarrollo y Examen Clínico ─────────────
    def _build_tab_neuro(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Cuadro Clínico y Exploración Física
        lay.addWidget(self._lbl_bold("Cuadro Clínico Actual:"))
        self.input_cuadro_clinico = QTextEdit()
        self.input_cuadro_clinico.setPlaceholderText("Manifestaciones clínicas actuales, síntomas predominantes, intensidad y frecuencia...")
        self.input_cuadro_clinico.setMinimumHeight(85)
        lay.addWidget(self.input_cuadro_clinico)

        lay.addWidget(self._lbl_bold("Exploración Física:"))
        self.input_exploracion_fisica = QTextEdit()
        self.input_exploracion_fisica.setPlaceholderText("Inspección general, desarrollo somatométrico, características físicas relevantes...")
        self.input_exploracion_fisica.setMinimumHeight(80)
        lay.addWidget(self.input_exploracion_fisica)

        # Hábitos exterior y Autonomía motora
        g_mot = QGridLayout()
        g_mot.setSpacing(12)

        g_mot.addWidget(self._lbl_bold("Hábitos Exterior (Conductas observadas):"), 0, 0)
        self.input_habitos_exterior = QTextEdit()
        self.input_habitos_exterior.setPlaceholderText("Porte, contacto visual, cooperación, atención, aseo, postura, lenguaje corporal...")
        self.input_habitos_exterior.setMinimumHeight(85)
        g_mot.addWidget(self.input_habitos_exterior, 1, 0)

        g_mot.addWidget(self._lbl_bold("Autonomía Motora (Fina y Gruesa):"), 0, 1)
        self.input_autonomia_motora = QTextEdit()
        self.input_autonomia_motora.setPlaceholderText("Motricidad fina (pinza digital, trazo) y motricidad gruesa (marcha, equilibrio, tono postural)...")
        self.input_autonomia_motora.setMinimumHeight(85)
        g_mot.addWidget(self.input_autonomia_motora, 1, 1)
        lay.addLayout(g_mot)

        # Etapas del Neurodesarrollo
        lay.addWidget(self._lbl_bold("Etapas del Neurodesarrollo:"))

        g_neuro = QGridLayout()
        g_neuro.setSpacing(12)

        g_neuro.addWidget(self._lbl("• Etapa Prenatal:"), 0, 0)
        self.input_etapa_prenatal = QTextEdit()
        self.input_etapa_prenatal.setPlaceholderText("Control prenatal, salud materna durante gestación, amenazas de parto, exposición a fármacos...")
        self.input_etapa_prenatal.setMinimumHeight(80)
        g_neuro.addWidget(self.input_etapa_prenatal, 0, 1)

        g_neuro.addWidget(self._lbl("• Etapa Neonatal:"), 1, 0)
        self.input_etapa_neonatal = QTextEdit()
        self.input_etapa_neonatal.setPlaceholderText("Tipo de parto, semanas gestacionales, llanto al nacer, peso, apgar, necesidad de oxígeno...")
        self.input_etapa_neonatal.setMinimumHeight(80)
        g_neuro.addWidget(self.input_etapa_neonatal, 1, 1)

        g_neuro.addWidget(self._lbl("• Desarrollo Psicomotor:"), 2, 0)
        self.input_desarrollo_psicomotor = QTextEdit()
        self.input_desarrollo_psicomotor.setPlaceholderText("Edades de sostén cefálico, sedestación, gateo, primeros pasos, primeras palabras, control de esfínteres...")
        self.input_desarrollo_psicomotor.setMinimumHeight(80)
        g_neuro.addWidget(self.input_desarrollo_psicomotor, 2, 1)

        lay.addLayout(g_neuro)

        # Instrumentos utilizados de evaluación
        lay.addWidget(self._lbl_bold("Instrumentos Utilizados de Evaluación (Tests, escalas, cuestionarios aplicados):"))
        self.input_instrumentos_eval = QTextEdit()
        self.input_instrumentos_eval.setPlaceholderText("Pruebas psicométricas, reactivos proyectivos, escalas conductuales administradas...")
        self.input_instrumentos_eval.setMinimumHeight(80)
        lay.addWidget(self.input_instrumentos_eval)

        # IPX: Impresión Diagnóstica + Condición / Patología seleccionable
        lay.addWidget(self._lbl_bold("IPX: Impresión Diagnóstica y Condición Clínica (Criterios CIE / DSM):"))

        pat_row = QHBoxLayout()
        pat_row.setSpacing(8)
        pat_row.addWidget(self._lbl("Condición / Patología:"), 0)

        self.combo_patologia = QComboBox()
        self.combo_patologia.setView(QListView())
        self.combo_patologia.addItems(DEFAULT_CONDICIONES_CLINICAS)
        self.combo_patologia.setToolTip("Selecciona la condición o diagnóstico principal para filtrar y clasificar.")
        pat_row.addWidget(self.combo_patologia, 1)

        btn_nueva_pat = QPushButton("➕ Nueva")
        btn_nueva_pat.setObjectName("btnSecondary")
        btn_nueva_pat.setToolTip("Agregar una nueva condición o patología al catálogo")
        btn_nueva_pat.clicked.connect(self._agregar_nueva_patologia)
        pat_row.addWidget(btn_nueva_pat)
        lay.addLayout(pat_row)

        self.input_ipx = QTextEdit()
        self.input_ipx.setPlaceholderText("Impresión diagnóstica principal, criterios sustentados, conclusiones y recomendaciones de abordaje terapéutico...")
        self.input_ipx.setMinimumHeight(100)
        self.input_ipx.setStyleSheet("""
            QTextEdit {
                border: 2px solid #93c5fd;
                border-radius: 8px;
                background: #f0fdf4;
                font-weight: 600;
                color: #0f172a;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #2563eb;
                background: #ffffff;
            }
        """)
        lay.addWidget(self.input_ipx)

        lay.addStretch()
        scroll.setWidget(w)
        return scroll

    # ── Pestaña 6: Evolución, Visitas y Recordatorios ──────────
    def _build_tab_evolucion(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)

        # Tarjeta resumen inteligente (Última visita + Recordatorio + Próxima cita)
        resumen_card = QFrame()
        resumen_card.setObjectName("subCard")
        r_lay = QVBoxLayout(resumen_card)
        r_lay.setSpacing(6)

        top_info = QHBoxLayout()
        self.lbl_ultima_visita = QLabel("🕒 Última visita: Sin visitas registradas aún")
        self.lbl_ultima_visita.setStyleSheet("font-weight: bold; color: #1e3a8a; font-size: 13px;")
        top_info.addWidget(self.lbl_ultima_visita, 1)

        self.lbl_proxima_cita = QLabel("📅 Próxima cita: Ninguna programada")
        self.lbl_proxima_cita.setStyleSheet("font-weight: 600; color: #047857; font-size: 13px;")
        top_info.addWidget(self.lbl_proxima_cita)
        r_lay.addLayout(top_info)

        self.lbl_recordatorio_pendiente = QLabel("📌 Recordatorio pendiente: Ninguno")
        self.lbl_recordatorio_pendiente.setWordWrap(True)
        self.lbl_recordatorio_pendiente.setStyleSheet(
            "background: #fefce8; border: 1px solid #fde047; border-radius: 6px; "
            "color: #854d0e; padding: 8px 10px; font-size: 13px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_recordatorio_pendiente)

        self.lbl_medicacion_activa = QLabel("💊 Medicación / Recetas activas: Sin medicación registrada")
        self.lbl_medicacion_activa.setWordWrap(True)
        self.lbl_medicacion_activa.setStyleSheet(
            "background: #faf5ff; border: 1px solid #ddd6fe; border-radius: 6px; "
            "color: #6d28d9; padding: 7px 10px; font-size: 12.5px; font-weight: 500;"
        )
        r_lay.addWidget(self.lbl_medicacion_activa)
        lay.addWidget(resumen_card)

        # Formulario de nueva visita / nota adicional
        lay.addWidget(self._lbl_bold("Registrar Visita / Nota Adicional de Seguimiento:"))
        form_row = QHBoxLayout()
        form_row.setSpacing(10)

        self.visita_fecha = SmartDateEdit(QDate.currentDate())
        self.visita_fecha.setMinimumWidth(165)
        form_row.addWidget(self._labeled_field("Fecha:", self.visita_fecha), 0)

        self.visita_hora = QTimeEdit(QTime.currentTime())
        self.visita_hora.setDisplayFormat("HH:mm")
        self.visita_hora.setMinimumWidth(100)
        form_row.addWidget(self._labeled_field("Hora:", self.visita_hora), 0)

        self.visita_tipo = QComboBox()
        self.visita_tipo.addItems(["Primera vez", "Sucesiva", "Control", "Seguimiento"])
        form_row.addWidget(self._labeled_field("Tipo:", self.visita_tipo), 1)
        lay.addLayout(form_row)

        self.visita_evolucion = QTextEdit()
        self.visita_evolucion.setPlaceholderText(
            "Detalles de esta visita, evolución observada, temas tratados, avances o cambios..."
        )
        self.visita_evolucion.setMinimumHeight(80)
        self.visita_evolucion.setMaximumHeight(110)
        lay.addWidget(self.visita_evolucion)

        self.visita_recordatorio = QLineEdit()
        self.visita_recordatorio.setPlaceholderText(
            "📌 Nota adicional / Recordatorio para la próxima visita (ej: Traer informe, evaluar tarea...)"
        )
        self.visita_recordatorio.setMaxLength(200)
        lay.addWidget(self.visita_recordatorio)

        v_btns = QHBoxLayout()
        self.btn_guardar_visita = QPushButton("➕ Guardar Visita")
        self.btn_guardar_visita.setObjectName("btnSuccess")
        self.btn_guardar_visita.clicked.connect(self._guardar_visita)

        btn_nueva_visita = QPushButton("🧹 Limpiar Visita")
        btn_nueva_visita.setObjectName("btnSecondary")
        btn_nueva_visita.clicked.connect(self._limpiar_visita_form)

        btn_del_visita = QPushButton("🗑 Eliminar Visita")
        btn_del_visita.setObjectName("btnDanger")
        btn_del_visita.clicked.connect(self._eliminar_visita)

        v_btns.addWidget(self.btn_guardar_visita)
        v_btns.addWidget(btn_nueva_visita)
        v_btns.addWidget(btn_del_visita)
        v_btns.addStretch()
        lay.addLayout(v_btns)

        # Tabla cronológica de visitas del paciente
        lay.addWidget(self._lbl_bold("Historial Cronológico de Visitas y Notas:"))
        self.tabla_visitas = QTableWidget(0, 6)
        self.tabla_visitas.setHorizontalHeaderLabels([
            "Fecha", "Hora", "Tipo", "Evolución / Detalles", "Recordatorio", "ID"
        ])
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.tabla_visitas.setColumnHidden(5, True)
        self.tabla_visitas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_visitas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_visitas.setAlternatingRowColors(True)
        self.tabla_visitas.verticalHeader().setVisible(False)
        self.tabla_visitas.setMinimumHeight(160)
        self.tabla_visitas.itemDoubleClicked.connect(self._cargar_visita_click)
        lay.addWidget(self.tabla_visitas, 1)

        scroll.setWidget(w)
        return scroll

    # ══════════════════════════════════════════════════════════
    # LÓGICA Y PERSISTENCIA
    # ══════════════════════════════════════════════════════════

    def _actualizar_edad(self, fnac: QDate):
        """Calcula la edad automáticamente a partir de la fecha de nacimiento."""
        hoy = QDate.currentDate()
        edad = hoy.year() - fnac.year()
        if (hoy.month(), hoy.day()) < (fnac.month(), fnac.day()):
            edad -= 1
        self.input_edad.setText(str(max(0, edad)))

    def load_data(self):
        """Carga historias clínicas y pacientes desde Firebase."""
        historias = []
        if hasattr(self.db, "obtener_historias_clinicas"):
            try:
                historias = self.db.obtener_historias_clinicas()
            except Exception as e:
                print(f"[WARN] Error cargando historias: {e}")
                historias = []
        elif hasattr(self.db, "_db") and self.db._db:
            try:
                docs = self.db._db.collection("historias_clinicas").stream()
                historias = [d.to_dict() | {"id": d.id} for d in docs]
            except Exception:
                historias = []

        pacientes = []
        if hasattr(self.db, "obtener_pacientes"):
            try:
                pacientes = self.db.obtener_pacientes()
            except Exception as e:
                print(f"[WARN] Error cargando pacientes en historias: {e}")
                pacientes = []

        sesiones = []
        if hasattr(self.db, "obtener_sesiones"):
            try:
                sesiones = self.db.obtener_sesiones()
            except Exception as e:
                print(f"[WARN] Error cargando sesiones en historias: {e}")
                sesiones = []

        citas = []
        if hasattr(self.db, "obtener_citas"):
            try:
                citas = self.db.obtener_citas()
            except Exception as e:
                print(f"[WARN] Error cargando citas en historias: {e}")
                citas = []

        recetas = []
        if hasattr(self.db, "obtener_todas_recetas"):
            try:
                recetas = self.db.obtener_todas_recetas()
            except Exception as e:
                print(f"[WARN] Error cargando recetas en historias: {e}")
                recetas = []

        self._historias_cache = historias
        self._pacientes_cache = pacientes
        self._sesiones_cache = sesiones
        self._citas_cache = citas
        self._recetas_cache = recetas
        self._cargar_catalogo_condiciones()
        self._poblar_combo_pacientes()
        self._actualizar_opciones_filtros()
        self._poblar_tabla(historias)
        self._filtrar_tabla()
        if self._paciente_id or self.input_cedula.text().strip():
            ced_num = self.input_cedula.text().strip()
            ced_full = f"{self.combo_tipo_cedula.currentText()}{ced_num}" if ced_num else ""
            self._actualizar_estado_visitas_paciente(
                self._paciente_id, ced_full, auto_set_primera_vez=False
            )

    def _cargar_catalogo_condiciones(self):
        """Carga condiciones estándar + personalizadas desde Firestore e historias existentes."""
        condiciones = list(DEFAULT_CONDICIONES_CLINICAS)
        extras = []
        if hasattr(self.db, "obtener_condiciones_clinicas"):
            try:
                extras.extend(self.db.obtener_condiciones_clinicas())
            except Exception:
                pass
        for h in self._historias_cache:
            pat = (h.get("patologia", "") or "").strip()
            if pat:
                extras.append(pat)

        existentes_lower = {c.lower() for c in condiciones}
        for e in sorted(set(extras), key=str.lower):
            if e and e.lower() not in existentes_lower:
                condiciones.append(e)
                existentes_lower.add(e.lower())

        prev_sel = self.combo_patologia.currentText() if hasattr(self, "combo_patologia") else "Sin especificar"
        if hasattr(self, "combo_patologia"):
            self.combo_patologia.blockSignals(True)
            self.combo_patologia.clear()
            self.combo_patologia.addItems(condiciones)
            idx = self.combo_patologia.findText(prev_sel)
            self.combo_patologia.setCurrentIndex(max(0, idx))
            self.combo_patologia.blockSignals(False)

        if hasattr(self, "combo_filtro_patologia"):
            prev_f = self.combo_filtro_patologia.currentText()
            self.combo_filtro_patologia.blockSignals(True)
            self.combo_filtro_patologia.clear()
            self.combo_filtro_patologia.addItems(["Condición / IPX: Todas"] + condiciones)
            idx_f = self.combo_filtro_patologia.findText(prev_f)
            self.combo_filtro_patologia.setCurrentIndex(max(0, idx_f))
            self.combo_filtro_patologia.blockSignals(False)

    def _agregar_nueva_patologia(self):
        """Permite crear una nueva condición/patología y guardarla en el catálogo."""
        nombre, ok = QInputDialog.getText(
            self,
            "Nueva Condición / Patología",
            "Escribe el nombre de la nueva condición o diagnóstico (ej: Discalculia, TOC):"
        )
        if not ok:
            return
        nombre = " ".join(nombre.strip().split())
        if len(nombre) < 2 or len(nombre) > 80:
            QMessageBox.warning(
                self, "Nombre inválido", "El nombre debe tener entre 2 y 80 caracteres."
            )
            return

        idx_dup = self.combo_patologia.findText(nombre, Qt.MatchFlag.MatchFixedString)
        if idx_dup >= 0:
            self.combo_patologia.setCurrentIndex(idx_dup)
            QMessageBox.information(self, "Aviso", f"'{nombre}' ya existe en el catálogo; ha sido seleccionado.")
            return

        if hasattr(self.db, "crear_condicion_clinica"):
            self.db.crear_condicion_clinica(nombre)

        self.combo_patologia.addItem(nombre)
        self.combo_patologia.setCurrentIndex(self.combo_patologia.count() - 1)
        if hasattr(self, "combo_filtro_patologia"):
            self.combo_filtro_patologia.addItem(nombre)
        QMessageBox.information(self, "✅ Agregado", f"Condición '{nombre}' agregada al catálogo.")
        if self._paciente_id or self.input_cedula.text().strip():
            self._actualizar_estado_visitas_paciente(
                self._paciente_id, self.input_cedula.text().strip()
            )

    def _poblar_combo_pacientes(self, filtro: str = ""):
        """Rellena el selector de pacientes registrados (opcionalmente filtrado)."""
        prev_pid = self._paciente_id
        q = (filtro or "").strip().lower()
        self._syncing_combo = True
        self.combo_paciente.clear()
        self.combo_paciente.addItem("-- Seleccionar paciente registrado --", "")
        for p in sorted(self._pacientes_cache, key=lambda x: x.get("nombre", "").lower()):
            ced = p.get("cedula", "S/C")
            nom = p.get("nombre", "")
            if q and (q not in ced.lower() and q not in nom.lower()):
                continue
            pnf = p.get("pnf", "")
            etiqueta = f"{ced} — {nom}" + (f" ({pnf})" if pnf and pnf != "No aplica / Externo" else "")
            self.combo_paciente.addItem(etiqueta, p.get("id", ""))
        if prev_pid:
            idx = self.combo_paciente.findData(prev_pid)
            if idx >= 0:
                self.combo_paciente.setCurrentIndex(idx)
        self._syncing_combo = False

    def _filtrar_combo_pacientes(self, text: str):
        """Filtra la lista desplegable de pacientes sin perder la selección actual."""
        self._poblar_combo_pacientes(text)

    def _actualizar_opciones_filtros(self):
        """Actualiza dinámicamente secciones y años en los filtros de Historia Clínica."""
        secciones = set()
        anios = set()
        for h in self._historias_cache:
            acad = self._resolver_datos_academicos(h)
            if acad["seccion"]:
                secciones.add(acad["seccion"])
            if acad["anio_academico"]:
                anios.add(acad["anio_academico"])
        for p in self._pacientes_cache:
            sec = normalize_seccion(p.get("seccion", ""))
            if sec:
                secciones.add(sec)
            anio = str(p.get("anio_academico", "")).strip()
            if anio:
                anios.add(anio)

        prev_s = self.combo_filtro_sec.currentText()
        self.combo_filtro_sec.blockSignals(True)
        self.combo_filtro_sec.clear()
        self.combo_filtro_sec.addItems(["Todas Secc.", "Sin asignar"] + sorted(secciones))
        idx_s = self.combo_filtro_sec.findText(prev_s)
        self.combo_filtro_sec.setCurrentIndex(max(0, idx_s))
        self.combo_filtro_sec.blockSignals(False)

        prev_a = self.combo_filtro_anio.currentText()
        self.combo_filtro_anio.blockSignals(True)
        self.combo_filtro_anio.clear()
        self.combo_filtro_anio.addItems(["Todos Años", "Sin asignar"] + sorted(anios, reverse=True))
        idx_a = self.combo_filtro_anio.findText(prev_a)
        self.combo_filtro_anio.setCurrentIndex(max(0, idx_a))
        self.combo_filtro_anio.blockSignals(False)

    def _resolver_datos_academicos(self, h: dict) -> dict:
        """Obtiene PNF, Trayecto, Sección y Año desde el paciente vinculado o desde la historia."""
        pid = h.get("paciente_id", "")
        ced = (h.get("cedula", "") or "").strip().lower()
        pac = None
        if pid:
            pac = next((p for p in self._pacientes_cache if p.get("id") == pid), None)
        if not pac and ced:
            pac = next((p for p in self._pacientes_cache if (p.get("cedula", "") or "").strip().lower() == ced), None)
        src = pac if pac else h
        return {
            "pnf": src.get("pnf", "") or "",
            "trayecto": src.get("trayecto", "") or "",
            "seccion": normalize_seccion(src.get("seccion", "")),
            "anio_academico": str(src.get("anio_academico", "") or "").strip(),
        }

    def _actualizar_badge_academico(self, pac: dict | None):
        """Muestra el resumen académico del paciente vinculado."""
        if not pac:
            self.lbl_paciente_acad.setText("Sin paciente vinculado")
            return
        pnf = pac.get("pnf", "") or "Sin asignar"
        if pnf == "No aplica / Externo":
            self.lbl_paciente_acad.setText("👤 Externo / No aplica")
            return
        partes = [pnf]
        if pac.get("trayecto"):
            partes.append(pac["trayecto"])
        if pac.get("seccion"):
            partes.append(f"Secc. {pac['seccion']}")
        if pac.get("anio_academico"):
            partes.append(str(pac["anio_academico"]))
        self.lbl_paciente_acad.setText("🎓 " + " · ".join(partes))

    def seleccionar_paciente_por_id(self, paciente_id: str):
        """Selecciona un paciente por ID (llamado desde Identificación o desde el combo)."""
        if not paciente_id:
            return
        self._poblar_combo_pacientes()
        idx = self.combo_paciente.findData(paciente_id)
        if idx >= 0:
            self._syncing_combo = True
            self.combo_paciente.setCurrentIndex(idx)
            self._syncing_combo = False
            self._cargar_o_preparar_paciente(paciente_id)
            if hasattr(self, "main_tabs"):
                self.main_tabs.setCurrentIndex(1)

    def _on_paciente_seleccionado(self, index: int):
        """Maneja la selección de un paciente en el combo superior."""
        if self._syncing_combo or index < 0:
            return
        pid = self.combo_paciente.itemData(index)
        if not pid:
            return
        self._cargar_o_preparar_paciente(pid)

    def _cargar_o_preparar_paciente(self, pid: str):
        """Si el paciente ya tiene historia (1 a 1), la carga para editar; si no, autocompleta datos."""
        pac = next((p for p in self._pacientes_cache if p.get("id") == pid), None)
        if not pac:
            return

        ced_pac = (pac.get("cedula", "") or "").strip().lower()
        existente = next(
            (
                h for h in self._historias_cache
                if h.get("paciente_id") == pid
                or (ced_pac and (h.get("cedula", "") or "").strip().lower() == ced_pac)
            ),
            None,
        )
        if existente:
            self._cargar_historia_dict(existente)
            self._paciente_id = pid
            self._actualizar_badge_academico(pac)
            self.form_title.setText(
                f"Expediente N° {existente.get('num_historia', '')} — {pac.get('nombre', '')} (Historia existente)"
            )
            return

        # Paciente sin historia previa: limpiar y autocompletar datos de identificación
        self.clear_form(keep_combo=True)
        self._paciente_id = pid
        self._actualizar_badge_academico(pac)
        self.form_title.setText(f"Nueva Historia Clínica — {pac.get('nombre', '')}")

        self.input_nombre.setText(pac.get("nombre", ""))
        idx_sexo = self.combo_sexo.findText(pac.get("sexo", "Masculino"))
        self.combo_sexo.setCurrentIndex(max(0, idx_sexo))

        ced = pac.get("cedula", "")
        if "-" in ced:
            pref, num = ced.split("-", 1)
            idx_p = self.combo_tipo_cedula.findText(f"{pref}-")
            self.combo_tipo_cedula.setCurrentIndex(max(0, idx_p))
            self.input_cedula.setText(num)
        else:
            self.input_cedula.setText(ced)

        fnac = pac.get("fecha_nac", "")
        if fnac:
            d = QDate.fromString(fnac, "dd/MM/yyyy")
            if d.isValid():
                self.input_fecha_nac.setDate(d)
        if pac.get("edad"):
            self.input_edad.setText(str(pac.get("edad")))

        tel = pac.get("telefono", "")
        if "-" in tel:
            p, n = tel.split("-", 1)
            idx_t = self.combo_prefijo_tel.findText(p)
            self.combo_prefijo_tel.setCurrentIndex(max(0, idx_t))
            self.input_telefono.setText(n)
        else:
            self.input_telefono.setText(tel)

        self.input_direccion.setText(pac.get("domicilio", ""))
        if pac.get("otros_datos"):
            self.input_motivo.setPlainText(pac.get("otros_datos", ""))
        self._generar_codigo_historia_actual(pac)
        self._actualizar_estado_visitas_paciente(pid, pac.get("cedula", ""))

    def _generar_codigo_historia_actual(self, pac: dict | None = None):
        """Genera un código único de historia clínica usando PNF, año y cédula."""
        if pac is None and self._paciente_id:
            pac = next((p for p in self._pacientes_cache if p.get("id") == self._paciente_id), None)
        pnf = pac.get("pnf", "") if pac else ""
        anio = str(pac.get("anio_academico", "") or QDate.currentDate().year()) if pac else str(QDate.currentDate().year())
        ced = pac.get("cedula", "") if pac else self.input_cedula.text().strip()
        codigo = generar_codigo_historia(
            pnf=pnf, cedula=ced, anio=anio, correlativo=len(self._historias_cache) + 1
        )
        self.input_num_historia.setText(codigo)

    def _obtener_visitas_paciente(self, pid: str | None, cedula: str = "") -> list:
        """Retorna las sesiones/visitas del paciente ordenadas de la más reciente a la más antigua."""
        ced_norm = (cedula or "").strip().lower()
        visitas = []
        for s in self._sesiones_cache:
            s_pid = s.get("paciente_id", "")
            s_ced = (s.get("paciente_cedula", "") or "").strip().lower()
            if (pid and s_pid == pid) or (ced_norm and s_ced == ced_norm):
                visitas.append(s)

        def _sort_key(v):
            d = QDate.fromString(v.get("fecha", ""), "dd/MM/yyyy")
            t = QTime.fromString(v.get("hora", "00:00"), "HH:mm")
            return (d.toString("yyyyMMdd") if d.isValid() else "00000000", t.toString("HHmm") if t.isValid() else "0000")

        visitas.sort(key=_sort_key, reverse=True)
        return visitas

    def _actualizar_estado_visitas_paciente(self, pid: str | None, cedula: str = "", auto_set_primera_vez: bool = True):
        """Detecta automáticamente Primera vez vs Sucesiva y actualiza la 6ta pestaña."""
        visitas = self._obtener_visitas_paciente(pid, cedula)
        tiene_historia = bool(self._historia_id)
        if not tiene_historia and (pid or cedula):
            ced_norm = (cedula or "").strip().lower()
            tiene_historia = any(
                (pid and h.get("paciente_id") == pid)
                or (ced_norm and (h.get("cedula", "") or "").strip().lower() == ced_norm)
                for h in self._historias_cache
            )

        es_primera = (not tiene_historia) and (len(visitas) == 0)
        if auto_set_primera_vez:
            self.chk_primera_vez.setChecked(es_primera)

        if es_primera:
            self.lbl_estado_visita.setText("🆕 Primera consulta")
            self.lbl_estado_visita.setStyleSheet(
                "font-size: 12px; font-weight: bold; color: #047857; "
                "background: #ecfdf5; border: 1px solid #a7f3d0; "
                "border-radius: 10px; padding: 3px 10px;"
            )
            if hasattr(self, "visita_tipo"):
                self.visita_tipo.setCurrentText("Primera vez")
        else:
            n_visita = len(visitas) + 1
            self.lbl_estado_visita.setText(f"🔄 Consulta sucesiva (Visita N° {n_visita})")
            self.lbl_estado_visita.setStyleSheet(
                "font-size: 12px; font-weight: bold; color: #1d4ed8; "
                "background: #eff6ff; border: 1px solid #bfdbfe; "
                "border-radius: 10px; padding: 3px 10px;"
            )
            if hasattr(self, "visita_tipo"):
                self.visita_tipo.setCurrentText("Sucesiva")

        if not hasattr(self, "tabla_visitas"):
            return

        # Poblar tabla cronológica de visitas
        self.tabla_visitas.setRowCount(0)
        for i, v in enumerate(visitas):
            self.tabla_visitas.insertRow(i)
            self.tabla_visitas.setItem(i, 0, QTableWidgetItem(v.get("fecha", "—")))
            self.tabla_visitas.setItem(i, 1, QTableWidgetItem(v.get("hora", "—")))
            self.tabla_visitas.setItem(i, 2, QTableWidgetItem(v.get("tipo", "Sucesiva")))
            self.tabla_visitas.setItem(i, 3, QTableWidgetItem(v.get("evolucion", v.get("notas", ""))))
            self.tabla_visitas.setItem(i, 4, QTableWidgetItem(v.get("nota_recordatorio", "")))
            self.tabla_visitas.setItem(i, 5, QTableWidgetItem(v.get("id", "")))

        # Resumen de última visita y recordatorio
        if visitas:
            ult = visitas[0]
            f_ult = ult.get("fecha", "—")
            d_ult = QDate.fromString(f_ult, "dd/MM/yyyy")
            dias_txt = ""
            if d_ult.isValid():
                dias = d_ult.daysTo(QDate.currentDate())
                dias_txt = " (hoy)" if dias == 0 else (f" (hace {dias} día(s))" if dias > 0 else "")
            self.lbl_ultima_visita.setText(f"🕒 Última visita: {f_ult}{dias_txt} · {len(visitas)} visita(s)")
            rec = ult.get("nota_recordatorio", "").strip()
            if rec:
                self.lbl_recordatorio_pendiente.setText(f"📌 Recordatorio de la visita ({f_ult}): {rec}")
            else:
                evo = ult.get("evolucion", ult.get("notas", "")).strip()
                self.lbl_recordatorio_pendiente.setText(
                    f"📝 Última nota ({f_ult}): {evo[:140]}" if evo else "📌 Recordatorio pendiente: Ninguno"
                )
        else:
            self.lbl_ultima_visita.setText("🕒 Última visita: Sin visitas registradas aún")
            self.lbl_recordatorio_pendiente.setText("📌 Recordatorio pendiente: Ninguno")

        # Próxima cita en Agenda (y nota de cita si existe)
        hoy = QDate.currentDate()
        citas_fut = []
        for c in self._citas_cache:
            if c.get("estado") in ("Cancelada", "Completada"):
                continue
            if pid and c.get("paciente_id") != pid:
                continue
            dc = QDate.fromString(c.get("fecha", ""), "dd/MM/yyyy")
            if dc.isValid() and dc >= hoy:
                citas_fut.append((dc, c))
        citas_fut.sort(key=lambda x: x[0])
        if citas_fut:
            _, prox = citas_fut[0]
            nota_c = f" · Nota: {prox.get('notas')}" if prox.get("notas") else ""
            self.lbl_proxima_cita.setText(
                f"📅 Próxima cita: {prox.get('fecha', '')} {prox.get('hora', '')} ({prox.get('estado', '')}){nota_c}"
            )
        else:
            self.lbl_proxima_cita.setText("📅 Próxima cita: Ninguna programada")

        # Medicación / Recetas activas desde Fármacos
        if hasattr(self, "lbl_medicacion_activa"):
            recetas_activas = [
                r for r in self._recetas_cache
                if pid and r.get("paciente_id") == pid
                and r.get("estado_tratamiento", "Activo") == "Activo"
            ]
            if recetas_activas:
                items = [
                    f"{r.get('nombre_comercial') or r.get('nombre_generico')} ({r.get('recetacion_dosis', '').splitlines()[0][:45]})"
                    for r in recetas_activas[:3]
                ]
                self.lbl_medicacion_activa.setText(
                    "💊 Medicación / Recetas activas: " + "  ·  ".join(items)
                )
            else:
                self.lbl_medicacion_activa.setText(
                    "💊 Medicación / Recetas activas: Sin medicación registrada"
                )

    def _poblar_tabla(self, historias: list):
        self.table.setRowCount(0)
        for i, h in enumerate(historias):
            self.table.insertRow(i)
            acad = self._resolver_datos_academicos(h)
            visitas = self._obtener_visitas_paciente(h.get("paciente_id"), h.get("cedula", ""))
            ult_fecha = visitas[0].get("fecha", "—") if visitas else "—"
            self.table.setItem(i, 0, QTableWidgetItem(h.get("num_historia", f"HC-{i+1:03d}")))
            self.table.setItem(i, 1, QTableWidgetItem(h.get("cedula", "—")))
            self.table.setItem(i, 2, QTableWidgetItem(h.get("nombre", "—")))
            self.table.setItem(i, 3, QTableWidgetItem(acad["pnf"] or "Sin asignar"))
            self.table.setItem(i, 4, QTableWidgetItem(acad["trayecto"] or "—"))
            self.table.setItem(i, 5, QTableWidgetItem(acad["seccion"] or "—"))
            self.table.setItem(i, 6, QTableWidgetItem(acad["anio_academico"] or "—"))
            self.table.setItem(i, 7, QTableWidgetItem(h.get("patologia", "") or "Sin especificar"))
            self.table.setItem(i, 8, QTableWidgetItem(str(len(visitas))))
            self.table.setItem(i, 9, QTableWidgetItem(ult_fecha))
            self.table.setItem(i, 10, QTableWidgetItem(h.get("fecha_elaboracion", "—")))
            self.table.setItem(i, 11, QTableWidgetItem(h.get("id", "")))

        self.lbl_count.setText(f"{len(historias)} historia(s) registrada(s)")

    def _filtrar_tabla(self, *args):
        q = self.search_input.text().lower().strip()
        f_pnf = self.combo_filtro_pnf.currentText()
        f_tray = self.combo_filtro_tray.currentText()
        f_sec = self.combo_filtro_sec.currentText()
        f_anio = self.combo_filtro_anio.currentText()
        f_pat = self.combo_filtro_patologia.currentText() if hasattr(self, "combo_filtro_patologia") else "Condición / IPX: Todas"
        f_tipo = self.combo_filtro_tipo.currentText()
        usar_fecha = self.chk_filtro_fecha.isChecked()
        f_desde = self.date_filtro_desde.date()
        f_hasta = self.date_filtro_hasta.date()

        visibles = 0
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 11)
            hist_id = id_item.text() if id_item else ""
            h = next((x for x in self._historias_cache if x.get("id") == hist_id), {})

            num = self.table.item(row, 0).text().lower() if self.table.item(row, 0) else ""
            ced = self.table.item(row, 1).text().lower() if self.table.item(row, 1) else ""
            nom = self.table.item(row, 2).text().lower() if self.table.item(row, 2) else ""

            ok = (not q) or (q in num) or (q in ced) or (q in nom)
            if ok:
                acad = self._resolver_datos_academicos(h)
                if f_pnf == "Sin asignar":
                    ok = not acad["pnf"]
                elif f_pnf != "Todos PNF":
                    ok = acad["pnf"] == f_pnf

                if ok:
                    if f_tray == "Sin asignar":
                        ok = not acad["trayecto"]
                    elif f_tray != "Todos Tray.":
                        ok = acad["trayecto"] == f_tray

                if ok:
                    if f_sec == "Sin asignar":
                        ok = not acad["seccion"]
                    elif f_sec != "Todas Secc.":
                        ok = acad["seccion"] == f_sec

                if ok:
                    if f_anio == "Sin asignar":
                        ok = not acad["anio_academico"]
                    elif f_anio != "Todos Años":
                        ok = acad["anio_academico"] == f_anio

                if ok and f_pat != "Condición / IPX: Todas":
                    pat_h = (h.get("patologia", "") or "Sin especificar").strip()
                    ok = pat_h == f_pat

                if ok and f_tipo != "Consulta: Todas":
                    primera = bool(h.get("primera_vez", True))
                    ok = primera if f_tipo == "Primera vez" else (not primera)

                if ok and usar_fecha:
                    d_elab = QDate.fromString(h.get("fecha_elaboracion", ""), "dd/MM/yyyy")
                    ok = d_elab.isValid() and (f_desde <= d_elab <= f_hasta)

            self.table.setRowHidden(row, not ok)
            if ok:
                visibles += 1

        total = len(self._historias_cache)
        if visibles == total:
            self.lbl_count.setText(f"{total} historia(s) registrada(s)")
        else:
            self.lbl_count.setText(f"Mostrando {visibles} de {total} historia(s)")

    def _limpiar_filtros(self):
        for w in (
            self.combo_filtro_pnf, self.combo_filtro_tray,
            self.combo_filtro_sec, self.combo_filtro_anio,
            self.combo_filtro_patologia, self.combo_filtro_tipo
        ):
            w.blockSignals(True)
            w.setCurrentIndex(0)
            w.blockSignals(False)
        self.chk_filtro_fecha.blockSignals(True)
        self.chk_filtro_fecha.setChecked(False)
        self.chk_filtro_fecha.blockSignals(False)
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        self._filtrar_tabla()

    def _abrir_historia_seleccionada(self):
        """Abre en la pestaña de Expediente la fila seleccionada de la tabla."""
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selección", "Selecciona una historia clínica de la tabla para abrirla.")
            return
        self._cargar_historia_click(self.table.item(rows[0].row(), 0))

    def _cargar_historia_click(self, item):
        row = item.row()
        id_item = self.table.item(row, 11)
        if not id_item:
            return
        hist_id = id_item.text()
        h = next((x for x in self._historias_cache if x.get("id") == hist_id), None)
        if not h:
            return
        self._cargar_historia_dict(h)
        if hasattr(self, "main_tabs"):
            self.main_tabs.setCurrentIndex(1)

    def _cargar_historia_dict(self, h: dict):
        """Carga los datos de una historia clínica en el formulario."""
        self._historia_id = h.get("id")
        self._paciente_id = h.get("paciente_id") or None

        # Sincronizar combo superior con paciente vinculado
        pac = None
        if self._paciente_id:
            pac = next((p for p in self._pacientes_cache if p.get("id") == self._paciente_id), None)
        if not pac and h.get("cedula"):
            ced_h = h.get("cedula", "").strip().lower()
            pac = next((p for p in self._pacientes_cache if (p.get("cedula", "") or "").strip().lower() == ced_h), None)
            if pac:
                self._paciente_id = pac.get("id")

        self._syncing_combo = True
        if self._paciente_id:
            idx = self.combo_paciente.findData(self._paciente_id)
            self.combo_paciente.setCurrentIndex(idx if idx >= 0 else 0)
        else:
            self.combo_paciente.setCurrentIndex(0)
        self._syncing_combo = False
        self._actualizar_badge_academico(pac)

        self.form_title.setText(f"Expediente N° {h.get('num_historia', '')} — {h.get('nombre', '')}")
        self.btn_guardar.setText("💾 Actualizar Historia")
        self._actualizar_estado_visitas_paciente(
            self._paciente_id, h.get("cedula", ""), auto_set_primera_vez=False
        )

        # Cargar campos de cabecera
        self.input_num_historia.setText(h.get("num_historia", ""))
        self.input_nombre.setText(h.get("nombre", ""))
        idx_sexo = self.combo_sexo.findText(h.get("sexo", "Masculino"))
        self.combo_sexo.setCurrentIndex(max(0, idx_sexo))

        cedula_str = h.get("cedula", "")
        if "-" in cedula_str:
            pref, num = cedula_str.split("-", 1)
            idx_p = self.combo_tipo_cedula.findText(f"{pref}-")
            self.combo_tipo_cedula.setCurrentIndex(max(0, idx_p))
            self.input_cedula.setText(num)
        else:
            self.input_cedula.setText(cedula_str)

        self.input_edad.setText(str(h.get("edad", "")))
        self.chk_primera_vez.setChecked(h.get("primera_vez", True))

        if h.get("fecha_elaboracion"):
            d = QDate.fromString(h.get("fecha_elaboracion"), "dd/MM/yyyy")
            if d.isValid():
                self.input_fecha_elab.setDate(d)

        # Tab 1
        if h.get("fecha_ingreso"):
            d_ing = QDate.fromString(h.get("fecha_ingreso"), "dd/MM/yyyy")
            if d_ing.isValid(): self.input_fecha_ingreso.setDate(d_ing)
        if h.get("fecha_egreso"):
            d_eg = QDate.fromString(h.get("fecha_egreso"), "dd/MM/yyyy")
            if d_eg.isValid(): self.input_fecha_egreso.setDate(d_eg)

        self.input_lugar_nac.setText(h.get("lugar_nacimiento", ""))
        if h.get("fecha_nacimiento"):
            d_nac = QDate.fromString(h.get("fecha_nacimiento"), "dd/MM/yyyy")
            if d_nac.isValid(): self.input_fecha_nac.setDate(d_nac)

        tel = h.get("telefono", "")
        if "-" in tel:
            p, n = tel.split("-", 1)
            idx_tel = self.combo_prefijo_tel.findText(p)
            self.combo_prefijo_tel.setCurrentIndex(max(0, idx_tel))
            self.input_telefono.setText(n)
        else:
            self.input_telefono.setText(tel)

        self.input_direccion.setText(h.get("direccion", ""))
        idx_ins = self.combo_instruccion.findText(h.get("nivel_instruccion", ""))
        self.combo_instruccion.setCurrentIndex(max(0, idx_ins))
        self.input_ocupacion.setText(h.get("ocupacion", ""))
        self.input_religion.setText(h.get("creencias_religiosas", ""))
        self.input_entorno_familiar.setPlainText(h.get("entorno_familiar", ""))
        self.input_referencias.setText(h.get("referencias", ""))

        # Tab 2
        self.input_motivo.setPlainText(h.get("motivo_consulta", ""))
        self.input_ant_no_patologicos.setPlainText(h.get("ant_no_patologicos", ""))
        self.input_ant_patologicos.setPlainText(h.get("ant_patologicos", ""))
        self.input_ant_heredo_mentales.setPlainText(h.get("ant_heredo_mentales", ""))
        self.input_gestas_perdidas.setText(h.get("gestas_perdidas", ""))
        self.input_atencion_psic_previa.setText(h.get("atencion_psicologica_previa", ""))
        self.input_eval_especialidades.setPlainText(h.get("evaluaciones_especialidad", ""))

        # Tab 3: Representante con campos independientes
        self.input_rep_nombre.setText(h.get("rep_nombre", ""))
        rep_ced = h.get("rep_cedula", "")
        if "-" in rep_ced:
            p, n = rep_ced.split("-", 1)
            idx_p = self.combo_rep_tipo_cedula.findText(f"{p}-")
            self.combo_rep_tipo_cedula.setCurrentIndex(max(0, idx_p))
            self.input_rep_cedula.setText(n)
        else:
            self.input_rep_cedula.setText(rep_ced)

        self.input_rep_edad.setText(str(h.get("rep_edad", "")))

        rep_tel = h.get("rep_telefono", "")
        if "-" in rep_tel:
            p, n = rep_tel.split("-", 1)
            idx_rep_tel = self.combo_rep_prefijo.findText(p)
            self.combo_rep_prefijo.setCurrentIndex(max(0, idx_rep_tel))
            self.input_rep_telefono.setText(n)
        else:
            self.input_rep_telefono.setText(rep_tel)

        idx_rep_ins = self.combo_rep_instruccion.findText(h.get("rep_instruccion", ""))
        self.combo_rep_instruccion.setCurrentIndex(max(0, idx_rep_ins))
        self.input_rep_ocupacion.setText(h.get("rep_ocupacion", ""))
        self.input_rep_infancia.setPlainText(h.get("rep_infancia", ""))
        self.input_rep_adultez.setPlainText(h.get("rep_adultez", ""))
        self.input_rep_etapa_amorosa.setPlainText(h.get("rep_etapa_amorosa", ""))

        # Tab 4
        self.input_pregunta_feliz.setPlainText(h.get("pregunta_feliz", ""))
        self.input_pregunta_modificar.setPlainText(h.get("pregunta_modificar", ""))
        self.input_pregunta_futuro.setPlainText(h.get("pregunta_futuro", ""))

        # Tab 5
        self.input_cuadro_clinico.setPlainText(h.get("cuadro_clinico", ""))
        self.input_exploracion_fisica.setPlainText(h.get("exploracion_fisica", ""))
        self.input_habitos_exterior.setPlainText(h.get("habitos_exterior", ""))
        self.input_autonomia_motora.setPlainText(h.get("autonomia_motora", ""))
        self.input_etapa_prenatal.setPlainText(h.get("etapa_prenatal", ""))
        self.input_etapa_neonatal.setPlainText(h.get("etapa_neonatal", ""))
        self.input_desarrollo_psicomotor.setPlainText(h.get("desarrollo_psicomotor", ""))
        self.input_instrumentos_eval.setPlainText(h.get("instrumentos_evaluacion", ""))
        pat = (h.get("patologia", "") or "Sin especificar").strip()
        if hasattr(self, "combo_patologia"):
            idx_pat = self.combo_patologia.findText(pat)
            if idx_pat < 0 and pat:
                self.combo_patologia.addItem(pat)
                idx_pat = self.combo_patologia.count() - 1
            self.combo_patologia.setCurrentIndex(max(0, idx_pat))
        self.input_ipx.setPlainText(h.get("ipx", ""))

    def to_dict(self) -> dict:
        ced_num = self.input_cedula.text().strip()
        cedula_completa = f"{self.combo_tipo_cedula.currentText()}{ced_num}" if ced_num else ""
        tel_num = self.input_telefono.text().strip()
        tel_completo = f"{self.combo_prefijo_tel.currentText()}-{tel_num}" if tel_num else ""

        rep_ced_num = self.input_rep_cedula.text().strip()
        rep_cedula_completa = f"{self.combo_rep_tipo_cedula.currentText()}{rep_ced_num}" if rep_ced_num else ""
        rep_tel_num = self.input_rep_telefono.text().strip()
        rep_tel_completo = f"{self.combo_rep_prefijo.currentText()}-{rep_tel_num}" if rep_tel_num else ""

        pac = next((p for p in self._pacientes_cache if p.get("id") == self._paciente_id), None) if self._paciente_id else None

        return {
            "paciente_id":                self._paciente_id or "",
            "pnf":                        pac.get("pnf", "") if pac else "",
            "trayecto":                   pac.get("trayecto", "") if pac else "",
            "seccion":                    pac.get("seccion", "") if pac else "",
            "anio_academico":             str(pac.get("anio_academico", "")) if pac else "",
            "num_historia":               self.input_num_historia.text().strip(),
            "fecha_elaboracion":          self.input_fecha_elab.date().toString("dd/MM/yyyy"),
            "hora_elaboracion":           self.input_hora_elab.time().toString("HH:mm"),
            "primera_vez":                self.chk_primera_vez.isChecked(),
            "nombre":                     self.input_nombre.text().strip(),
            "sexo":                       self.combo_sexo.currentText(),
            "cedula":                     cedula_completa,
            "edad":                       self.input_edad.text().strip(),
            # Filiación
            "fecha_ingreso":              self.input_fecha_ingreso.date().toString("dd/MM/yyyy"),
            "fecha_egreso":               self.input_fecha_egreso.date().toString("dd/MM/yyyy"),
            "lugar_nacimiento":           self.input_lugar_nac.text().strip(),
            "fecha_nacimiento":           self.input_fecha_nac.date().toString("dd/MM/yyyy"),
            "telefono":                   tel_completo,
            "direccion":                  self.input_direccion.text().strip(),
            "nivel_instruccion":          self.combo_instruccion.currentText(),
            "ocupacion":                  self.input_ocupacion.text().strip(),
            "creencias_religiosas":       self.input_religion.text().strip(),
            "entorno_familiar":           self.input_entorno_familiar.toPlainText().strip(),
            "referencias":                self.input_referencias.text().strip(),
            # Antecedentes
            "motivo_consulta":            self.input_motivo.toPlainText().strip(),
            "ant_no_patologicos":         self.input_ant_no_patologicos.toPlainText().strip(),
            "ant_patologicos":            self.input_ant_patologicos.toPlainText().strip(),
            "ant_heredo_mentales":        self.input_ant_heredo_mentales.toPlainText().strip(),
            "gestas_perdidas":            self.input_gestas_perdidas.text().strip(),
            "atencion_psicologica_previa": self.input_atencion_psic_previa.text().strip(),
            "evaluaciones_especialidad":  self.input_eval_especialidades.toPlainText().strip(),
            # Representante (CAMPOS INDEPENDIENTES)
            "rep_nombre":                 self.input_rep_nombre.text().strip(),
            "rep_cedula":                 rep_cedula_completa,
            "rep_edad":                   self.input_rep_edad.text().strip(),
            "rep_telefono":               rep_tel_completo,
            "rep_edad_tel":               f"{self.input_rep_edad.text().strip()} años - {rep_tel_completo}".strip(" -"),
            "rep_instruccion":            self.combo_rep_instruccion.currentText(),
            "rep_ocupacion":              self.input_rep_ocupacion.text().strip(),
            "rep_infancia":               self.input_rep_infancia.toPlainText().strip(),
            "rep_adultez":                self.input_rep_adultez.toPlainText().strip(),
            "rep_etapa_amorosa":          self.input_rep_etapa_amorosa.toPlainText().strip(),
            # Emocional
            "pregunta_feliz":             self.input_pregunta_feliz.toPlainText().strip(),
            "pregunta_modificar":         self.input_pregunta_modificar.toPlainText().strip(),
            "pregunta_futuro":            self.input_pregunta_futuro.toPlainText().strip(),
            # Neurodesarrollo
            "cuadro_clinico":             self.input_cuadro_clinico.toPlainText().strip(),
            "exploracion_fisica":         self.input_exploracion_fisica.toPlainText().strip(),
            "habitos_exterior":           self.input_habitos_exterior.toPlainText().strip(),
            "autonomia_motora":           self.input_autonomia_motora.toPlainText().strip(),
            "etapa_prenatal":             self.input_etapa_prenatal.toPlainText().strip(),
            "etapa_neonatal":             self.input_etapa_neonatal.toPlainText().strip(),
            "desarrollo_psicomotor":      self.input_desarrollo_psicomotor.toPlainText().strip(),
            "instrumentos_evaluacion":    self.input_instrumentos_eval.toPlainText().strip(),
            "patologia":                  self.combo_patologia.currentText() if hasattr(self, "combo_patologia") else "Sin especificar",
            "ipx":                        self.input_ipx.toPlainText().strip(),
        }

    def save_data(self):
        """Valida y guarda la historia clínica en Firebase."""
        num_hist = self.input_num_historia.text().strip().upper()
        self.input_num_historia.setText(num_hist)
        ok_num, msg_num = validate_num_historia(num_hist)
        if not ok_num:
            QMessageBox.warning(self, "N° de Historia inválido", msg_num)
            self.input_num_historia.setFocus()
            return

        # Verificar que el N° de historia sea único
        dup_num = next(
            (
                h for h in self._historias_cache
                if (h.get("num_historia", "") or "").strip().upper() == num_hist
                and h.get("id") != self._historia_id
            ),
            None,
        )
        if dup_num:
            QMessageBox.warning(
                self,
                "N° de Historia duplicado",
                f"El código '{num_hist}' ya pertenece a {dup_num.get('nombre', 'otro paciente')}.\n"
                "Usa el botón ✨ para generar un código único."
            )
            self.input_num_historia.setFocus()
            return

        nombre = " ".join(self.input_nombre.text().strip().split())
        valido_nom, msg_nom = validate_person_name(nombre)
        if not valido_nom:
            QMessageBox.warning(self, "Nombre inválido", msg_nom)
            self.input_nombre.setFocus()
            return

        ced_num = self.input_cedula.text().strip()
        if ced_num:
            ok_ced, msg_ced = validate_cedula_num(ced_num)
            if not ok_ced:
                QMessageBox.warning(self, "Cédula inválida", msg_ced)
                self.input_cedula.setFocus()
                return

        ok_tel, msg_tel = validate_telefono_num(self.input_telefono.text().strip())
        if not ok_tel:
            QMessageBox.warning(self, "Teléfono inválido", msg_tel)
            self.input_telefono.setFocus()
            return

        datos = self.to_dict()

        # Sincronización bidireccional con Identificación (/pacientes)
        try:
            ced_completa = datos.get("cedula", "").strip()
            if not self._paciente_id and ced_completa:
                pac_match = next(
                    (
                        p for p in self._pacientes_cache
                        if (p.get("cedula", "") or "").strip().lower() == ced_completa.lower()
                    ),
                    None,
                )
                if pac_match:
                    self._paciente_id = pac_match.get("id")
                    datos["paciente_id"] = self._paciente_id

            paciente_payload = {
                "nombre": datos.get("nombre", ""),
                "cedula": ced_completa,
                "sexo": datos.get("sexo", "Masculino"),
                "fecha_nac": datos.get("fecha_nacimiento", ""),
                "edad": datos.get("edad", ""),
                "domicilio": datos.get("direccion", ""),
                "telefono": datos.get("telefono", ""),
                "motivo_consulta": datos.get("motivo_consulta", ""),
            }

            if self._paciente_id and hasattr(self.db, "actualizar_paciente"):
                self.db.actualizar_paciente(self._paciente_id, paciente_payload)
            elif not self._paciente_id and ced_completa and hasattr(self.db, "crear_paciente"):
                paciente_payload["pnf"] = "No aplica / Externo"
                paciente_payload["trayecto"] = ""
                paciente_payload["seccion"] = ""
                paciente_payload["anio_academico"] = ""
                nuevo_pid = self.db.crear_paciente(paciente_payload)
                if nuevo_pid:
                    self._paciente_id = nuevo_pid
                    datos["paciente_id"] = nuevo_pid
        except Exception as e_sync:
            print(f"[WARN] Sincronización paciente desde Historia: {e_sync}")

        # Regla 1 a 1: evitar duplicar historia si el paciente ya tiene una registrada
        if not self._historia_id:
            ced_actual = datos.get("cedula", "").strip().lower()
            existente = next(
                (
                    h for h in self._historias_cache
                    if (self._paciente_id and h.get("paciente_id") == self._paciente_id)
                    or (ced_actual and (h.get("cedula", "") or "").strip().lower() == ced_actual)
                ),
                None,
            )
            if existente:
                resp = QMessageBox.question(
                    self,
                    "Historia existente detectada",
                    f"Este paciente ya tiene la historia '{existente.get('num_historia', '')}' registrada.\n\n"
                    "¿Deseas actualizar esa historia existente con los datos actuales?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return
                self._historia_id = existente.get("id")

        try:
            if self._historia_id:
                if hasattr(self.db, "actualizar_historia_clinica"):
                    self.db.actualizar_historia_clinica(self._historia_id, datos)
                elif hasattr(self.db, "_db") and self.db._db:
                    self.db._db.collection("historias_clinicas").document(self._historia_id).update(datos)
                QMessageBox.information(self, "✅ Éxito", "Historia clínica actualizada correctamente.")
            else:
                # Inyectar user_id del médico en sesión
                uid = self.db.get_current_user_id()
                if not uid:
                    try:
                        from core.auth_manager import AuthManager
                        uid = AuthManager().get_uid()
                    except Exception:
                        pass
                datos["user_id"] = uid or ""
                if hasattr(self.db, "crear_historia_clinica"):
                    nuevo_id = self.db.crear_historia_clinica(datos)
                elif hasattr(self.db, "_db") and self.db._db:
                    ref = self.db._db.collection("historias_clinicas").add(datos)
                    nuevo_id = ref[1].id
                else:
                    nuevo_id = None
                self._historia_id = nuevo_id
                QMessageBox.information(self, "✅ Éxito", "Historia clínica registrada exitosamente.")

            self.load_data()
            if self._historia_id:
                self.historia_guardada.emit(self._historia_id)
            if self._paciente_id:
                self.paciente_sincronizado.emit(self._paciente_id)
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar la historia clínica:\n{e}")

    def _eliminar_historia(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selección", "Selecciona una historia clínica para eliminar.")
            return

        row = rows[0].row()
        id_item = self.table.item(row, 11)
        if not id_item or not id_item.text():
            return

        reply = QMessageBox.question(
            self, "Confirmar eliminación",
            "¿Estás seguro de eliminar esta historia clínica?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                hist_id = id_item.text()
                if hasattr(self.db, "eliminar_historia_clinica"):
                    self.db.eliminar_historia_clinica(hist_id)
                elif hasattr(self.db, "_db") and self.db._db:
                    self.db._db.collection("historias_clinicas").document(hist_id).delete()
                self.clear_form()
                self.load_data()
                QMessageBox.information(self, "✅", "Historia clínica eliminada.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    def imprimir_pdf(self):
        """Genera un PDF profesional con la Historia Clínica completa."""
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Incompleto", "Ingresa los datos del paciente antes de generar el PDF.")
            return

        try:
            from ui.dialogs.pdf_generator import generar_pdf_historia_clinica

            slug = nombre.replace(" ", "_")
            num = self.input_num_historia.text().strip() or "HC"
            fecha_str = self.input_fecha_elab.date().toString("yyyyMMdd")
            default_name = f"HistoriaClinica_{slug}_{num}_{fecha_str}.pdf"

            path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Historia Clínica PDF", default_name, "PDF (*.pdf)"
            )
            if path:
                datos = self.to_dict()
                generar_pdf_historia_clinica(path, datos)
                QMessageBox.information(self, "✅ PDF generado", f"Historia Clínica guardada exitosamente en:\n{path}")
        except ImportError:
            QMessageBox.warning(self, "Módulo no disponible", "ReportLab no está instalado. Ejecuta: pip install reportlab")
        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", str(e))

    def clear_form(self, keep_combo: bool = False):
        """Limpia todos los campos del formulario."""
        self._historia_id = None
        if not keep_combo:
            self._paciente_id = None
            self._syncing_combo = True
            if hasattr(self, "combo_paciente"):
                self.combo_paciente.setCurrentIndex(0)
            self._syncing_combo = False
            if hasattr(self, "lbl_paciente_acad"):
                self.lbl_paciente_acad.setText("Sin paciente vinculado")
        self.form_title.setText("Expediente de Historia Clínica")
        self.btn_guardar.setText("💾 Guardar Historia")

        # Generar sugerencia de N° correlativo
        proximo_n = len(self._historias_cache) + 1
        self.input_num_historia.setText(f"HC-{proximo_n:03d}")
        self.input_fecha_elab.setDate(QDate.currentDate())
        self.input_hora_elab.setTime(QTime.currentTime())
        self.chk_primera_vez.setChecked(True)

        self.input_nombre.clear()
        self.combo_sexo.setCurrentIndex(0)
        self.combo_tipo_cedula.setCurrentIndex(0)
        self.input_cedula.clear()
        self.input_edad.clear()

        # Tab 1
        self.input_fecha_ingreso.setDate(QDate.currentDate())
        self.input_fecha_egreso.setDate(QDate.currentDate().addMonths(6))
        self.input_lugar_nac.clear()
        self.input_fecha_nac.setDate(QDate.currentDate().addYears(-15))
        self.combo_prefijo_tel.setCurrentIndex(0)
        self.input_telefono.clear()
        self.input_direccion.clear()
        self.combo_instruccion.setCurrentIndex(0)
        self.input_ocupacion.clear()
        self.input_religion.clear()
        self.input_entorno_familiar.clear()
        self.input_referencias.clear()

        # Tab 2
        self.input_motivo.clear()
        self.input_ant_no_patologicos.clear()
        self.input_ant_patologicos.clear()
        self.input_ant_heredo_mentales.clear()
        self.input_gestas_perdidas.clear()
        self.input_atencion_psic_previa.clear()
        self.input_eval_especialidades.clear()

        # Tab 3 (Representante independiente)
        self.input_rep_nombre.clear()
        self.combo_rep_tipo_cedula.setCurrentIndex(0)
        self.input_rep_cedula.clear()
        self.input_rep_edad.clear()
        self.combo_rep_prefijo.setCurrentIndex(0)
        self.input_rep_telefono.clear()
        self.combo_rep_instruccion.setCurrentIndex(0)
        self.input_rep_ocupacion.clear()
        self.input_rep_infancia.clear()
        self.input_rep_adultez.clear()
        self.input_rep_etapa_amorosa.clear()

        # Tab 4
        self.input_pregunta_feliz.clear()
        self.input_pregunta_modificar.clear()
        self.input_pregunta_futuro.clear()

        # Tab 5
        self.input_cuadro_clinico.clear()
        self.input_exploracion_fisica.clear()
        self.input_habitos_exterior.clear()
        self.input_autonomia_motora.clear()
        self.input_etapa_prenatal.clear()
        self.input_etapa_neonatal.clear()
        self.input_desarrollo_psicomotor.clear()
        self.input_instrumentos_eval.clear()
        if hasattr(self, "combo_patologia"):
            self.combo_patologia.setCurrentIndex(0)
        self.input_ipx.clear()

        self.tabs.setCurrentIndex(0)
        if hasattr(self, "visita_evolucion"):
            self._limpiar_visita_form()
        if not keep_combo:
            self._actualizar_estado_visitas_paciente(None, "", auto_set_primera_vez=True)

    # ── Gestión de Visitas y Notas de Evolución (Pestaña 6) ────
    def _ir_a_agendar_cita(self):
        """Solicita abrir Agenda con el paciente actual preseleccionado."""
        if not self._paciente_id:
            QMessageBox.information(
                self,
                "Paciente requerido",
                "Primero selecciona o guarda un paciente para poder agendarle una cita."
            )
            return
        self.agendar_cita_requested.emit(self._paciente_id)

    def _ir_a_farmacos(self):
        """Solicita abrir Fármacos con el paciente actual preseleccionado."""
        if not self._paciente_id:
            QMessageBox.information(
                self,
                "Paciente requerido",
                "Primero selecciona o guarda un paciente para poder recetar fármacos."
            )
            return
        self.farmacos_requested.emit(self._paciente_id)

    def _limpiar_visita_form(self):
        self._visita_id = None
        if hasattr(self, "visita_fecha"):
            self.visita_fecha.setDate(QDate.currentDate())
            self.visita_hora.setTime(QTime.currentTime())
            self.visita_evolucion.clear()
            self.visita_recordatorio.clear()
            self.btn_guardar_visita.setText("➕ Guardar Visita")

    def _cargar_visita_click(self, item):
        row = item.row()
        id_item = self.tabla_visitas.item(row, 5)
        if not id_item:
            return
        vid = id_item.text()
        v = next((x for x in self._sesiones_cache if x.get("id") == vid), None)
        if not v:
            return
        self._visita_id = vid
        d = QDate.fromString(v.get("fecha", ""), "dd/MM/yyyy")
        if d.isValid():
            self.visita_fecha.setDate(d)
        t = QTime.fromString(v.get("hora", ""), "HH:mm")
        if t.isValid():
            self.visita_hora.setTime(t)
        idx_t = self.visita_tipo.findText(v.get("tipo", "Sucesiva"))
        self.visita_tipo.setCurrentIndex(max(0, idx_t))
        self.visita_evolucion.setPlainText(v.get("evolucion", v.get("notas", "")))
        self.visita_recordatorio.setText(v.get("nota_recordatorio", ""))
        self.btn_guardar_visita.setText("💾 Actualizar Visita")

    def _guardar_visita(self):
        """Guarda o actualiza una visita/nota adicional vinculada al paciente y su historia."""
        if not self._paciente_id and not self.input_nombre.text().strip():
            QMessageBox.warning(
                self,
                "Paciente requerido",
                "Selecciona un paciente o completa sus datos antes de registrar una visita."
            )
            return

        evolucion = self.visita_evolucion.toPlainText().strip()
        recordatorio = self.visita_recordatorio.text().strip()
        if not evolucion and not recordatorio:
            QMessageBox.warning(
                self,
                "Nota vacía",
                "Escribe la evolución de la visita o un recordatorio antes de guardar."
            )
            self.visita_evolucion.setFocus()
            return

        fecha_str = self.visita_fecha.date().toString("dd/MM/yyyy")
        hora_str = self.visita_hora.time().toString("HH:mm")
        ced_num = self.input_cedula.text().strip()
        ced_completa = f"{self.combo_tipo_cedula.currentText()}{ced_num}" if ced_num else ""

        # Anti-duplicación: evitar 2 visitas idénticas para el mismo paciente en misma fecha y hora
        if not self._visita_id:
            visitas_pac = self._obtener_visitas_paciente(self._paciente_id, ced_completa)
            dup = next(
                (v for v in visitas_pac if v.get("fecha") == fecha_str and v.get("hora") == hora_str),
                None,
            )
            if dup:
                QMessageBox.warning(
                    self,
                    "Visita duplicada",
                    f"Ya existe una visita registrada el {fecha_str} a las {hora_str} para este paciente."
                )
                return

        datos = {
            "paciente_id": self._paciente_id or "",
            "paciente_nombre": self.input_nombre.text().strip(),
            "paciente_cedula": ced_completa,
            "historia_id": self._historia_id or "",
            "fecha": fecha_str,
            "hora": hora_str,
            "tipo": self.visita_tipo.currentText(),
            "evolucion": evolucion,
            "notas": evolucion,
            "nota_recordatorio": recordatorio,
        }

        try:
            if self._visita_id and hasattr(self.db, "actualizar_sesion"):
                self.db.actualizar_sesion(self._visita_id, datos)
                QMessageBox.information(self, "✅", "Visita actualizada correctamente.")
            else:
                if hasattr(self.db, "crear_sesion"):
                    self.db.crear_sesion(datos)
                QMessageBox.information(self, "✅", "Visita agregada al historial del paciente.")
            self._limpiar_visita_form()
            self.load_data()
            self._actualizar_estado_visitas_paciente(self._paciente_id, ced_completa, auto_set_primera_vez=True)
            self.visita_actualizada.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la visita:\n{e}")

    def _eliminar_visita(self):
        rows = self.tabla_visitas.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selección", "Selecciona una visita de la tabla para eliminar.")
            return
        vid = self.tabla_visitas.item(rows[0].row(), 5).text()
        if not vid:
            return
        reply = QMessageBox.question(
            self, "Confirmar", "¿Eliminar esta visita del historial?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.db, "eliminar_sesion") and self.db.eliminar_sesion(vid):
                self._limpiar_visita_form()
                self.load_data()
                self._actualizar_estado_visitas_paciente(
                    self._paciente_id, self.input_cedula.text().strip(), auto_set_primera_vez=True
                )
                self.visita_actualizada.emit()
                QMessageBox.information(self, "✅", "Visita eliminada.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar la visita.")

    # ── Helpers UI ─────────────────────────────────────────────
    def _lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("font-size: 13px; font-weight: 600;")
        l.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        l.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        return l

    def _labeled_field(self, label: str, field: QWidget) -> QWidget:
        """Agrupa etiqueta + control para que no se separen al estrechar el panel."""
        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        row = QHBoxLayout(wrap)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)
        row.addWidget(self._lbl(label), 0)
        row.addWidget(field, 1)
        wrap.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return wrap

    def _lbl_bold(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("font-size: 13px; color: #2a72de; font-weight: 700; margin-top: 6px; margin-bottom: 2px;")
        return l

    @staticmethod
    def _sep() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet("background: #e2e8f0; max-height: 1.5px; border: none; margin: 4px 0;")
        return f
