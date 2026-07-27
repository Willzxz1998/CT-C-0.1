from __future__ import annotations

from datetime import datetime
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd
import streamlit as st

from src.config import (
    CITATION_FORMAT_EXAMPLE,
    CREATOR_ONLY_SUBPANELS,
    CREATOR_PASSWORD,
    DATA_CONTRIBUTION_PANEL,
    DATA_TYPES,
    DEFAULT_YEAR,
    EXCEL_PATH,
    MISSING_DATA_LOG_PATH,
    PRODUCTION_VIEW,
    PRODUCT_TYPES,
    SNF_PROVINCES,
    USER_MANUAL_PANEL,
    USER_MANUAL_PATH,
    USER_SUBPANELS,
)
from src.terminology import help_text, term_label
from src.ui_helpers import (
    deployment_stability_note,
    render_homepage_product_highlights,
    render_site_footer,
)
from src.data_loader import (
    filter_by_year,
    get_available_filters,
    get_production_summary,
    read_excel_data,
    read_production_data,
)
from src.calculations import (
    add_potential_products,
    aggregate_for_view,
    aggregate_production_for_view,
    summary_by_crop,
    summary_by_province,
    stacked_by_province_and_crop,
)
from src.visualizations import (
    bar_chart_rank_by_crop,
    pie_chart_by_province,
    stacked_bar_by_province_and_crop,
    choropleth_snf,
)


