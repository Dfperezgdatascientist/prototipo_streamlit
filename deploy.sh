#!/bin/bash
# ─────────────────────────────────────────────────────────────
# deploy.sh — Despliegue en servidor físico Linux
# Uso: bash deploy.sh
# ─────────────────────────────────────────────────────────────

APP_DIR="/opt/autoservicio"
APP_USER="autoservicio"
PORT=8080
DOMAIN="autoservicio.tuempresa.com"   # o IP del servidor

echo "=============================="
echo " Despliegue Autoservicio Diners"
echo "=============================="

# 1. Instalar dependencias del sistema
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv

# 2. Crear directorio y copiar archivos
sudo mkdir -p $APP_DIR
sudo cp app.py requirements.txt $APP_DIR/

# 3. Crear entorno virtual e instalar librerías
python3 -m venv $APP_DIR/venv
$APP_DIR/venv/bin/pip install --upgrade pip
$APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt

# 4. Crear archivo de configuración Streamlit
mkdir -p $APP_DIR/.streamlit
cat > $APP_DIR/.streamlit/config.toml << EOF
[server]
port = $PORT
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
EOF

# 5. Crear servicio systemd para que arranque automáticamente
sudo tee /etc/systemd/system/autoservicio.service > /dev/null << EOF
[Unit]
Description=Autoservicio Diners Club
After=network.target

[Service]
Type=simple
User=$APP_USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/streamlit run app.py
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# 6. Habilitar e iniciar servicio
sudo systemctl daemon-reload
sudo systemctl enable autoservicio
sudo systemctl start autoservicio

echo ""
echo "✅ Desplegado en http://$DOMAIN:$PORT"
echo "   Ver estado:   sudo systemctl status autoservicio"
echo "   Ver logs:     sudo journalctl -u autoservicio -f"
echo "   Reiniciar:    sudo systemctl restart autoservicio"
