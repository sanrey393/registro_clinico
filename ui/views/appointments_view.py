# ui/views/appointments_view.py — Reescritura completa con calendario visual
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QComboBox, QDateEdit, QTimeEdit,
    QTextEdit, QTabWidget, QGridLayout, QSizePolicy,
    QGraphicsDropShadowEffect, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPalette

STYLE = """
QWidget { font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }
QLabel { background: transparent; border: none; }
QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {
    border: 1.5px solid #e2e8f0; border-radius: 7px;
    padding: 5px 9px; background: #ffffff; color: #374151;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border-color: #4d9ef7; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView { border: 1px solid #e2e8f0;
    selection-background-color: #e0f2fe; border-radius: 6px; }
QTableWidget { background: #fff; border: 1px solid #e2e8f0;
    border-radius: 8px; gridline-color: transparent;
    alternate-background-color: #f8fafc; }
QHeaderView::section { background: #f1f5f9; color: #475569;
    font-weight: bold; border: none; padding: 8px;
    border-bottom: 2px solid #cbd5e1; }
QTableWidget::item { padding: 6px; }
QTableWidget::item:selected { background: #dbeafe; color: #1e40af; }
QFrame#card { background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; }
QPushButton#btnPrimary { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #4d9ef7, stop:1 #3275e5); color: white; border: none;
    border-radius: 8px; font-weight: bold; padding: 9px 20px; }
QPushButton#btnPrimary:hover { background: #3275e5; }
QPushButton#btnSuccess { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
    stop:0 #10b981, stop:1 #059669); color: white; border: none;
    border-radius: 8px; font-weight: bold; padding: 9px 20px; }
QPushButton#btnDanger { background: #fee2e2; color: #dc2626;
    border: 1px solid #fecaca; border-radius: 8px;
    font-weight: bold; padding: 8px 16px; }
QPushButton#btnSecondary { background: #f1f5f9; color: #475569;
    border: 1px solid #e2e8f0; border-radius: 8px; padding: 8px 16px; }
QPushButton#btnSecondary:hover { background: #e2e8f0; }
QPushButton#dayBtn { background: transparent; border: 1px solid transparent;
    border-radius: 6px; font-size: 12px; padding: 4px; }
QPushButton#dayBtn:hover { background: #e0f2fe; border-color: #bae6fd; }
QPushButton#dayBtnToday { background: #3b82f6; color: white;
    border-radius: 6px; font-size: 12px; font-weight: bold; padding: 4px; }
QPushButton#dayBtnSelected { background: #dbeafe; border: 2px solid #3b82f6;
    border-radius: 6px; font-size: 12px; font-weight: bold; padding: 4px; }
QPushButton#dayBtnHasCitas { background: #f0fdf4;
    border: 1px solid #86efac; border-radius: 6px; font-size: 12px; padding: 4px; }
QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; }
QTabBar::tab { background: #f1f5f9; color: #64748b; padding: 8px 18px;
    margin-right: 2px; border-top-left-radius: 7px; border-top-right-radius: 7px; }
QTabBar::tab:selected { background: #fff; color: #1a73e8; font-weight: bold;
    border-bottom: 2px solid #1a73e8; }
"""

STATUS_COLORS = {
    "Programada":  "#3b82f6",
    "Confirmada":  "#10b981",
    "Completada":  "#6b7280",
    "Cancelada":   "#ef4444",
    "Reprogramada":"#f59e0b",
}


