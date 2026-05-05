from __future__ import annotations

from datetime import datetime
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

import pandas as pd
import streamlit as st

from src.config import (
    DATA_TYPES,
    PRODUCT_TYPES,
    SNF_PROVINCES,
    DEFAULT_YEAR,
    MISSING_DATA_LOG_PATH,
)
from src.data_loader import read_excel_data, filter_by_year, get_available_filters
from src.calculations import (
    add_potential_products,
    aggregate_for_view,
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
)


@st.cache_data
def load_data_for_year(year: int = DEFAULT_YEAR):
    df = read_excel_data()
    df_year = filter_by_year(df, year)
    provinces, crops = get_available_filters(df_year)
    return df_year, provinces, crops


def load_intro_text() -> str:
    docx_path = Path("data/Intro&Ref of SusTool.docx")
    if docx_path.exists():
        try:
            with zipfile.ZipFile(docx_path) as zf:
                xml_bytes = zf.read("word/document.xml")
            root = ET.fromstring(xml_bytes)
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = []
            for p in root.findall(".//w:p", ns):
                parts = [t.text for t in p.findall(".//w:t", ns) if t.text]
                line = "".join(parts).strip()
                if line:
                    paragraphs.append(line)
            if paragraphs:
                return "\n\n".join(paragraphs)
        except Exception:
            pass
    intro_path = Path("content/intro_references.md")
    if intro_path.exists():
        return intro_path.read_text(encoding="utf-8")
    return (
        "# Circular Cultivation and Chemistry SusTool\n\n"
        "Please add introduction, user manual, scope, and references in `content/intro_references.md`.\n"
    )


def load_references_text() -> str:
    text = load_intro_text()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    ref_start = 0
    for i, line in enumerate(lines):
        if "reference" in line.lower():
            ref_start = i
            break
    refs = lines[ref_start:] if ref_start else lines[-20:]
    return "\n\n".join(refs)


def load_homepage_text_without_references() -> str:
    text = load_intro_text()
    lines = text.splitlines()
    output: list[str] = []
    for line in lines:
        if "reference" in line.lower():
            break
        output.append(line)
    cleaned = "\n".join(output).strip()
    return cleaned if cleaned else text


