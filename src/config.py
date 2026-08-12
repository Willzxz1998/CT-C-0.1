import os

# Official English province names (SNF region, NUTS2).
SNF_PROVINCES = [
    "Zeeland",
    "North Brabant",
    "Limburg (Netherlands)",
    "East Flanders",
    "West Flanders",
    "Flemish Brabant",
    "Antwerp",
    "Limburg (Belgium)",
]

NUTS2_TO_PROVINCE = {
    "NL41": "North Brabant",
    "NL42": "Limburg (Netherlands)",
    "NL34": "Zeeland",
    "BE21": "Antwerp",
    "BE22": "Limburg (Belgium)",
    "BE23": "East Flanders",
    "BE24": "Flemish Brabant",
    "BE25": "West Flanders",
}

# Internal reference year (not shown in the public UI).
DEFAULT_YEAR = 2022

DATA_TYPES = {
    "Horticultural Production Overview": "production_kt",
    "Residue Inventory Overview": "residue_kt",
    "Potential Biochar Production": "biochar_potential_kt",
    "Potential Compost Production": "compost_potential_kt",
    "GWP of horticultural production and residue utilization": "gwp_total_kgco2eq_per_kg_crop",
}

PRODUCT_TYPES = [
    "Potential Biochar Production",
    "Potential Compost Production",
]

PRODUCTION_VIEW = "Horticultural Production Overview"

DATA_CONTRIBUTION_PANEL = "Data Contribution"
USER_MANUAL_PANEL = "User Manual"

# Subpanels visible to public users (browsing the tool).
USER_SUBPANELS = [
    "Homepage",
    "Circular horticultural cultivation value chain",
    DATA_CONTRIBUTION_PANEL,
    USER_MANUAL_PANEL,
    "References",
]

# Extra subpanels for creators/maintainers only.
CREATOR_ONLY_SUBPANELS = [
    "Methods & Data",
]

# Set SUSTOOL_CREATOR_PASSWORD in Streamlit secrets or environment variables.
CREATOR_PASSWORD = os.environ.get("SUSTOOL_CREATOR_PASSWORD", "ctc-maintainer")

EXCEL_PATH = "data/CTCdata.xlsx"
GEOJSON_PATH = "data/geo/snf_nuts2.geojson"
USER_MANUAL_PATH = "content/user_manual.md"

SHEETS = {
    "production": "Crop_production",
    "residue": "Residue_inventory",
    "conversion": "Conversion_parameters",
    "crop_emi": "Crop_pro_emi",
    "resi_uti_emi": "Resi_uti_emission",
}

COLS = {
    "year": "Year",
    "nuts_id": "NUTS_ID",
    "province": "Province",
    "crop": "Crop",
    "crop_residue": "Crop_name",
    "production_kt": "Production",
    "residue_type": "Residue_type",
    "residue_kt": "Residue",
    "biochar_yield": "Biochar_yield",
    "initial_moisture": "Initial_moisture",
    "final_moisture": "Final_moisture",
    "pyrolysis_tech": "Pyrolysis_tech",
    "compost_yield": "Compost_yield",
    "composting_tech": "Composting_tech",
}

# Map Excel / legacy labels to official English province names.
PROVINCE_ALIASES = {
    "Noord-Brabant": "North Brabant",
    "Noord Brabant": "North Brabant",
    "Limburg (NL)": "Limburg (Netherlands)",
    "Limburg (BE)": "Limburg (Belgium)",
    "Antwerp Province": "Antwerp",
    "Prov. Oost-Vlaanderen": "East Flanders",
    "Prov. West-Vlaanderen": "West Flanders",
    "Prov. Vlaams-Brabant": "Flemish Brabant",
    "Prov. Antwerpen": "Antwerp",
}

PROVINCE_CENTROIDS = {
    "Zeeland": {"lat": 51.49, "lon": 3.90},
    "North Brabant": {"lat": 51.55, "lon": 5.20},
    "Limburg (Netherlands)": {"lat": 51.10, "lon": 5.95},
    "East Flanders": {"lat": 51.02, "lon": 3.85},
    "West Flanders": {"lat": 51.02, "lon": 2.95},
    "Flemish Brabant": {"lat": 50.88, "lon": 4.70},
    "Antwerp": {"lat": 51.25, "lon": 4.75},
    "Limburg (Belgium)": {"lat": 50.98, "lon": 5.45},
}

MISSING_DATA_LOG_PATH = "data/user_missing_data_submissions.csv"

# Standard citation format for user-submitted data.
CITATION_FORMAT_EXAMPLE = (
    "Author, A. A., & Author, B. B. (Year). Title of article or report. "
    "Journal/Publisher. https://doi.org/xx.xxxx/xxxxx"
)

CHART_COLORS = [
    "#1B5E20",
    "#2E7D32",
    "#43A047",
    "#66BB6A",
    "#81C784",
    "#A5D6A7",
    "#C8E6C9",
    "#FFB74D",
    "#8D6E63",
    "#5D4037",
]
