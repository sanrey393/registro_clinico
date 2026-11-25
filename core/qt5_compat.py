# core/qt5_compat.py
# Capa de compatibilidad transparente PyQt6 -> PyQt5 para arquitectura 32 bits
# (Windows x86 y Linux i386/i686). Se importa antes que cualquier módulo PyQt.

import sys
import types

try:
    import PyQt6  # noqa: F401
    _HAS_PYQT6 = True
except ImportError:
    _HAS_PYQT6 = False

if not _HAS_PYQT6:
    from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg  # type: ignore

    # ── QtCore enum aliases (PyQt6 scoped enums -> PyQt5 flat enums) ──
    Qt = QtCore.Qt
    for _attr, _alias in [
        ("AlignmentFlag", Qt),
        ("ItemDataRole", Qt),
        ("CursorShape", Qt),
        ("WindowType", Qt),
        ("CheckState", Qt),
        ("Key", Qt),
        ("AspectRatioMode", Qt),
        ("TransformationMode", Qt),
        ("GlobalColor", Qt),
        ("Orientation", Qt),
        ("FocusPolicy", Qt),
        ("TextInteractionFlag", Qt),
        ("SortOrder", Qt),
        ("ScrollBarPolicy", Qt),
        ("PenStyle", Qt),
        ("BrushStyle", Qt),
        ("CaseSensitivity", Qt),
        ("DayOfWeek", Qt),
        ("DateFormat", Qt),
        ("ToolButtonStyle", Qt),
        ("TextElideMode", Qt),
        ("ItemFlag", Qt),
        ("MatchFlag", Qt),
        ("ContextMenuPolicy", Qt),
        ("WindowState", Qt),
        ("ApplicationAttribute", Qt),
    ]:
        if not hasattr(Qt, _attr):
            setattr(Qt, _attr, _alias)

    # ── QtGui moved classes & enum aliases ──
    for _cls_name in ("QAction", "QActionGroup", "QShortcut"):
        if not hasattr(QtGui, _cls_name) and hasattr(QtWidgets, _cls_name):
            setattr(QtGui, _cls_name, getattr(QtWidgets, _cls_name))

    if not hasattr(QtGui.QPainter, "RenderHint"):
        QtGui.QPainter.RenderHint = QtGui.QPainter
    if not hasattr(QtGui.QFont, "Weight"):
        QtGui.QFont.Weight = QtGui.QFont
    if not hasattr(QtGui.QPalette, "ColorRole"):
        QtGui.QPalette.ColorRole = QtGui.QPalette
    if not hasattr(QtGui.QPalette, "ColorGroup"):
        QtGui.QPalette.ColorGroup = QtGui.QPalette
    if not hasattr(QtGui.QKeySequence, "StandardKey"):
        QtGui.QKeySequence.StandardKey = QtGui.QKeySequence

    # ── QtWidgets enum aliases ──
    if not hasattr(QtWidgets.QFrame, "Shape"):
        QtWidgets.QFrame.Shape = QtWidgets.QFrame
    if not hasattr(QtWidgets.QFrame, "Shadow"):
        QtWidgets.QFrame.Shadow = QtWidgets.QFrame
    if not hasattr(QtWidgets.QHeaderView, "ResizeMode"):
        QtWidgets.QHeaderView.ResizeMode = QtWidgets.QHeaderView
    if not hasattr(QtWidgets.QAbstractItemView, "SelectionBehavior"):
        QtWidgets.QAbstractItemView.SelectionBehavior = QtWidgets.QAbstractItemView
    if not hasattr(QtWidgets.QAbstractItemView, "SelectionMode"):
        QtWidgets.QAbstractItemView.SelectionMode = QtWidgets.QAbstractItemView
    if not hasattr(QtWidgets.QAbstractItemView, "EditTrigger"):
        QtWidgets.QAbstractItemView.EditTrigger = QtWidgets.QAbstractItemView
    if not hasattr(QtWidgets.QTableWidget, "SelectionBehavior"):
        QtWidgets.QTableWidget.SelectionBehavior = QtWidgets.QAbstractItemView
    if not hasattr(QtWidgets.QTableWidget, "EditTrigger"):
        QtWidgets.QTableWidget.EditTrigger = QtWidgets.QAbstractItemView
    if not hasattr(QtWidgets.QMessageBox, "StandardButton"):
        QtWidgets.QMessageBox.StandardButton = QtWidgets.QMessageBox
    if not hasattr(QtWidgets.QMessageBox, "Icon"):
        QtWidgets.QMessageBox.Icon = QtWidgets.QMessageBox
    if not hasattr(QtWidgets.QDialog, "DialogCode"):
        QtWidgets.QDialog.DialogCode = QtWidgets.QDialog
    if not hasattr(QtWidgets.QSizePolicy, "Policy"):
        QtWidgets.QSizePolicy.Policy = QtWidgets.QSizePolicy
    if not hasattr(QtWidgets.QLineEdit, "EchoMode"):
        QtWidgets.QLineEdit.EchoMode = QtWidgets.QLineEdit
    if not hasattr(QtWidgets.QTabWidget, "TabPosition"):
        QtWidgets.QTabWidget.TabPosition = QtWidgets.QTabWidget

    # QFontMetrics.horizontalAdvance ya existe en PyQt5.11+; fallback por si acaso
    if not hasattr(QtGui.QFontMetrics, "horizontalAdvance"):
        QtGui.QFontMetrics.horizontalAdvance = QtGui.QFontMetrics.width

    # Registrar módulos falsos PyQt6.* apuntando a PyQt5.*
    pkg = types.ModuleType("PyQt6")
    pkg.QtCore = QtCore
    pkg.QtGui = QtGui
    pkg.QtWidgets = QtWidgets
    pkg.QtSvg = QtSvg
    sys.modules["PyQt6"] = pkg
    sys.modules["PyQt6.QtCore"] = QtCore
    sys.modules["PyQt6.QtGui"] = QtGui
    sys.modules["PyQt6.QtWidgets"] = QtWidgets
    sys.modules["PyQt6.QtSvg"] = QtSvg