class CalendarWidget(QWidget):
    """Calendario mensual con indicadores de citas."""
    day_selected = pyqtSignal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_month = QDate.currentDate()
        self._selected = QDate.currentDate()
        self._citas_dates: set[str] = set()
        self._day_buttons: dict[str, QPushButton] = {}
        self._build()

    def set_citas_dates(self, dates: set[str]):
        self._citas_dates = dates
        self._refresh_buttons()

    def _build(self):
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(8, 8, 8, 8)
        self._root.setSpacing(6)
        self._build_nav()
        self._build_grid()

    def _build_nav(self):
        nav = QHBoxLayout()
        btn_prev = QPushButton("◀")
        btn_prev.setMaximumWidth(32)
        btn_prev.setObjectName("btnSecondary")
        btn_prev.clicked.connect(self._prev_month)

        self.lbl_month = QLabel()
        self.lbl_month.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_month.setStyleSheet("font-size: 14px; font-weight: bold; color: #1a2744;")

        btn_next = QPushButton("▶")
        btn_next.setMaximumWidth(32)
        btn_next.setObjectName("btnSecondary")
        btn_next.clicked.connect(self._next_month)

        nav.addWidget(btn_prev)
        nav.addWidget(self.lbl_month, 1)
        nav.addWidget(btn_next)
        self._root.addLayout(nav)

    def _build_grid(self):
        self._grid_widget = QWidget()
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(3)

        days_header = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
        for col, d in enumerate(days_header):
            lbl = QLabel(d)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("font-size: 11px; font-weight: bold; color: #64748b;")
            self._grid.addWidget(lbl, 0, col)

        self._root.addWidget(self._grid_widget)
        self._update_calendar()

    def _update_calendar(self):
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        self.lbl_month.setText(
            f"{meses[self._current_month.month()-1]}  {self._current_month.year()}"
        )

        # Limpiar botones anteriores
        for btn in self._day_buttons.values():
            btn.deleteLater()
        self._day_buttons.clear()

        first = QDate(self._current_month.year(), self._current_month.month(), 1)
        start_col = (first.dayOfWeek() - 1) % 7
        days_in_month = first.daysInMonth()
        today = QDate.currentDate()

        for day in range(1, days_in_month + 1):
            date = QDate(self._current_month.year(), self._current_month.month(), day)
            pos = start_col + day - 1
            row, col = divmod(pos, 7)

            btn = QPushButton(str(day))
            btn.setFixedSize(34, 30)
            date_str = date.toString("yyyy-MM-dd")

            if date == today:
                btn.setObjectName("dayBtnToday")
            elif date == self._selected:
                btn.setObjectName("dayBtnSelected")
            elif date_str in self._citas_dates:
                btn.setObjectName("dayBtnHasCitas")
                btn.setToolTip("Hay citas este día")
            else:
                btn.setObjectName("dayBtn")

            btn.clicked.connect(lambda _, d=date: self._on_day_clicked(d))
            self._grid.addWidget(btn, row + 1, col)
            self._day_buttons[date_str] = btn

    def _refresh_buttons(self):
        self._update_calendar()

    def _on_day_clicked(self, date: QDate):
        self._selected = date
        self._update_calendar()
        self.day_selected.emit(date)

    def _prev_month(self):
        self._current_month = self._current_month.addMonths(-1)
        self._update_calendar()

    def _next_month(self):
        self._current_month = self._current_month.addMonths(1)
        self._update_calendar()


