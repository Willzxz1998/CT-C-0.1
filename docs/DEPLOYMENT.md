# Long-term hosting of SusTool on lcatraining.nl

This guide is for the **WordPress site administrator** of [lcatraining.nl](https://www.lcatraining.nl).

---

## Plain-language answers

### What is SSH?
**SSH** (Secure Shell) is how you log into the website **server** from your computer (Terminal / PuTTY), similar to remote desktop but for the command line.  
You need it to install Python/Docker and keep SusTool running in the background.

Where to find it (typical WordPress hosts):
- Hosting control panel → **SSH Access** / **Shell Access** / **Server details**
- Or ask your hosting provider / university IT for: **hostname**, **username**, **password or SSH key**

Example login:
```bash
ssh YOUR_USERNAME@YOUR_SERVER_HOST
```

### Is nginx needed if the tool is on the group website?
**Yes, if SusTool runs on the same server as WordPress** (recommended for 24/7).

- **WordPress** serves pages (including `/index.php/sustool/`).
- **SusTool (Streamlit)** is a separate Python app (usually on port `8501`).
- **nginx** (or Apache) acts as a **reverse proxy**: visitors open an HTTPS URL on `lcatraining.nl`, and nginx secretly forwards that traffic to Streamlit.

Without nginx/Apache proxy, visitors would have to open something like `http://server-ip:8501`, which is insecure and usually blocked.

### What is an SSL certificate?
**SSL/TLS** makes the site use **https://** (padlock in the browser).  
WordPress on lcatraining.nl already uses HTTPS. The proxied SusTool path must also use HTTPS.

Common options:
- **Let's Encrypt** (free) via Certbot — often already set up for WordPress
- Certificate provided by your hosting panel (cPanel / Plesk / Cloudflare)

You usually do **not** buy a separate certificate if the main site already has HTTPS; you reuse the same certificate for the new path or subdomain.

---

## Two hosting modes

| Mode | Always awake? | What you need |
|------|---------------|---------------|
| **A. Keep Streamlit Cloud + WordPress iframe** (current) | No (free Cloud sleeps) | Nothing extra; already works |
| **B. Self-host on the WordPress server** | Yes | SSH + nginx + SSL + systemd/Docker |

**For long-term stay on lcatraining.nl without “Get this app back”, choose Mode B.**

---

## What you (admin) should provide / collect

Copy this checklist and fill it in (send to whoever installs the app, or keep for yourself):

1. **SSH host** — e.g. `lcatraining.nl` or `ssh.yourhost.com`  
   Find: hosting panel → SSH / Server Information
2. **SSH username**
3. **SSH password** or **private SSH key** (prefer key; do not commit keys to Git)
4. **Web server type** — nginx or Apache?  
   Find: hosting panel, or ask IT; on the server often `nginx -v` or `httpd -v`
5. **Document root / WordPress path** — e.g. `/var/www/html` or `/home/user/public_html`
6. **Preferred SusTool URL** (pick one):
   - Path: `https://www.lcatraining.nl/sustool-app/`
   - Or subdomain: `https://sustool.lcatraining.nl`
7. **Whether you can install system packages** (`sudo apt install …`) — yes/no
8. **GitHub repo URL** (already): `https://github.com/Willzxz1998/CT-C-0.1.git`

Once you have SSH access, the files under `deploy/` in this repository can be installed.

---

## Mode B — install overview

1. SSH into the server  
2. Clone the repo and install Python dependencies (or use Docker)  
3. Run Streamlit as a **systemd service** (auto-start on reboot)  
4. Add **nginx** location block (files in `deploy/nginx-sustool.conf`)  
5. Confirm **SSL** already covers the site (or run Certbot)  
6. Update the WordPress **Custom HTML** iframe to point to the new HTTPS URL  

Detailed commands: `deploy/README.md`

---

## WordPress iframe (after self-host)

Replace the Streamlit Cloud URL with your proxied URL:

```html
<iframe
  src="https://www.lcatraining.nl/sustool-app/?embed=true"
  style="width:100%; height:1200px; border:none;"
  allowfullscreen
  title="Circular Cultivation and Chemistry Sustainability Tool">
</iframe>
```

Until self-hosting is ready, keep:

```html
src="https://ctcsustool.streamlit.app/?embed=true"
```
