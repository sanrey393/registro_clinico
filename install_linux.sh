#!/usr/bin/env bash
# Instalador Universal de PSIQUE para Linux (Ubuntu, Debian, Mint, Fedora, Arch, etc.)
# Uso: chmod +x install_linux.sh && ./install_linux.sh

set -e

APP_NAME="PSIQUE"
INSTALL_DIR="$HOME/.local/share/psique"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCH="$(uname -m)"

echo "=========================================="
echo "  Instalador de $APP_NAME para Linux ($ARCH)"
echo "=========================================="

if [ "$ARCH" = "i386" ] || [ "$ARCH" = "i686" ]; then
    echo "[AVISO] Arquitectura de 32 bits ($ARCH) detectada."
    echo "        PyQt6 oficial no distribuye binarios compilados para Linux 32 bits."
    echo "        Se intentará usar python3-pyqt6 del sistema si está disponible."
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 no está instalado. Instálalo con tu gestor de paquetes:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  Fedora:        sudo dnf install python3 python3-pip"
    echo "  Arch:          sudo pacman -S python python-pip"
    exit 1
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR"

# Preservar archivos de configuración y datos si ya existe una instalación previa
for f in ".env" "firebase_service_account.json" ".vault.key" ".license.dat"; do
    if [ -f "$INSTALL_DIR/$f" ]; then
        cp -f "$INSTALL_DIR/$f" "/tmp/psique_backup_$f"
    fi
done

echo "[1/4] Copiando archivos de la aplicación en $INSTALL_DIR..."
cp -rf "$SCRIPT_DIR/"* "$INSTALL_DIR/" 2>/dev/null || true

for f in ".env" "firebase_service_account.json" ".vault.key" ".license.dat"; do
    if [ -f "/tmp/psique_backup_$f" ]; then
        mv -f "/tmp/psique_backup_$f" "$INSTALL_DIR/$f"
    fi
done

# Si viene un binario precompilado (PSIQUE / SistemaClinico), usarlo directamente
if [ -x "$INSTALL_DIR/SistemaClinico" ]; then
    echo "[2/4] Binario Linux precompilado detectado."
    LAUNCH_CMD="$INSTALL_DIR/SistemaClinico"
else
    echo "[2/4] Configurando entorno virtual Python..."
    if [ "$ARCH" = "i386" ] || [ "$ARCH" = "i686" ]; then
        python3 -m venv --system-site-packages "$INSTALL_DIR/.venv"
    else
        python3 -m venv "$INSTALL_DIR/.venv"
    fi
    "$INSTALL_DIR/.venv/bin/pip" install --upgrade pip
    if [ -f "$INSTALL_DIR/requirements.txt" ]; then
        "$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"
    fi
    LAUNCH_CMD="$INSTALL_DIR/.venv/bin/python $INSTALL_DIR/main.py"
fi

echo "[3/4] Creando lanzador en $BIN_DIR/psique..."
cat > "$BIN_DIR/psique" <<EOF
#!/usr/bin/env bash
cd "$INSTALL_DIR"
exec $LAUNCH_CMD "\$@"
EOF
chmod +x "$BIN_DIR/psique"

echo "[4/4] Creando acceso directo en el menú de aplicaciones..."
ICON_PATH="$INSTALL_DIR/data/app_icon.png"
cat > "$DESKTOP_DIR/psique.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=PSIQUE - Registro Clínico
Comment=Sistema de Gestión Clínico Psicológica
Exec=$BIN_DIR/psique
Icon=$ICON_PATH
Terminal=false
Categories=Office;MedicalSoftware;
EOF
chmod +x "$DESKTOP_DIR/psique.desktop"

echo ""
echo "✅ $APP_NAME instalado correctamente en $INSTALL_DIR"
echo "   Puedes iniciarlo desde tu menú de aplicaciones o ejecutando: psique"
