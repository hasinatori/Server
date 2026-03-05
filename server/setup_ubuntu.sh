#!/bin/bash

# Ubuntu Server Setup Script
# Führe aus: sudo bash setup_ubuntu.sh

echo "=========================================="
echo "Ubuntu Server Setup für Flask-App"
echo "=========================================="

# System aktualisieren
echo "[1/6] Aktualisiere System..."
apt update && apt upgrade -y

# Python und pip installieren
echo "[2/6] Installiere Python und Dependencies..."
apt install -y python3 python3-pip python3-venv git

# Nginx installieren
echo "[3/6] Installiere Nginx..."
apt install -y nginx

# Verzeichnis erstellen
echo "[4/6] Richte Verzeichnisse ein..."
mkdir -p /var/www/server
cd /var/www/server

# Virtual Environment erstellen
echo "[5/6] Erstelle Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate

# Dependencies installieren
echo "[6/6] Installiere Python Packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Gunicorn setup
echo ""
echo "=========================================="
echo "✓ Installation abgeschlossen!"
echo "=========================================="
echo ""
echo "Nächste Schritte:"
echo "1. Starten: source venv/bin/activate && gunicorn -w 4 -b 0.0.0.0:5000 Server:app"
echo "2. Oder mit systemd (für Autostart) - siehe nginx.conf Kommentare"
echo ""
