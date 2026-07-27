"""Reusable UI fragments: homepage footer, product highlights, deployment notes."""

from __future__ import annotations

CONTACT_EMAIL = "xinzhi.zhong@maastrichtuniversity.nl"
TOOL_CITATION = (
    "Circular Cultivation and Chemistry Sustainability Tool (SusTool), "
    "Maastricht University / Interreg Circulaire Teelt en Chemie, "
    "https://www.lcatraining.nl/index.php/sustool/ (accessed YYYY-MM-DD)."
)
RECOMMENDED_LICENSE = "Creative Commons Attribution 4.0 International (CC BY 4.0)"


def render_homepage_product_highlights() -> None:
    """Visually highlight the three major valorisation products on the homepage."""
    import streamlit as st

    st.markdown("### Major valorisation products")
    c1, c2, c3 = st.columns(3)
    cards = [
        (
            c1,
            "Biochar",
            "#1b5e20",
            "Carbon-rich solid from pyrolysis of horticultural residues; "
            "potential for soil amendment and carbon storage (dry mass basis).",
        ),
        (
            c2,
            "Compost",
            "#2e7d32",
            "Stabilised organic material from aerobic decomposition; "
            "supports nutrient recycling and soil health (wet mass basis).",
        ),
        (
            c3,
            "Coumaric acid",
            "#388e3c",
            "Functional phenolic compound recoverable through biorefinery routes; "
            "part of advanced circular chemistry pathways in the project.",
        ),
    ]
    for col, title, color, desc in cards:
        with col:
            st.markdown(
                f"""
<div style="background:linear-gradient(135deg,{color},#66bb6a);
            color:#fff;padding:1.4rem 1.2rem;border-radius:14px;min-height:170px;
            box-shadow:0 4px 14px rgba(27,94,32,0.22);">
  <div style="font-size:1.35rem;font-weight:700;margin-bottom:0.5rem;">{title}</div>
  <div style="font-size:0.95rem;line-height:1.55;opacity:0.95;">{desc}</div>
</div>
""",
                unsafe_allow_html=True,
            )


def render_site_footer() -> None:
    """Homepage footer: funding, disclaimer, citation, license, contact."""
    from pathlib import Path

    import streamlit as st
    st.markdown("### Funding acknowledgement")
    f1, f2 = st.columns([1, 3])
    with f1:
        logo_path = Path("assets/interreg_logo.svg")
        if logo_path.exists():
            st.image(str(logo_path), width=180)
        else:
            st.markdown(
                '<a href="https://www.interreg.eu/" target="_blank" rel="noopener">Interreg</a>',
                unsafe_allow_html=True,
            )
    with f2:
        st.markdown(
            "Funded by the **Interreg Circulaire Teelt en Chemie** project "
            "(Circular Cultivation and Chemistry)."
        )

    st.markdown("### Disclaimer")
    st.markdown(
        """
This Sustainability Tool is provided for **research, education, and decision-support** purposes only.
Data and visualisations are compiled from published sources and project datasets; **no guarantee**
is made regarding completeness, accuracy, or fitness for a particular commercial or regulatory use.
Users remain **responsible for interpretation, verification, and any decisions** based on this tool.
"""
    )

    st.markdown("### Citation")
    st.markdown(
        f"If you use data or outputs from this tool in publications or reports, please cite:\n\n"
        f"> {TOOL_CITATION}"
    )

    st.markdown("### License")
    st.markdown(
        f"Tool documentation and publicly shared outputs are recommended for reuse under "
        f"**{RECOMMENDED_LICENSE}**, unless a specific dataset is subject to separate licensing. "
        f"User-contributed data remain the property of the contributor unless otherwise agreed."
    )

    st.markdown("### Contact")
    st.markdown(f"**Contact person:** [{CONTACT_EMAIL}](mailto:{CONTACT_EMAIL})")


def deployment_stability_note() -> str:
    """Explain Streamlit Community Cloud sleep behaviour for maintainers."""
    return """
### Application availability (Streamlit Community Cloud)

**Cause:** On the free Streamlit Community Cloud tier, apps **spin down after ~15 minutes of inactivity**.
The first visitor after sleep may see *“Get this app back”* while the container restarts. This is a
**hosting-platform limitation**, not a bug in SusTool.

**What we configured in this repo:**
- `enableCORS = false` and iframe-friendly settings in `.streamlit/config.toml` for embedding on lcatraining.nl.
- Data cache invalidation when `data/CTCdata.xlsx` changes.

**Feasible improvements:**
1. **Primary access via iframe** on [lcatraining.nl](https://www.lcatraining.nl/index.php/sustool/) so users stay in the group website.
2. **Paid Streamlit Cloud** or **self-hosted** deployment (Docker + systemd/nginx on your server) for 24/7 uptime.
3. Optional external **uptime ping** (e.g. cron hitting the app every 10 min) — may violate free-tier fair use; not recommended long term.

**Public access:** In Streamlit Cloud → **App settings → Sharing**, set visibility to **Public** and remove any
email allow-list. SusTool code does not enforce email login; restrictions are only in the Cloud dashboard.
"""
