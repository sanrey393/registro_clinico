# ui/views/identificacion_view.py
# Vista principal de Identificación del Paciente

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QFrame, QMessageBox, QComboBox,
    QDateEdit, QTextEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QSizePolicy, QFileDialog, QScrollArea,
    QGridLayout, QSpacerItem, QApplication
)
from PyQt6.QtCore import Qt, QDate, QSize, QTimer
from PyQt6.QtGui import QPixmap, QImage, QFont, QColor, QIntValidator


class IdentificacionView(QWidget):
    """
    Vista de inicio del sistema. Permite registrar y buscar pacientes.
    Layout:
      ┌─── Formulario Identificación ────┬─── Panel Foto ───┐
      │                                  │                  │
      ├──────── Listado de Pacientes ─────────────────────── ┤
      │  Búsqueda por cédula  [Buscar] [Ver Todo] [Anterior]│
      │  Tabla de pacientes                                  │
      └──────────────────────────────────────────────────────┘
    """

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
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        # ── Sección superior: Formulario + Foto ──
        top_row = QHBoxLayout()
        top_row.setSpacing(16)
        top_row.addWidget(self._build_form_panel(), 3)
        top_row.addWidget(self._build_photo_panel(), 1)
        root.addLayout(top_row)

        # ── Separador ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background: #dee2e6; max-height: 1px;")
        root.addWidget(sep)

        # ── Sección inferior: Listado + Búsqueda ──
        root.addWidget(self._build_listado_panel(), 1)

    # ══════════════════════════════════════════════════════════════
    # Panel Formulario de Identificación
    # ══════════════════════════════════════════════════════════════

    def _build_form_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet("""
            QFrame#rightPanel {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)

        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setOffset(0, 3)
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        # Título
        title = QLabel("🪪  Identificación")
        title.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #1a2744; "
            "border: none; background: transparent;"
        )
        layout.addWidget(title)

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
        grid.addWidget(self.input_nombre, row, 1)

        grid.addWidget(self._lbl("Sexo:"), row, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self.combo_sexo = QComboBox()
        self.combo_sexo.addItems(["Masculino", "Femenino", "Otro"])
        self.combo_sexo.setStyleSheet(self._combo_style())
        grid.addWidget(self.combo_sexo, row, 3)
        row += 1

        # ── Fila 2: Fecha Nac | Edad | Estado Civil ────────────
        grid.addWidget(self._lbl("F. Nacimiento:"), row, 0)
        self.input_fnac = QDateEdit()
        self.input_fnac.setCalendarPopup(True)
        self.input_fnac.setDisplayFormat("dd/MM/yyyy")
        self.input_fnac.setDate(QDate.currentDate().addYears(-25))
        self.input_fnac.setStyleSheet(self._field_style())
        self.input_fnac.dateChanged.connect(self._calcular_edad)
        grid.addWidget(self.input_fnac, row, 1)

        edad_civil_row = QHBoxLayout()
        edad_civil_row.setSpacing(8)

        self.lbl_edad = QLineEdit()
        self.lbl_edad.setReadOnly(True)
        self.lbl_edad.setPlaceholderText("Edad")
        self.lbl_edad.setMaximumWidth(70)
        self.lbl_edad.setStyleSheet(
            self._field_style() + "QLineEdit { background: #f8fafc; color: #475569; }"
        )

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

        # ── Fila 4: Aseguradora ────────────────────────────────
        grid.addWidget(self._lbl("Aseguradora:"), row, 0)
        self.input_aseguradora = self._field(placeholder="Nombre de la aseguradora")
        grid.addWidget(self.input_aseguradora, row, 1, 1, 3)
        row += 1

        # ── Fila 5: Email ──────────────────────────────────────
        grid.addWidget(self._lbl("Email:"), row, 0)
        email_row = QHBoxLayout()
        email_row.setSpacing(0)
        self.input_email = self._field(placeholder="correo@ejemplo.com")
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
        self.input_otros.setStyleSheet(
            "QTextEdit { border: 1.5px solid #e2e8f0; border-radius: 7px; "
            "padding: 6px; font-size: 13px; background: #ffffff; }"
            "QTextEdit:focus { border-color: #4d9ef7; }"
        )
        grid.addWidget(self.input_otros, row, 1, 1, 3)
        row += 1

        layout.addLayout(grid)

        # ── Botones Guardar / Cancelar ──────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.btn_guardar = QPushButton("💾  Guardar")
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #4d9ef7, stop:1 #3275e5);
                color: white; border: none; border-radius: 7px;
                font-size: 13px; font-weight: bold;
                padding: 8px 22px;
            }
            QPushButton:hover { background: #3275e5; }
        """)
        self.btn_guardar.clicked.connect(self._guardar)

        self.btn_imprimir = QPushButton("🖨️  Imprimir Expediente")
        self.btn_imprimir.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white; border: none; border-radius: 7px;
                font-size: 13px; font-weight: bold;
                padding: 8px 18px;
            }
            QPushButton:hover { background: #d97706; }
        """)
        self.btn_imprimir.clicked.connect(self._imprimir_expediente)

        self.btn_cancelar = QPushButton("✖  Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background: #f1f5f9; color: #64748b;
                border: 1px solid #e2e8f0; border-radius: 7px;
                font-size: 13px; padding: 8px 20px;
            }
            QPushButton:hover { background: #e2e8f0; color: #374151; }
        """)
        self.btn_cancelar.clicked.connect(self._cancelar)

        btn_row.addWidget(self.btn_guardar)
        btn_row.addWidget(self.btn_imprimir)
        btn_row.addWidget(self.btn_cancelar)
        layout.addLayout(btn_row)

        # Calcular edad al iniciar
        self._calcular_edad()

        return panel

    # ══════════════════════════════════════════════════════════════
    # Panel de Foto
    # ══════════════════════════════════════════════════════════════

    def _build_photo_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("rightPanel")
        panel.setStyleSheet("""
            QFrame#rightPanel {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
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
        panel.setStyleSheet("""
            QFrame#rightPanel {
                background: #ffffff;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)

        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 18))
        shadow.setOffset(0, 3)
        panel.setGraphicsEffect(shadow)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Título
        title = QLabel("👥  Listado de Pacientes")
        title.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #1a2744; "
            "border: none; background: transparent;"
        )
        layout.addWidget(title)

        # ── Sección Búsqueda ────────────────────────────────────
        busqueda_frame = QFrame()
        busqueda_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        busqueda_layout = QHBoxLayout(busqueda_frame)
        busqueda_layout.setContentsMargins(12, 8, 12, 8)
        busqueda_layout.setSpacing(10)

        lbl_busqueda = QLabel("🔍  Búsqueda:")
        lbl_busqueda.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #1a2744; "
            "border: none; background: transparent;"
        )
        busqueda_layout.addWidget(lbl_busqueda)

        # Selector prefijo cédula para búsqueda
        self.combo_busq_tipo = QComboBox()
        self.combo_busq_tipo.addItems(["V-", "E-", "P-", "J-"])
        self.combo_busq_tipo.setMaximumWidth(60)
        self.combo_busq_tipo.setStyleSheet(self._combo_style())
        busqueda_layout.addWidget(self.combo_busq_tipo)

        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Nº de cédula del paciente...")
        self.input_busqueda.setValidator(QIntValidator(0, 99999999))
        self.input_busqueda.setStyleSheet(
            "QLineEdit { border: 1.5px solid #e2e8f0; border-radius: 6px; "
            "padding: 6px 12px; font-size: 13px; background: white; max-width: 200px; }"
            "QLineEdit:focus { border-color: #4d9ef7; }"
        )
        self.input_busqueda.returnPressed.connect(self._buscar)
        busqueda_layout.addWidget(self.input_busqueda)

        btn_buscar = QPushButton("🔍  Buscar")
        btn_buscar.setStyleSheet(self._action_btn_style("#4d9ef7"))
        btn_buscar.clicked.connect(self._buscar)
        busqueda_layout.addWidget(btn_buscar)

        btn_ver_todo = QPushButton("📋  Ver Todo")
        btn_ver_todo.setStyleSheet(self._action_btn_style("#20c997"))
        btn_ver_todo.clicked.connect(self._ver_todo)
        busqueda_layout.addWidget(btn_ver_todo)

        btn_previa = QPushButton("⏮  Búsqueda Previa")
        btn_previa.setStyleSheet(self._action_btn_style("#6f42c1"))
        btn_previa.clicked.connect(self._restaurar_busqueda_previa)
        busqueda_layout.addWidget(btn_previa)

        busqueda_layout.addStretch()

        self.lbl_resultado_busq = QLabel("")
        self.lbl_resultado_busq.setStyleSheet(
            "font-size: 12px; color: #6c757d; border: none; background: transparent;"
        )
        busqueda_layout.addWidget(self.lbl_resultado_busq)

        layout.addWidget(busqueda_frame)

        # ── Tabla de Pacientes ──────────────────────────────────
        self.tabla_pacientes = QTableWidget(0, 6)
        self.tabla_pacientes.setHorizontalHeaderLabels([
            "Cédula", "Nombre Completo", "Edad", "Teléfono", "Email", "Aseguradora"
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

    def _guardar(self):
        """Valida y guarda el paciente en Firebase."""
        nombre = self.input_nombre.text().strip()
        cedula_num = self.input_cedula.text().strip()
        email = self.input_email.text().strip()

        if not nombre:
            QMessageBox.warning(self, "Campo requerido", "El nombre es obligatorio.")
            self.input_nombre.setFocus()
            return
        if not cedula_num:
            QMessageBox.warning(self, "Campo requerido", "La cédula es obligatoria.")
            self.input_cedula.setFocus()
            return
        if email and "@" not in email:
            QMessageBox.warning(self, "Email inválido", "El email debe contener @.")
            self.input_email.setFocus()
            return

        telefono_completo = (
            f"{self.combo_prefijo.currentText()}-{self.input_telefono.text()}"
            if self.input_telefono.text() else ""
        )
        cedula_completa = f"{self.combo_tipo_cedula.currentText()}{cedula_num}"

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
            # Mantener retrocompatibilidad con campos anteriores
            "motivo_consulta": self.input_otros.toPlainText().strip(),
        }

        try:
            if self._paciente_id_actual:
                datos["updated_at"] = True  # Se sobreescribe por SERVER_TIMESTAMP en manager
                # Actualizar preservando user_id existente
                self.db._db.collection("pacientes").document(
                    self._paciente_id_actual
                ).update(datos)
                QMessageBox.information(self, "✅ Éxito", "Paciente actualizado correctamente.")
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
                self.db.crear_paciente(datos)
                QMessageBox.information(self, "✅ Éxito", "Paciente registrado correctamente.")

            self._cancelar()
            self._cargar_pacientes()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{e}")

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
        self._quitar_foto()
        self.btn_guardar.setText("💾  Guardar")
        self._calcular_edad()

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
        self._poblar_tabla(self._pacientes_cache)

    def _poblar_tabla(self, pacientes: list):
        """Rellena la tabla con la lista de pacientes."""
        self.tabla_pacientes.setRowCount(0)
        for i, p in enumerate(pacientes):
            self.tabla_pacientes.insertRow(i)
            cedula   = p.get("cedula", p.get("id", ""))
            nombre   = p.get("nombre", "")
            edad     = str(p.get("edad", ""))
            telefono = p.get("telefono", "")
            email    = p.get("email", "")
            aseg     = p.get("aseguradora", "")

            items = [cedula, nombre, edad, telefono, email, aseg]
            for j, val in enumerate(items):
                item = QTableWidgetItem(val)
                self.tabla_pacientes.setItem(i, j, item)

            # Guardar ID oculto
            self.tabla_pacientes.item(i, 0).setData(
                Qt.ItemDataRole.UserRole, p.get("id")
            )

        n = len(pacientes)
        self.lbl_resultado_busq.setText(
            f"{n} paciente(s) encontrado(s)" if n else "Sin resultados"
        )

    def _buscar(self):
        """Busca pacientes por número de cédula."""
        tipo = self.combo_busq_tipo.currentText()
        num  = self.input_busqueda.text().strip()

        if not num:
            self._ver_todo()
            return

        # Guardar búsqueda previa
        self._cache_busqueda_previa = self._pacientes_cache.copy()

        busq = f"{tipo}{num}"
        encontrados = [
            p for p in self._pacientes_cache
            if busq.lower() in p.get("cedula", "").lower()
            or num in p.get("cedula", "")
        ]
        self._poblar_tabla(encontrados)

    def _ver_todo(self):
        """Muestra todos los pacientes."""
        self.input_busqueda.clear()
        self._poblar_tabla(self._pacientes_cache)

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

        self.btn_guardar.setText("✏️  Actualizar")
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
        l.setStyleSheet(
            "font-size: 13px; color: #374151; font-weight: 500; "
            "background: transparent; border: none;"
        )
        l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return l

    def _field(self, placeholder: str = "") -> QLineEdit:
        f = QLineEdit()
        f.setPlaceholderText(placeholder)
        f.setStyleSheet(self._field_style())
        return f

    @staticmethod
    def _field_style() -> str:
        return (
            "QLineEdit { border: 1.5px solid #e2e8f0; border-radius: 7px; "
            "padding: 6px 10px; font-size: 13px; background: #ffffff; color: #374151; }"
            "QLineEdit:focus { border-color: #4d9ef7; background: #fff; }"
        )

    @staticmethod
    def _combo_style() -> str:
        return (
            "QComboBox { border: 1.5px solid #e2e8f0; border-radius: 7px; "
            "padding: 5px 8px; font-size: 13px; background: #ffffff; color: #374151; }"
            "QComboBox:focus { border-color: #4d9ef7; }"
            "QComboBox::drop-down { border: none; width: 20px; }"
            "QComboBox QAbstractItemView { border: 1px solid #e2e8f0; "
            "selection-background-color: #e0f2fe; border-radius: 6px; }"
        )

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
