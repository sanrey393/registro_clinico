import sys
import os
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def load_stylesheet(app):
    # Cargar los estilos desde el archivo QSS
    from core.app_paths import resource_path
    style_path = resource_path(os.path.join("styles", "theme.qss"))
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Advertencia: No se encontró theme.qss. Usando estilos por defecto.")


def main():
    from PyQt6.QtGui import QIcon
    from core.app_paths import resource_path

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    for icon_rel in ("data/app_icon.ico", "data/app_icon.png"):
        icon_p = resource_path(icon_rel)
        if os.path.exists(icon_p):
            app.setWindowIcon(QIcon(icon_p))
            break

    # Inicializar la ventana principal directamente (acceso libre con cuenta Firebase)
    window = MainWindow()
    window.show()

    # Ejecutar el ciclo de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
