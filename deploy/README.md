# Self-host SusTool next to WordPress (lcatraining.nl)

**Preferred public URL:** `https://www.lcatraining.nl/sustool-app/`

Your host uses **Apache** (confirmed from WordPress System Info), document root:

`/data/www/vhosts/lcatraining.nl/httpdocs/`

See also: `docs/FIND_SSH_ACCESS.md` (how to find SSH credentials in Plesk).

## Quick path (systemd + Apache)

### 1. On the server (SSH)

```bash
sudo mkdir -p /opt/sustool
sudo chown "$USER":"$USER" /opt/sustool
cd /opt/sustool
git clone https://github.com/Willzxz1998/CT-C-0.1.git .
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Install systemd service

```bash
sudo cp deploy/sustool.service /etc/systemd/system/sustool.service
# Edit User= and WorkingDirectory= if needed
sudo systemctl daemon-reload
sudo systemctl enable --now sustool
sudo systemctl status sustool
```

Streamlit listens on `127.0.0.1:8501` only.

### 3. Apache reverse proxy (not nginx)

Enable modules (Debian/Ubuntu style; on Plesk use the panel or ask IT):

```bash
sudo a2enmod proxy proxy_http proxy_wstunnel rewrite headers ssl
```

Add the directives from `deploy/apache-sustool.conf` to the **HTTPS** VirtualHost for `www.lcatraining.nl`
(Plesk: Domains → Apache & nginx Settings → Additional directives for HTTPS).

```bash
sudo apachectl configtest && sudo systemctl reload apache2
```

### 4. SSL

WordPress already uses `https://www.lcatraining.nl`. Reuse the same certificate for `/sustool-app/`.
If needed: Certbot / Plesk SSL/TLS Certificates.

### 5. WordPress iframe

```html
<iframe
  src="https://www.lcatraining.nl/sustool-app/?embed=true"
  style="width:100%; height:1200px; border:none;"
  allowfullscreen
  title="Circular Cultivation and Chemistry Sustainability Tool">
</iframe>
```

---

## Alternative: Docker

```bash
cd /opt/sustool
docker compose -f deploy/docker-compose.yml up -d
```

Then use the same Apache proxy to `127.0.0.1:8501`.
