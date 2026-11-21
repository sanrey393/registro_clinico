# ui/views/historia_clinica_view.py
# Módulo completo y profesional de Historia Clínica (Psicología y Neurodesarrollo)

import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QTextEdit, QComboBox, QDateEdit, QTimeEdit,
    QGridLayout, QTabWidget, QSizePolicy, QCheckBox,
    QGraphicsDropShadowEffect, QScrollArea, QAbstractItemView,
    QFileDialog, QListView
)
from PyQt6.QtCore import Qt, QDate, QTime
from PyQt6.QtGui import QColor, QFont, QIntValidator

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
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
    color: white; border: none; border-radius: 8px;
    font-weight: bold; padding: 10px 22px; font-size: 13.5px;
}
QPushButton#btnPrimary:hover { background: #1d4ed8; }
QPushButton#btnPdf {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #f59e0b, stop:1 #d97706);
    color: white; border: none; border-radius: 8px;
    font-weight: bold; padding: 10px 20px; font-size: 13.5px;
}
QPushButton#btnPdf:hover { background: #d97706; }
QPushButton#btnSuccess {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #10b981, stop:1 #059669);
    color: white; border: none; border-radius: 8px;
    font-weight: bold; padding: 9px 18px; font-size: 13.5px;
}
QPushButton#btnSuccess:hover { background: #059669; }
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

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._historia_id = None
        self._historias_cache = []
        self._pacientes_cache = []
        self.setStyleSheet(STYLE)
        self.setup_ui()
        self.load_data()

    def focus_new_form(self):
        """Limpia el formulario y enfoca el campo de nombre para una nueva historia."""
        self.clear_form()
        self.input_nombre.setFocus()

    def focus_search(self):
        """Pone el foco en el buscador de historias."""
        self.search_input.setFocus()

    # ══════════════════════════════════════════════════════════
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ══════════════════════════════════════════════════════════

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(14)

        # Panel Izquierdo: Lista de Historias y Búsqueda (35% ancho)
        root.addLayout(self._build_left_panel(), 4)

        # Panel Derecho: Formulario Estructurado con Tabs (65% ancho)
        root.addWidget(self._build_right_panel(), 7)

    # ── Panel Izquierdo (Búsqueda y Tabla) ─────────────────────
    def _build_left_panel(self) -> QVBoxLayout:
        lay = QVBoxLayout()
        lay.setSpacing(10)

        # Título
        header = QHBoxLayout()
        t = QLabel("📋 Historias Clínicas")
        t.setStyleSheet("font-size: 19px; font-weight: bold; color: #0f172a;")
        header.addWidget(t)
        header.addStretch()

        btn_nueva = QPushButton("➕ Nueva Historia")
        btn_nueva.setObjectName("btnSuccess")
        btn_nueva.clicked.connect(self.clear_form)
        header.addWidget(btn_nueva)
        lay.addLayout(header)

        # Buscador por cédula o nombre
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por Cédula o Nombre...")
        self.search_input.textChanged.connect(self._filtrar_tabla)
        search_row.addWidget(self.search_input)

        btn_refresh = QPushButton("🔄")
        btn_refresh.setObjectName("btnSecondary")
        btn_refresh.setFixedWidth(40)
        btn_refresh.setToolTip("Recargar lista de historias")
        btn_refresh.clicked.connect(self.load_data)
        search_row.addWidget(btn_refresh)
        lay.addLayout(search_row)

        # Tabla de historias
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels([
            "N° Historia", "Cédula", "Paciente", "Fecha", "ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnHidden(4, True)  # ID oculto
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
        self.form_title = QLabel("Expediente de Historia Clínica")
        self.form_title.setStyleSheet("font-size: 17px; font-weight: bold; color: #1e3a8a;")
        lay.addWidget(self.form_title)

        # Cabecera en filas flexibles (evita solapes del grid de 7 columnas)
        header = QVBoxLayout()
        header.setSpacing(10)

        # Fila 0: N° Historia | Fecha | Hora
        row0 = QHBoxLayout()
        row0.setSpacing(12)

        self.input_num_historia = QLineEdit()
        self.input_num_historia.setPlaceholderText("Ej: HC-001")
        self.input_num_historia.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        row0.addWidget(self._labeled_field("N° Historia:", self.input_num_historia), 2)

        self.input_fecha_elab = QDateEdit(QDate.currentDate())
        self.input_fecha_elab.setCalendarPopup(True)
        self.input_fecha_elab.setDisplayFormat("dd/MM/yyyy")
        self.input_fecha_elab.setMaximumWidth(140)
        row0.addWidget(self._labeled_field("Fecha Elab.:", self.input_fecha_elab), 0)

        self.input_hora_elab = QTimeEdit(QTime.currentTime())
        self.input_hora_elab.setDisplayFormat("HH:mm")
        self.input_hora_elab.setMaximumWidth(100)
        row0.addWidget(self._labeled_field("Hora:", self.input_hora_elab), 0)
        header.addLayout(row0)

        # Fila 1: Nombre | Sexo
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombres y Apellidos completos del paciente")
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

        self.tabs.addTab(self.tab_filiacion, "1. 👤 Filiación / Ingreso")
        self.tabs.addTab(self.tab_antecedentes, "2. 🩺 Antecedentes")
        self.tabs.addTab(self.tab_representante, "3. 👨‍👩‍👧 Representante")
        self.tabs.addTab(self.tab_emocional, "4. 💭 Autoexploración")
        self.tabs.addTab(self.tab_neuro, "5. 🧠 Neurodesarrollo / IPX")

        lay.addWidget(self.tabs, 1)

        # ── Botones de Acción Inferiores ──
        btn_bar = QHBoxLayout()
        btn_bar.setSpacing(12)

        self.btn_guardar = QPushButton("💾 Guardar Historia")
        self.btn_guardar.setObjectName("btnPrimary")
        self.btn_guardar.clicked.connect(self.save_data)

        self.btn_imprimir = QPushButton("🖨️ Imprimir Historia PDF")
        self.btn_imprimir.setObjectName("btnPdf")
        self.btn_imprimir.clicked.connect(self.imprimir_pdf)

        self.btn_limpiar = QPushButton("✖ Limpiar")
        self.btn_limpiar.setObjectName("btnSecondary")
        self.btn_limpiar.clicked.connect(self.clear_form)

        btn_bar.addWidget(self.btn_guardar)
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
        self.input_fecha_ingreso = QDateEdit(QDate.currentDate())
        self.input_fecha_ingreso.setCalendarPopup(True)
        self.input_fecha_ingreso.setDisplayFormat("dd/MM/yyyy")
        g.addWidget(self.input_fecha_ingreso, 0, 1)

        g.addWidget(self._lbl("Fecha de Egreso:"), 0, 2)
        self.input_fecha_egreso = QDateEdit(QDate.currentDate().addMonths(6))
        self.input_fecha_egreso.setCalendarPopup(True)
        self.input_fecha_egreso.setDisplayFormat("dd/MM/yyyy")
        g.addWidget(self.input_fecha_egreso, 0, 3)

        # Lugar y fecha de nacimiento
        g.addWidget(self._lbl("Lugar de Nacimiento:"), 1, 0)
        self.input_lugar_nac = QLineEdit()
        self.input_lugar_nac.setPlaceholderText("Ciudad, Estado, País de nacimiento")
        g.addWidget(self.input_lugar_nac, 1, 1)

        g.addWidget(self._lbl("Fecha de Nacimiento:"), 1, 2)
        self.input_fecha_nac = QDateEdit(QDate.currentDate().addYears(-15))
        self.input_fecha_nac.setCalendarPopup(True)
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

        # IPX: Impresión Diagnóstica
        lay.addWidget(self._lbl_bold("IPX: Impresión Diagnóstica (Criterios clínicos / CIE / DSM):"))
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

        self._historias_cache = historias
        self._poblar_tabla(historias)

    def _poblar_tabla(self, historias: list):
        self.table.setRowCount(0)
        for i, h in enumerate(historias):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(h.get("num_historia", f"HC-{i+1:03d}")))
            self.table.setItem(i, 1, QTableWidgetItem(h.get("cedula", "—")))
            self.table.setItem(i, 2, QTableWidgetItem(h.get("nombre", "—")))
            self.table.setItem(i, 3, QTableWidgetItem(h.get("fecha_elaboracion", "—")))
            self.table.setItem(i, 4, QTableWidgetItem(h.get("id", "")))

        self.lbl_count.setText(f"{len(historias)} historia(s) registrada(s)")

    def _filtrar_tabla(self, text: str):
        q = text.lower().strip()
        for row in range(self.table.rowCount()):
            num = self.table.item(row, 0).text().lower() if self.table.item(row, 0) else ""
            ced = self.table.item(row, 1).text().lower() if self.table.item(row, 1) else ""
            nom = self.table.item(row, 2).text().lower() if self.table.item(row, 2) else ""
            visible = (q in num) or (q in ced) or (q in nom)
            self.table.setRowHidden(row, not visible)

    def _cargar_historia_click(self, item):
        row = item.row()
        id_item = self.table.item(row, 4)
        if not id_item:
            return
        hist_id = id_item.text()
        h = next((x for x in self._historias_cache if x.get("id") == hist_id), None)
        if not h:
            return

        self._historia_id = hist_id
        self.form_title.setText(f"Expediente N° {h.get('num_historia', '')} — {h.get('nombre', '')}")
        self.btn_guardar.setText("💾 Actualizar Historia")

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

        return {
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
            "ipx":                        self.input_ipx.toPlainText().strip(),
        }

    def save_data(self):
        """Valida y guarda la historia clínica en Firebase."""
        nombre = self.input_nombre.text().strip()
        if not nombre:
            QMessageBox.warning(self, "Campo requerido", "El nombre del paciente es obligatorio.")
            self.input_nombre.setFocus()
            return

        datos = self.to_dict()

        try:
            if self._historia_id:
                if hasattr(self.db, "actualizar_historia_clinica"):
                    self.db.actualizar_historia_clinica(self._historia_id, datos)
                elif hasattr(self.db, "_db") and self.db._db:
                    self.db._db.collection("historias_clinicas").document(self._historia_id).update(datos)
                QMessageBox.information(self, "✅ Éxito", "Historia clínica actualizada correctamente.")
            else:
                # Inyectar user_id del médico en sesión
                datos["user_id"] = self.db.get_current_user_id()
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
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", f"No se pudo guardar la historia clínica:\n{e}")

    def _eliminar_historia(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selección", "Selecciona una historia clínica para eliminar.")
            return

        row = rows[0].row()
        id_item = self.table.item(row, 4)
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

    def clear_form(self):
        """Limpia todos los campos del formulario."""
        self._historia_id = None
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
        self.input_ipx.clear()

        self.tabs.setCurrentIndex(0)

    # ── Helpers UI ─────────────────────────────────────────────
    def _lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("font-size: 13px; color: #334155; font-weight: 600;")
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
        l.setStyleSheet("font-size: 13px; color: #1e3a8a; font-weight: 700; margin-top: 6px; margin-bottom: 2px;")
        return l

    @staticmethod
    def _sep() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet("background: #e2e8f0; max-height: 1.5px; border: none; margin: 4px 0;")
        return f
