"""Reusable UI fragments: header, footer, homepage blocks, deployment notes."""

from __future__ import annotations

import re
from pathlib import Path

CONTACT_EMAIL = "xinzhi.zhong@maastrichtuniversity.nl"
TOOL_CITATION = (
    "Circular Cultivation and Chemistry Sustainability Tool (SusTool), "
    "Maastricht University / Interreg Circulaire Teelt en Chemie, "
    "https://www.lcatraining.nl/index.php/sustool/ (accessed YYYY-MM-DD)."
)
RECOMMENDED_LICENSE = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
INTERREG_LOGO_PATH = Path("assets/interreg_vlaanderen_nederland.svg")
INTERREG_PROJECT_NAME = "Interreg Vlaanderen–Nederland · Circulaire Teelt en Chemie"


def _strip_inline_citations(text: str) -> str:
    """Remove parenthetical author–year citations such as (Ghiat et al., 2022)."""
    cleaned = re.sub(r"\s*\([A-Z][^)]*\d{4}[^)]*\)", "", text)
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def _sentence_case(text: str) -> str:
    """Capitalise the first alphabetic character of a sentence."""
    text = text.strip()
    if not text:
        return text
    for i, ch in enumerate(text):
        if ch.isalpha():
            return text[:i] + ch.upper() + text[i + 1 :]
    return text


def render_interreg_logo(*, width: int = 220) -> None:
    """Show the official Interreg Vlaanderen–Nederland programme logo."""
    import streamlit as st

    if INTERREG_LOGO_PATH.exists():
        st.image(str(INTERREG_LOGO_PATH), width=width)
    else:
        fallback = Path("assets/interreg_vlaanderen_nederland.jpeg")
        if fallback.exists():
            st.image(str(fallback), width=width)
        else:
            st.caption("Interreg Vlaanderen–Nederland")


