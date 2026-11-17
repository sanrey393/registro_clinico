# ui/dialogs/report_dialog.py
# Diálogo de Reportes del Sistema Clínico

import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


REPORT_STYLE = """
    QDialog {
        background: #f8fafc;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }
    QTabWidget::pane {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        background: #ffffff;
    }
    QTabBar::tab {
        background: #f1f5f9;
        color: #64748b;
        padding: 9px 20px;
        margin-right: 2px;
        border-top-left-radius: 7px;
        border-top-right-radius: 7px;
        font-size: 13px;
        font-weight: 500;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        color: #1a73e8;
        font-weight: bold;
        border-bottom: 2px solid #1a73e8;
    }
    QLabel#secTitle {
        font-size: 15px;
        font-weight: bold;
        color: #1a2744;
    }
    QLabel#kpiValue {
        font-size: 32px;
        font-weight: bold;
        color: #1a73e8;
    }
    QLabel#kpiLabel {
        font-size: 12px;
        color: #6c757d;
    }
    QFrame#kpiCard {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
    }
    QTableWidget {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        gridline-color: transparent;
        font-size: 13px;
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
    QTableWidget::item { padding: 7px; }
    QTableWidget::item:selected { background: #e0f2fe; color: #0369a1; }
    QPushButton#exportBtn {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #10b981, stop:1 #059669);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
        font-weight: bold;
        padding: 10px 22px;
    }
    QPushButton#exportBtn:hover {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #059669, stop:1 #047857);
    }
    QPushButton#refreshBtn {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 13px;
        padding: 9px 18px;
    }
    QPushButton#refreshBtn:hover { background: #e2e8f0; }
    QLabel { background: transparent; }
"""


