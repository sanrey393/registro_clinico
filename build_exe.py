# build_exe.py
# Script automatizado para compilar el Sistema Clinico en ejecutable Windows con PyInstaller
# y crear el instalador con InnoSetup.
#
# Uso:
#   python build_exe.py              -> Solo PyInstaller
#   python build_exe.py --installer  -> PyInstaller + InnoSetup
#
# Requiere:
#   - PyInstaller instalado: pip install pyinstaller
#   - InnoSetup 6+ instalado en la ruta por defecto (solo para --installer)

import os
import sys
import subprocess
import shutil
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist", "SistemaClinico")
PYTHON   = sys.executable

ISCC_PATHS = [
    r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    r"C:\Program Files\Inno Setup 6\ISCC.exe",
]

# Archivos de configuracion que se copian JUNTO al .exe (no empaquetados adentro)
CONFIG_FILES = [
    ".env",
    "firebase_service_account.json",
    "version.json",
]


def build_exe():
    print("=" * 60)
    print("  Compilando Sistema de Registro Clinico con PyInstaller")
    print("=" * 60)

    if not os.path.exists(os.path.join(BASE_DIR, "main.py")):
        print("[ERROR] No se encontro main.py en:", BASE_DIR)
        sys.exit(1)

    spec_file = os.path.join(BASE_DIR, "SistemaClinico.spec")
    if not os.path.exists(spec_file):
        print("[ERROR] No se encontro SistemaClinico.spec")
        sys.exit(1)

    cmd = [PYTHON, "-m", "PyInstaller", spec_file, "--noconfirm", "--clean"]
    print("\nEjecutando:", " ".join(cmd))
    ret = subprocess.run(cmd, cwd=BASE_DIR)

    if ret.returncode != 0:
        print("\n[ERROR] Fallo la compilacion con PyInstaller.")
        sys.exit(ret.returncode)

    # Copiar archivos de configuracion junto al .exe
    print("\nCopiando archivos de configuracion a dist/SistemaClinico/ ...")
    for filename in CONFIG_FILES:
        src = os.path.join(BASE_DIR, filename)
        dst = os.path.join(DIST_DIR, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  [OK] {filename}")
        else:
            print(f"  [ADVERTENCIA] {filename} no encontrado - el sistema puede no autenticarse correctamente.")

    # Asegurar copia de python3t.dll para compatibilidad con cryptography / _rust.pyd (Python 3.13+)
    abi3t_src = os.path.join(os.path.dirname(PYTHON), "abi3t-compat", "python3t.dll")
    if os.path.exists(abi3t_src):
        internal_dir = os.path.join(DIST_DIR, "_internal")
        if os.path.exists(internal_dir):
            shutil.copy2(abi3t_src, os.path.join(internal_dir, "python3t.dll"))
        shutil.copy2(abi3t_src, os.path.join(DIST_DIR, "python3t.dll"))
        print("  [OK] python3t.dll copiado para soporte de cryptography (_rust)")

    size_mb = sum(
        f.stat().st_size for f in __import__("pathlib").Path(DIST_DIR).rglob("*") if f.is_file()
    ) / (1024 * 1024)

    print(f"\n[EXITO] Compilacion completada.")
    print(f"  Ubicacion: {DIST_DIR}")
    print(f"  Tamano total: {size_mb:.1f} MB")


def build_installer():
    print("\n" + "=" * 60)
    print("  Creando instalador con InnoSetup")
    print("=" * 60)

    iscc = None
    for path in ISCC_PATHS:
        if os.path.exists(path):
            iscc = path
            break

    if not iscc:
        print("[ERROR] InnoSetup no encontrado en las rutas habituales.")
        print("        Descargalo en: https://jrsoftware.org/isdl.php")
        print("        Instala y vuelve a ejecutar con --installer")
        sys.exit(1)

    iss_file = os.path.join(BASE_DIR, "installer_setup.iss")
    if not os.path.exists(iss_file):
        print("[ERROR] No se encontro installer_setup.iss")
        sys.exit(1)

    # Verificar que el exe compilado existe
    exe_path = os.path.join(DIST_DIR, "SistemaClinico.exe")
    if not os.path.exists(exe_path):
        print("[ERROR] SistemaClinico.exe no encontrado en dist/. Compila primero con PyInstaller.")
        sys.exit(1)

    cmd = [iscc, iss_file]
    print(f"\nEjecutando: {iscc} installer_setup.iss")
    ret = subprocess.run(cmd, cwd=BASE_DIR)

    if ret.returncode != 0:
        print("\n[ERROR] Fallo la creacion del instalador.")
        sys.exit(ret.returncode)

    output_dir = os.path.join(BASE_DIR, "Output")
    installers = list(__import__("pathlib").Path(output_dir).glob("*.exe")) if os.path.exists(output_dir) else []
    if installers:
        inst = installers[0]
        size_mb = inst.stat().st_size / (1024 * 1024)
        print(f"\n[EXITO] Instalador creado:")
        print(f"  {inst}")
        print(f"  Tamano: {size_mb:.1f} MB")
    else:
        print(f"\n[EXITO] Instalador creado en: {output_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compilar Sistema Clinico")
    parser.add_argument("--installer", action="store_true", help="Tambien crear instalador con InnoSetup")
    args = parser.parse_args()

    build_exe()
    if args.installer:
        build_installer()
    else:
        print("\nTip: Ejecuta con --installer para crear tambien el instalador de Windows.")
        print("     Requiere InnoSetup 6+ instalado.")