def render_site_header() -> None:
    """Branding header with programme logo (shown on all pages)."""
    import streamlit as st

    st.markdown(
        '<div class="site-header">',
        unsafe_allow_html=True,
    )
    col_logo, col_text = st.columns([1, 2])
    with col_logo:
        render_interreg_logo(width=240)
    with col_text:
        st.markdown(
            f"""
<div class="site-header-text">
  <strong>{INTERREG_PROJECT_NAME}</strong><br/>
  <span style="color:#546e7a;font-size:0.95rem;">
    Circular Cultivation and Chemistry — Sustainability Tool
  </span>
</div>
""",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


def render_homepage_scope_metrics() -> None:
    """Key scope indicators below the homepage hero title."""
    import streamlit as st

    items = [
        (
            "Horticultural crops included",
            "33 vegetables and 10 fruits",
        ),
        (
            "Region covered",
            "5 provinces in Flanders, Belgium and 3 provinces in the southern Netherlands",
        ),
        (
            "Residue-based products",
            "Biochar, compost, coumaric acid, and more",
        ),
    ]
    cols = st.columns(len(items))
    for col, (title, body) in zip(cols, items):
        with col:
            st.markdown(
                f"""
<div class="metric-card">
  <div class="metric-card-title">{title}</div>
  <div class="metric-card-body">{body}</div>
</div>
""",
                unsafe_allow_html=True,
            )


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
            "potential for soil amendment and carbon storage.",
        ),
        (
            c2,
            "Compost",
            "#2e7d32",
            "Stabilised organic material from aerobic decomposition; "
            "supports nutrient recycling and soil health.",
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


def render_structured_home_intro(paragraphs: list[str]) -> None:
    """Render project/tool introduction from docx paragraphs with clear sections."""
    import streamlit as st

    # Strip reference section
    intro_lines: list[str] = []
    for line in paragraphs:
        if line.strip().lower().startswith("reference"):
            break
        intro_lines.append(line.strip())

    project_blurb = ""
    tool_purpose = ""
    tool_objective = ""
    tracks: list[str] = []
    section = None

    for line in intro_lines:
        lower = line.lower()
        if line == "Introduction":
            continue
        if lower.startswith("about the circular cultivation"):
            section = "project"
            continue
        if lower.startswith("about the sustainability tool"):
            section = "tool"
            continue
        if lower.startswith("the project focuses on three tracks"):
            section = "tracks"
            continue
        if lower.startswith("purpose of this tool"):
            tool_purpose = line.split(":", 1)[-1].strip()
            section = "tool"
            continue
        if lower.startswith("objective of this tool"):
            tool_objective = line.split(":", 1)[-1].strip()
            section = "tool"
            continue
        # Skip the long "Specifically, ..." inventory sentence on the homepage.
        if lower.startswith("specifically,"):
            section = "tool"
            continue

        if section == "project" and not lower.startswith("the project focuses"):
            project_blurb = line if not project_blurb else f"{project_blurb} {line}"
        elif section == "tracks":
            if line and not line.endswith(":"):
                tracks.append(_sentence_case(line.rstrip(".")))

    tool_purpose = _sentence_case(_strip_inline_citations(tool_purpose))
    tool_objective = _sentence_case(_strip_inline_citations(tool_objective))
    # Remove year mention from the objective (database year is documented in the User Manual).
    tool_objective = re.sub(
        r"\s*of year\s+\d{4}\.?",
        ".",
        tool_objective,
        flags=re.IGNORECASE,
    )
    tool_objective = re.sub(r"\.\s*\.", ".", tool_objective).strip()
    if tool_objective and not tool_objective.endswith("."):
        tool_objective += "."

    st.markdown("### About the project")
    if project_blurb:
        st.markdown(
            f'<div class="intro-panel">{_sentence_case(project_blurb)}</div>',
            unsafe_allow_html=True,
        )

    if tracks:
        st.markdown("#### Project focus — three tracks")
        tcols = st.columns(min(len(tracks), 3))
        for i, track in enumerate(tracks[:3]):
            with tcols[i]:
                st.markdown(
                    f"""
<div class="how-card">
  <b>Track {i + 1}</b><br>{track}
</div>
""",
                    unsafe_allow_html=True,
                )

    st.markdown("### About this Sustainability Tool")
    if tool_purpose:
        st.markdown(f"**Purpose.** {tool_purpose}")
    if tool_objective:
        st.markdown(f"**Objective.** {tool_objective}")


def render_site_footer() -> None:
    """Homepage footer: funding logo, disclaimer, citation, license, contact — structured panels."""
    import streamlit as st

    st.markdown("---")
    st.markdown("### Funding acknowledgement")
    f1, f2 = st.columns([1, 2])
    with f1:
        render_interreg_logo(width=260)
    with f2:
        st.markdown(
            """
<div class="footer-panel">
<p><strong>Funded by the Interreg Circulaire Teelt en Chemie project</strong><br/>
(Circular Cultivation and Chemistry), supported by
<strong>Interreg Vlaanderen–Nederland</strong>.</p>
</div>
""",
            unsafe_allow_html=True,
        )

    note1, note2 = st.columns(2)
    with note1:
        st.markdown(
            """
<div class="footer-panel">
<h4>Disclaimer</h4>
<p>This Sustainability Tool is provided for <strong>research, education, and decision-support</strong>
purposes only. Data and visualisations are compiled from published sources and project datasets;
<strong>no guarantee</strong> is made regarding completeness, accuracy, or fitness for a particular
commercial or regulatory use. Users remain <strong>responsible for interpretation, verification,
and any decisions</strong> based on this tool.</p>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
<div class="footer-panel">
<h4>License</h4>
<p>Tool documentation and publicly shared outputs are recommended for reuse under
<strong>{RECOMMENDED_LICENSE}</strong>, unless a specific dataset is subject to separate licensing.
User-contributed data remain the property of the contributor unless otherwise agreed.</p>
</div>
""",
            unsafe_allow_html=True,
        )
    with note2:
        st.markdown(
            f"""
<div class="footer-panel">
<h4>Citation</h4>
<p>If you use data or outputs from this tool in publications or reports, please cite:</p>
<blockquote style="margin:0.5rem 0;padding:0.75rem 1rem;background:#fff;border-left:4px solid #2e7d32;">
{TOOL_CITATION}
</blockquote>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
<div class="footer-panel">
<h4>Contact</h4>
<p><strong>Contact person:</strong><br/>
<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</div>
""",
            unsafe_allow_html=True,
        )


def deployment_stability_note() -> str:
    """Explain Streamlit Community Cloud sleep behaviour and hosting alternatives."""
    return """
### Application availability (Streamlit Community Cloud)

**Can code keep the app always awake on Streamlit Community (free)?**  
**No.** There is no supported in-app keep-alive that reliably prevents sleep on the free tier.

**Long-term hosting on lcatraining.nl:** see `docs/DEPLOYMENT.md` and `deploy/` for nginx + systemd configs.
Self-hosting requires SSH access to the WordPress/server host, nginx reverse proxy, and an SSL certificate.
"""
