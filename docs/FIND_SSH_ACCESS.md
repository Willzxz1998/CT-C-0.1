# Find SSH and hosting details for lcatraining.nl (administrator guide)

Your WordPress “System Info” already tells us important facts:

| Item | Value from your report |
|------|-------------------------|
| Site | https://www.lcatraining.nl |
| Document root | `/data/www/vhosts/lcatraining.nl/httpdocs/` |
| Web server | **Apache** (not nginx) |
| PHP | 8.3.33 |
| Likely control panel | **Plesk** (path `/data/www/vhosts/...` is typical of Plesk) |
| Preferred tool URL | **https://www.lcatraining.nl/sustool-app/** |

SusTool still needs a place to **run Python/Streamlit**. WordPress alone cannot run Streamlit. Options:

1. **SSH into this same server** and run Streamlit + Apache reverse proxy (best long-term).
2. Keep Streamlit Cloud + iframe (works now, but free Cloud can sleep).

---

## 1. Where to find SSH hostname, username, password/key

### Step A — Open the hosting control panel (Plesk)

1. In your browser try one of these (common Plesk login URLs):
   - `https://www.lcatraining.nl:8443`
   - `https://lcatraining.nl:8443`
   - Or the panel URL your university/hosting provider gave you
2. Log in with the **same credentials** you use to manage the website (or the “admin” / “subscription” login from IT).

If you only use WordPress (`/wp-admin`) and never saw a panel like Plesk/cPanel:  
ask the person who bought/hosts the domain (Maastricht University IT / faculty web host) for **SSH and Plesk access**. WordPress admin ≠ full server admin.

### Step B — In Plesk: SSH settings

Typical path:

1. **Websites & Domains** → click **lcatraining.nl**
2. Look for **Web Hosting Access** / **SSH Access** / **Hosting & DNS**
3. Find:
   - **SSH access**: set to *Enabled* (sometimes “/bin/bash” instead of “Forbidden”)
   - **System user** (this is your **SSH username**) — often looks like `lcatrain` or a short account name
   - **Password**: set/reset here if needed

### Step C — Hostname for SSH

Usually one of:

| Candidate | When to use |
|-----------|-------------|
| `www.lcatraining.nl` | Often works if SSH is enabled on the same host |
| `lcatraining.nl` | Same |
| A name like `server123.hostingprovider.nl` | Shown in Plesk under **Server Information** or in the welcome email from the host |

Test from your Mac Terminal:

```bash
ssh YOUR_SSH_USERNAME@www.lcatraining.nl
```

If it fails, try the hostname from Plesk **Tools & Settings → Server Information** (or the host’s welcome email).

### Step D — Password vs SSH key

- **Password**: the system-user password you set in Plesk (Web Hosting Access).
- **SSH key** (recommended):
  1. On your Mac: `ssh-keygen -t ed25519 -C "sustool-admin"`
  2. Copy public key: `cat ~/.ssh/id_ed25519.pub`
  3. In Plesk: **SSH Keys** / **Authorized keys** → paste the public key  
     (or ask IT to add it)

**Never** put the private key (the file without `.pub`) into WordPress, GitHub, or chat.

### Step E — Confirm document root (you already have this)

From System Info:

`/data/www/vhosts/lcatraining.nl/httpdocs/`

After SSH login, check:

```bash
pwd
ls /data/www/vhosts/lcatraining.nl/httpdocs/ | head
```

You should see WordPress files (`wp-config.php`, `wp-content`, …).

---

## 2. Checklist — fill this in before installing SusTool

```
SSH hostname:     __________________
SSH username:     __________________
Auth method:      [ ] password   [ ] SSH key
Can use sudo?:    [ ] yes   [ ] no   [ ] unknown
Control panel:    [ ] Plesk   [ ] other: ________
Apache modules OK for proxy?: [ ] yes   [ ] need IT
Preferred URL:    https://www.lcatraining.nl/sustool-app/
GitHub repo:      https://github.com/Willzxz1998/CT-C-0.1.git
```

Send the filled checklist (without passwords) when you are ready; installation commands can then be tailored.

---

## 3. Important limitations on shared hosting

Many Plesk “web hosting” accounts:

- allow SSH file editing,
- but **do not** allow installing system packages, Docker, or long-running processes without IT approval.

If SSH works but you **cannot** run Streamlit as a service, ask university/faculty IT for one of:

- permission to run a systemd/Docker service for SusTool, or  
- a small VM / container next to the WordPress host.

Meanwhile the site can keep using:

`https://ctcsustool.streamlit.app/?embed=true` inside the WordPress page.

---

## 4. After self-host works — WordPress iframe

On page `https://www.lcatraining.nl/index.php/sustool/`, set:

```html
<iframe
  src="https://www.lcatraining.nl/sustool-app/?embed=true"
  style="width:100%; height:1200px; border:none;"
  allowfullscreen
  title="Circular Cultivation and Chemistry Sustainability Tool">
</iframe>
```

Apache config for this path: `deploy/apache-sustool.conf`  
Install steps: `deploy/README.md`
