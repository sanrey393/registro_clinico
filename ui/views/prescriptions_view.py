# ui/views/prescriptions_view.py
# Módulo de Recetación y Gestión de Fármacos por Paciente

import os
import json
import datetime
import urllib.request
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QComboBox, QDateEdit, QTextEdit,
    QGridLayout, QCompleter, QScrollArea, QAbstractItemView,
    QApplication, QFileDialog, QListView
)
from PyQt6.QtCore import Qt, QDate, QStringListModel, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from ui.widgets.smart_date_edit import SmartDateEdit
from ui.widgets.app_icons import svg_icon

from data.farmacos_catalogo import (
    obtener_catalogo_completo,
    guardar_o_actualizar_farmaco,
    buscar_farmacos,
    obtener_laboratorios
)

STYLE = """
QWidget {
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
    font-size: 13px;
    color: #1e293b;
}

/* Campos de entrada */
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #ffffff;
    border: 1.5px solid #cbd5e1;
    border-radius: 7px;
    padding: 7px 10px;
    color: #1e293b;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border-color: #2563eb;
    background-color: #ffffff;
}

/* Tabla */
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #f1f5f9;
    selection-background-color: #eff6ff;
    selection-color: #1d4ed8;
    alternate-background-color: #f8fafc;
}
QHeaderView::section {
    background-color: #f8fafc;
    color: #475569;
    font-weight: 700;
    font-size: 12px;
    border: none;
    padding: 8px;
    border-bottom: 2px solid #e2e8f0;
}
QTableWidget::item {
    padding: 6px;
    border-bottom: 1px solid #f1f5f9;
}

/* Botones con estilo coherente */
QPushButton#btnPrimary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
    color: white; border: none; border-radius: 7px;
    font-weight: bold; padding: 8px 18px;
}
QPushButton#btnPrimary:hover { background: #1d4ed8; }

QPushButton#btnSuccess {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #059669);
    color: white; border: none; border-radius: 7px;
    font-weight: bold; padding: 8px 18px;
}
QPushButton#btnSuccess:hover { background: #059669; }

QPushButton#btnWarning {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #d97706);
    color: white; border: none; border-radius: 7px;
    font-weight: bold; padding: 8px 18px;
}
QPushButton#btnWarning:hover { background: #d97706; }

QPushButton#btnDanger {
    background: #fef2f2; color: #dc2626;
    border: 1px solid #fecaca; border-radius: 7px;
    padding: 7px 14px; font-weight: 600;
}
QPushButton#btnDanger:hover { background: #fee2e2; }

QPushButton#btnSecondary {
    background: #f1f5f9; color: #475569;
    border: 1px solid #cbd5e1; border-radius: 7px;
    padding: 7px 14px; font-weight: 600;
}
QPushButton#btnSecondary:hover { background: #e2e8f0; color: #0f172a; }
"""

from core.app_paths import app_dir
_LOCAL_RECETAS_FILE = os.path.join(app_dir(), "recetas_guardadas.json")


class OnlineDrugSearchThread(QThread):
    """Hilo secundario para consultar la API de fármacos sin bloquear la interfaz."""
    results_ready = pyqtSignal(list)

    def __init__(self, term: str):
        super().__init__()
        self.term = term

    def run(self):
        term_clean = self.term.strip()
        if len(term_clean) < 3:
            return
        try:
            url = f"https://clinicaltables.nlm.nih.gov/api/rxterms/v3/search?terms={urllib.parse.quote(term_clean)}&maxList=10"
            req = urllib.request.Request(url, headers={"User-Agent": "AntigravityClinical/1.0"})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                # data[1] contiene la lista de nombres de fármacos devueltos por la API
                if len(data) > 1 and isinstance(data[1], list):
                    self.results_ready.emit(data[1])
        except Exception:
            pass