class AppointmentsView(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._cita_id = None
        self._pacientes_cache = []
        self._citas_cache = []
        self.setStyleSheet(STYLE)
        self.setup_ui()
        if hasattr(self.db, "get_current_user_id") and self.db.get_current_user_id():
            self.load_data()

    def focus_new_form(self):
        self.clear_form()
        self.combo_paciente.setFocus()

    # ══════════════════════════════════════════════════════════
    # UI Principal
    # ══════════════════════════════════════════════════════════

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        # Izquierda: tabs calendario + lista
        tabs = QTabWidget()
        tabs.addTab(self._build_calendar_tab(), "  📅  Calendario  ")
        tabs.addTab(self._build_list_tab(), "  📋  Lista de Citas  ")
        root.addWidget(tabs, 3)

        # Derecha: formulario
        root.addWidget(self._build_form_panel(), 2)

    # ── Tab Calendario ───────────────────────────────────────

    def _build_calendar_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        self.calendar = CalendarWidget()
        self.calendar.day_selected.connect(self._on_day_selected)
        lay.addWidget(self.calendar)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height:1px;")
        lay.addWidget(sep)

        self.lbl_day_title = QLabel("Selecciona un día para ver las citas")
        self.lbl_day_title.setStyleSheet("font-weight: bold; color: #1a2744; font-size: 13px;")
        lay.addWidget(self.lbl_day_title)

        self.list_day_citas = QTableWidget(0, 3)
        self.list_day_citas.setHorizontalHeaderLabels(["Hora", "Paciente", "Estado"])
        self.list_day_citas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.list_day_citas.setMaximumHeight(160)
        self.list_day_citas.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.list_day_citas.verticalHeader().setVisible(False)
        self.list_day_citas.itemDoubleClicked.connect(self._cargar_cita_desde_calendario)
        lay.addWidget(self.list_day_citas)

        # Leyenda colores
        legend = QHBoxLayout()
        for status, color in STATUS_COLORS.items():
            dot = QLabel(f"● {status}")
            dot.setStyleSheet(f"color: {color}; font-size: 11px;")
            legend.addWidget(dot)
        legend.addStretch()
        lay.addLayout(legend)
        return w

    # ── Tab Lista ────────────────────────────────────────────

    def _build_list_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por paciente, fecha o estado...")
        self.search_input.textChanged.connect(self._filtrar_tabla)
        lay.addWidget(self.search_input)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Paciente", "Fecha", "Hora", "Tipo", "Estado"])
        for i in range(5):
            self.table.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Stretch if i in (0, 3) else QHeaderView.ResizeMode.ResizeToContents
            )
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(self._cargar_cita)
        lay.addWidget(self.table)

        btn_row = QHBoxLayout()
        btn_nueva = QPushButton("➕  Nueva Cita")
        btn_nueva.setObjectName("btnSuccess")
        btn_nueva.clicked.connect(self.clear_form)
        btn_eliminar = QPushButton("🗑  Eliminar")
        btn_eliminar.setObjectName("btnDanger")
        btn_eliminar.clicked.connect(self._eliminar)
        btn_row.addWidget(btn_nueva)
        btn_row.addWidget(btn_eliminar)
        btn_row.addStretch()
        self.lbl_count = QLabel("0 citas")
        self.lbl_count.setStyleSheet("color:#6c757d; font-size:12px;")
        btn_row.addWidget(self.lbl_count)
        lay.addLayout(btn_row)

        return w

    # ── Formulario ───────────────────────────────────────────

    def _build_form_panel(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)

        self.form_title = QLabel("📅  Nueva Cita")
        self.form_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a2744;")
        lay.addWidget(self.form_title)
        lay.addWidget(self._sep())

        grid = QGridLayout()
        grid.setSpacing(8)

        grid.addWidget(self._lbl("👤 Paciente:"), 0, 0)
        self.combo_paciente = QComboBox()
        self.combo_paciente.setEditable(True)
        self.combo_paciente.lineEdit().setPlaceholderText("Buscar paciente...")
        grid.addWidget(self.combo_paciente, 0, 1)

        grid.addWidget(self._lbl("📅 Fecha:"), 1, 0)
        self.input_fecha = QDateEdit(QDate.currentDate())
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDisplayFormat("dd/MM/yyyy")
        grid.addWidget(self.input_fecha, 1, 1)

        grid.addWidget(self._lbl("🕐 Hora:"), 2, 0)
        self.input_hora = QTimeEdit(QTime(8, 0))
        self.input_hora.setDisplayFormat("HH:mm")
        grid.addWidget(self.input_hora, 2, 1)

        grid.addWidget(self._lbl("🏷 Tipo:"), 3, 0)
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "Consulta general", "Control", "Primera vez",
            "Procedimiento", "Urgencia", "Teleconsulta"
        ])
        grid.addWidget(self.combo_tipo, 3, 1)

        grid.addWidget(self._lbl("🚦 Estado:"), 4, 0)
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(list(STATUS_COLORS.keys()))
        grid.addWidget(self.combo_estado, 4, 1)

        grid.addWidget(self._lbl("📝 Notas:"), 5, 0, Qt.AlignmentFlag.AlignTop)
        self.input_notas = QTextEdit()
        self.input_notas.setPlaceholderText("Observaciones o instrucciones para la cita...")
        self.input_notas.setMaximumHeight(80)
        grid.addWidget(self.input_notas, 5, 1)

        lay.addLayout(grid)
        lay.addWidget(self._sep())
        lay.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_guardar = QPushButton("💾  Guardar Cita")
        self.btn_guardar.setObjectName("btnPrimary")
        self.btn_guardar.clicked.connect(self.save_data)
        btn_cancel = QPushButton("✖  Limpiar")
        btn_cancel.setObjectName("btnSecondary")
        btn_cancel.clicked.connect(self.clear_form)
        btn_row.addWidget(self.btn_guardar)
        btn_row.addWidget(btn_cancel)
        lay.addLayout(btn_row)

        return card

    # ══════════════════════════════════════════════════════════
    # Lógica
    # ══════════════════════════════════════════════════════════

    def load_data(self):
        try:
            self._pacientes_cache = self.db.obtener_pacientes()
        except Exception:
            self._pacientes_cache = []

        self.combo_paciente.clear()
        for p in self._pacientes_cache:
            self.combo_paciente.addItem(
                f"{p.get('nombre', '')}  [{p.get('cedula', '')}]",
                userData=p.get("id")
            )

        try:
            self._citas_cache = (
                self.db.obtener_citas() if hasattr(self.db, "obtener_citas") else []
            )
        except Exception:
            self._citas_cache = []

        # Fechas con citas para el calendario
        dates_with_citas: set[str] = set()
        for c in self._citas_cache:
            fecha = c.get("fecha", "")
            try:
                d = QDate.fromString(fecha, "dd/MM/yyyy")
                if d.isValid():
                    dates_with_citas.add(d.toString("yyyy-MM-dd"))
            except Exception:
                pass
        self.calendar.set_citas_dates(dates_with_citas)

        self._poblar_tabla(self._citas_cache)

    def _poblar_tabla(self, citas: list):
        self.table.setRowCount(0)
        for i, c in enumerate(citas):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(c.get("paciente_nombre", "")))
            self.table.setItem(i, 1, QTableWidgetItem(c.get("fecha", "")))
            self.table.setItem(i, 2, QTableWidgetItem(c.get("hora", "")))
            self.table.setItem(i, 3, QTableWidgetItem(c.get("tipo", "")))
            status = c.get("estado", "")
            status_item = QTableWidgetItem(status)
            color = STATUS_COLORS.get(status, "#6b7280")
            status_item.setForeground(QColor(color))
            self.table.setItem(i, 4, status_item)
            # ID oculto en columna 0
            self.table.item(i, 0).setData(Qt.ItemDataRole.UserRole, c.get("id"))

        self.lbl_count.setText(f"{len(citas)} cita(s)")

    def _on_day_selected(self, date: QDate):
        fecha_str = date.toString("dd/MM/yyyy")
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                 "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        self.lbl_day_title.setText(
            f"Citas del {date.day()} de {meses[date.month()-1]} de {date.year()}"
        )
        citas_del_dia = [
            c for c in self._citas_cache if c.get("fecha") == fecha_str
        ]
        self.list_day_citas.setRowCount(0)
        for i, c in enumerate(citas_del_dia):
            self.list_day_citas.insertRow(i)
            self.list_day_citas.setItem(i, 0, QTableWidgetItem(c.get("hora", "")))
            self.list_day_citas.setItem(i, 1, QTableWidgetItem(c.get("paciente_nombre", "")))
            estado = c.get("estado", "")
            item = QTableWidgetItem(estado)
            item.setForeground(QColor(STATUS_COLORS.get(estado, "#6b7280")))
            self.list_day_citas.setItem(i, 2, item)
            self.list_day_citas.item(i, 0).setData(Qt.ItemDataRole.UserRole, c.get("id"))

        # También prefill la fecha en el formulario
        self.input_fecha.setDate(date)

    def _cargar_cita_desde_calendario(self, item):
        cita_id = self.list_day_citas.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        c = next((x for x in self._citas_cache if x.get("id") == cita_id), None)
        if c:
            self._rellenar_form(c)

    def _cargar_cita(self, item):
        cita_id = self.table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
        c = next((x for x in self._citas_cache if x.get("id") == cita_id), None)
        if c:
            self._rellenar_form(c)

    def _rellenar_form(self, c: dict):
        self._cita_id = c.get("id")
        idx = self.combo_paciente.findData(c.get("paciente_id"))
        if idx >= 0:
            self.combo_paciente.setCurrentIndex(idx)
        else:
            self.combo_paciente.setCurrentText(c.get("paciente_nombre", ""))

        d = QDate.fromString(c.get("fecha", ""), "dd/MM/yyyy")
        if d.isValid():
            self.input_fecha.setDate(d)
        t = QTime.fromString(c.get("hora", ""), "HH:mm")
        if t.isValid():
            self.input_hora.setTime(t)

        self.combo_tipo.setCurrentText(c.get("tipo", ""))
        self.combo_estado.setCurrentText(c.get("estado", ""))
        self.input_notas.setPlainText(c.get("notas", ""))
        self.form_title.setText("✏️  Editar Cita")
        self.btn_guardar.setText("✏️  Actualizar")

    def save_data(self):
        paciente_text = self.combo_paciente.currentText().strip()
        if not paciente_text:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un paciente.")
            return

        paciente_id = self.combo_paciente.currentData()
        paciente_nombre = paciente_text.split("[")[0].strip()

        datos = {
            "paciente_id":     paciente_id or "",
            "paciente_nombre": paciente_nombre,
            "fecha":           self.input_fecha.date().toString("dd/MM/yyyy"),
            "hora":            self.input_hora.time().toString("HH:mm"),
            "tipo":            self.combo_tipo.currentText(),
            "estado":          self.combo_estado.currentText(),
            "notas":           self.input_notas.toPlainText().strip(),
        }

        try:
            if self._cita_id:
                self.db._db.collection("citas").document(self._cita_id).update(datos)
                QMessageBox.information(self, "✅", "Cita actualizada.")
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
                if hasattr(self.db, "crear_cita"):
                    self.db.crear_cita(datos)
                else:
                    self.db._db.collection("citas").add(datos)
                QMessageBox.information(self, "✅", "Cita registrada.")
            self.clear_form()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

    def _eliminar(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selección", "Selecciona una cita para eliminar.")
            return
        cita_id = self.table.item(rows[0].row(), 0).data(Qt.ItemDataRole.UserRole)
        if not cita_id:
            return
        reply = QMessageBox.question(self, "Confirmar", "¿Eliminar esta cita?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db._db.collection("citas").document(cita_id).delete()
                self.clear_form()
                self.load_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    def _filtrar_tabla(self, text: str):
        q = text.lower()
        for row in range(self.table.rowCount()):
            visible = any(
                q in (self.table.item(row, col).text().lower() if self.table.item(row, col) else "")
                for col in range(5)
            )
            self.table.setRowHidden(row, not visible)

    def clear_form(self):
        self._cita_id = None
        self.combo_paciente.setCurrentIndex(-1)
        self.combo_paciente.clearEditText()
        self.input_fecha.setDate(QDate.currentDate())
        self.input_hora.setTime(QTime(8, 0))
        self.combo_tipo.setCurrentIndex(0)
        self.combo_estado.setCurrentIndex(0)
        self.input_notas.clear()
        self.form_title.setText("📅  Nueva Cita")
        self.btn_guardar.setText("💾  Guardar Cita")

    def on_item_selected(self):
        pass

    def _lbl(self, text: str) -> QLabel:
        l = QLabel(text)
        l.setStyleSheet("font-size: 12px; color: #374151; font-weight: 500;")
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return l
    @staticmethod
    def _sep() -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setStyleSheet("background: #e2e8f0; max-height: 1px; border: none;")
        return f

