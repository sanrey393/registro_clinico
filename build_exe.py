# build_exe.py
# Script automatizado para compilar el Sistema Clínico en un ejecutable de Windows con PyInstaller.

import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("=== Iniciando compilación de Sistema de Registro Clínico ===")
    
    # 1. Verificar archivos críticos
    if not os.path.exists(os.path.join(BASE_DIR, "main.py")):
        print("[ERROR] No se encontró main.py")
        sys.exit(1)

    # 2. Configurar rutas de recursos a incluir
    data_folders = [
        ("styles", "styles"),
        ("data", "data"),
    ]

    add_data_args = []
    for src, dst in data_folders:
        src_path = os.path.join(BASE_DIR, src)
        if os.path.exists(src_path):
            add_data_args.extend(["--add-data", f"{src_path};{dst}"])

    # Incluir credenciales de Firebase si existen
    sa_file = os.path.join(BASE_DIR, "firebase_service_account.json")
    if os.path.exists(sa_file):
        add_data_args.extend(["--add-data", f"{sa_file};."])

    env_file = os.path.join(BASE_DIR, ".env")
    if os.path.exists(env_file):
        add_data_args.extend(["--add-data", f"{env_file};."])

    # 3. Argumentos para PyInstaller
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",             # Crea una carpeta distribuible (ideal para Inno Setup)
        "--windowed",           # Sin consola negra de CMD
        "--name", "SistemaClinico",
        *add_data_args,
        os.path.join(BASE_DIR, "main.py")
    ]

    print("\nEjecutando PyInstaller...")
    ret = subprocess.run(cmd)

    if ret.returncode == 0:
        print("\n[ÉXITO] Compilación completada con éxito.")
        print(f"Los binarios ejecutables se encuentran en: {os.path.join(BASE_DIR, 'dist', 'SistemaClinico')}")
    else:
        print("\n[ERROR] Falló la compilación.")
        sys.exit(ret.returncode)

if __name__ == "__main__":
    build()

