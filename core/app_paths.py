import os
import sys


def app_dir() -> str:
    """
    Carpeta raíz del programa:
    - En modo compilado (.exe): carpeta donde está el ejecutable.
    - En modo desarrollo (.py): carpeta raíz del proyecto.
    """
    if getattr(sys, "frozen", False):
        # sys.executable apunta al .exe instalado por el usuario
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_app_env() -> str | None:
    """
    Carga el .env del programa instalado, buscando en este orden:
    1. Carpeta del ejecutable (.exe) — instalación en otra PC
    2. Carpeta _MEIPASS — recursos empaquetados por PyInstaller
    3. Carpeta de trabajo actual (cwd)
    4. Raíz del proyecto (modo desarrollo)
    """
    from dotenv import load_dotenv

    candidates = []

    if getattr(sys, "frozen", False):
        # Prioridad 1: junto al .exe (donde el usuario pone el .env al instalar)
        candidates.append(os.path.join(os.path.dirname(sys.executable), ".env"))
        # Prioridad 2: dentro del paquete extraído por PyInstaller
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, ".env"))
    else:
        # Modo desarrollo: raíz del proyecto
        candidates.append(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"
        ))

    # Siempre intentar el directorio de trabajo actual
    candidates.append(os.path.join(os.getcwd(), ".env"))

    for path in candidates:
        if path and os.path.isfile(path):
            load_dotenv(path, override=True)  # override=True para garantizar carga
            print(f"[INFO] .env cargado desde: {path}")
            return path

    load_dotenv()
    print("[WARN] No se encontró archivo .env en ninguna ubicación esperada.")
    return None


def resource_path(relative_path: str) -> str:
    """
    Obtiene la ruta absoluta a un recurso estático (estilos, datos, iconos):
    - En modo compilado: busca en _internal/<relative_path> o _MEIPASS/<relative_path>.
    - En modo desarrollo: busca desde la raíz del proyecto.
    """
    if getattr(sys, "frozen", False):
        base_internal = os.path.join(os.path.dirname(sys.executable), "_internal")
        cand1 = os.path.join(base_internal, relative_path)
        if os.path.exists(cand1):
            return cand1
        
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            cand2 = os.path.join(meipass, relative_path)
            if os.path.exists(cand2):
                return cand2

        cand3 = os.path.join(os.path.dirname(sys.executable), relative_path)
        if os.path.exists(cand3):
            return cand3

    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), relative_path)

