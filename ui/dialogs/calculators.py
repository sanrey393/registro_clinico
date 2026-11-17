# ui/dialogs/calculators.py
# Diálogos de calculadoras clínicas: IMC, Dosis y Edad

import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFormLayout, QFrame, QDateEdit, QComboBox,
    QDoubleSpinBox, QSpinBox, QWidget, QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor


# ══════════════════════════════════════════════════════════════════
# Estilo compartido para todos los diálogos
# ══════════════════════════════════════════════════════════════════

DIALOG_STYLE = """
    QDialog {
        background: #f8fafc;
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }
    QLabel#dlgTitle {
        font-size: 20px;
        font-weight: bold;
        color: #1a2744;
    }
    QLabel#dlgSubtitle {
        font-size: 13px;
        color: #6c757d;
    }
    QLabel#resultBox {
        background: #e8f4fd;
        border: 1.5px solid #90cdf4;
        border-radius: 10px;
        padding: 16px;
        font-size: 15px;
        color: #1a365d;
        font-weight: bold;
    }
    QLineEdit, QDoubleSpinBox, QSpinBox, QDateEdit, QComboBox {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 7px;
        padding: 7px 12px;
        font-size: 14px;
        color: #2d3748;
        min-height: 32px;
    }
    QLineEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus,
    QDateEdit:focus, QComboBox:focus {
        border: 1.5px solid #4d9ef7;
    }
    QPushButton#calcBtn {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #4d9ef7, stop:1 #3275e5);
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 15px;
        font-weight: bold;
        padding: 10px 24px;
    }
    QPushButton#calcBtn:hover {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
            stop:0 #3275e5, stop:1 #285ec2);
    }
    QPushButton#clearBtn {
        background: #f1f5f9;
        color: #64748b;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        font-size: 14px;
        padding: 10px 20px;
    }
    QPushButton#clearBtn:hover {
        background: #e2e8f0;
    }
    QFrame#divider {
        background: #e2e8f0;
        max-height: 1px;
    }
    QLabel { background: transparent; }
"""


def _header(icon: str, title: str, subtitle: str) -> QWidget:
    """Cabecera con ícono, título y subtítulo."""
    w = QWidget()
    lay = QVBoxLayout(w)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(4)

    top = QHBoxLayout()
    ico = QLabel(icon)
    ico.setStyleSheet("font-size: 32px; background: transparent;")
    top.addWidget(ico)
    top.addSpacing(8)

    text_col = QVBoxLayout()
    t = QLabel(title)
    t.setObjectName("dlgTitle")
    s = QLabel(subtitle)
    s.setObjectName("dlgSubtitle")
    text_col.addWidget(t)
    text_col.addWidget(s)
    top.addLayout(text_col)
    top.addStretch()
    lay.addLayout(top)
    return w


def _divider() -> QFrame:
    d = QFrame()
    d.setObjectName("divider")
    d.setFrameShape(QFrame.Shape.HLine)
    return d


# ══════════════════════════════════════════════════════════════════
# Diálogo IMC
# ══════════════════════════════════════════════════════════════════

