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
    
    # ── Validación de Licencia y Protección de Hardware (Machine Lock) ──
    from core.license_manager import LicenseManager
    from ui.dialogs.license_dialog import LicenseDialog
    from database.firebase_manager import FirebaseManager
    
    db_mgr = FirebaseManager()
    lic_mgr = LicenseManager()

    # Intentar validación silenciosa (local o nube)
    valida, _ = lic_mgr.is_license_valid(db_mgr)
    if not valida:
        # Intenta consultar si ya lo activaste en Firebase
        activado_remoto, _ = lic_mgr.check_cloud_activation(db_mgr)
        if activado_remoto:
            valida = True
    
    if not valida:
        # Abrir ventana de activación si aún no está autorizada
        dlg = LicenseDialog(db_manager=db_mgr)
        if dlg.exec() != 1:  # Si cerró o canceló sin activar
            sys.exit(0)

    # Inicializar la ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar el ciclo de eventos
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
