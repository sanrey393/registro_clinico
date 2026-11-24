# ui/widgets/smart_date_edit.py
# Campo de fecha validado que permite escribir DD/MM/AAAA directamente o usar el calendario

from PyQt6.QtCore import Qt, QDate, pyqtSignal, QPoint
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QCalendarWidget, QFrame, QVBoxLayout
)
from ui.widgets.app_icons import svg_icon


class SmartDateEdit(QWidget):
    """
    Reemplazo amigable de QDateEdit:
    - Permite seleccionar todo (doble clic o arrastrar) y escribir números directamente (DD/MM/AAAA).
    - Formatea automáticamente las barras '/' sin trabar la tecla Backspace.
    - Valida fechas reales (dd/MM/yyyy entre 1900 y 2100) y ofrece botón de calendario 📅.
    """

    dateChanged = pyqtSignal(QDate)

    def __init__(self, initial_date: QDate | None = None, parent=None):
        super().__init__(parent)
        self._current_date = (
            initial_date if (initial_date and initial_date.isValid()) else QDate.currentDate()
        )
        self._popup = None
        self._calendar = None
        self._setup_ui()
        self.setDate(self._current_date)

    def _setup_ui(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)

        self.line_edit = QLineEdit()
        self.line_edit.setObjectName("smartDateInput")
        self.line_edit.setPlaceholderText("DD/MM/AAAA")
        self.line_edit.setMaxLength(10)
        self.line_edit.setToolTip(
            "Escribe la fecha con números (DD/MM/AAAA, ej: 15052002 → 15/05/2002) o usa el calendario."
        )
        self.line_edit.textEdited.connect(self._on_text_edited)
        self.line_edit.editingFinished.connect(self._on_editing_finished)
        lay.addWidget(self.line_edit, 1)

        self.btn_cal = QPushButton("")
        self.btn_cal.setObjectName("smartDateBtn")
        self.btn_cal.setIcon(svg_icon("calendar", color="#64748b", size=15))
        self.btn_cal.setFixedSize(32, 32)
        self.btn_cal.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cal.setToolTip("Abrir calendario")
        self.btn_cal.clicked.connect(self._toggle_calendar)
        lay.addWidget(self.btn_cal)

        self._apply_normal_style()

    def _apply_normal_style(self):
        self.line_edit.setStyleSheet("")

    def _apply_error_style(self):
        self.line_edit.setStyleSheet(
            "border: 1.5px solid #ef4444; background-color: rgba(239, 68, 68, 0.12);"
        )

    @staticmethod
    def _format_digits(digits: str) -> str:
        digits = digits[:8]
        if len(digits) <= 2:
            return digits
        if len(digits) <= 4:
            return f"{digits[:2]}/{digits[2:]}"
        return f"{digits[:2]}/{digits[2:4]}/{digits[4:]}"

    def _on_text_edited(self, raw_text: str):
        cursor_pos = self.line_edit.cursorPosition()
        digits_before_cursor = sum(1 for c in raw_text[:cursor_pos] if c.isdigit())
        digits = "".join(c for c in raw_text if c.isdigit())[:8]
        formatted = self._format_digits(digits)

        if formatted != raw_text:
            self.line_edit.blockSignals(True)
            self.line_edit.setText(formatted)
            self.line_edit.blockSignals(False)

        # Reposicionar cursor según cantidad de dígitos escritos
        new_pos = digits_before_cursor
        if digits_before_cursor > 2:
            new_pos += 1
        if digits_before_cursor > 4:
            new_pos += 1
        self.line_edit.setCursorPosition(min(new_pos, len(formatted)))

        if len(digits) == 8:
            d = QDate.fromString(formatted, "dd/MM/yyyy")
            if d.isValid() and 1900 <= d.year() <= 2100:
                self._apply_normal_style()
                if d != self._current_date:
                    self._current_date = d
                    self.dateChanged.emit(d)
            else:
                self._apply_error_style()
        else:
            self._apply_normal_style()

    def _on_editing_finished(self):
        digits = "".join(c for c in self.line_edit.text() if c.isdigit())
        if len(digits) == 8:
            d = QDate.fromString(self._format_digits(digits), "dd/MM/yyyy")
            if d.isValid() and 1900 <= d.year() <= 2100:
                self._apply_normal_style()
                if d != self._current_date:
                    self._current_date = d
                    self.dateChanged.emit(d)
                return
        # Restaurar última fecha válida si quedó incompleta o inválida
        self.setDate(self._current_date)
        self._apply_normal_style()

    def _toggle_calendar(self):
        if self._popup is None:
            self._popup = QFrame(self, Qt.WindowType.Popup)
            self._popup.setStyleSheet(
                "QFrame { background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; }"
            )
            p_lay = QVBoxLayout(self._popup)
            p_lay.setContentsMargins(6, 6, 6, 6)
            self._calendar = QCalendarWidget()
            self._calendar.setGridVisible(True)
            self._calendar.clicked.connect(self._on_calendar_picked)
            p_lay.addWidget(self._calendar)

        self._calendar.setSelectedDate(self._current_date)
        pos = self.mapToGlobal(QPoint(0, self.height() + 2))
        self._popup.move(pos)
        self._popup.show()

    def _on_calendar_picked(self, qdate: QDate):
        self.setDate(qdate)
        if self._popup:
            self._popup.hide()

    # ── API compatible con QDateEdit ─────────────────────────────
    def date(self) -> QDate:
        return self._current_date

    def setDate(self, qdate: QDate):
        if qdate and qdate.isValid():
            changed = qdate != self._current_date
            self._current_date = qdate
            self.line_edit.blockSignals(True)
            self.line_edit.setText(qdate.toString("dd/MM/yyyy"))
            self.line_edit.blockSignals(False)
            self._apply_normal_style()
            if changed:
                self.dateChanged.emit(qdate)

    def setCalendarPopup(self, enabled: bool):
        self.btn_cal.setVisible(bool(enabled))

    def setDisplayFormat(self, _fmt: str):
        pass

    def setStyleSheet(self, style: str):
        # Ignorar estilos pensados para QDateEdit para mantener el diseño limpio del input + botón
        pass