class IMCDialog(QDialog):
    """Calculadora de Índice de Masa Corporal."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculadora de IMC")
        self.setMinimumWidth(420)
        self.setStyleSheet(DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        lay.addWidget(_header("⚖️", "Calculadora de IMC",
                               "Índice de Masa Corporal — clasificación OMS"))
        lay.addWidget(_divider())

        # Formulario
        form = QFormLayout()
        form.setSpacing(12)

        self.spin_peso = QDoubleSpinBox()
        self.spin_peso.setRange(1, 500)
        self.spin_peso.setDecimals(1)
        self.spin_peso.setSuffix("  kg")
        self.spin_peso.setValue(70.0)

        self.spin_talla = QDoubleSpinBox()
        self.spin_talla.setRange(30, 250)
        self.spin_talla.setDecimals(1)
        self.spin_talla.setSuffix("  cm")
        self.spin_talla.setValue(170.0)

        self.combo_sexo = QComboBox()
        self.combo_sexo.addItems(["Masculino", "Femenino"])

        form.addRow("Peso:", self.spin_peso)
        form.addRow("Talla:", self.spin_talla)
        form.addRow("Sexo:", self.combo_sexo)
        lay.addLayout(form)

        # Resultado
        self.lbl_result = QLabel("Ingresa los datos y presiona Calcular.")
        self.lbl_result.setObjectName("resultBox")
        self.lbl_result.setWordWrap(True)
        self.lbl_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_result.setMinimumHeight(70)
        lay.addWidget(self.lbl_result)

        # Tabla de referencia
        ref = QLabel(
            "<b>Clasificación OMS:</b>  "
            "< 18.5 Bajo peso &nbsp;|&nbsp; "
            "18.5–24.9 Normal &nbsp;|&nbsp; "
            "25–29.9 Sobrepeso &nbsp;|&nbsp; "
            "≥ 30 Obesidad"
        )
        ref.setStyleSheet("font-size: 11px; color: #6c757d;")
        ref.setWordWrap(True)
        lay.addWidget(ref)

        # Botones
        btns = QHBoxLayout()
        btn_calc = QPushButton("⚡  Calcular")
        btn_calc.setObjectName("calcBtn")
        btn_calc.clicked.connect(self._calcular)

        btn_clear = QPushButton("Limpiar")
        btn_clear.setObjectName("clearBtn")
        btn_clear.clicked.connect(self._limpiar)

        btns.addWidget(btn_calc)
        btns.addWidget(btn_clear)
        lay.addLayout(btns)

    def _calcular(self):
        peso = self.spin_peso.value()
        talla_cm = self.spin_talla.value()
        talla_m = talla_cm / 100.0
        imc = peso / (talla_m ** 2)

        if imc < 18.5:
            cat = "⚠️ Bajo peso"
            color = "#fef3c7"
            border = "#f59e0b"
            text_color = "#92400e"
        elif imc < 25:
            cat = "✅ Peso normal"
            color = "#d1fae5"
            border = "#10b981"
            text_color = "#065f46"
        elif imc < 30:
            cat = "🟠 Sobrepeso"
            color = "#ffedd5"
            border = "#f97316"
            text_color = "#7c2d12"
        else:
            cat = "🔴 Obesidad"
            color = "#fee2e2"
            border = "#ef4444"
            text_color = "#7f1d1d"

        self.lbl_result.setStyleSheet(f"""
            QLabel {{
                background: {color};
                border: 1.5px solid {border};
                border-radius: 10px;
                padding: 16px;
                font-size: 16px;
                color: {text_color};
                font-weight: bold;
            }}
        """)
        self.lbl_result.setText(
            f"IMC = {imc:.2f}  →  {cat}\n"
            f"Peso: {peso} kg  |  Talla: {talla_cm} cm"
        )

    def _limpiar(self):
        self.spin_peso.setValue(70.0)
        self.spin_talla.setValue(170.0)
        self.lbl_result.setStyleSheet(DIALOG_STYLE + " QLabel#resultBox { background:#e8f4fd; border:1.5px solid #90cdf4; color:#1a365d; }")
        self.lbl_result.setText("Ingresa los datos y presiona Calcular.")


# ══════════════════════════════════════════════════════════════════
# Diálogo Calculadora de Dosis
# ══════════════════════════════════════════════════════════════════

class DosisDialog(QDialog):
    """Calculadora de dosis por peso corporal (mg/kg)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculadora de Dosis")
        self.setMinimumWidth(430)
        self.setStyleSheet(DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        lay.addWidget(_header("💊", "Calculadora de Dosis",
                               "Calcula la dosis total según peso corporal"))
        lay.addWidget(_divider())

        form = QFormLayout()
        form.setSpacing(12)

        self.input_medicamento = QLineEdit()
        self.input_medicamento.setPlaceholderText("Ej. Amoxicilina")

        self.spin_peso = QDoubleSpinBox()
        self.spin_peso.setRange(0.5, 300)
        self.spin_peso.setDecimals(1)
        self.spin_peso.setSuffix("  kg")
        self.spin_peso.setValue(70.0)

        self.spin_dosis_kg = QDoubleSpinBox()
        self.spin_dosis_kg.setRange(0.01, 1000)
        self.spin_dosis_kg.setDecimals(2)
        self.spin_dosis_kg.setSuffix("  mg/kg")
        self.spin_dosis_kg.setValue(10.0)

        self.spin_frecuencia = QSpinBox()
        self.spin_frecuencia.setRange(1, 24)
        self.spin_frecuencia.setSuffix("  veces/día")
        self.spin_frecuencia.setValue(3)

        self.spin_dias = QSpinBox()
        self.spin_dias.setRange(1, 365)
        self.spin_dias.setSuffix("  días")
        self.spin_dias.setValue(7)

        form.addRow("Medicamento:", self.input_medicamento)
        form.addRow("Peso del paciente:", self.spin_peso)
        form.addRow("Dosis estándar:", self.spin_dosis_kg)
        form.addRow("Frecuencia:", self.spin_frecuencia)
        form.addRow("Duración del tratamiento:", self.spin_dias)
        lay.addLayout(form)

        self.lbl_result = QLabel("Ingresa los datos y presiona Calcular.")
        self.lbl_result.setObjectName("resultBox")
        self.lbl_result.setWordWrap(True)
        self.lbl_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_result.setMinimumHeight(90)
        lay.addWidget(self.lbl_result)

        btns = QHBoxLayout()
        btn_calc = QPushButton("⚡  Calcular")
        btn_calc.setObjectName("calcBtn")
        btn_calc.clicked.connect(self._calcular)

        btn_clear = QPushButton("Limpiar")
        btn_clear.setObjectName("clearBtn")
        btn_clear.clicked.connect(self._limpiar)

        btns.addWidget(btn_calc)
        btns.addWidget(btn_clear)
        lay.addLayout(btns)

    def _calcular(self):
        peso = self.spin_peso.value()
        dosis_kg = self.spin_dosis_kg.value()
        freq = self.spin_frecuencia.value()
        dias = self.spin_dias.value()
        med = self.input_medicamento.text() or "Medicamento"

        dosis_total_dia = peso * dosis_kg
        dosis_por_toma = dosis_total_dia / freq
        dosis_total_tratamiento = dosis_total_dia * dias

        self.lbl_result.setText(
            f"<b>{med}</b><br>"
            f"Dosis por toma: <b>{dosis_por_toma:.1f} mg</b>  "
            f"({freq}x/día)<br>"
            f"Dosis diaria total: <b>{dosis_total_dia:.1f} mg</b><br>"
            f"Total del tratamiento ({dias} días): <b>{dosis_total_tratamiento:.1f} mg</b>"
        )
        self.lbl_result.setTextFormat(Qt.TextFormat.RichText)

    def _limpiar(self):
        self.input_medicamento.clear()
        self.spin_peso.setValue(70.0)
        self.spin_dosis_kg.setValue(10.0)
        self.spin_frecuencia.setValue(3)
        self.spin_dias.setValue(7)
        self.lbl_result.setText("Ingresa los datos y presiona Calcular.")


# ══════════════════════════════════════════════════════════════════
# Diálogo Calculadora de Edad
# ══════════════════════════════════════════════════════════════════

class EdadDialog(QDialog):
    """Calcula la edad exacta (años, meses, días) desde la fecha de nacimiento."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculadora de Edad")
        self.setMinimumWidth(400)
        self.setStyleSheet(DIALOG_STYLE)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(16)

        lay.addWidget(_header("🎂", "Calculadora de Edad",
                               "Calcula la edad exacta en años, meses y días"))
        lay.addWidget(_divider())

        form = QFormLayout()
        form.setSpacing(12)

        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del paciente (opcional)")

        self.date_nacimiento = QDateEdit()
        self.date_nacimiento.setCalendarPopup(True)
        self.date_nacimiento.setDisplayFormat("dd/MM/yyyy")
        # Por defecto: hace 30 años
        hoy = QDate.currentDate()
        self.date_nacimiento.setDate(hoy.addYears(-30))
        self.date_nacimiento.setMaximumDate(hoy)

        self.date_referencia = QDateEdit()
        self.date_referencia.setCalendarPopup(True)
        self.date_referencia.setDisplayFormat("dd/MM/yyyy")
        self.date_referencia.setDate(hoy)

        form.addRow("Paciente:", self.input_nombre)
        form.addRow("Fecha de nacimiento:", self.date_nacimiento)
        form.addRow("Fecha de referencia:", self.date_referencia)
        lay.addLayout(form)

        self.lbl_result = QLabel("Ingresa la fecha de nacimiento y presiona Calcular.")
        self.lbl_result.setObjectName("resultBox")
        self.lbl_result.setWordWrap(True)
        self.lbl_result.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_result.setMinimumHeight(90)
        lay.addWidget(self.lbl_result)

        btns = QHBoxLayout()
        btn_calc = QPushButton("⚡  Calcular")
        btn_calc.setObjectName("calcBtn")
        btn_calc.clicked.connect(self._calcular)

        btn_hoy = QPushButton("Fecha de hoy")
        btn_hoy.setObjectName("clearBtn")
        btn_hoy.clicked.connect(lambda: self.date_referencia.setDate(QDate.currentDate()))

        btns.addWidget(btn_calc)
        btns.addWidget(btn_hoy)
        lay.addLayout(btns)

    def _calcular(self):
        nac = self.date_nacimiento.date()
        ref = self.date_referencia.date()

        if nac >= ref:
            self.lbl_result.setText("⚠️ La fecha de nacimiento debe ser anterior a la fecha de referencia.")
            return

        # Cálculo exacto de años, meses y días
        anios = ref.year() - nac.year()
        meses = ref.month() - nac.month()
        dias  = ref.day()  - nac.day()

        if dias < 0:
            meses -= 1
            # Días del mes anterior
            prev_month = ref.addMonths(-1)
            dias += prev_month.daysInMonth()

        if meses < 0:
            anios -= 1
            meses += 12

        nombre = self.input_nombre.text()
        prefijo = f"<b>{nombre}</b><br>" if nombre else ""

        # Clasificación por etapa
        if anios < 1:
            etapa = f"🍼 Lactante ({meses} meses)"
        elif anios < 3:
            etapa = f"👶 Infante"
        elif anios < 12:
            etapa = f"🧒 Niño/a"
        elif anios < 18:
            etapa = f"🧑 Adolescente"
        elif anios < 65:
            etapa = f"🧑‍💼 Adulto/a"
        else:
            etapa = f"👴 Adulto mayor"

        total_dias = nac.daysTo(ref)

        self.lbl_result.setTextFormat(Qt.TextFormat.RichText)
        self.lbl_result.setText(
            f"{prefijo}"
            f"Edad: <b>{anios} años, {meses} meses, {dias} días</b><br>"
            f"Etapa vital: <b>{etapa}</b><br>"
            f"Total de días vividos: <b>{total_dias:,}</b>"
        )
