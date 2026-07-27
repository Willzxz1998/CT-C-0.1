# Deployment and public access — SusTool

## Streamlit Community Cloud sleep behaviour

Free-tier apps **spin down after ~15 minutes of inactivity**. The first visitor may need to click **“Get this app back”** while the container restarts. This is imposed by **Streamlit hosting**, not by SusTool application code.

**Recommendations for production use:**

| Option | Uptime | Notes |
|--------|--------|-------|
| Embed on [lcatraining.nl/sustool](https://www.lcatraining.nl/index.php/sustool/) | Same as Cloud | Primary user entry; iframe with `?embed=true` |
| Streamlit Cloud **paid** workspace | Higher | Less aggressive sleep |
| **Self-host** (Docker + nginx on group server) | 24/7 | Full control; see Phase B nginx notes in project history |

Avoid relying on automated uptime pings on the free tier (may conflict with fair-use policies).

## Public access (remove email restriction)

Email allow-lists are configured in **Streamlit Cloud**, not in `app.py`:

1. Open [share.streamlit.io](https://share.streamlit.io) → your app → **Settings**
2. Under **Sharing**, set visibility to **Public**
3. Remove any **Viewer email** restrictions

SusTool does not implement email login in code. Maintainer tools remain protected via `?maintainer=1` + password (optional `creator_mode` in secrets).

## After code or data changes

```bash
git add …
git commit -m "…"
git push origin main
```

Then **Reboot app** in Streamlit Cloud. Users embedding via WordPress should hard-refresh (`Cmd+Shift+R`).