def render_home():
    st.title("Circular Cultivation and Chemistry SusTool")
    st.markdown(
        """
<style>
.home-content h1 { font-size: 2.0rem; font-weight: 800; margin-bottom: 0.6rem; }
.home-content h2 { font-size: 1.4rem; font-weight: 700; margin-top: 1.2rem; margin-bottom: 0.4rem; }
.home-content h3 { font-size: 1.15rem; font-weight: 700; margin-top: 1.0rem; margin-bottom: 0.3rem; }
.home-content p, .home-content li { font-size: 1.02rem; line-height: 1.65; }
</style>
""",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='home-content'>{load_homepage_text_without_references()}</div>", unsafe_allow_html=True)


def render_visualization_panel():
    st.title("Circular horticultural cultivation value chain")

    # Sidebar: multi-level filters
    st.sidebar.header("Filters")

    if st.sidebar.button("Reload data"):
        st.cache_data.clear()
        st.rerun()

    data_type_label = st.sidebar.selectbox(
        "1. Data type",
        options=list(DATA_TYPES.keys()),
        index=0,
    )

    year = st.sidebar.number_input(
        "Year", min_value=2000, max_value=2100, value=DEFAULT_YEAR, step=1
    )

    df_year, provinces_all, crops_all = load_data_for_year(year)

    # Residue type filter (only for residue and potential products)
    residue_types_all = []
    if "residue_type" in df_year.columns:
        residue_types_all = sorted(df_year["residue_type"].dropna().unique().tolist())

    # Geographic scope
    geo_scope = st.sidebar.radio(
        "2. Geographic scope",
        options=["Entire SNF region", "Single province", "Multiple provinces"],
        index=0,
    )

    if geo_scope == "Entire SNF region":
        selected_provinces = SNF_PROVINCES
    elif geo_scope == "Single province":
        selected_provinces = [
            st.sidebar.selectbox("Province", options=SNF_PROVINCES)
        ]
    else:
        selected_provinces = st.sidebar.multiselect(
            "Provinces",
            options=SNF_PROVINCES,
            default=SNF_PROVINCES,
        )

    # Crop selection
    selected_crops = st.sidebar.multiselect(
        "3. Crops",
        options=crops_all,
        default=crops_all,
    )

    selected_residue_types = None
    if data_type_label != "Horticultural Production Overview" and residue_types_all:
        selected_residue_types = st.sidebar.multiselect(
            "Residue type",
            options=residue_types_all,
            default=residue_types_all,
        )

    # Residue utilization scenario – only for potential product types
    utilization_rate = 1.0
    if data_type_label in PRODUCT_TYPES:
        utilization_percent = st.sidebar.slider(
            "4. Residue utilization (%)",
            min_value=1,
            max_value=100,
            value=50,
            step=1,
        )
        utilization_rate = utilization_percent / 100.0

    # Calculations
    df_with_products = add_potential_products(df_year, utilization_rate=utilization_rate)
    grouped = aggregate_for_view(
        df_with_products,
        data_type_label=data_type_label,
        provinces=selected_provinces,
        crops=selected_crops,
        residue_types=selected_residue_types,
    )

    by_crop = summary_by_crop(grouped)
    by_crop = by_crop[by_crop["value"] > 0]
    by_province = summary_by_province(grouped)
    stacked = stacked_by_province_and_crop(grouped)

    value_label = data_type_label

    # Summary of current selection
    st.markdown(
        f"""
**View:** {data_type_label}  
**Year:** {year}  
**Provinces:** {", ".join(selected_provinces) if selected_provinces else "None"}  
**Crops:** {", ".join(selected_crops) if selected_crops else "None"}  
{"**Residue type:** " + ", ".join(selected_residue_types) if selected_residue_types else ""}
{"**Residue utilization:** " + str(int(utilization_rate * 100)) + "%" if data_type_label in PRODUCT_TYPES else ""}
"""
    )

    filtered_for_tech = df_with_products.copy()
    if selected_provinces:
        filtered_for_tech = filtered_for_tech[filtered_for_tech["province"].isin(selected_provinces)]
    if selected_crops:
        filtered_for_tech = filtered_for_tech[filtered_for_tech["crop"].isin(selected_crops)]
    if selected_residue_types:
        filtered_for_tech = filtered_for_tech[filtered_for_tech["residue_type"].isin(selected_residue_types)]
    hover_info_col = None
    by_crop_with_hover = by_crop.copy()
    if data_type_label == "Potential Biochar Production":
        hover_info_col = "hover_info"
        meta = (
            filtered_for_tech.groupby("crop", as_index=False)
            .apply(
                lambda g: pd.Series(
                    {
                        "hover_info": "Pyrolysis: "
                        + "; ".join(
                            sorted(
                                g["pyrolysis_tech"]
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
        if data_type_label == "Horticultural Production Overview":
            st.subheader("Horticultural Production Overview")
            fig_bar = bar_chart_rank_by_crop(
                by_crop,
                "Horticultural Production Overview",
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
        fig_pie = pie_chart_by_province(by_province, value_label, title="Provincial contribution", unit="kt")
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        if data_type_label == "Horticultural Production Overview":
            fig_stack = stacked_bar_by_province_and_crop(
                stacked,
                "Horticultural production overview",
                title="Overview",
                unit="kt",
            )
        else:
            fig_stack = stacked_bar_by_province_and_crop(stacked, value_label, title="Overview", unit="kt")
        st.plotly_chart(fig_stack, use_container_width=True)

    with tab4:
        st.subheader("SNF choropleth map")
        fig_map = choropleth_snf(by_province, value_label)
        st.plotly_chart(fig_map, use_container_width=True)


def render_missing_data_panel():
    st.title("Missing data")
    year = st.number_input("Year", min_value=2000, max_value=2100, value=DEFAULT_YEAR, step=1)
    df_year, _, _ = load_data_for_year(year)

    missing_prod = df_year[df_year["missing_production"]][["nuts_id", "province", "crop"]].drop_duplicates()
    missing_residue = df_year[df_year["missing_residue"]][["nuts_id", "province", "crop", "residue_type"]].drop_duplicates()
    missing_biochar = df_year[df_year["missing_biochar_yield"]][
        ["nuts_id", "province", "crop", "residue_type"]
    ].drop_duplicates()

    c1, c2, c3 = st.columns(3)
    c1.metric("Missing crop production records", len(missing_prod))
    c2.metric("Missing residue records", len(missing_residue))
    c3.metric("Missing biochar-yield records", len(missing_biochar))

    st.subheader("Missing crop production")
    st.dataframe(missing_prod, use_container_width=True, hide_index=True)
    st.subheader("Missing residue inventory")
    st.dataframe(missing_residue, use_container_width=True, hide_index=True)
    st.subheader("Missing biochar yield")
    st.dataframe(missing_biochar, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.subheader("Submit missing data")
    st.caption("Submitted records are saved automatically.")

    with st.form("missing_data_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nuts_id = col1.text_input("NUTS_ID", value="BE23")
        province = col2.text_input("Province", value="East Flanders")
        crop = col1.text_input("Crop", value="Blueberry")
        residue_type = col2.text_input("Residue type", value="Resid")
        residue_kt = col1.number_input("Residue (kt)", min_value=0.0, value=10.0, step=0.1)
        biochar_yield = col2.number_input("Biochar yield", min_value=0.0, value=0.0, step=0.01)
        pyrolysis_tech = st.text_input("Pyrolysis technology parameters")
        notes = st.text_area("Notes / source")
        submitted = st.form_submit_button("Save submission")

    if submitted:
        log_path = Path(MISSING_DATA_LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        row = pd.DataFrame(
            [
                {
                    "submitted_at_utc": datetime.utcnow().isoformat(),
                    "year": year,
                    "nuts_id": nuts_id,
                    "province": province,
                    "crop": crop,
                    "residue_type": residue_type,
                    "residue_kt": residue_kt,
                    "biochar_yield": biochar_yield,
                    "pyrolysis_tech": pyrolysis_tech,
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
        st.success("Submission saved successfully.")


def render_about():
    st.title("Methods & data")
    st.markdown(
        """
### Updating the data

- All core data are loaded from `data/CTCdata.xlsx` (3 sheets).
- This version uses NUTS2 IDs (`NL41`, `NL42`, `NL34`, `BE21`, `BE22`, `BE23`, `BE24`, `BE25`) and maps them to province names.
- You can update production, residue inventory, conversion yields, and technology references directly in Excel.
- As long as the column structure is compatible, **no Python code changes are required**.

### Map and geography

- The map uses the **NUTS2 boundaries** of the 8 SNF provinces in `data/geo/snf_nuts2.geojson`.
- The GeoJSON property `name` must match the `province` names in the Excel file.

### Extending to more years

- Add additional years as rows in Excel (change the `year` column accordingly).
- Use the **Year** input in the Visualization Panel to explore different years.

### Handling missing values

- If some columns are missing or contain empty values:
  - `residue_usable_fraction` defaults to 1.0
  - `biochar_yield` and `compost_yield` default to 0
  - `moisture_content` defaults to 0.5
  - `ca_content` defaults to 0
- You can adjust these defaults in `src/data_loader.py` (the `defaults` dictionary).

---

## Deployment and domain (overview)

### 1. Deploy to Streamlit Community Cloud (recommended)

1. Push this project to a GitHub repository.
2. Log in to [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Create a new app:
   - Select your GitHub repo.
   - Set `Main file` to `app.py`.
   - Ensure `requirements.txt` is present.
4. After deployment, you will get a public URL like  
   `https://your-project-name.streamlit.app`.

### 2. Connect a custom domain

1. Purchase a domain (e.g. `sustainabilitytool.eu`, `horti-biomass.eu`, `snf-circularity.org`).
2. In your domain DNS settings, add a **CNAME** record:
   - Host: e.g. `portal` (or `@` for root).
   - Type: `CNAME`.
   - Value: your Streamlit URL (e.g. `your-project-name.streamlit.app`).
3. In Streamlit app settings, configure the **Custom Domain** to match your domain.
4. Wait for DNS to propagate (typically 10–60 minutes).

### 3. Maintenance

- **Update Excel data**:
  - Edit your Excel file locally.
  - Commit and push to GitHub (or upload to your deployment platform).
  - Trigger a redeploy if needed.
- **Add more crops or years**:
  - Add rows in Excel; the app will automatically pick them up.
- **Backups**:
  - Regularly back up your Excel data and repository.
"""
    )


def render_references_panel():
    st.title(" ")
    st.markdown(load_references_text())


def main():
    st.sidebar.header("Research Tool")
    st.sidebar.markdown("**Circular Cultivation and Chemistry SusTool**")
    subpanel = st.sidebar.radio(
        "Subpanel",
        options=[
            "Homepage",
            "Circular horticultural cultivation value chain",
            "Missing data",
            "CIRCULCA (Coming soon)",
            "Methods & Data",
            "References",
        ],
        index=0,
    )

    if subpanel == "Homepage":
        render_home()
    elif subpanel == "Circular horticultural cultivation value chain":
        render_visualization_panel()
    elif subpanel == "Missing data":
        render_missing_data_panel()
    elif subpanel == "References":
        render_references_panel()
    elif subpanel == "CIRCULCA (Coming soon)":
        st.title("CIRCULCA")
        st.info("This add-on will be designed in the next version.")
    else:
        render_about()


if __name__ == "__main__":
    main()

