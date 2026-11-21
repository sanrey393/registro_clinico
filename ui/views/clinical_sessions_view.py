# ui/views/clinical_sessions_view.py — Reescritura completa
# Módulo de Sesiones Clínicas con formulario médico completo

import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFrame, QMessageBox, QTextEdit, QComboBox, QDateTimeEdit,
    QFormLayout, QGridLayout, QTabWidget, QSizePolicy,
    QGraphicsDropShadowEffect, QCompleter, QScrollArea, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDateTime, QStringListModel, QSortFilterProxyModel
from PyQt6.QtGui import QColor, QFont

STYLE = """
QWidget { font-family: 'Segoe UI', 'Inter', sans-serif; font-size: 13px; }
QLabel { background: transparent; border: none; }
QLineEdit, QTextEdit, QComboBox, QDateTimeEdit, QDoubleSpinBox {
    border: 1.5px solid #e2e8f0;
    border-radius: 7px;
    padding: 5px 9px;
    background: #ffffff;
    color: #374151;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateTimeEdit:focus {
    border-color: #4d9ef7;
}
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    border: 1px solid #e2e8f0;
    selection-background-color: #e0f2fe;
    border-radius: 6px;
}
QTableWidget {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
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
QFrame#card {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}
QPushButton#btnPrimary {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #4d9ef7, stop:1 #3275e5);
    color: white; border: none; border-radius: 8px;
    font-weight: bold; padding: 9px 20px;
}
QPushButton#btnPrimary:hover { background: #3275e5; }
QPushButton#btnSuccess {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #10b981, stop:1 #059669);
    color: white; border: none; border-radius: 8px;
    font-weight: bold; padding: 9px 20px;
}
QPushButton#btnSuccess:hover { background: #059669; }
QPushButton#btnPdf {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #f59e0b, stop:1 #d97706);
    color: white; border: none; border-radius: 8px;
    font-weight: bold; padding: 9px 18px;
}
QPushButton#btnPdf:hover { background: #d97706; }
QPushButton#btnDanger {
    background: #fee2e2; color: #dc2626;
    border: 1px solid #fecaca; border-radius: 8px;
    font-weight: bold; padding: 8px 16px;
}
QPushButton#btnDanger:hover { background: #fecaca; }
QPushButton#btnSecondary {
    background: #f1f5f9; color: #475569;
    border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 8px 16px;
}
QPushButton#btnSecondary:hover { background: #e2e8f0; }
QTabWidget::pane { border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; }
QTabBar::tab {
    background: #f1f5f9; color: #64748b;
    padding: 8px 18px; margin-right: 2px;
    border-top-left-radius: 7px; border-top-right-radius: 7px;
    font-weight: 500;
}
QTabBar::tab:selected { background: #fff; color: #1a73e8; font-weight: bold; border-bottom: 2px solid #1a73e8; }
"""

