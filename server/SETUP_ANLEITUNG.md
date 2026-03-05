# Vollständige Anleitung: Ubuntu Server mit kostenloser Domain

## 📋 SCHRITT 1: Ubuntu Server Installation

1. **Ubuntu Server ISO herunterladen:** https://ubuntu.com/download/server
2. **Installation durchführen:**
   - VM oder physisch installieren
   - Hostname: z.B. `my-server`
   - SSH-Server aktivieren
   - Passwort merken

3. **IP-Adresse notieren:**
   ```bash
   hostname -I
   ```

---

## 📋 SCHRITT 2: Kostenlose Domain mit DynDNS

**Option A: No-IP (Empfohlen)**
- Website: https://www.noip.com
- Kostenlos bis 3 Domains
- Registriere dich und erstelle Subdomain (z.B. `meinserver.ddns.net`)
- Installiere DynDNS Updater auf Ubuntu:
  ```bash
  sudo apt install noip2
  sudo noip2 -C  # Konfigurieren
  sudo systemctl restart noip2
  ```

**Option B: FreeDNS (noch kostenfloser)**
- Website: https://freedns.afraid.org
- Registriere & erstelle Subdomain

---

## 📋 SCHRITT 3: Firewall & Port-Forwarding

**Auf deinem Router:**
1. Gehe zu Router-Admin (z.B. 192.168.1.1)
2. Port Forwarding einrichten:
   - Port 80 (HTTP) → Ubuntu IP:80
   - Port 443 (HTTPS) → Ubuntu IP:443
3. UPnP aktiviert lassen für DynDNS

**Auf Ubuntu:**
```bash
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw status
```

---

## 📋 SCHRITT 4: Server-Setup auf Ubuntu

1. **Dateien hochladen:**
   ```bash
   # Von deinem PC:
   scp -r e:\server user@your-server-ip:/home/user/server
   
   # Oder clone (falls git):
   git clone your-repo /var/www/server
   ```

2. **Setup-Script ausführen:**
   ```bash
   cd /var/www/server
   sudo bash setup_ubuntu.sh
   ```

3. **Server.py in /var/www/server verschieben:**
   ```bash
   sudo cp Server.py templates/ /var/www/server/
   sudo chown -R www-data:www-data /var/www/server
   ```

---

## 📋 SCHRITT 5: SSL/HTTPS mit Let's Encrypt

**Installation:**
```bash
sudo apt install certbot python3-certbot-nginx -y
```

**Zertifikat erstellen:**
```bash
# Ersetze mit deiner Domain!
sudo certbot certonly --standalone \
  -d meinserver.ddns.net \
  -d www.meinserver.ddns.net \
  --agree-tos \
  -m deine-email@example.com
```

**Auto-Renewal:**
```bash
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
sudo certbot renew --dry-run  # Test
```

---

## 📋 SCHRITT 6: Nginx Konfiguration

1. **Konfiguration kopieren:**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/server
   ```

2. **Domain anpassen in nginx.conf:**
   ```bash
   sudo nano /etc/nginx/sites-available/server
   # Ersetze: your-domain.example.com → meinserver.ddns.net
   ```

3. **Aktivieren:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/server /etc/nginx/sites-enabled/
   sudo rm /etc/nginx/sites-enabled/default  # Standard-Site deaktivieren
   ```

4. **Test & Start:**
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## 📋 SCHRITT 7: Flask-Server starten

**Option A: Manuell (zum Testen)**
```bash
cd /var/www/server
source venv/bin/activate
gunicorn -w 4 -b 127.0.0.1:5000 Server:app
```

**Option B: Mit Systemd (Produktion)**
```bash
sudo cp flask-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable flask-server.service
sudo systemctl start flask-server.service
sudo systemctl status flask-server.service
```

---

## 🔐 SCHRITT 8: Admin-Passwort ändern

1. **Zur Admin-Seite:**
   ```
   https://meinserver.ddns.net/admin/login
   ```

2. **Anmelden mit Standard-Credentials:**
   ```
   Benutzername: admin
   Passwort: admin123
   ```

3. **Passwort-Datenbankeingang ändern:**
   ```bash
   cd /var/www/server
   source venv/bin/activate
   python3 << 'EOF'
   from Server import app, db, Admin
   from werkzeug.security import generate_password_hash
   
   with app.app_context():
       admin = Admin.query.filter_by(username='admin').first()
       admin.password = generate_password_hash('DEIN-NEUES-PASSWORT')
       db.session.commit()
       print("Passwort geändert!")
   EOF
   ```

---

## 🚀 SCHRITT 9: Alle Geräte im Netzwerk können zugreifen

**Von jedem Gerät (PC, Handy, etc.) im **gleichen Netzwerk**:**

1. **Lokal (Router-IP):**
   ```
   http://192.168.1.X:5000  (wenn direkter Port)
   ```

2. **Von überall (über Domain):**
   ```
   https://meinserver.ddns.net
   ```

3. **API-Zugriff:**
   ```
   https://meinserver.ddns.net/api/status
   ```

---

## 📊 Monitoring & Logs

**Logs anschauen:**
```bash
# Nginx
sudo tail -f /var/log/nginx/server_access.log
sudo tail -f /var/log/nginx/server_error.log

# Flask Service
sudo journalctl -u flask-server.service -f

# System
htop
```

---

## 🔧 Häufige Probleme

| Problem | Lösung |
|---------|--------|
| "Verbindung abgelehnt" | Port Forwarding checken, Firewall öffnen |
| "Zertifikat ungültig" | certbot erneut ausführen, DNS propagiert? (24h) |
| "502 Bad Gateway" | Flask-Service läuft? `systemctl status flask-server` |
| "413 Payload Too Large" | `client_max_body_size` in nginx.conf erhöhen |
| DynDNS aktualisiert nicht | noip2 Service restarten: `sudo systemctl restart noip2` |

---

## 📝 Wichtige Befehle

```bash
# Server Status
sudo systemctl status flask-server.service

# Server neu starten
sudo systemctl restart flask-server.service

# Nginx neu laden
sudo systemctl reload nginx

# Zertifikat Status
sudo certbot certificates

# Ubuntu Updates
sudo apt update && sudo apt upgrade -y
```

---

## ✅ Checkliste für die Inbetriebnahme

- [ ] Ubuntu installiert & aktualisiert
- [ ] No-IP Account erstellt & Domain registriert
- [ ] DynDNS auf Ubuntu konfiguriert
- [ ] Port Forwarding im Router eingerichtet
- [ ] Firewall aktiviert & Ports geöffnet
- [ ] Server-Dateien hochgeladen
- [ ] Setup-Script ausgeführt
- [ ] SSL-Zertifikat erstellt
- [ ] Nginx konfiguriert & getestet
- [ ] Flask Service läuft
- [ ] Admin-Passwort geändert
- [ ] Von außen erreichbar (https://meinserver.ddns.net)

---

**Support:** Bei Fragen Logs checken oder Ubuntu Forum befragen!
