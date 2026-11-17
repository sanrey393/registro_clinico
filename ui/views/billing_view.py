from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QFormLayout, QFrame, QMessageBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt

class BillingView(QWidget):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        left_panel = QVBoxLayout()
        title_label = QLabel("Gestión de Facturación")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1a2744;")
        left_panel.addWidget(title_label)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["ID Paciente", "Concepto", "Monto", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        left_panel.addWidget(self.table)
        
        main_layout.addLayout(left_panel, 2)

        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 4)
        right_panel.setGraphicsEffect(shadow)

        form_layout = QVBoxLayout(right_panel)
        form_layout.setContentsMargins(20, 20, 20, 20)

        form_title = QLabel("Detalles de Factura")
        form_title.setStyleSheet("font-size: 16px; font-weight: bold; border: none;")
        form_layout.addWidget(form_title)

        f_layout = QFormLayout()
        self.input_paciente = QLineEdit()
        self.input_concepto = QLineEdit()
        self.input_monto = QDoubleSpinBox()
        self.input_monto.setMaximum(99999.99)
        self.input_estado = QLineEdit()
        self.input_estado.setPlaceholderText("Pendiente / Pagada")
        
        for widget in [self.input_paciente, self.input_concepto, self.input_estado]:
            widget.setStyleSheet("padding: 5px; border: 1px solid #ccc; border-radius: 4px;")

        f_layout.addRow("ID Paciente:", self.input_paciente)
        f_layout.addRow("Concepto:", self.input_concepto)
        f_layout.addRow("Monto ($):", self.input_monto)
        f_layout.addRow("Estado:", self.input_estado)
        
        form_layout.addLayout(f_layout)

        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar Factura")
        self.btn_guardar.setStyleSheet("background-color: #fd7e14; color: white; padding: 8px; border-radius: 5px; font-weight: bold;")
        self.btn_guardar.clicked.connect(self.save_data)
        
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setStyleSheet("background-color: #f0f3f8; color: #333; padding: 8px; border-radius: 5px;")
        self.btn_limpiar.clicked.connect(self.clear_form)

        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_limpiar)
        form_layout.addLayout(btn_layout)
        form_layout.addStretch()

        main_layout.addWidget(right_panel, 1)
        self.current_id = None

    def load_data(self):
        pass

    def clear_form(self):
        self.current_id = None
        self.input_paciente.clear()
        self.input_concepto.clear()
        self.input_monto.setValue(0.0)
        self.input_estado.clear()
        self.btn_guardar.setText("Guardar Factura")

    def save_data(self):
        datos = {
            "paciente_id": self.input_paciente.text(),
            "concepto": self.input_concepto.text(),
            "monto": self.input_monto.value(),
            "estado": self.input_estado.text() or "pendiente"
        }
        
        if not datos["paciente_id"]:
            QMessageBox.warning(self, "Error", "El ID del paciente es obligatorio.")
            return

        if self.current_id:
            self.db.actualizar_factura(self.current_id, datos)
            QMessageBox.information(self, "Éxito", "Factura actualizada.")
        else:
            self.db.crear_factura(datos)
            QMessageBox.information(self, "Éxito", "Factura creada exitosamente.")
            
        self.clear_form()
        self.load_data()
