# Deployment, stability, and WordPress embedding — SusTool

## 1. Can code keep Streamlit Community Cloud always awake?

**No — not reliably on the free tier.**

Streamlit Community Cloud **spins down apps after ~15 minutes of inactivity**. The first visitor after sleep may see **“Get this app back”** while the container restarts. This is imposed by **Streamlit hosting**, not by SusTool code.

| Approach | Works on free tier? | Recommendation |
|----------|---------------------|----------------|
| In-app keep-alive loop | No | Not supported; wastes resources |
| External cron ping every 5–10 min | Unreliable | May violate fair-use; not recommended |
| Paid Streamlit Cloud workspace | Partially | Less aggressive sleep |
| Self-hosted / Railway / Render | Yes | **Best for research-group production use** |

---

## 2. Alternative platforms (transfer the same codebase)

SusTool is a standard Streamlit app (`app.py` + `requirements.txt`). You can deploy the **same GitHub repo** on:

| Platform | Always on | Custom domain | WordPress iframe |
|----------|-----------|---------------|------------------|
| **Self-hosted** (Linux + nginx) | Yes | Yes (`lcatraining.nl/...`) | Yes |
| **Streamlit Cloud paid** | Better | Yes | Yes |
| **Railway** | Yes* | Yes | Yes |
| **Render** | Yes* | Yes | Yes |
| **Fly.io** (Docker) | Yes* | Yes | Yes |
| **Hugging Face Spaces** (Streamlit) | Usually | HF URL | Yes (test embed) |

\*Check each provider’s free/paid limits.

**Minimum files needed:** `app.py`, `requirements.txt`, `runtime.txt`, `data/`, `src/`, `.streamlit/config.toml`.

---

## 3. Embed in your WordPress research group site

You already embed via iframe on:

`https://www.lcatraining.nl/index.php/sustool/`

```html
<iframe
  src="https://ctcsustool.streamlit.app/?embed=true"
  style="width:100%; height:1200px; border:none;"
  allowfullscreen
  title="Circular Cultivation and Chemistry SusTool">
</iframe>
```

Use **`?embed=true`** and the root Streamlit URL only (avoid sub-path URLs that cause redirect loops).

---

## 4. Self-host under lcatraining.nl (24/7, full control)

**What we need from your research group / IT:**

1. **SSH access** to the WordPress server or a dedicated VM (same network as `lcatraining.nl`).
2. **Python 3.11+** or **Docker** on that server.
3. **Clone the repo** and install: `pip install -r requirements.txt`.
4. **Run Streamlit** as a service, e.g.  
   `streamlit run app.py --server.port 8501 --server.address 127.0.0.1`
5. **nginx reverse proxy** — example:

```nginx
location /sustool-app/ {
    proxy_pass http://127.0.0.1:8501/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

6. **SSL certificate** (Let's Encrypt) for HTTPS.
7. **WordPress iframe** updated to `https://www.lcatraining.nl/sustool-app/?embed=true` (or your chosen path).

SusTool is already configured for iframe embedding (`.streamlit/config.toml`: `enableCORS = false`).

---

## 5. Public access (remove email restriction)

Email allow-lists are set in **Streamlit Cloud → Settings → Sharing**, not in application code:

1. Set visibility to **Public**
2. Remove all **Viewer email** restrictions

Maintainer tools remain protected via `?maintainer=1` + password (see `.streamlit/secrets.toml.example`).

---

## 6. After code or data changes

```bash
git add …
git commit -m "…"
git push origin main
```

Then **Reboot app** on Streamlit Cloud (or restart the systemd service if self-hosted).  
WordPress users: hard-refresh the page (`Cmd+Shift+R`).
