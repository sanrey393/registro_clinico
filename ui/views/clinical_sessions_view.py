# ui/views/clinical_sessions_view.py
# Bitácora y Reporte Global de Consultas (Opción A: lectura unificada de sesiones + pacientes)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QComboBox, QGridLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QColor
from ui.widgets.smart_date_edit import SmartDateEdit
from ui.widgets.app_icons import svg_icon
from core.academic_catalog import PNF_OPTIONS, ALL_TRAYECTOS, normalize_seccion

STYLE = """
QWidget { font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }
QLabel { background: transparent; border: none; }
QLineEdit, QComboBox {
    border: 1.5px solid #cbd5e1;
    border-radius: 7px;
    padding: 5px 9px;
    background: #ffffff;
    color: #0f172a;
}
QLineEdit:focus, QComboBox:focus { border-color: #2563eb; }
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
    padding: 8px;
    border-bottom: 2px solid #cbd5e1;
}
QTableWidget::item { padding: 6px; }
QTableWidget::item:selected { background: #dbeafe; color: #1e40af; }
QFrame#kpiCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
}
QPushButton#btnPrimary {
    background: #2563eb; color: white; border: none;
    border-radius: 7px; font-weight: bold; padding: 8px 16px;
}
QPushButton#btnPrimary:hover { background: #1d4ed8; }
QPushButton#btnSecondary {
    background: #f8fafc; color: #334155; border: 1px solid #cbd5e1;
    border-radius: 7px; font-weight: 600; padding: 7px 14px;
}
QPushButton#btnSecondary:hover { background: #e2e8f0; }
QPushButton#btnDanger {
    background: #fee2e2; color: #dc2626; border: 1px solid #fecaca;
    border-radius: 7px; font-weight: bold; padding: 7px 14px;
}
QPushButton#btnDanger:hover { background: #fecaca; }
"""


