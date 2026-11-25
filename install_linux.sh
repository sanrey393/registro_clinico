#!/usr/bin/env bash
# Instalador Universal de PSIQUE (Rama 32-bit - PyQt5) para Linux (Canaima, Debian, Ubuntu, Mint, etc.)
# Uso: chmod +x install_linux.sh && ./install_linux.sh

set -e

APP_NAME="PSIQUE (32-bit)"
INSTALL_DIR="$HOME/.local/share/psique"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCH="$(uname -m)"

echo "================================================="
echo "  Instalador de $APP_NAME para Linux ($ARCH)"
echo "================================================="

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] python3 no está instalado. Instálalo con:"
    echo "  sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip"
    exit 1
fi

# En Linux 32 bits (i386/i686 / Canaima), instalar PyQt5 desde apt evita compilaciones pesadas
if [ "$ARCH" = "i386" ] || [ "$ARCH" = "i686" ]; then
    if command -v apt-get >/dev/null 2>&1; then
        echo "[INFO] Instalando librerías base PyQt5 desde repositorios Debian/Canaima (apt)..."
        sudo apt-get update || true
        sudo apt-get install -y python3-venv python3-pip python3-pyqt5 python3-pyqt5.qtsvg \
            python3-reportlab python3-requests python3-cryptography python3-dotenv || true
    fi
fi

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$DESKTOP_DIR"

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

if [ -x "$INSTALL_DIR/SistemaClinico" ]; then
    echo "[2/4] Binario Linux precompilado detectado."
    LAUNCH_CMD="$INSTALL_DIR/SistemaClinico"
else
    echo "[2/4] Configurando entorno virtual Python (PyQt5)..."
    python3 -m venv --system-site-packages "$INSTALL_DIR/.venv"
    "$INSTALL_DIR/.venv/bin/pip" install --upgrade pip || true
    if [ "$ARCH" = "i386" ] || [ "$ARCH" = "i686" ]; then
        "$INSTALL_DIR/.venv/bin/pip" install Pyrebase4 python-dotenv requests reportlab cryptography || true
    elif [ -f "$INSTALL_DIR/requirements.txt" ]; then
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
Comment=Sistema de Gestión Clínico Psicológica (32-bit)
Exec=$BIN_DIR/psique
Icon=$ICON_PATH
Terminal=false
Categories=Office;MedicalSoftware;
EOF
chmod +x "$DESKTOP_DIR/psique.desktop"

echo ""
echo "✅ $APP_NAME instalado correctamente en $INSTALL_DIR"
echo "   Puedes iniciarlo desde tu menú de aplicaciones o ejecutando: psique"