class ReportDialog(QDialog):
    """Diálogo de reportes con resumen del sistema y exportación."""

    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("📊 Reportes del Sistema")
        self.setMinimumSize(700, 540)
        self.setStyleSheet(REPORT_STYLE)
        self._build_ui()
        self._cargar_datos()

    # ── UI ───────────────────────────────────────────────────────

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(14)

        # Cabecera
        header = QHBoxLayout()
        ico = QLabel("📊")
        ico.setStyleSheet("font-size: 30px;")
        header.addWidget(ico)
        header.addSpacing(8)
        col = QVBoxLayout()
        t = QLabel("Reportes del Sistema Clínico")
        t.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a2744;")
        s = QLabel(f"Generado: {datetime.datetime.now().strftime('%d/%m/%Y  %H:%M')}")
        s.setStyleSheet("font-size: 12px; color: #6c757d;")
        col.addWidget(t)
        col.addWidget(s)
        header.addLayout(col)
        header.addStretch()

        btn_refresh = QPushButton("🔄  Actualizar")
        btn_refresh.setObjectName("refreshBtn")
        btn_refresh.clicked.connect(self._cargar_datos)
        header.addWidget(btn_refresh)
        lay.addLayout(header)

        # Separador
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height:1px;")
        lay.addWidget(sep)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_summary_tab(), "  📋  Resumen  ")
        self.tabs.addTab(self._build_patients_tab(), "  👥  Pacientes  ")
        self.tabs.addTab(self._build_export_tab(), "  💾  Exportar  ")
        lay.addWidget(self.tabs)

    # ── Tab Resumen ──────────────────────────────────────────────

    def _build_summary_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(16)

        # KPI cards row
        self.kpi_row = QHBoxLayout()
        self.kpi_row.setSpacing(14)

        self.kpi_pacientes   = self._make_kpi("—", "Total Pacientes",   "#4d9ef7")
        self.kpi_citas_hoy   = self._make_kpi("—", "Citas Hoy",         "#6f42c1")
        self.kpi_sesiones    = self._make_kpi("—", "Sesiones Registradas", "#20c997")
        self.kpi_recetas     = self._make_kpi("—", "Recetas Emitidas",  "#e83e8c")

        self.kpi_row.addWidget(self.kpi_pacientes)
        self.kpi_row.addWidget(self.kpi_citas_hoy)
        self.kpi_row.addWidget(self.kpi_sesiones)
        self.kpi_row.addWidget(self.kpi_recetas)
        lay.addLayout(self.kpi_row)

        # Información del día
        day_lbl = QLabel("📅  Información de hoy")
        day_lbl.setObjectName("secTitle")
        lay.addWidget(day_lbl)

        hoy = datetime.datetime.now()
        self.info_hoy = QLabel(
            f"Fecha: <b>{hoy.strftime('%A, %d de %B de %Y')}</b>  |  "
            f"Hora: <b>{hoy.strftime('%H:%M')}</b>"
        )
        self.info_hoy.setTextFormat(Qt.TextFormat.RichText)
        self.info_hoy.setStyleSheet(
            "background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px;"
            "padding:12px; font-size:13px; color:#166534;"
        )
        lay.addWidget(self.info_hoy)
        lay.addStretch()

        return w

    def _make_kpi(self, value: str, label: str, color: str) -> QFrame:
        card = QFrame()
        card.setObjectName("kpiCard")
        card.setMinimumHeight(90)
        inner = QVBoxLayout(card)
        inner.setContentsMargins(16, 14, 16, 14)
        inner.setSpacing(2)

        v = QLabel(value)
        v.setObjectName("kpiValue")
        v.setStyleSheet(f"font-size: 30px; font-weight: bold; color: {color};")
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        l = QLabel(label)
        l.setObjectName("kpiLabel")
        l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        l.setWordWrap(True)

        inner.addWidget(v)
        inner.addWidget(l)
        # Guardar referencia al valor para actualizar
        card._value_label = v
        return card

    # ── Tab Pacientes ────────────────────────────────────────────

    def _build_patients_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(20, 20, 20, 20)
        lay.setSpacing(12)

        t = QLabel("Lista de Pacientes Registrados")
        t.setObjectName("secTitle")
        lay.addWidget(t)

        self.patients_table = QTableWidget(0, 4)
        self.patients_table.setHorizontalHeaderLabels(["Nombre", "Edad", "Teléfono", "Motivo"])
        self.patients_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.patients_table.setAlternatingRowColors(True)
        self.patients_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.patients_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        lay.addWidget(self.patients_table)

        return w

    # ── Tab Exportar ─────────────────────────────────────────────

    def _build_export_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        t = QLabel("Exportar Datos del Sistema")
        t.setObjectName("secTitle")
        lay.addWidget(t)

        desc = QLabel(
            "Exporta la información del sistema a un archivo de texto (TXT) o CSV.\n"
            "Incluye: listado de pacientes, resumen de citas y recetas."
        )
        desc.setStyleSheet("color: #6c757d; font-size: 13px;")
        desc.setWordWrap(True)
        lay.addWidget(desc)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #e2e8f0; max-height:1px;")
        lay.addWidget(sep)

        # Opciones de exportación
        opts_row = QHBoxLayout()
        opts_row.setSpacing(16)

        btn_txt = QPushButton("📄  Exportar como TXT")
        btn_txt.setObjectName("exportBtn")
        btn_txt.clicked.connect(lambda: self._exportar("txt"))

        btn_csv = QPushButton("📊  Exportar como CSV")
        btn_csv.setObjectName("exportBtn")
        btn_csv.setStyleSheet(
            btn_txt.styleSheet() +
            "QPushButton#exportBtn { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #6f42c1, stop:1 #5a32a3); }"
        )
        btn_csv.clicked.connect(lambda: self._exportar("csv"))

        btn_pdf = QPushButton("🖨️  Exportar como PDF")
        btn_pdf.setObjectName("exportBtn")
        btn_pdf.setStyleSheet(
            btn_txt.styleSheet() +
            "QPushButton#exportBtn { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            "stop:0 #dc2626, stop:1 #b91c1c); }"
        )
        btn_pdf.clicked.connect(lambda: self._exportar("pdf"))

        opts_row.addWidget(btn_txt)
        opts_row.addWidget(btn_csv)
        opts_row.addWidget(btn_pdf)
        lay.addLayout(opts_row)

        self.lbl_export_status = QLabel("")
        self.lbl_export_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_export_status.setStyleSheet("font-size: 13px; color: #10b981; font-weight: bold;")
        lay.addWidget(self.lbl_export_status)

        lay.addStretch()
        return w

    # ── Lógica ───────────────────────────────────────────────────

    def _cargar_datos(self):
        """Carga los datos desde Firebase y actualiza los KPIs."""
        try:
            pacientes = self.db.obtener_pacientes()
            n_pac = len(pacientes)
        except Exception:
            pacientes = []
            n_pac = 0

        # KPIs
        self.kpi_pacientes._value_label.setText(str(n_pac))
        self.kpi_citas_hoy._value_label.setText("—")
        self.kpi_sesiones._value_label.setText("—")
        self.kpi_recetas._value_label.setText("—")

        # Tabla de pacientes
        self.patients_table.setRowCount(0)
        for i, p in enumerate(pacientes):
            self.patients_table.insertRow(i)
            self.patients_table.setItem(i, 0, QTableWidgetItem(p.get("nombre", "—")))
            self.patients_table.setItem(i, 1, QTableWidgetItem(str(p.get("edad", "—"))))
            self.patients_table.setItem(i, 2, QTableWidgetItem(p.get("telefono", "—")))
            self.patients_table.setItem(i, 3, QTableWidgetItem(p.get("motivo_consulta", "—")))

        # Actualizar timestamp
        hoy = datetime.datetime.now()
        self.info_hoy.setText(
            f"Fecha: <b>{hoy.strftime('%A, %d de %B de %Y')}</b>  |  "
            f"Hora: <b>{hoy.strftime('%H:%M')}</b>  |  "
            f"Pacientes registrados: <b>{n_pac}</b>"
        )

    def _exportar(self, fmt: str):
        """Exporta los datos a TXT, CSV o PDF."""
        hoy = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar reporte",
            f"reporte_clinico_{hoy}.{fmt}",
            f"Archivos {fmt.upper()} (*.{fmt})"
        )
        if not filename:
            return

        try:
            pacientes = self.db.obtener_pacientes()
        except Exception:
            pacientes = []

        if fmt == "pdf":
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
                from reportlab.lib import colors
                from ui.dialogs.pdf_generator import _get_base_styles, NumberedCanvas

                doc = SimpleDocTemplate(filename, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=40)
                styles = _get_base_styles()
                story = []

                story.append(Paragraph("<b>REPORTE GENERAL DEL SISTEMA CLÍNICO</b>", styles['ClinicaTitle']))
                story.append(Paragraph(f"Emitido: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['ClinicaSubtitle']))
                story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb"), spaceBefore=4, spaceAfter=12))

                story.append(Paragraph(f"<b>Total Pacientes Registrados:</b> {len(pacientes)}", styles['DocSectionTitle']))
                story.append(Spacer(1, 8))

                table_data = [[
                    Paragraph("<b>Nombre</b>", styles['HeaderCell']),
                    Paragraph("<b>Edad</b>", styles['HeaderCell']),
                    Paragraph("<b>Teléfono</b>", styles['HeaderCell']),
                    Paragraph("<b>Motivo / Observaciones</b>", styles['HeaderCell'])
                ]]
                for p in pacientes:
                    table_data.append([
                        Paragraph(p.get("nombre", "—"), styles['CellTextBold']),
                        Paragraph(str(p.get("edad", "—")), styles['CellText']),
                        Paragraph(p.get("telefono", "—"), styles['CellText']),
                        Paragraph(p.get("motivo_consulta", p.get("otros_datos", "—"))[:60], styles['CellText'])
                    ])
                if len(table_data) == 1:
                    table_data.append([
                        Paragraph("Sin pacientes", styles['CellText']),
                        Paragraph("—", styles['CellText']),
                        Paragraph("—", styles['CellText']),
                        Paragraph("—", styles['CellText'])
                    ])

                t = Table(table_data, colWidths=[180, 50, 110, 200])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2563eb")),
                    ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
                    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]))
                story.append(t)
                doc.build(story, canvasmaker=NumberedCanvas)
            except Exception as e:
                QMessageBox.critical(self, "Error al generar PDF", str(e))
                return
        else:
            with open(filename, "w", encoding="utf-8") as f:
                if fmt == "txt":
                    f.write("=" * 60 + "\n")
                    f.write("   REPORTE SISTEMA DE REGISTRO CLÍNICO\n")
                    f.write(f"   Generado: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(f"TOTAL PACIENTES: {len(pacientes)}\n\n")
                    f.write("LISTADO DE PACIENTES:\n")
                    f.write("-" * 60 + "\n")
                    for p in pacientes:
                        f.write(f"  Nombre   : {p.get('nombre', '—')}\n")
                        f.write(f"  Edad     : {p.get('edad', '—')}\n")
                        f.write(f"  Teléfono : {p.get('telefono', '—')}\n")
                        f.write(f"  Motivo   : {p.get('motivo_consulta', '—')}\n")
                        f.write("-" * 40 + "\n")
                else:  # csv
                    f.write("Nombre,Edad,Teléfono,Email,Motivo de Consulta\n")
                    for p in pacientes:
                        nombre   = p.get("nombre", "").replace(",", ";")
                        edad     = str(p.get("edad", ""))
                        tel      = p.get("telefono", "").replace(",", ";")
                        email    = p.get("email", "").replace(",", ";")
                        motivo   = p.get("motivo_consulta", "").replace(",", ";")
                        f.write(f"{nombre},{edad},{tel},{email},{motivo}\n")

        self.lbl_export_status.setText(f"✅ Reporte exportado exitosamente: {filename.split('/')[-1].split(chr(92))[-1]}")
        QTimer.singleShot(5000, lambda: self.lbl_export_status.setText(""))