st.set_page_config(
    page_title="Circular Cultivation and Chemistry SusTool",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def inject_global_styles() -> None:
    st.markdown(
        """
<style>
/* Hide Streamlit chrome so the tool blends into the host website (lcatraining.nl) */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
[data-testid="stToolbar"] {visibility: hidden; height: 0;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {visibility: hidden;}

/* Hide the "Built with Streamlit" badge and any link back to streamlit.io */
a[href^="https://streamlit.io"],
a[href*="streamlit.io"],
[class*="viewerBadge"],
[data-testid="stAppViewBlockContainer"] + div a[href*="streamlit.io"] {
  display: none !important;
}

/* Hide the per-chart Streamlit fullscreen (expand) button */
[data-testid="StyledFullScreenButton"],
[data-testid="StyledFullScreenFrame"] button,
button[title="View fullscreen"],
button[title="Exit fullscreen"] {
  display: none !important;
}

/* Sidebar is unused (navigation/filters are in the main area); hide it and its toggle */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
  display: none !important;
}

/* Top navigation styling */
[data-testid="stAppViewContainer"] [role="radiogroup"] > label {
  margin-right: 0.4rem;
}

[data-testid="stAppViewContainer"] {
  background: linear-gradient(180deg, #f4faf4 0%, #ffffff 28%);
}
.hero-banner {
  background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 55%, #66bb6a 100%);
  color: #ffffff;
  padding: 2rem 2.2rem;
  border-radius: 16px;
  margin-bottom: 1.25rem;
  box-shadow: 0 8px 24px rgba(27, 94, 32, 0.18);
}
.hero-banner h1 {
  color: #ffffff !important;
  font-size: 2.1rem;
  margin: 0 0 0.35rem 0;
}
.hero-banner p {
  color: #e8f5e9;
  font-size: 1.05rem;
  margin: 0;
  line-height: 1.6;
}
.metric-card {
  background: #ffffff;
  border: 1px solid #c8e6c9;
  border-radius: 12px;
  padding: 1rem 1.1rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.04);
}
.how-card {
  background: #ffffff;
  border-left: 4px solid #2e7d32;
  border-radius: 10px;
  padding: 1rem 1.1rem;
  min-height: 140px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.home-content h2 { color: #1b4332; font-size: 1.45rem; margin-top: 1.2rem; }
.home-content h3 { color: #2e7d32; font-size: 1.15rem; margin-top: 0.9rem; }
.home-content p, .home-content li { font-size: 1.02rem; line-height: 1.72; color: #263238; }
.view-summary {
  background: #f1f8e9;
  border-radius: 10px;
  padding: 0.85rem 1rem;
  border: 1px solid #c5e1a5;
  margin-bottom: 1rem;
}
.site-footer {
  background: #f8fbf8;
  border-top: 1px solid #c8e6c9;
  padding: 1.5rem 0 0.5rem 0;
  margin-top: 2rem;
}
</style>
""",
        unsafe_allow_html=True,
    )


def get_creator_password() -> str:
    try:
        return str(st.secrets.get("creator_password", CREATOR_PASSWORD))
    except Exception:
        return CREATOR_PASSWORD


def is_creator() -> bool:
    if st.session_state.get("is_creator"):
        return True
    try:
        if bool(st.secrets.get("creator_mode", False)):
            st.session_state["is_creator"] = True
            return True
    except Exception:
        pass
    return False


def render_creator_gate() -> None:
    """Maintainer unlock — only shown when URL contains ?maintainer=1."""
    if is_creator():
        return
    if st.query_params.get("maintainer", "") != "1":
        return
    with st.expander("Maintainer sign-in", expanded=True):
        pwd = st.text_input("Password", type="password", key="creator_password_input")
        if st.button("Unlock maintainer tools"):
            if pwd == get_creator_password():
                st.session_state["is_creator"] = True
                st.rerun()
            elif pwd:
                st.error("Incorrect password.")


def navigation_options() -> list[str]:
    options = list(USER_SUBPANELS)
    if is_creator():
        insert_at = len(options)
        for panel in CREATOR_ONLY_SUBPANELS:
            if panel not in options:
                options.insert(insert_at, panel)
                insert_at += 1
        if "CIRCULCA (Coming soon)" not in options:
            options.insert(-1, "CIRCULCA (Coming soon)")
    return options


@st.cache_data
def load_residue_data_for_year(year: int = DEFAULT_YEAR, data_mtime: float = 0.0):
    df = read_excel_data()
    df_year = filter_by_year(df, year)
    provinces, crops = get_available_filters(df_year)
    return df_year, provinces, crops


@st.cache_data
def load_production_for_year(year: int = DEFAULT_YEAR, data_mtime: float = 0.0):
    prod = read_production_data(year=year)
    provinces, crops = get_available_filters(prod)
    return prod, provinces, crops


def get_ctcdata_mtime() -> float:
    """Used to automatically invalidate cached data after Excel updates."""
    try:
        return float(Path(EXCEL_PATH).stat().st_mtime)
    except Exception:
        return 0.0


def load_intro_paragraphs() -> list[str]:
    docx_path = Path("data/Intro&Ref of SusTool.docx")
    if docx_path.exists():
        try:
            with zipfile.ZipFile(docx_path) as zf:
                xml_bytes = zf.read("word/document.xml")
            root = ET.fromstring(xml_bytes)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs: list[str] = []
            for p in root.findall(".//w:p", ns):
                parts = [t.text for t in p.findall(".//w:t", ns) if t.text]
                line = "".join(parts).strip()
                if line:
                    paragraphs.append(line)
            if paragraphs:
                return paragraphs
        except Exception:
            pass
    intro_path = Path("content/intro_references.md")
    if intro_path.exists():
        return [line for line in intro_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [
        "Introduction",
        "Circular Cultivation and Chemistry SusTool supports exploration of horticultural biomass in the SNF region.",
    ]


def paragraphs_without_references(paragraphs: list[str]) -> list[str]:
    out: list[str] = []
    for line in paragraphs:
        if line.strip().lower() == "reference" or line.strip().lower().startswith("reference "):
            break
        out.append(line)
    return out


def format_paragraphs_as_markdown(paragraphs: list[str]) -> str:
    blocks: list[str] = []
    for line in paragraphs:
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if stripped == "Introduction":
            blocks.append("## Introduction")
        elif lower.startswith("about ") or lower.startswith("purpose of") or lower.startswith("objective of"):
            title = stripped.rstrip(":").strip()
            blocks.append(f"### {title}")
        elif stripped.endswith(":") and len(stripped) < 90:
            blocks.append(f"### {stripped.rstrip(':')}")
        else:
            blocks.append(stripped)
    return "\n\n".join(blocks)


def load_references_text() -> str:
    paragraphs = load_intro_paragraphs()
    refs: list[str] = []
    capture = False
    for line in paragraphs:
        if line.strip().lower().startswith("reference"):
            capture = True
        if capture:
            refs.append(line)
    if not refs:
        refs = paragraphs[-12:]
    return "\n\n".join(refs)


def render_home():
    inject_global_styles()
    summary = get_production_summary(DEFAULT_YEAR)

    st.markdown(
        """
<div class="hero-banner">
  <h1>Circular Cultivation and Chemistry SusTool</h1>
  <p>Explore horticultural production, residue inventories, and circular valorisation pathways across the SNF region.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Production in database (kt)", f"{summary['total_production_kt']:,.1f}")
    m2.metric("Crops with production data", summary["crop_count"])
    m3.metric("SNF provinces covered", summary["province_count"])
    m4.metric("Production records", summary["record_count"])

    render_homepage_product_highlights()

    st.markdown("### How to use this tool")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
<div class="how-card">
<b>1. Choose a view</b><br>
Open <i>Circular horticultural cultivation value chain</i> and pick production, residue, or potential product views.
</div>
""",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
<div class="how-card">
<b>2. Filter the region</b><br>
Select geographic scope and crops to focus on the SNF provinces relevant to your analysis.
</div>
""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
<div class="how-card">
<b>3. Explore charts & map</b><br>
Compare crop rankings, provincial contributions, stacked overviews, and the interactive SNF choropleth map.
</div>
""",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    intro_md = format_paragraphs_as_markdown(paragraphs_without_references(load_intro_paragraphs()))
    st.markdown('<div class="home-content">', unsafe_allow_html=True)
    st.markdown(intro_md)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Project focus")
    st.markdown(
        """
1. Compile and update crop production and residue inventories for the SNF region.
2. Compare provincial and crop-level circular valorisation opportunities.
3. Evaluate potential biochar and compost outputs under utilisation scenarios.
4. Support evidence-based decisions on sustainable horticultural value chains.
"""
    )

    st.markdown('<div class="site-footer">', unsafe_allow_html=True)
    render_site_footer()
    st.markdown("</div>", unsafe_allow_html=True)


def render_visualization_panel():
    inject_global_styles()
    st.title("Circular horticultural cultivation value chain")

    with st.expander("Filters", expanded=True):
        top = st.columns([2, 1])
        data_type_label = top[0].selectbox(
            "1. Data type",
            options=list(DATA_TYPES.keys()),
            index=0,
            help=help_text("Residue inventory"),
        )
        is_production_view = data_type_label == PRODUCTION_VIEW
        year = DEFAULT_YEAR  # Fixed reference year; documented in User Manual
        if top[1].button("Reload data", help="Refresh charts after updating data/CTCdata.xlsx"):
            st.cache_data.clear()
            st.rerun()

        if is_production_view:
            prod_df, provinces_all, crops_all = load_production_for_year(
                year, data_mtime=get_ctcdata_mtime()
            )
            residue_types_all: list[str] = []
            df_year = None
        else:
            df_year, provinces_all, crops_all = load_residue_data_for_year(
                year, data_mtime=get_ctcdata_mtime()
            )
            residue_types_all = []
            if df_year is not None and "residue_type" in df_year.columns:
                residue_types_all = sorted(df_year["residue_type"].dropna().unique().tolist())

        mid = st.columns([1, 2])
        geo_scope = mid[0].radio(
            "2. Geographic scope",
            options=["Entire SNF region", "Single province", "Multiple provinces"],
            index=0,
        )

        if geo_scope == "Entire SNF region":
            selected_provinces = SNF_PROVINCES
        elif geo_scope == "Single province":
            selected_provinces = [mid[1].selectbox("Province", options=SNF_PROVINCES)]
        else:
            selected_provinces = mid[1].multiselect(
                "Provinces",
                options=SNF_PROVINCES,
                default=SNF_PROVINCES,
            )

        selected_crops = st.multiselect(
            "3. Crops",
            options=crops_all,
            default=crops_all,
        )

        selected_residue_types = None
        if not is_production_view and residue_types_all:
            selected_residue_types = st.multiselect(
                "Residue type",
                options=residue_types_all,
                default=residue_types_all,
                help=help_text("Resid"),
            )

        utilization_rate = 1.0
        if data_type_label in PRODUCT_TYPES:
            utilization_percent = st.slider(
                "4. Residue utilization (%)",
                min_value=1,
                max_value=100,
                value=50,
                step=1,
                help=help_text("Residue utilization"),
            )
            utilization_rate = utilization_percent / 100.0

    # Terminology hints for the active view
    if data_type_label == "Potential Biochar Production":
        st.caption(
            f"{term_label('Biochar', 'Biochar')} (dry mass) · "
            f"{term_label('Pyrolysis', 'Pyrolysis')} · "
            f"{term_label('Biochar yield', 'Biochar yield')}",
            unsafe_allow_html=True,
        )
    elif data_type_label == "Potential Compost Production":
        st.caption(
            f"{term_label('Compost', 'Compost')} (wet mass) · "
            f"{term_label('Residue inventory', 'Residue inventory')}",
            unsafe_allow_html=True,
        )
    elif data_type_label == "Residue Inventory Overview":
        st.caption(
            f"{term_label('Residue inventory', 'Residue inventory')} (wet mass)",
            unsafe_allow_html=True,
        )

    if is_production_view:
        grouped = aggregate_production_for_view(
            prod_df,
            provinces=selected_provinces,
            crops=selected_crops,
        )
        filtered_for_tech = prod_df.copy()
    else:
        df_with_products = add_potential_products(df_year, utilization_rate=utilization_rate)
        grouped = aggregate_for_view(
            df_with_products,
            data_type_label=data_type_label,
            provinces=selected_provinces,
            crops=selected_crops,
            residue_types=selected_residue_types,
        )
        filtered_for_tech = df_with_products.copy()

    by_crop = summary_by_crop(grouped)
    by_crop = by_crop[by_crop["value"] > 0]
    by_province = summary_by_province(grouped)
    stacked = stacked_by_province_and_crop(grouped)

    value_label = data_type_label

    summary_bits = [
        f"**View:** {data_type_label}",
        f"**Provinces:** {', '.join(selected_provinces) if selected_provinces else 'None'}",
        f"**Crops:** {', '.join(selected_crops) if selected_crops else 'None'}",
    ]
    if is_production_view:
        summary_bits.append("**Data source:** `Crop_production` sheet (backend)")
        summary_bits.append(f"**Crops loaded:** {len(crops_all)} ({', '.join(crops_all)})")
    if selected_residue_types:
        summary_bits.append(f"**Residue type:** {', '.join(selected_residue_types)}")
    if data_type_label in PRODUCT_TYPES:
        summary_bits.append(f"**Residue utilization:** {int(utilization_rate * 100)}%")

    summary_html = "<br/>".join(summary_bits)
    st.markdown(f'<div class="view-summary">{summary_html}</div>', unsafe_allow_html=True)

    if selected_provinces:
        filtered_for_tech = filtered_for_tech[
            filtered_for_tech["province"].isin(selected_provinces)
        ]
    if selected_crops:
        filtered_for_tech = filtered_for_tech[filtered_for_tech["crop"].isin(selected_crops)]
    if selected_residue_types and "residue_type" in filtered_for_tech.columns:
        filtered_for_tech = filtered_for_tech[
            filtered_for_tech["residue_type"].isin(selected_residue_types)
        ]

    hover_info_col = None
    by_crop_with_hover = by_crop.copy()
    if data_type_label == "Potential Biochar Production":
        hover_info_col = "hover_info"

        def _biochar_hover(g: pd.DataFrame) -> pd.Series:
            parts: list[str] = []
            for _, row in g.drop_duplicates(subset=["pyrolysis_tech"]).iterrows():
                tech = str(row.get("pyrolysis_tech", "")).strip()
                if not tech or tech.lower() == "data unavailable":
                    continue
                y = pd.to_numeric(row.get("biochar_yield"), errors="coerce")
                if pd.notna(y) and y > 0:
                    parts.append(f"{tech} — Biochar yield: {y * 100:.1f}%")
                else:
                    parts.append(f"{tech} — Biochar yield: n/a")
            hover = "; ".join(sorted(parts)[:4]) if parts else "No pyrolysis record"
            return pd.Series({"hover_info": hover})

        meta = (
            filtered_for_tech.groupby("crop", as_index=False)
            .apply(_biochar_hover, include_groups=False)
            .reset_index(drop=True)
        )
        by_crop_with_hover = by_crop.merge(meta, on="crop", how="left")

        with st.expander("Pyrolysis technology and biochar yield (reference)", expanded=False):
            ref = (
                filtered_for_tech[pd.to_numeric(filtered_for_tech["biochar_yield"], errors="coerce") > 0]
                .drop_duplicates(subset=["crop", "pyrolysis_tech", "biochar_yield"])
                .sort_values(["crop", "pyrolysis_tech"])
            )
            if ref.empty:
                st.caption("No pyrolysis records for the current selection.")
            else:
                display = ref.assign(
                    **{
                        "Pyrolysis technology": ref["pyrolysis_tech"].astype(str),
                        "Biochar yield": (
                            pd.to_numeric(ref["biochar_yield"], errors="coerce") * 100
                        ).map(lambda x: f"{x:.1f}%"),
                        "Crop": ref["crop"],
                    }
                )
                st.dataframe(
                    display[["Crop", "Pyrolysis technology", "Biochar yield"]],
                    use_container_width=True,
                    hide_index=True,
                )
    elif data_type_label == "Potential Compost Production":
        hover_info_col = "hover_info"
        meta = (
            filtered_for_tech.groupby("crop", as_index=False)
            .apply(
                lambda g: pd.Series(
                    {
                        "hover_info": "Composting: "
                        + "; ".join(
                            sorted(
                                g["composting_tech"]
                                .fillna("Data unavailable")
                                .astype(str)
                                .unique()
                            )[:3]
                        )
                    }
                )
            )
            .reset_index(drop=True)
        )
        by_crop_with_hover = by_crop.merge(meta, on="crop", how="left")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Crop ranking (Bar)",
        "Province contribution (Pie)",
        "Overview",
        "SNF map",
    ])

    with tab1:
        if is_production_view:
            st.subheader("Horticultural production overview")
            fig_bar = bar_chart_rank_by_crop(
                by_crop,
                "Crop production",
                title="Crop production",
                unit="kt",
            )
        else:
            st.subheader(data_type_label)
            fig_bar = bar_chart_rank_by_crop(
                by_crop_with_hover,
                value_label,
                title="Crop ranking",
                unit="kt",
                hover_col=hover_info_col,
            )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        pie_title = "Provincial contribution" if is_production_view else "Provincial contribution"
        fig_pie = pie_chart_by_province(by_province, value_label, title=pie_title, unit="kt")
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        stack_label = "Horticultural production" if is_production_view else value_label
        fig_stack = stacked_bar_by_province_and_crop(
            stacked,
            stack_label,
            title="Overview by province and crop",
            unit="kt",
        )
        st.plotly_chart(fig_stack, use_container_width=True)

    with tab4:
        st.subheader("SNF choropleth map")
        fig_map = choropleth_snf(by_province, value_label)
        st.plotly_chart(fig_map, use_container_width=True)


def render_data_contribution_panel():
    st.title(DATA_CONTRIBUTION_PANEL)
    st.markdown(
        """
Help us expand and improve the SNF horticultural database. You can contribute:

- **Production data** for the **23 vegetables and 10 fruit crops** in the study region;
- **Biochar yield** obtained from your residues (dry-mass basis);
- Corresponding **pyrolysis technologies** and process conditions;
- **References and data sources** supporting your submission.

Accepted contributions will be reviewed by the research team. **Contributors whose data are accepted will receive an acknowledgement email.**
"""
    )

    st.markdown("#### Submission guidelines")
    st.markdown(
        f"""
- Use **wet mass (kt)** for residue inventory and **dry mass** for biochar yield unless stated otherwise.
- Align crop names with the project crop list where possible.
- Provide **complete metadata**: province/NUTS ID, crop, residue type, units, and method.
- Include a **standard citation** for your source (see format below).

**Required citation format (example):**

> {CITATION_FORMAT_EXAMPLE}
"""
    )

    year = DEFAULT_YEAR
    df_year, _, _ = load_residue_data_for_year(year, data_mtime=get_ctcdata_mtime())

    missing_prod = df_year[df_year["missing_production"]][["nuts_id", "province", "crop"]].drop_duplicates()
    missing_residue = df_year[df_year["missing_residue"]][
        ["nuts_id", "province", "crop", "residue_type"]
    ].drop_duplicates()
    missing_biochar = df_year[df_year["missing_biochar_yield"]][
        ["nuts_id", "province", "crop", "residue_type"]
    ].drop_duplicates()

    if is_creator():
        c1, c2, c3 = st.columns(3)
        c1.metric("Missing crop production records", len(missing_prod))
        c2.metric("Missing residue records", len(missing_residue))
        c3.metric("Missing biochar-yield records", len(missing_biochar))

        st.subheader("Internal gap tables (maintainers)")
        st.dataframe(missing_prod, use_container_width=True, hide_index=True)
        st.dataframe(missing_residue, use_container_width=True, hide_index=True)
        st.dataframe(missing_biochar, use_container_width=True, hide_index=True)
        st.markdown("---")

    st.subheader("Submit your data")
    st.caption("Fields marked with guidance help us validate and cite your contribution.")

    with st.form("data_contribution_form", clear_on_submit=True):
        st.markdown("**Contact (for acknowledgement email)**")
        contributor_email = st.text_input("Your email address", placeholder="name@institution.edu")

        col1, col2 = st.columns(2)
        nuts_id = col1.text_input("NUTS_ID", value="BE23", help=help_text("NUTS2"))
        province = col2.selectbox("Province", options=SNF_PROVINCES)
        crop = col1.text_input("Crop", value="Blueberry")
        residue_type = col2.selectbox(
            "Residue type",
            options=["Resid", "Farm food loss"],
            help=help_text("Resid"),
        )
        production_kt = col1.number_input("Production (kt, optional)", min_value=0.0, value=0.0, step=0.1)
        residue_kt = col2.number_input(
            "Residue inventory (kt, wet mass)",
            min_value=0.0,
            value=10.0,
            step=0.1,
            help=help_text("Residue inventory"),
        )
        biochar_yield = col1.number_input(
            "Biochar yield (dry mass ratio, e.g. 0.18 = 18%)",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01,
            help=help_text("Biochar yield"),
        )
        pyrolysis_tech = col2.text_input(
            "Pyrolysis technology / conditions",
            help=help_text("Pyrolysis"),
        )
        citation = st.text_area(
            "Reference / citation (required format)",
            placeholder=CITATION_FORMAT_EXAMPLE,
        )
        notes = st.text_area("Notes, methods, and data quality information")
        submitted = st.form_submit_button("Submit contribution")

    if submitted:
        if not contributor_email.strip():
            st.error("Please provide your email address for acknowledgement.")
            return
        if not citation.strip():
            st.error("Please provide a reference/citation for your data.")
            return

        log_path = Path(MISSING_DATA_LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        row = pd.DataFrame(
            [
                {
                    "submitted_at_utc": datetime.utcnow().isoformat(),
                    "year": year,
                    "contributor_email": contributor_email.strip(),
                    "nuts_id": nuts_id,
                    "province": province,
                    "crop": crop,
                    "residue_type": residue_type,
                    "production_kt": production_kt,
                    "residue_kt": residue_kt,
                    "biochar_yield": biochar_yield,
                    "pyrolysis_tech": pyrolysis_tech,
                    "citation": citation.strip(),
                    "notes": notes,
                }
            ]
        )
        if log_path.exists():
            existing = pd.read_csv(log_path)
            out = pd.concat([existing, row], ignore_index=True)
        else:
            out = row
        out.to_csv(log_path, index=False)
        st.success(
            "Thank you — your contribution was saved and will be reviewed. "
            "If accepted, you will receive an acknowledgement email."
        )


def render_user_manual_panel():
    st.title(USER_MANUAL_PANEL)
    manual_path = Path(USER_MANUAL_PATH)
    if manual_path.exists():
        st.markdown(manual_path.read_text(encoding="utf-8"))
    else:
        st.warning("User manual file not found.")


def render_about():
    st.title("Methods & data")
    st.markdown(
        """
### Updating the data

- All core data are loaded from `data/CTCdata.xlsx` (3 sheets).
- **Horticultural production overview** reads only the `Crop_production` sheet.
- Residue and product views use `Residue_inventory` merged with `Conversion_parameters`.
- NUTS2 IDs map to the eight SNF provinces; boundaries come from `data/geo/snf_nuts2.geojson`.

### Maintainer access

- Public users see browsing, visualisation, Data Contribution, and User Manual.
- Maintainers: open the app with `?maintainer=1` and sign in (password in Streamlit secrets as `creator_password`).

### Deployment

Push updates to GitHub and reboot the Streamlit Cloud app to refresh the live deployment.
"""
    )
    st.markdown(deployment_stability_note())


def render_references_panel():
    st.title("References")
    st.markdown(load_references_text())


def main():
    inject_global_styles()
    render_creator_gate()

    # Top navigation in the main area so it always works inside an iframe
    # (independent of whether the Streamlit sidebar is open).
    options = navigation_options()
    if "active_subpanel" not in st.session_state or st.session_state["active_subpanel"] not in options:
        st.session_state["active_subpanel"] = options[0]

    subpanel = st.radio(
        "Navigate",
        options=options,
        index=options.index(st.session_state["active_subpanel"]),
        horizontal=True,
        label_visibility="collapsed",
        key="active_subpanel",
    )
    st.markdown("<hr style='margin-top:0.2rem; margin-bottom:0.8rem;'/>", unsafe_allow_html=True)

    if subpanel == "Homepage":
        render_home()
    elif subpanel == "Circular horticultural cultivation value chain":
        render_visualization_panel()
    elif subpanel == DATA_CONTRIBUTION_PANEL:
        render_data_contribution_panel()
    elif subpanel == USER_MANUAL_PANEL:
        render_user_manual_panel()
    elif subpanel == "References":
        render_references_panel()
    elif subpanel == "CIRCULCA (Coming soon)":
        st.title("CIRCULCA")
        st.info("This add-on will be designed in the next version.")
    elif subpanel == "Methods & Data":
        render_about()
    else:
        st.warning("Unknown section.")


if __name__ == "__main__":
    main()