class ClinicalSessionsView(QWidget):
    """
    Bitácora Global de Consultas:
    Centraliza todas las visitas registradas en Historia Clínica y citas completadas en Agenda,
    con métricas rápidas, filtros académicos/fecha y acceso directo al expediente del paciente.
    """

    abrir_historia_requested = pyqtSignal(str)
    sesion_actualizada = pyqtSignal()

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._sesiones_cache = []
        self._pacientes_cache = []
        self.setup_ui()
        if hasattr(self.db, "get_current_user_id") and self.db.get_current_user_id():
            self.load_data()

    def focus_new_form(self):
        self.search_input.setFocus()

    def setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(12)

        # Encabezado
        header = QHBoxLayout()
        title_box = QVBoxLayout()
        title_box.setSpacing(2)
        title = QLabel("📊  Bitácora de Consultas y Seguimiento")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        sub = QLabel(
            "Resumen automático de todas las visitas registradas en Historia Clínica y citas completadas en Agenda."
        )
        sub.setStyleSheet("font-size: 12px; color: #64748b;")
        title_box.addWidget(title)
        title_box.addWidget(sub)
        header.addLayout(title_box, 1)

        btn_refresh = QPushButton("🔄 Actualizar")
        btn_refresh.setObjectName("btnSecondary")
        btn_refresh.clicked.connect(self.load_data)
        header.addWidget(btn_refresh)
        root.addLayout(header)

        # Tarjetas KPI rápidas
        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(10)
        self.lbl_kpi_total = self._make_kpi_card(kpi_row, "Total Consultas", "0", "#1e3a8a")
        self.lbl_kpi_primera = self._make_kpi_card(kpi_row, "🆕 Primera Vez", "0", "#047857")
        self.lbl_kpi_sucesiva = self._make_kpi_card(kpi_row, "🔄 Sucesivas", "0", "#2563eb")
        self.lbl_kpi_pacientes = self._make_kpi_card(kpi_row, "👥 Pacientes Atendidos", "0", "#7c3aed")
        root.addLayout(kpi_row)

        # Barra de búsqueda y filtros
        filt_frame = QFrame()
        filt_frame.setObjectName("filterBox")
        filt_v = QVBoxLayout(filt_frame)
        filt_v.setContentsMargins(12, 10, 12, 10)
        filt_v.setSpacing(8)

        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por cédula, nombre, evolución o recordatorio...")
        self.search_input.textChanged.connect(self._aplicar_filtros)
        row1.addWidget(self.search_input, 2)

        self.combo_filtro_tipo = QComboBox()
        self.combo_filtro_tipo.addItems(["Tipo: Todos", "Primera vez", "Sucesiva", "Control", "Seguimiento"])
        self.combo_filtro_tipo.currentTextChanged.connect(self._aplicar_filtros)
        row1.addWidget(self.combo_filtro_tipo, 1)

        self.chk_fecha = QCheckBox("Rango de fechas:")
        self.chk_fecha.toggled.connect(self._aplicar_filtros)
        row1.addWidget(self.chk_fecha)

        self.date_desde = SmartDateEdit(QDate.currentDate().addMonths(-1))
        self.date_desde.setMinimumWidth(155)
        self.date_desde.dateChanged.connect(self._aplicar_filtros)
        row1.addWidget(self.date_desde)

        self.date_hasta = SmartDateEdit(QDate.currentDate())
        self.date_hasta.setMinimumWidth(155)
        self.date_hasta.dateChanged.connect(self._aplicar_filtros)
        row1.addWidget(self.date_hasta)

        btn_limpiar = QPushButton("🧹 Limpiar")
        btn_limpiar.setObjectName("btnSecondary")
        btn_limpiar.clicked.connect(self._limpiar_filtros)
        row1.addWidget(btn_limpiar)
        filt_v.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(8)
        self.combo_filtro_pnf = QComboBox()
        self.combo_filtro_pnf.addItems(["Todos los PNF", "Sin asignar"] + PNF_OPTIONS)
        self.combo_filtro_pnf.currentTextChanged.connect(self._aplicar_filtros)

        self.combo_filtro_tray = QComboBox()
        self.combo_filtro_tray.addItems(["Todos los Trayectos", "Sin asignar"] + ALL_TRAYECTOS)
        self.combo_filtro_tray.currentTextChanged.connect(self._aplicar_filtros)

        self.combo_filtro_sec = QComboBox()
        self.combo_filtro_sec.addItems(["Todas las Secciones", "Sin asignar"])
        self.combo_filtro_sec.currentTextChanged.connect(self._aplicar_filtros)

        self.combo_filtro_anio = QComboBox()
        self.combo_filtro_anio.addItems(["Todos los Años", "Sin asignar"])
        self.combo_filtro_anio.currentTextChanged.connect(self._aplicar_filtros)

        row2.addWidget(self.combo_filtro_pnf, 2)
        row2.addWidget(self.combo_filtro_tray, 1)
        row2.addWidget(self.combo_filtro_sec, 1)
        row2.addWidget(self.combo_filtro_anio, 1)
        filt_v.addLayout(row2)
        root.addWidget(filt_frame)

        # Tabla principal de bitácora
        self.table = QTableWidget(0, 12)
        self.table.setHorizontalHeaderLabels([
            "Fecha", "Hora", "Cédula", "Paciente", "PNF", "Trayecto",
            "Sección", "Año", "Tipo", "Evolución / Detalles", "Recordatorio", "ID"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeMode.Stretch)
        self.table.setColumnHidden(11, True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(self._abrir_historia_fila)
        root.addWidget(self.table, 1)

        # Barra inferior
        bottom = QHBoxLayout()
        self.lbl_count = QLabel("0 consultas registradas")
        self.lbl_count.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 500;")
        bottom.addWidget(self.lbl_count)
        bottom.addStretch()

        btn_abrir = QPushButton(" Abrir Historia Clínica")
        btn_abrir.setObjectName("btnPrimary")
        btn_abrir.setIcon(svg_icon("file-text", color="#ffffff", size=15))
        btn_abrir.clicked.connect(self._abrir_historia_seleccionada)
        bottom.addWidget(btn_abrir)

        btn_del = QPushButton(" Eliminar Registro")
        btn_del.setObjectName("btnDanger")
        btn_del.setIcon(svg_icon("trash", color="#dc2626", size=15))
        btn_del.clicked.connect(self._eliminar_registro)
        bottom.addWidget(btn_del)
        root.addLayout(bottom)

    def _make_kpi_card(self, parent_lay: QHBoxLayout, titulo: str, valor: str, color: str) -> QLabel:
        card = QFrame()
        card.setObjectName("kpiCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(2)
        lbl_t = QLabel(titulo)
        lbl_t.setStyleSheet("font-size: 12px; color: #64748b; font-weight: 600;")
        lbl_v = QLabel(valor)
        lbl_v.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
        v.addWidget(lbl_t)
        v.addWidget(lbl_v)
        parent_lay.addWidget(card, 1)
        return lbl_v

    def load_data(self):
        try:
            self._sesiones_cache = self.db.obtener_sesiones() if hasattr(self.db, "obtener_sesiones") else []
        except Exception:
            self._sesiones_cache = []
        try:
            self._pacientes_cache = self.db.obtener_pacientes() if hasattr(self.db, "obtener_pacientes") else []
        except Exception:
            self._pacientes_cache = []

        # Ordenar cronológicamente (más reciente primero)
        def _sort_key(s):
            d = QDate.fromString(s.get("fecha", ""), "dd/MM/yyyy")
            t = QTime.fromString(s.get("hora", "00:00"), "HH:mm")
            return (
                d.toString("yyyyMMdd") if d.isValid() else "00000000",
                t.toString("HHmm") if t.isValid() else "0000",
            )

        self._sesiones_cache.sort(key=_sort_key, reverse=True)
        self._actualizar_opciones_filtros()
        self._aplicar_filtros()

    def _resolver_paciente(self, s: dict) -> dict | None:
        pid = s.get("paciente_id", "")
        ced = (s.get("paciente_cedula", "") or "").strip().lower()
        if pid:
            pac = next((p for p in self._pacientes_cache if p.get("id") == pid), None)
            if pac:
                return pac
        if ced:
            return next(
                (p for p in self._pacientes_cache if (p.get("cedula", "") or "").strip().lower() == ced),
                None,
            )
        return None

    def _actualizar_opciones_filtros(self):
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

        prev_s = self.combo_filtro_sec.currentText()
        self.combo_filtro_sec.blockSignals(True)
        self.combo_filtro_sec.clear()
        self.combo_filtro_sec.addItems(["Todas las Secciones", "Sin asignar"] + secciones)
        self.combo_filtro_sec.setCurrentIndex(max(0, self.combo_filtro_sec.findText(prev_s)))
        self.combo_filtro_sec.blockSignals(False)

        prev_a = self.combo_filtro_anio.currentText()
        self.combo_filtro_anio.blockSignals(True)
        self.combo_filtro_anio.clear()
        self.combo_filtro_anio.addItems(["Todos los Años", "Sin asignar"] + anios)
        self.combo_filtro_anio.setCurrentIndex(max(0, self.combo_filtro_anio.findText(prev_a)))
        self.combo_filtro_anio.blockSignals(False)

    def _aplicar_filtros(self, *args):
        q = self.search_input.text().strip().lower()
        f_tipo = self.combo_filtro_tipo.currentText()
        f_pnf = self.combo_filtro_pnf.currentText()
        f_tray = self.combo_filtro_tray.currentText()
        f_sec = self.combo_filtro_sec.currentText()
        f_anio = self.combo_filtro_anio.currentText()
        usar_fecha = self.chk_fecha.isChecked()
        d_desde = self.date_desde.date()
        d_hasta = self.date_hasta.date()

        filtradas = []
        for s in self._sesiones_cache:
            pac = self._resolver_paciente(s)
            ced = (pac.get("cedula", "") if pac else s.get("paciente_cedula", "")) or ""
            nom = (pac.get("nombre", "") if pac else s.get("paciente_nombre", "")) or ""
            evo = s.get("evolucion", s.get("notas", "")) or ""
            rec = s.get("nota_recordatorio", "") or ""
            pnf = (pac.get("pnf", "") if pac else "") or ""
            tray = (pac.get("trayecto", "") if pac else "") or ""
            sec = normalize_seccion(pac.get("seccion", "")) if pac else ""
            anio = str(pac.get("anio_academico", "")).strip() if pac else ""
            tipo = s.get("tipo", "Sucesiva")

            if q and (
                q not in ced.lower()
                and q not in nom.lower()
                and q not in evo.lower()
                and q not in rec.lower()
            ):
                continue

            if f_tipo != "Tipo: Todos" and tipo != f_tipo:
                continue

            if f_pnf == "Sin asignar":
                if pnf:
                    continue
            elif f_pnf != "Todos los PNF" and pnf != f_pnf:
                continue

            if f_tray == "Sin asignar":
                if tray:
                    continue
            elif f_tray != "Todos los Trayectos" and tray != f_tray:
                continue

            if f_sec == "Sin asignar":
                if sec:
                    continue
            elif f_sec != "Todas las Secciones" and sec != f_sec:
                continue

            if f_anio == "Sin asignar":
                if anio:
                    continue
            elif f_anio != "Todos los Años" and anio != f_anio:
                continue

            if usar_fecha:
                ds = QDate.fromString(s.get("fecha", ""), "dd/MM/yyyy")
                if not ds.isValid() or not (d_desde <= ds <= d_hasta):
                    continue

            filtradas.append((s, pac))

        self._poblar_tabla(filtradas)

    def _poblar_tabla(self, registros: list):
        self.table.setRowCount(0)
        n_primera = 0
        n_sucesiva = 0
        pacientes_unicos = set()

        for i, (s, pac) in enumerate(registros):
            self.table.insertRow(i)
            ced = (pac.get("cedula", "") if pac else s.get("paciente_cedula", "")) or "—"
            nom = (pac.get("nombre", "") if pac else s.get("paciente_nombre", "")) or "—"
            pnf = (pac.get("pnf", "") if pac else "") or "Sin asignar"
            tray = (pac.get("trayecto", "") if pac else "") or "—"
            sec = (normalize_seccion(pac.get("seccion", "")) if pac else "") or "—"
            anio = (str(pac.get("anio_academico", "")).strip() if pac else "") or "—"
            tipo = s.get("tipo", "Sucesiva")
            evo = s.get("evolucion", s.get("notas", "")) or ""
            rec = s.get("nota_recordatorio", "") or ""
            pid = (pac.get("id", "") if pac else s.get("paciente_id", "")) or ""

            if tipo == "Primera vez":
                n_primera += 1
            else:
                n_sucesiva += 1
            if pid or ced != "—":
                pacientes_unicos.add(pid or ced)

            vals = [
                s.get("fecha", "—"),
                s.get("hora", "—"),
                ced,
                nom,
                pnf,
                tray,
                sec,
                anio,
                tipo,
                evo,
                rec,
                s.get("id", ""),
            ]
            for j, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if j == 8:
                    item.setForeground(QColor("#047857" if tipo == "Primera vez" else "#1d4ed8"))
                self.table.setItem(i, j, item)

            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, pid)

        total = len(registros)
        self.lbl_kpi_total.setText(str(total))
        self.lbl_kpi_primera.setText(str(n_primera))
        self.lbl_kpi_sucesiva.setText(str(n_sucesiva))
        self.lbl_kpi_pacientes.setText(str(len(pacientes_unicos)))
        self.lbl_count.setText(f"{total} consulta(s) mostrada(s) de {len(self._sesiones_cache)} registradas")

    def _limpiar_filtros(self):
        for w in (
            self.combo_filtro_tipo, self.combo_filtro_pnf,
            self.combo_filtro_tray, self.combo_filtro_sec, self.combo_filtro_anio
        ):
            w.blockSignals(True)
            w.setCurrentIndex(0)
            w.blockSignals(False)
        self.chk_fecha.blockSignals(True)
        self.chk_fecha.setChecked(False)
        self.chk_fecha.blockSignals(False)
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        self._aplicar_filtros()

    def _abrir_historia_seleccionada(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selección", "Selecciona un registro de la bitácora.")
            return
        self._abrir_historia_fila(self.table.item(rows[0].row(), 0))

    def _abrir_historia_fila(self, item):
        pid = self.table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        if not pid:
            QMessageBox.information(
                self, "Sin vínculo", "Este registro no tiene un paciente vinculado."
            )
            return
        self.abrir_historia_requested.emit(pid)

    def _eliminar_registro(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selección", "Selecciona un registro para eliminar.")
            return
        sid = self.table.item(rows[0].row(), 11).text()
        if not sid:
            return
        reply = QMessageBox.question(
            self, "Confirmar", "¿Eliminar esta consulta de la bitácora y del historial?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self.db, "eliminar_sesion") and self.db.eliminar_sesion(sid):
                self.load_data()
                self.sesion_actualizada.emit()
                QMessageBox.information(self, "✅", "Registro eliminado.")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el registro.")
