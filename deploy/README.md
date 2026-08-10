# Self-host SusTool next to WordPress (lcatraining.nl)

Use these files on the server that hosts [lcatraining.nl](https://www.lcatraining.nl).

## Quick path (systemd + nginx)

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

Streamlit should listen on `127.0.0.1:8501` only (not public).

### 3. nginx reverse proxy

Copy the snippet from `nginx-sustool.conf` into your site’s nginx config  
(often `/etc/nginx/sites-available/lcatraining.nl` or a file under `conf.d/`).

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 4. SSL

If WordPress already uses HTTPS with Let's Encrypt, the same certificate usually covers `/sustool-app/`.

If not:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d www.lcatraining.nl -d lcatraining.nl
```

### 5. WordPress

Edit the SusTool page Custom HTML iframe `src` to:

`https://www.lcatraining.nl/sustool-app/?embed=true`

---

## Alternative: Docker

```bash
cd /opt/sustool
docker compose -f deploy/docker-compose.yml up -d
```

Then use the same nginx proxy to `127.0.0.1:8501`.