class ClinicalSessionsView(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self._sesion_id = None
        self._pacientes_cache = []
        self.setStyleSheet(STYLE)
        self.setup_ui()
        if hasattr(self.db, "get_current_user_id") and self.db.get_current_user_id():
            self.load_data()

    def focus_new_form(self):
        self.clear_form()
        self.combo_paciente.setFocus()

    # ══════════════════════════════════════════════════════════
    # UI
    # ══════════════════════════════════════════════════════════

    def setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(14)

        # ── Columna izquierda: Lista + filtros ──
        root.addLayout(self._build_left_panel(), 2)

        # ── Columna derecha: Formulario ──
        root.addWidget(self._build_right_panel(), 3)

    # ── Panel izquierdo ──────────────────────────────────────

    def _build_left_panel(self) -> QVBoxLayout:
        lay = QVBoxLayout()
        lay.setSpacing(10)

        # Título
        t = QLabel("🏥  Sesiones Clínicas")
        t.setStyleSheet("font-size: 18px; font-weight: bold; color: #1a2744;")
        lay.addWidget(t)

        # Búsqueda rápida
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar por paciente o diagnóstico...")
        self.search_input.textChanged.connect(self._filtrar_tabla)
        lay.addWidget(self.search_input)

        # Tabla
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Paciente", "Fecha", "Tipo", "Diagnóstico", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.itemDoubleClicked.connect(self._cargar_sesion)
        lay.addWidget(self.table)

        # Contador
        self.lbl_count = QLabel("0 sesiones registradas")
        self.lbl_count.setStyleSheet("color: #6c757d; font-size: 12px;")
        lay.addWidget(self.lbl_count)

        # Botones inferiores
        btn_row = QHBoxLayout()
        btn_nueva = QPushButton("➕  Nueva Sesión")
        btn_nueva.setObjectName("btnSuccess")
        btn_nueva.clicked.connect(self.clear_form)
        btn_eliminar = QPushButton("🗑  Eliminar")
        btn_eliminar.setObjectName("btnDanger")
        btn_eliminar.clicked.connect(self._eliminar)
        btn_row.addWidget(btn_nueva)
        btn_row.addWidget(btn_eliminar)
        lay.addLayout(btn_row)

        return lay

    # ── Panel derecho: formulario médico ────────────────────

    def _build_right_panel(self) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        scroll = QScrollArea()
        scroll.setWidget(card)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        lay = QVBoxLayout(card)
        lay.setContentsMargins(20, 18, 20, 18)
        lay.setSpacing(12)

        # Título del formulario
        self.form_title = QLabel("📋  Nueva Sesión Clínica")
        self.form_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #1a2744;")
        lay.addWidget(self.form_title)

        sep = self._sep()
        lay.addWidget(sep)

        # ── Datos básicos ──
        grid1 = QGridLayout()
        grid1.setSpacing(8)

        # Paciente
        grid1.addWidget(self._lbl("👤 Paciente:"), 0, 0)
        self.combo_paciente = QComboBox()
        self.combo_paciente.setEditable(True)
        self.combo_paciente.setPlaceholderText("Buscar por nombre o cédula...")
        self.combo_paciente.lineEdit().setPlaceholderText("Buscar por nombre o cédula...")
        grid1.addWidget(self.combo_paciente, 0, 1, 1, 3)

        # Fecha y hora
        grid1.addWidget(self._lbl("📅 Fecha/Hora:"), 1, 0)
        self.input_fecha = QDateTimeEdit(QDateTime.currentDateTime())
        self.input_fecha.setDisplayFormat("dd/MM/yyyy  HH:mm")
        self.input_fecha.setCalendarPopup(True)
        grid1.addWidget(self.input_fecha, 1, 1)

        # Tipo de consulta
        grid1.addWidget(self._lbl("🏷 Tipo:"), 1, 2)
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems([
            "Primera vez", "Seguimiento", "Control",
            "Urgencia", "Procedimiento", "Teleconsulta"
        ])
        grid1.addWidget(self.combo_tipo, 1, 3)

        lay.addLayout(grid1)
        lay.addWidget(self._sep())

        # ── Motivo y anamnesis ──
        sec1 = self._section("📝  Consulta")
        lay.addWidget(sec1)

        grid2 = QGridLayout()
        grid2.setSpacing(8)
        grid2.addWidget(self._lbl("Motivo:"), 0, 0, Qt.AlignmentFlag.AlignTop)
        self.input_motivo = QTextEdit()
        self.input_motivo.setPlaceholderText("Motivo de consulta referido por el paciente...")
        self.input_motivo.setMaximumHeight(60)
        grid2.addWidget(self.input_motivo, 0, 1)

        grid2.addWidget(self._lbl("Enfermedad actual:"), 1, 0, Qt.AlignmentFlag.AlignTop)
        self.input_anamnesis = QTextEdit()
        self.input_anamnesis.setPlaceholderText("Historia de la enfermedad actual...")
        self.input_anamnesis.setMaximumHeight(70)
        grid2.addWidget(self.input_anamnesis, 1, 1)
        lay.addLayout(grid2)

        lay.addWidget(self._sep())

        # ── Examen físico ──
        sec2 = self._section("🩺  Examen Físico")
        lay.addWidget(sec2)

        grid3 = QGridLayout()
        grid3.setSpacing(8)

        vitals = [
            ("TA (mmHg):", "input_ta", "120/80"),
            ("FC (lpm):", "input_fc", "72"),
            ("FR (rpm):", "input_fr", "16"),
            ("Temp (°C):", "input_temp", "36.5"),
            ("Peso (kg):", "input_peso", "70"),
            ("Talla (m):", "input_talla", "1.70"),
        ]
        for i, (lbl, attr, ph) in enumerate(vitals):
            row, col = divmod(i, 3)
            grid3.addWidget(self._lbl(lbl), row, col * 2)
            field = QLineEdit()
            field.setPlaceholderText(ph)
            field.setMaximumWidth(90)
            setattr(self, attr, field)
            grid3.addWidget(field, row, col * 2 + 1)

        lay.addLayout(grid3)

        grid3b = QGridLayout()
        grid3b.setSpacing(8)
        grid3b.addWidget(self._lbl("Examen físico:"), 0, 0, Qt.AlignmentFlag.AlignTop)
        self.input_examen = QTextEdit()
        self.input_examen.setPlaceholderText("Hallazgos relevantes del examen físico...")
        self.input_examen.setMaximumHeight(70)
        grid3b.addWidget(self.input_examen, 0, 1)
        lay.addLayout(grid3b)

        lay.addWidget(self._sep())

        # ── Diagnóstico ──
        sec3 = self._section("🔬  Diagnóstico y Plan")
        lay.addWidget(sec3)

        grid4 = QGridLayout()
        grid4.setSpacing(8)

        grid4.addWidget(self._lbl("Diagnóstico:"), 0, 0, Qt.AlignmentFlag.AlignTop)
        self.input_diagnostico = QTextEdit()
        self.input_diagnostico.setPlaceholderText("Diagnóstico principal y diagnósticos diferenciales...")
        self.input_diagnostico.setMaximumHeight(60)
        grid4.addWidget(self.input_diagnostico, 0, 1)

        grid4.addWidget(self._lbl("Plan / Indicaciones:"), 1, 0, Qt.AlignmentFlag.AlignTop)
        self.input_plan = QTextEdit()
        self.input_plan.setPlaceholderText("Plan terapéutico, indicaciones médicas, paraclínicos...")
        self.input_plan.setMaximumHeight(70)
        grid4.addWidget(self.input_plan, 1, 1)

        grid4.addWidget(self._lbl("Próxima cita:"), 2, 0)
        self.input_proxima = QLineEdit()
        self.input_proxima.setPlaceholderText("Ej: 2 semanas, 1 mes...")
        grid4.addWidget(self.input_proxima, 2, 1)

        lay.addLayout(grid4)

        # ── Botones ──
        lay.addWidget(self._sep())
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_guardar = QPushButton("💾  Guardar Sesión")
        self.btn_guardar.setObjectName("btnPrimary")
        self.btn_guardar.clicked.connect(self.save_data)

        self.btn_imprimir = QPushButton("🖨️  Imprimir Sesión")
        self.btn_imprimir.setObjectName("btnPdf")
        self.btn_imprimir.clicked.connect(self._imprimir_sesion)

        btn_limpiar = QPushButton("✖  Limpiar")
        btn_limpiar.setObjectName("btnSecondary")
        btn_limpiar.clicked.connect(self.clear_form)

        btn_row.addWidget(self.btn_guardar)
        btn_row.addWidget(self.btn_imprimir)
        btn_row.addWidget(btn_limpiar)
        lay.addLayout(btn_row)

        # Retornamos el scroll que envuelve la tarjeta
        return scroll

    # ══════════════════════════════════════════════════════════
    # Lógica
    # ══════════════════════════════════════════════════════════

    def load_data(self):
        """Carga sesiones y pacientes desde Firebase."""
        try:
            self._pacientes_cache = self.db.obtener_pacientes()
        except Exception:
            self._pacientes_cache = []

        # Cargar nombres en combo paciente
        self.combo_paciente.clear()
        for p in self._pacientes_cache:
            cedula = p.get("cedula", "")
            nombre = p.get("nombre", "")
            self.combo_paciente.addItem(f"{nombre}  [{cedula}]", userData=p.get("id"))

        # Cargar sesiones
        try:
            sesiones = self.db.obtener_sesiones() if hasattr(self.db, "obtener_sesiones") else []
        except Exception:
            sesiones = []

        self._sesiones_cache = sesiones
        self._poblar_tabla(sesiones)

    def _poblar_tabla(self, sesiones: list):
        self.table.setRowCount(0)
        for i, s in enumerate(sesiones):
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(s.get("paciente_nombre", s.get("paciente_id", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(s.get("fecha", "")))
            self.table.setItem(i, 2, QTableWidgetItem(s.get("tipo", "")))
            self.table.setItem(i, 3, QTableWidgetItem(s.get("diagnostico", "")[:60]))
            # ID oculto
            id_item = QTableWidgetItem(s.get("id", ""))
            self.table.setItem(i, 4, id_item)

        self.lbl_count.setText(f"{len(sesiones)} sesión(es) registrada(s)")

    def _filtrar_tabla(self, text: str):
        q = text.lower()
        for row in range(self.table.rowCount()):
            visible = any(
                q in (self.table.item(row, col).text().lower() if self.table.item(row, col) else "")
                for col in range(4)
            )
            self.table.setRowHidden(row, not visible)

    def _cargar_sesion(self, item):
        """Doble clic en fila: carga la sesión en el formulario."""
        row = item.row()
        id_item = self.table.item(row, 4)
        if not id_item:
            return
        sesion_id = id_item.text()
        s = next((x for x in self._sesiones_cache if x.get("id") == sesion_id), None)
        if not s:
            return

        self._sesion_id = sesion_id

        # Paciente
        idx = self.combo_paciente.findData(s.get("paciente_id"))
        if idx >= 0:
            self.combo_paciente.setCurrentIndex(idx)
        else:
            self.combo_paciente.setCurrentText(s.get("paciente_nombre", ""))

        # Fecha
        try:
            fecha_str = s.get("fecha", "")
            dt = QDateTime.fromString(fecha_str, "dd/MM/yyyy  HH:mm")
            if dt.isValid():
                self.input_fecha.setDateTime(dt)
        except Exception:
            pass

        idx_tipo = self.combo_tipo.findText(s.get("tipo", ""))
        self.combo_tipo.setCurrentIndex(max(0, idx_tipo))

        self.input_motivo.setPlainText(s.get("motivo", ""))
        self.input_anamnesis.setPlainText(s.get("anamnesis", ""))
        self.input_ta.setText(s.get("ta", ""))
        self.input_fc.setText(s.get("fc", ""))
        self.input_fr.setText(s.get("fr", ""))
        self.input_temp.setText(s.get("temp", ""))
        self.input_peso.setText(s.get("peso", ""))
        self.input_talla.setText(s.get("talla", ""))
        self.input_examen.setPlainText(s.get("examen_fisico", ""))
        self.input_diagnostico.setPlainText(s.get("diagnostico", ""))
        self.input_plan.setPlainText(s.get("plan", ""))
        self.input_proxima.setText(s.get("proxima_cita", ""))
        self.form_title.setText("✏️  Editar Sesión Clínica")
        self.btn_guardar.setText("✏️  Actualizar")

    def save_data(self):
        paciente_text = self.combo_paciente.currentText().strip()
        if not paciente_text:
            QMessageBox.warning(self, "Campo requerido", "Selecciona un paciente.")
            return

        # Intentar obtener ID del paciente desde el combo
        paciente_id = self.combo_paciente.currentData()
        paciente_nombre = paciente_text.split("[")[0].strip()

        datos = {
            "paciente_id":     paciente_id or "",
            "paciente_nombre": paciente_nombre,
            "fecha":           self.input_fecha.dateTime().toString("dd/MM/yyyy  HH:mm"),
            "tipo":            self.combo_tipo.currentText(),
            "motivo":          self.input_motivo.toPlainText().strip(),
            "anamnesis":       self.input_anamnesis.toPlainText().strip(),
            "ta":              self.input_ta.text().strip(),
            "fc":              self.input_fc.text().strip(),
            "fr":              self.input_fr.text().strip(),
            "temp":            self.input_temp.text().strip(),
            "peso":            self.input_peso.text().strip(),
            "talla":           self.input_talla.text().strip(),
            "examen_fisico":   self.input_examen.toPlainText().strip(),
            "diagnostico":     self.input_diagnostico.toPlainText().strip(),
            "plan":            self.input_plan.toPlainText().strip(),
            "proxima_cita":    self.input_proxima.text().strip(),
        }

        try:
            if self._sesion_id:
                self.db._db.collection("sesiones").document(self._sesion_id).update(datos)
                QMessageBox.information(self, "✅ Éxito", "Sesión actualizada correctamente.")
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
                if hasattr(self.db, "crear_sesion"):
                    self.db.crear_sesion(datos)
                else:
                    self.db._db.collection("sesiones").add(datos)
                QMessageBox.information(self, "✅ Éxito", "Sesión registrada correctamente.")

            self.clear_form()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la sesión:\n{e}")

    def _eliminar(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "Selección", "Selecciona una sesión para eliminar.")
            return
        row = rows[0].row()
        id_item = self.table.item(row, 4)
        if not id_item or not id_item.text():
            return

        reply = QMessageBox.question(self, "Confirmar",
            "¿Eliminar esta sesión clínica?\nEsta acción no se puede deshacer.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db._db.collection("sesiones").document(id_item.text()).delete()
                self.clear_form()
                self.load_data()
                QMessageBox.information(self, "✅", "Sesión eliminada.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar:\n{e}")

    def _imprimir_sesion(self):
        """Genera e imprime la sesión actual en PDF."""
        paciente_text = self.combo_paciente.currentText().strip()
        if not paciente_text:
            QMessageBox.warning(self, "Incompleto", "Selecciona un paciente antes de imprimir la sesión.")
            return

        try:
            from ui.dialogs.pdf_generator import generar_pdf_sesion
            from PyQt6.QtWidgets import QFileDialog

            fecha_str = self.input_fecha.dateTime().toString("yyyyMMdd_HHmm")
            paciente_slug = paciente_text.split("[")[0].strip().replace(" ", "_")
            default_name = f"Sesion_{paciente_slug}_{fecha_str}.pdf"

            path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Sesión Clínica PDF", default_name, "PDF (*.pdf)"
            )
            if path:
                datos = {
                    "paciente_nombre": paciente_text,
                    "fecha":           self.input_fecha.dateTime().toString("dd/MM/yyyy  HH:mm"),
                    "tipo":            self.combo_tipo.currentText(),
                    "motivo":          self.input_motivo.toPlainText().strip(),
                    "anamnesis":       self.input_anamnesis.toPlainText().strip(),
                    "ta":              self.input_ta.text().strip(),
                    "fc":              self.input_fc.text().strip(),
                    "fr":              self.input_fr.text().strip(),
                    "temp":            self.input_temp.text().strip(),
                    "peso":            self.input_peso.text().strip(),
                    "talla":           self.input_talla.text().strip(),
                    "examen_fisico":   self.input_examen.toPlainText().strip(),
                    "diagnostico":     self.input_diagnostico.toPlainText().strip(),
                    "plan":            self.input_plan.toPlainText().strip(),
                    "proxima_cita":    self.input_proxima.text().strip(),
                }
                generar_pdf_sesion(path, datos)
                QMessageBox.information(self, "✅ PDF generado", f"Informe de sesión guardado en:\n{path}")
        except ImportError:
            QMessageBox.warning(self, "PDF no disponible", "Instala reportlab: pip install reportlab")
        except Exception as e:
            QMessageBox.critical(self, "Error al generar PDF", str(e))

    def clear_form(self):
        self._sesion_id = None
        self.combo_paciente.setCurrentIndex(-1)
        self.combo_paciente.clearEditText()
        self.input_fecha.setDateTime(QDateTime.currentDateTime())
        self.combo_tipo.setCurrentIndex(0)
        for attr in ("input_motivo", "input_anamnesis", "input_examen",
                     "input_diagnostico", "input_plan"):
            getattr(self, attr).clear()
        for attr in ("input_ta", "input_fc", "input_fr", "input_temp",
                     "input_peso", "input_talla", "input_proxima"):
            getattr(self, attr).clear()
        self.form_title.setText("📋  Nueva Sesión Clínica")
        self.btn_guardar.setText("💾  Guardar Sesión")

    # ── Helpers ──────────────────────────────────────────────

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

    @staticmethod
    def _section(title: str) -> QLabel:
        l = QLabel(title)
        l.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #3b82f6; "
            "background: #eff6ff; border-radius: 6px; padding: 4px 8px;"
        )
        return l
