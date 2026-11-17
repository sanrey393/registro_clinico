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

    # 2. Configurar rutas de recursos a incluir DENTRO del paquete (_MEIPASS)
    #    Solo se incluyen carpetas de datos estáticos (estilos, catálogos).
    #    El .env y firebase_service_account.json NO se empaquetan dentro del binario;
    #    se copian JUNTO al .exe después de compilar (ver paso 4).
    data_folders = [
        ("styles", "styles"),
        ("data", "data"),
    ]

    add_data_args = []
    for src, dst in data_folders:
        src_path = os.path.join(BASE_DIR, src)
        if os.path.exists(src_path):
            add_data_args.extend(["--add-data", f"{src_path};{dst}"])

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

    if ret.returncode != 0:
        print("\n[ERROR] Falló la compilación.")
        sys.exit(ret.returncode)

    # 4. Copiar archivos de configuración JUNTO al .exe en dist/SistemaClinico/
    #    Así load_app_env() los encontrará en os.path.dirname(sys.executable)
    dist_dir = os.path.join(BASE_DIR, "dist", "SistemaClinico")

    for filename in [".env", "firebase_service_account.json"]:
        src_file = os.path.join(BASE_DIR, filename)
        dst_file = os.path.join(dist_dir, filename)
        if os.path.exists(src_file):
            shutil.copy2(src_file, dst_file)
            print(f"[OK] {filename} copiado a dist/SistemaClinico/")
        else:
            print(f"[WARN] {filename} no encontrado — el sistema podría no autenticarse correctamente.")

    print(f"\n[ÉXITO] Compilación completada.")
    print(f"Distribución lista en: {dist_dir}")

if __name__ == "__main__":
    build()