class PrescriptionsView(QWidget):
    """
    Módulo de Recetación y Fármacos:
    - Selector del paciente al que se le prescribe.
    - Campos completos de escritura:
      * Nombre comercial
      * Nombre genérico
      * Laboratorio
      * Descripción e indicaciones
      * Contraindicaciones
      * Efectos secundarios
      * Interacciones
      * Recetación y dosis
    - Autocompletado conectado con Catálogo y API de fármacos.
    - Si el fármaco no está en la lista, la doctora lo escribe y se guarda en el catálogo y la receta.
    - Botones exactos: 'Buscar', 'Muestras todo', 'Guardar Receta', 'Editar', 'Nueva Receta', 'Imprimir PDF'.
    """

    receta_actualizada = pyqtSignal(dict)
    agendar_control_requested = pyqtSignal(str)

    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db = db_manager

        self._receta_actual_id = None
        self._pacientes_cache = []
        self._historias_cache = []
        self._recetas_cache = []
        self._catalogo_farmacos = []
        self._online_thread = None
        self._syncing_combo = False

        self._init_ui()
        self._cargar_catalogo_farmacos()
        if hasattr(self.db, "get_current_user_id") and self.db.get_current_user_id():
            self.load_data()

    def load_data(self):
        """Recarga pacientes, historias, recetas y alertas clínicas."""
        self._cargar_pacientes()
        try:
            self._historias_cache = (
                self.db.obtener_historias_clinicas()
                if self.db and hasattr(self.db, "obtener_historias_clinicas")
                else []
            )
        except Exception:
            self._historias_cache = []
        self._cargar_recetas()
        self._actualizar_alerta_clinica()

    # ── Construcción de la Interfaz ──────────────────────────────

    def _init_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(18, 14, 18, 14)
        root.setSpacing(12)

        # Scroll principal para el formulario de recetación
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        container = QWidget()
        lay_container = QVBoxLayout(container)
        lay_container.setContentsMargins(0, 0, 8, 0)
        lay_container.setSpacing(12)

        # 1. Panel de Recetación al Paciente (Formulario Principal)
        lay_container.addWidget(self._build_prescription_form_panel())

        # 2. Separador sutil
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #cbd5e1; max-height: 1px; border: none;")
        lay_container.addWidget(sep)

        # 3. Panel de Búsqueda e Historial de Recetas
        lay_container.addWidget(self._build_history_panel())

        scroll_area.setWidget(container)
        root.addWidget(scroll_area)

    def _build_prescription_form_panel(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(12)

        # Título del módulo
        top_row = QHBoxLayout()
        lbl_titulo = QLabel("💊  Recetación y Fármacos del Paciente")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: 800;")
        top_row.addWidget(lbl_titulo)

        top_row.addStretch()

        self.lbl_status = QLabel("Nueva Receta en Blanco")
        self.lbl_status.setStyleSheet("color: #0369a1; background: #e0f2fe; padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 11px;")
        top_row.addWidget(self.lbl_status)
        lay.addLayout(top_row)

        # ── Fila de Paciente, Fecha y Médico Tratante ───────────
        grid_paciente = QGridLayout()
        grid_paciente.setSpacing(10)

        # Selector de Paciente (Filtro + Desplegable clicable)
        grid_paciente.addWidget(self._lbl_negrita("👤 Paciente a Recetar: *"), 0, 0)
        pac_wrap = QWidget()
        pac_lay = QHBoxLayout(pac_wrap)
        pac_lay.setContentsMargins(0, 0, 0, 0)
        pac_lay.setSpacing(6)

        self.input_buscar_pac = QLineEdit()
        self.input_buscar_pac.setPlaceholderText("🔍 Filtrar cédula/nombre...")
        self.input_buscar_pac.setMaximumWidth(185)
        self.input_buscar_pac.textChanged.connect(self._filtrar_combo_pacientes)
        pac_lay.addWidget(self.input_buscar_pac)

        self.combo_paciente = QComboBox()
        self.combo_paciente.setView(QListView())
        self.combo_paciente.setEditable(False)
        self.combo_paciente.setToolTip("Haz clic para desplegar los pacientes registrados")
        self.combo_paciente.currentIndexChanged.connect(lambda _i: self._actualizar_alerta_clinica())
        pac_lay.addWidget(self.combo_paciente, 1)
        grid_paciente.addWidget(pac_wrap, 0, 1, 1, 2)

        # Fecha
        grid_paciente.addWidget(self._lbl_negrita("📅 Fecha:"), 0, 3)
        self.input_fecha = SmartDateEdit(QDate.currentDate())
        self.input_fecha.setMinimumWidth(160)
        grid_paciente.addWidget(self.input_fecha, 0, 4)

        # Médico, Especialidad y Estado del tratamiento
        grid_paciente.addWidget(self._lbl_negrita("🩺 Médico:"), 1, 0)
        self.input_medico = QLineEdit()
        self.input_medico.setPlaceholderText("Nombre del profesional de la salud...")
        grid_paciente.addWidget(self.input_medico, 1, 1)

        grid_paciente.addWidget(self._lbl_negrita("Especialidad:"), 1, 2)
        self.combo_especialidad = QComboBox()
        self.combo_especialidad.setView(QListView())
        self.combo_especialidad.setEditable(False)
        self.combo_especialidad.addItems([
            "Psiquiatría",
            "Psicología Clínica",
            "Neurología",
            "Neuropediatría",
            "Medicina General",
            "Medicina Interna",
            "Medicina Familiar",
            "Pediatría",
            "Psiquiatría Infanto-Juvenil",
            "Endocrinología",
            "Otra",
        ])
        self.combo_especialidad.setToolTip("Selecciona la especialidad médica que emite la receta")
        grid_paciente.addWidget(self.combo_especialidad, 1, 3)

        self.combo_estado_tratamiento = QComboBox()
        self.combo_estado_tratamiento.setView(QListView())
        self.combo_estado_tratamiento.addItems(["Activo", "Finalizado", "Suspendido"])
        self.combo_estado_tratamiento.setToolTip("Estado actual del tratamiento farmacológico")
        grid_paciente.addWidget(self.combo_estado_tratamiento, 1, 4)

        lay.addLayout(grid_paciente)

        # Alerta clínica (Alergias / Otros datos de Identificación + Condición IPX de Historia)
        self.lbl_alerta_clinica = QLabel("Selecciona un paciente para ver sus alergias, notas y condición clínica (IPX).")
        self.lbl_alerta_clinica.setWordWrap(True)
        self.lbl_alerta_clinica.setStyleSheet(
            "background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 7px; "
            "color: #475569; padding: 7px 10px; font-size: 12px;"
        )
        lay.addWidget(self.lbl_alerta_clinica)

        # Separador interno
        sep_in = QFrame()
        sep_in.setFrameShape(QFrame.Shape.HLine)
        sep_in.setStyleSheet("background: #f1f5f9; max-height: 1px; border: none;")
        lay.addWidget(sep_in)

        # ── Sección de Campos de Escritura del Fármaco ─────────
        lbl_sec_farmaco = QLabel("📝  Datos del Fármaco y Dosificación (Escriba o seleccione de la lista / API)")
        lbl_sec_farmaco.setStyleSheet("font-size: 13px; font-weight: 700;")
        lay.addWidget(lbl_sec_farmaco)

        grid_campos = QGridLayout()
        grid_campos.setSpacing(10)

        # 1. Nombre Comercial
        grid_campos.addWidget(self._lbl_campo("Nombre Comercial: *"), 0, 0)
        self.txt_comercial = QLineEdit()
        self.txt_comercial.setPlaceholderText("Ej. Tylenol, Advil, Zoloft, Ventolin, Prozac (escriba libremente o elija)...")
        self.txt_comercial.textChanged.connect(self._on_comercial_text_changed)
        grid_campos.addWidget(self.txt_comercial, 0, 1)

        # 2. Nombre Genérico
        grid_campos.addWidget(self._lbl_campo("Nombre Genérico / Principio: *"), 0, 2)
        self.txt_generico = QLineEdit()
        self.txt_generico.setPlaceholderText("Ej. Paracetamol, Ibuprofeno, Sertralina, Fluoxetina...")
        self.txt_generico.textChanged.connect(self._on_generico_text_changed)
        grid_campos.addWidget(self.txt_generico, 0, 3)

        # 3. Laboratorio
        grid_campos.addWidget(self._lbl_campo("Laboratorio:"), 1, 0)
        self.txt_laboratorio = QLineEdit()
        self.txt_laboratorio.setPlaceholderText("Ej. Pfizer, Bayer, Sanofi, GSK, Genfar...")
        grid_campos.addWidget(self.txt_laboratorio, 1, 1)

        # 4. Recetación y Dosis (Posología)
        grid_campos.addWidget(self._lbl_campo("Recetación y Dosis: *"), 1, 2)
        self.txt_dosis = QTextEdit()
        self.txt_dosis.setPlaceholderText("Pauta posológica: 500 mg cada 8 horas por 7 días por vía oral...")
        self.txt_dosis.setMaximumHeight(55)
        grid_campos.addWidget(self.txt_dosis, 1, 3)

        # 5. Descripción e Indicaciones
        grid_campos.addWidget(self._lbl_campo("Descripción e Indicaciones:"), 2, 0)
        self.txt_indicaciones = QTextEdit()
        self.txt_indicaciones.setPlaceholderText("Indicaciones terapéuticas, patología tratada, grupo...")
        self.txt_indicaciones.setMaximumHeight(55)
        grid_campos.addWidget(self.txt_indicaciones, 2, 1)

        # 6. Contraindicaciones
        grid_campos.addWidget(self._lbl_campo("Contraindicaciones:"), 2, 2)
        self.txt_contraindicaciones = QTextEdit()
        self.txt_contraindicaciones.setPlaceholderText("Casos donde no debe administrarse...")
        self.txt_contraindicaciones.setMaximumHeight(55)
        grid_campos.addWidget(self.txt_contraindicaciones, 2, 3)

        # 7. Efectos Secundarios
        grid_campos.addWidget(self._lbl_campo("Efectos Secundarios:"), 3, 0)
        self.txt_efectos = QTextEdit()
        self.txt_efectos.setPlaceholderText("Efectos adversos o precauciones...")
        self.txt_efectos.setMaximumHeight(55)
        grid_campos.addWidget(self.txt_efectos, 3, 1)

        # 8. Interacciones
        grid_campos.addWidget(self._lbl_campo("Interacciones:"), 3, 2)
        self.txt_interacciones = QTextEdit()
        self.txt_interacciones.setPlaceholderText("Interacciones con otros medicamentos o sustancias...")
        self.txt_interacciones.setMaximumHeight(55)
        grid_campos.addWidget(self.txt_interacciones, 3, 3)

        lay.addLayout(grid_campos)

        # ── Botones de Acción del Formulario ───────────────────
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        self.btn_nueva_receta = QPushButton("➕  Nueva Receta")
        self.btn_nueva_receta.setObjectName("btnSecondary")
        self.btn_nueva_receta.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_nueva_receta.clicked.connect(self.clear_form)
        btn_box.addWidget(self.btn_nueva_receta)

        btn_box.addStretch()

        self.btn_agendar_control = QPushButton(" Agendar Control")
        self.btn_agendar_control.setObjectName("btnSuccess")
        self.btn_agendar_control.setIcon(svg_icon("calendar", color="#047857", size=15))
        self.btn_agendar_control.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_agendar_control.setToolTip("Abrir Agenda con este paciente para programar cita de control")
        self.btn_agendar_control.clicked.connect(self._ir_a_agendar_control)
        btn_box.addWidget(self.btn_agendar_control)

        self.btn_imprimir = QPushButton(" Imprimir PDF")
        self.btn_imprimir.setObjectName("btnWarning")
        self.btn_imprimir.setIcon(svg_icon("printer", color="#475569", size=15))
        self.btn_imprimir.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_imprimir.clicked.connect(self._imprimir_pdf)
        btn_box.addWidget(self.btn_imprimir)

        self.btn_editar = QPushButton(" Editar Seleccionado")
        self.btn_editar.setObjectName("btnSecondary")
        self.btn_editar.setIcon(svg_icon("file-text", color="#475569", size=15))
        self.btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_editar.clicked.connect(self._editar_seleccionado_de_tabla)
        btn_box.addWidget(self.btn_editar)

        self.btn_eliminar = QPushButton(" Eliminar")
        self.btn_eliminar.setObjectName("btnDanger")
        self.btn_eliminar.setIcon(svg_icon("trash", color="#dc2626", size=15))
        self.btn_eliminar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_eliminar.clicked.connect(self._eliminar_receta)
        btn_box.addWidget(self.btn_eliminar)

        self.btn_guardar = QPushButton(" Guardar Receta")
        self.btn_guardar.setObjectName("btnPrimary")
        self.btn_guardar.setIcon(svg_icon("save", color="#ffffff", size=15))
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.clicked.connect(self._guardar_receta)
        btn_box.addWidget(self.btn_guardar)

        lay.addLayout(btn_box)

        return card

    def _build_history_panel(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 14, 18, 14)
        lay.setSpacing(10)

        # ── Barra de Búsqueda con los Botones "Buscar" y "Muestras todo" ──
        busq_bar = QHBoxLayout()
        busq_bar.setSpacing(10)

        lbl_b = QLabel("📋  Historial de Recetas:")
        lbl_b.setStyleSheet("font-size: 14px; font-weight: 700;")
        busq_bar.addWidget(lbl_b)

        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por paciente, cédula, nombre comercial, genérico o laboratorio...")
        self.input_buscar.returnPressed.connect(self._buscar)
        busq_bar.addWidget(self.input_buscar, stretch=2)

        # Botón Buscar
        self.btn_buscar = QPushButton("🔍  Buscar")
        self.btn_buscar.setObjectName("btnPrimary")
        self.btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_buscar.clicked.connect(self._buscar)
        busq_bar.addWidget(self.btn_buscar)

        # Botón Muestras todo
        self.btn_muestras_todo = QPushButton("📋  Muestras todo")
        self.btn_muestras_todo.setObjectName("btnSuccess")
        self.btn_muestras_todo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_muestras_todo.clicked.connect(self._muestras_todo)
        busq_bar.addWidget(self.btn_muestras_todo)

        lay.addLayout(busq_bar)

        # ── Tabla de Historial ──────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Paciente", "Nombre Comercial", "Nombre Genérico",
            "Laboratorio", "Recetación y Dosis", "Indicaciones"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(210)
        self.table.itemClicked.connect(self._on_table_item_clicked)
        self.table.itemDoubleClicked.connect(self._editar_seleccionado_de_tabla)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)

        lay.addWidget(self.table)

        self.lbl_contador_tabla = QLabel("Cargando recetas...")
        self.lbl_contador_tabla.setStyleSheet("color: #64748b; font-size: 11px;")
        lay.addWidget(self.lbl_contador_tabla)

        return card

    def _lbl_negrita(self, txt: str) -> QLabel:
        l = QLabel(txt)
        l.setStyleSheet("font-size: 12px; font-weight: 700; color: #1e293b;")
        return l

    def _lbl_campo(self, txt: str) -> QLabel:
        l = QLabel(txt)
        l.setStyleSheet("font-size: 12px; font-weight: 600; color: #475569;")
        return l

    # ── Conexión con Catálogo y API de Fármacos ──────────────────

    def _cargar_catalogo_farmacos(self):
        """Carga el catálogo local y configura los autocompletadores para los campos."""
        self._catalogo_farmacos = obtener_catalogo_completo()

        nombres_comerciales = []
        nombres_genericos = []
        for f in self._catalogo_farmacos:
            nc = f.get("nombre_comercial", "").strip()
            ng = f.get("nombre_generico", "").strip()
            if nc and nc not in nombres_comerciales:
                nombres_comerciales.append(nc)
            if ng and ng not in nombres_genericos:
                nombres_genericos.append(ng)

        # Autocompleter comercial
        self._completer_comercial = QCompleter(nombres_comerciales, self)
        self._completer_comercial.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer_comercial.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer_comercial.activated.connect(self._on_comercial_selected)
        self.txt_comercial.setCompleter(self._completer_comercial)

        # Autocompleter genérico
        self._completer_generico = QCompleter(nombres_genericos, self)
        self._completer_generico.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer_generico.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer_generico.activated.connect(self._on_generico_selected)
        self.txt_generico.setCompleter(self._completer_generico)

        # Autocompleter laboratorio
        labs = obtener_laboratorios()
        completer_lab = QCompleter(labs, self)
        completer_lab.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.txt_laboratorio.setCompleter(completer_lab)

    def _on_comercial_selected(self, text: str):
        """Al seleccionar un nombre comercial de la lista, autocompleta los demás campos si existe."""
        for f in self._catalogo_farmacos:
            if f.get("nombre_comercial", "").strip().lower() == text.strip().lower():
                self._aplicar_datos_farmaco_a_formulario(f)
                break

    def _on_generico_selected(self, text: str):
        """Al seleccionar un nombre genérico de la lista, autocompleta los demás campos si existe."""
        for f in self._catalogo_farmacos:
            if f.get("nombre_generico", "").strip().lower() == text.strip().lower():
                self._aplicar_datos_farmaco_a_formulario(f)
                break

    def _aplicar_datos_farmaco_a_formulario(self, f: dict):
        """Llena los campos del formulario con la información del fármaco seleccionado."""
        if not self.txt_comercial.text().strip():
            self.txt_comercial.setText(f.get("nombre_comercial", ""))
        if not self.txt_generico.text().strip():
            self.txt_generico.setText(f.get("nombre_generico", ""))
        if not self.txt_laboratorio.text().strip():
            self.txt_laboratorio.setText(f.get("laboratorio", ""))
        if not self.txt_dosis.toPlainText().strip():
            self.txt_dosis.setPlainText(f.get("recetacion_dosis", ""))
        if not self.txt_indicaciones.toPlainText().strip():
            self.txt_indicaciones.setPlainText(f.get("descripcion_indicaciones", ""))
        if not self.txt_contraindicaciones.toPlainText().strip():
            self.txt_contraindicaciones.setPlainText(f.get("contraindicaciones", ""))
        if not self.txt_efectos.toPlainText().strip():
            self.txt_efectos.setPlainText(f.get("efectos_secundarios", ""))
        if not self.txt_interacciones.toPlainText().strip():
            self.txt_interacciones.setPlainText(f.get("interacciones", ""))

    def _on_comercial_text_changed(self, text: str):
        """Búsqueda dinámica en API / Catálogo cuando se escribe."""
        # Consultar API si el texto tiene 3 o más letras
        if len(text.strip()) >= 3:
            self._consultar_api_farmacos(text.strip())

    def _on_generico_text_changed(self, text: str):
        """Búsqueda dinámica en API / Catálogo cuando se escribe."""
        if len(text.strip()) >= 3:
            self._consultar_api_farmacos(text.strip())

    def _consultar_api_farmacos(self, term: str):
        """Lanza búsqueda asíncrona a la API de fármacos."""
        try:
            if self._online_thread and self._online_thread.isRunning():
                return
            self._online_thread = OnlineDrugSearchThread(term)
            self._online_thread.results_ready.connect(self._incorporar_sugerencias_api)
            self._online_thread.start()
        except Exception:
            pass

    def _incorporar_sugerencias_api(self, nombres_api: list):
        """Agrega dinámicamente los fármacos traídos por la API al completer."""
        if not nombres_api:
            return
        model = self._completer_comercial.model()
        if isinstance(model, QStringListModel):
            actuales = model.stringList()
            nuevos = list(actuales)
            modificado = False
            for nom in nombres_api:
                if nom not in nuevos:
                    nuevos.append(nom)
                    modificado = True
            if modificado:
                model.setStringList(nuevos)

    # ── Carga de Pacientes y Recetas ─────────────────────────────

    def _cargar_pacientes(self):
        """Llena el combo de pacientes desde la base de datos."""
        self._pacientes_cache = []

        if self.db and hasattr(self.db, "obtener_pacientes"):
            try:
                self._pacientes_cache = self.db.obtener_pacientes()
            except Exception as e:
                print(f"[WARN] Error al obtener pacientes: {e}")

        # Si no hay pacientes en BD, intentar leer de local
        if not self._pacientes_cache:
            p_local = os.path.join(app_dir(), "pacientes_local.json")
            if os.path.exists(p_local):
                try:
                    with open(p_local, "r", encoding="utf-8") as f:
                        self._pacientes_cache = json.load(f)
                except Exception:
                    pass

        self._poblar_combo_pacientes(
            self.input_buscar_pac.text() if hasattr(self, "input_buscar_pac") else ""
        )

    def _poblar_combo_pacientes(self, filtro: str = ""):
        prev_data = self.combo_paciente.currentData() if self.combo_paciente.count() else None
        prev_id = prev_data.get("id") if isinstance(prev_data, dict) else None
        q = (filtro or "").strip().lower()
        self._syncing_combo = True
        self.combo_paciente.clear()
        self.combo_paciente.addItem("-- Seleccione un paciente --", None)
        for p in sorted(self._pacientes_cache, key=lambda x: (x.get("nombre", "") or "").lower()):
            nom = p.get("nombre", "") or p.get("nombre_completo", "Sin Nombre")
            ced = p.get("cedula", "")
            if q and (q not in nom.lower() and q not in ced.lower()):
                continue
            pnf = p.get("pnf", "")
            extra = f" · {pnf}" if pnf and pnf != "No aplica / Externo" else ""
            txt = f"{nom} (CI: {ced}{extra})" if ced else nom
            self.combo_paciente.addItem(txt, p)
        if prev_id:
            for i in range(self.combo_paciente.count()):
                d = self.combo_paciente.itemData(i)
                if isinstance(d, dict) and d.get("id") == prev_id:
                    self.combo_paciente.setCurrentIndex(i)
                    break
        self._syncing_combo = False

    def _filtrar_combo_pacientes(self, text: str):
        self._poblar_combo_pacientes(text)

    def seleccionar_paciente_por_id(self, paciente_id: str):
        """Selecciona un paciente por ID al navegar desde Identificación o Historia Clínica."""
        if not paciente_id:
            return
        if hasattr(self, "input_buscar_pac"):
            self.input_buscar_pac.clear()
        self._poblar_combo_pacientes()
        for i in range(self.combo_paciente.count()):
            d = self.combo_paciente.itemData(i)
            if isinstance(d, dict) and d.get("id") == paciente_id:
                self.combo_paciente.setCurrentIndex(i)
                break
        self._actualizar_alerta_clinica()

    def _actualizar_alerta_clinica(self):
        """Muestra alergias/notas de Identificación y Condición IPX de Historia Clínica."""
        if not hasattr(self, "lbl_alerta_clinica") or self._syncing_combo:
            return
        p = self.combo_paciente.currentData()
        if not isinstance(p, dict):
            self.lbl_alerta_clinica.setText(
                "Selecciona un paciente para ver sus alergias, notas y condición clínica (IPX)."
            )
            self.lbl_alerta_clinica.setStyleSheet(
                "background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 7px; "
                "color: #475569; padding: 7px 10px; font-size: 12px;"
            )
            return

        pid = p.get("id", "")
        ced = (p.get("cedula", "") or "").strip().lower()
        otros = (p.get("otros_datos", "") or "").strip()
        hist = next(
            (
                h for h in self._historias_cache
                if (pid and h.get("paciente_id") == pid)
                or (ced and (h.get("cedula", "") or "").strip().lower() == ced)
            ),
            None,
        )
        condicion = (hist.get("patologia", "") if hist else "") or "Sin especificar"
        if otros:
            self.lbl_alerta_clinica.setText(
                f"⚠️ Alergias / Notas (Identificación): {otros}   |   🧠 Condición IPX: {condicion}"
            )
            self.lbl_alerta_clinica.setStyleSheet(
                "background: #fefce8; border: 1px solid #fde047; border-radius: 7px; "
                "color: #854d0e; padding: 7px 10px; font-size: 12px; font-weight: 600;"
            )
        else:
            self.lbl_alerta_clinica.setText(
                f"🧠 Condición IPX: {condicion}   |   ✅ Sin alergias o alertas registradas en Identificación"
            )
            self.lbl_alerta_clinica.setStyleSheet(
                "background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 7px; "
                "color: #1e40af; padding: 7px 10px; font-size: 12px; font-weight: 500;"
            )

    def _ir_a_agendar_control(self):
        p = self.combo_paciente.currentData()
        if not isinstance(p, dict) or not p.get("id"):
            QMessageBox.information(
                self, "Paciente requerido", "Selecciona un paciente primero para agendarle un control."
            )
            return
        self.agendar_control_requested.emit(p.get("id"))

    def _cargar_recetas(self):
        """Carga el historial de recetas desde Firestore o JSON local."""
        self._recetas_cache = []

        if self.db and hasattr(self.db, "obtener_todas_recetas"):
            try:
                self._recetas_cache = self.db.obtener_todas_recetas()
            except Exception as e:
                print(f"[WARN] Error al leer recetas en Firestore: {e}")

        if not self._recetas_cache and os.path.exists(_LOCAL_RECETAS_FILE):
            try:
                with open(_LOCAL_RECETAS_FILE, "r", encoding="utf-8") as f:
                    self._recetas_cache = json.load(f)
            except Exception:
                self._recetas_cache = []

        self._poblar_tabla(self._recetas_cache)

    def _guardar_recetas_local(self):
        """Persiste las recetas en archivo JSON local de respaldo."""
        try:
            with open(_LOCAL_RECETAS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._recetas_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ERROR] Error al guardar recetas localmente: {e}")

    def _poblar_tabla(self, lista_recetas: list):
        """Llena la tabla con la lista de recetas."""
        self.table.blockSignals(True)
        self.table.setRowCount(len(lista_recetas))

        for row, r in enumerate(lista_recetas):
            fecha = r.get("fecha", "")
            paciente = r.get("paciente_nombre", "")
            comercial = r.get("nombre_comercial", "")
            generico = r.get("nombre_generico", "")
            lab = r.get("laboratorio", "")
            dosis = r.get("recetacion_dosis", "")
            ind = r.get("descripcion_indicaciones", "")

            it_fecha = QTableWidgetItem(str(fecha))
            it_paciente = QTableWidgetItem(str(paciente))
            it_paciente.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            it_paciente.setData(Qt.ItemDataRole.UserRole, r)

            it_comercial = QTableWidgetItem(str(comercial))
            it_generico = QTableWidgetItem(str(generico))
            it_lab = QTableWidgetItem(str(lab))
            it_dosis = QTableWidgetItem(str(dosis).replace("\n", " "))
            it_ind = QTableWidgetItem(str(ind).replace("\n", " "))

            self.table.setItem(row, 0, it_fecha)
            self.table.setItem(row, 1, it_paciente)
            self.table.setItem(row, 2, it_comercial)
            self.table.setItem(row, 3, it_generico)
            self.table.setItem(row, 4, it_lab)
            self.table.setItem(row, 5, it_dosis)
            self.table.setItem(row, 6, it_ind)

        self.table.blockSignals(False)
        self.lbl_contador_tabla.setText(f"Total: {len(lista_recetas)} receta(s) registradas")

    # ── Guardar, Editar y Eliminar ───────────────────────────────

    def _guardar_receta(self):
        """
        Guarda la receta para el paciente y si el fármaco es nuevo o editado,
        lo guarda en el catálogo de fármacos ('si no está en la lista que la doctora lo escriba y lo guarde').
        """
        # 1. Validar Paciente
        paciente_data = self.combo_paciente.currentData()
        paciente_texto = self.combo_paciente.currentText().strip()
        if not paciente_texto or paciente_texto.startswith("--"):
            QMessageBox.warning(self, "Paciente requerido", "Por favor seleccione o escriba el nombre del paciente.")
            self.combo_paciente.setFocus()
            return

        paciente_nombre = paciente_texto.split("(CI:")[0].strip() if "(CI:" in paciente_texto else paciente_texto
        paciente_id = paciente_data.get("id", "") if isinstance(paciente_data, dict) else ""

        # 2. Validar Datos del Fármaco
        comercial = self.txt_comercial.text().strip()
        generico = self.txt_generico.text().strip()
        lab = self.txt_laboratorio.text().strip() or "No especificado"
        dosis = self.txt_dosis.toPlainText().strip()
        indicaciones = self.txt_indicaciones.toPlainText().strip()
        contra = self.txt_contraindicaciones.toPlainText().strip()
        efectos = self.txt_efectos.toPlainText().strip()
        interacc = self.txt_interacciones.toPlainText().strip()

        if not comercial and not generico:
            QMessageBox.warning(self, "Fármaco requerido", "Debe indicar al menos el Nombre Comercial o el Nombre Genérico del fármaco.")
            self.txt_comercial.setFocus()
            return

        if not dosis:
            QMessageBox.warning(self, "Dosis requerida", "Por favor especifique la recetación y dosis (posología).")
            self.txt_dosis.setFocus()
            return

        # 3. Guardar / Registrar el Fármaco en el Catálogo para que quede memorizado
        farmaco_catalogo_datos = {
            "nombre_comercial": comercial or generico,
            "nombre_generico": generico or comercial,
            "laboratorio": lab,
            "recetacion_dosis": dosis,
            "descripcion_indicaciones": indicaciones or "Indicado según prescripción médica.",
            "contraindicaciones": contra,
            "efectos_secundarios": efectos,
            "interacciones": interacc,
        }
        guardar_o_actualizar_farmaco(farmaco_catalogo_datos)
        self._cargar_catalogo_farmacos()

        fecha_str = self.input_fecha.date().toString("dd/MM/yyyy")
        estado_trat = self.combo_estado_tratamiento.currentText() if hasattr(self, "combo_estado_tratamiento") else "Activo"

        # Evitar receta duplicada exacta en la misma fecha
        if not self._receta_actual_id:
            dup = next(
                (
                    r for r in self._recetas_cache
                    if (paciente_id and r.get("paciente_id") == paciente_id)
                    and r.get("fecha") == fecha_str
                    and (r.get("nombre_comercial", "") or "").lower() == comercial.lower()
                    and (r.get("recetacion_dosis", "") or "").strip().lower() == dosis.lower()
                ),
                None,
            )
            if dup:
                QMessageBox.warning(
                    self,
                    "Receta duplicada",
                    f"Ya existe una receta idéntica para {paciente_nombre} el {fecha_str}."
                )
                return

        # 4. Estructurar Datos de la Receta
        receta_datos = {
            "paciente_id": paciente_id,
            "paciente_nombre": paciente_nombre,
            "fecha": fecha_str,
            "medico": self.input_medico.text().strip(),
            "especialidad": self.combo_especialidad.currentText().strip(),
            "estado_tratamiento": estado_trat,
            "nombre_comercial": comercial,
            "nombre_generico": generico,
            "laboratorio": lab,
            "recetacion_dosis": dosis,
            "descripcion_indicaciones": indicaciones,
            "contraindicaciones": contra,
            "efectos_secundarios": efectos,
            "interacciones": interacc,
        }

        # Guardar en Firestore
        id_guardado = None
        if self._receta_actual_id:
            receta_datos["id"] = self._receta_actual_id
            if self.db and hasattr(self.db, "actualizar_receta"):
                self.db.actualizar_receta(self._receta_actual_id, receta_datos)
            # Actualizar en caché local
            for idx, r in enumerate(self._recetas_cache):
                if r.get("id") == self._receta_actual_id:
                    self._recetas_cache[idx] = receta_datos
                    break
            id_guardado = self._receta_actual_id
        else:
            uid = self.db.get_current_user_id() if hasattr(self.db, "get_current_user_id") else ""
            if not uid:
                try:
                    from core.auth_manager import AuthManager
                    uid = AuthManager().get_uid()
                except Exception:
                    pass
            receta_datos["user_id"] = uid or ""
            if self.db and hasattr(self.db, "crear_receta"):
                id_guardado = self.db.crear_receta(dict(receta_datos))
            if not id_guardado:
                import time
                id_guardado = f"rec_{int(time.time() * 1000)}"
            receta_datos["id"] = id_guardado
            self._recetas_cache.insert(0, receta_datos)

        self._guardar_recetas_local()
        self._poblar_tabla(self._recetas_cache)
        self.receta_actualizada.emit(receta_datos)

        QMessageBox.information(
            self, "✅ Receta Guardada",
            f"La receta para **{paciente_nombre}** con el fármaco **{comercial or generico}** ha sido guardada exitosamente."
        )

        self.clear_form()

    def _on_table_item_clicked(self, item):
        """Al hacer clic en la tabla se carga la receta en el formulario."""
        row = item.row()
        it = self.table.item(row, 1)
        if it:
            receta = it.data(Qt.ItemDataRole.UserRole)
            if receta:
                self._cargar_receta_en_formulario(receta)

    def _editar_seleccionado_de_tabla(self):
        """Carga la receta seleccionada para editarla."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleccionar", "Seleccione una receta de la tabla para editar.")
            return

        row = selected_rows[0].row()
        it = self.table.item(row, 1)
        if it:
            receta = it.data(Qt.ItemDataRole.UserRole)
            self._cargar_receta_en_formulario(receta)
            self.lbl_status.setText(f"✏️ Editando Receta de: {receta.get('paciente_nombre')}")
            self.btn_guardar.setText("💾  Actualizar Receta")
            self.txt_comercial.setFocus()

    def _cargar_receta_en_formulario(self, r: dict):
        """Pasa los datos de una receta existente a los campos de escritura."""
        self._receta_actual_id = r.get("id")

        # Seleccionar paciente
        p_nombre = r.get("paciente_nombre", "")
        idx = -1
        for i in range(self.combo_paciente.count()):
            if p_nombre and p_nombre in self.combo_paciente.itemText(i):
                idx = i
                break
        if idx >= 0:
            self.combo_paciente.setCurrentIndex(idx)
        else:
            self.combo_paciente.setCurrentIndex(0)

        if hasattr(self, "combo_estado_tratamiento"):
            idx_est = self.combo_estado_tratamiento.findText(r.get("estado_tratamiento", "Activo"))
            self.combo_estado_tratamiento.setCurrentIndex(max(0, idx_est))

        # Fecha
        f_str = r.get("fecha", "")
        if f_str:
            d = QDate.fromString(f_str, "dd/MM/yyyy")
            if d.isValid():
                self.input_fecha.setDate(d)

        self.input_medico.setText(r.get("medico", ""))
        esp = (r.get("especialidad", "") or "").strip()
        if esp:
            idx_esp = self.combo_especialidad.findText(esp)
            if idx_esp < 0:
                self.combo_especialidad.addItem(esp)
                idx_esp = self.combo_especialidad.count() - 1
            self.combo_especialidad.setCurrentIndex(idx_esp)
        else:
            self.combo_especialidad.setCurrentIndex(0)

        # Campos del fármaco
        self.txt_comercial.setText(r.get("nombre_comercial", ""))
        self.txt_generico.setText(r.get("nombre_generico", ""))
        self.txt_laboratorio.setText(r.get("laboratorio", ""))
        self.txt_dosis.setPlainText(r.get("recetacion_dosis", ""))
        self.txt_indicaciones.setPlainText(r.get("descripcion_indicaciones", ""))
        self.txt_contraindicaciones.setPlainText(r.get("contraindicaciones", ""))
        self.txt_efectos.setPlainText(r.get("efectos_secundarios", ""))
        self.txt_interacciones.setPlainText(r.get("interacciones", ""))

    def _eliminar_receta(self):
        """Elimina la receta seleccionada tras confirmación."""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Seleccionar", "Seleccione la receta que desea eliminar.")
            return

        row = selected_rows[0].row()
        it = self.table.item(row, 1)
        if not it:
            return

        receta = it.data(Qt.ItemDataRole.UserRole)
        p_nom = receta.get("paciente_nombre", "")
        f_nom = receta.get("nombre_comercial") or receta.get("nombre_generico")

        confirm = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Desea eliminar la receta de **{p_nom}** ({f_nom})?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            r_id = receta.get("id")
            if r_id and self.db and hasattr(self.db, "eliminar_receta"):
                try:
                    self.db.eliminar_receta(r_id)
                except Exception:
                    pass

            self._recetas_cache = [r for r in self._recetas_cache if r.get("id") != r_id]
            self._guardar_recetas_local()
            self._poblar_tabla(self._recetas_cache)
            self.clear_form()
            self.receta_actualizada.emit({"id": r_id, "deleted": True})
            QMessageBox.information(self, "Eliminado", "La receta ha sido eliminada.")

    # ── Botones "Buscar" y "Muestras todo" ────────────────────────

    def _buscar(self):
        """Filtra la tabla de recetas según el término ingresado."""
        termino = self.input_buscar.text().strip().lower()
        if not termino:
            self._poblar_tabla(self._recetas_cache)
            return

        filtradas = []
        for r in self._recetas_cache:
            candidatos = [
                r.get("paciente_nombre", ""),
                r.get("nombre_comercial", ""),
                r.get("nombre_generico", ""),
                r.get("laboratorio", ""),
                r.get("recetacion_dosis", ""),
                r.get("descripcion_indicaciones", ""),
                r.get("fecha", ""),
            ]
            if any(termino in c.lower() for c in candidatos):
                filtradas.append(r)

        self._poblar_tabla(filtradas)
        self.lbl_contador_tabla.setText(f"Resultados de búsqueda: {len(filtradas)} receta(s)")

    def _muestras_todo(self):
        """Restablece los filtros y muestra todo el historial."""
        self.input_buscar.clear()
        self._poblar_tabla(self._recetas_cache)

    # ── Imprimir Receta en PDF ───────────────────────────────────

    def _imprimir_pdf(self):
        """Genera el documento PDF formal de la receta médica."""
        paciente_texto = self.combo_paciente.currentText().strip()
        comercial = self.txt_comercial.text().strip()
        generico = self.txt_generico.text().strip()
        dosis = self.txt_dosis.toPlainText().strip()

        if not paciente_texto or paciente_texto.startswith("--"):
            QMessageBox.warning(self, "Incompleto", "Seleccione el paciente antes de generar el PDF.")
            return

        if not comercial and not generico:
            QMessageBox.warning(self, "Incompleto", "Ingrese los datos del fármaco antes de generar el PDF.")
            return

        try:
            from ui.dialogs.pdf_generator import generar_pdf_receta

            paciente_nombre = paciente_texto.split("(CI:")[0].strip()
            fecha_str = self.input_fecha.date().toString("yyyyMMdd")
            default_name = f"Receta_{paciente_nombre.replace(' ', '_')}_{fecha_str}.pdf"

            path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Receta en PDF", default_name, "Documento PDF (*.pdf)"
            )
            if path:
                medicamento_item = {
                    "nombre": f"{comercial} ({generico})" if comercial and generico else (comercial or generico),
                    "presentacion": self.txt_laboratorio.text().strip() or "Comprimidos",
                    "dosis": dosis,
                    "frecuencia": self.txt_indicaciones.toPlainText().strip() or "Según indicación médica",
                    "duracion": "Según evaluación clínica"
                }

                instrucciones_completas = (
                    f"Posología y Dosis:\n{dosis}\n\n"
                    f"Indicaciones: {self.txt_indicaciones.toPlainText().strip()}\n"
                )
                if self.txt_contraindicaciones.toPlainText().strip():
                    instrucciones_completas += f"Contraindicaciones: {self.txt_contraindicaciones.toPlainText().strip()}\n"
                if self.txt_interacciones.toPlainText().strip():
                    instrucciones_completas += f"Interacciones / Advertencias: {self.txt_interacciones.toPlainText().strip()}"

                generar_pdf_receta(path, {
                    "paciente_nombre": paciente_nombre,
                    "fecha": self.input_fecha.date().toString("dd/MM/yyyy"),
                    "medico": self.input_medico.text().strip() or "Dr(a). Tratante",
                    "especialidad": self.combo_especialidad.currentText().strip() or "Psiquiatría",
                    "instrucciones": instrucciones_completas,
                    "medicamentos": [medicamento_item],
                })
                QMessageBox.information(self, "✅ PDF Generado", f"La receta fue guardada exitosamente en:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", f"No se pudo crear el PDF:\n{e}")

    # ── Limpiar Formulario ───────────────────────────────────────

    def clear_form(self):
        """Limpia todos los campos para una nueva receta en blanco."""
        self._receta_actual_id = None
        if hasattr(self, "input_buscar_pac"):
            self.input_buscar_pac.clear()
        self.combo_paciente.setCurrentIndex(0)
        self.input_fecha.setDate(QDate.currentDate())
        if hasattr(self, "combo_estado_tratamiento"):
            self.combo_estado_tratamiento.setCurrentIndex(0)
        if hasattr(self, "combo_especialidad"):
            self.combo_especialidad.setCurrentIndex(0)
        self.txt_comercial.clear()
        self.txt_generico.clear()
        self.txt_laboratorio.clear()
        self.txt_dosis.clear()
        self.txt_indicaciones.clear()
        self.txt_contraindicaciones.clear()
        self.txt_efectos.clear()
        self.txt_interacciones.clear()
        self.lbl_status.setText("Nueva Receta en Blanco")
        self.btn_guardar.setText("💾  Guardar Receta")
        self._actualizar_alerta_clinica()

    def focus_new_form(self):
        """Acceso directo desde menú superior."""
        self.clear_form()
        self.txt_comercial.setFocus()


# Alias para compatibilidad total
FarmacosView = PrescriptionsView
