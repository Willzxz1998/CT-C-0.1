import os

SNF_PROVINCES = [
    "Zeeland",
    "Noord Brabant",
    "Limburg (NL)",
    "East Flanders",
    "West Flanders",
    "Flemish Brabant",
    "Antwerp Province",
    "Limburg (BE)",
]

NUTS2_TO_PROVINCE = {
    "NL41": "Noord Brabant",
    "NL42": "Limburg (NL)",
    "NL34": "Zeeland",
    "BE21": "Antwerp Province",
    "BE22": "Limburg (BE)",
    "BE23": "East Flanders",
    "BE24": "Flemish Brabant",
    "BE25": "West Flanders",
}

DEFAULT_YEAR = 2022

DATA_TYPES = {
    "Horticultural Production Overview": "production_kt",
    "Residue Inventory Overview": "residue_kt",
    "Potential Biochar Production": "biochar_potential_kt",
    "Potential Compost Production": "compost_potential_kt",
}

PRODUCT_TYPES = [
    "Potential Biochar Production",
    "Potential Compost Production",
]

PRODUCTION_VIEW = "Horticultural Production Overview"

# Subpanels visible to public users (browsing the tool).
USER_SUBPANELS = [
    "Homepage",
    "Circular horticultural cultivation value chain",
    "Missing data",
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

SHEETS = {
    "production": "Crop_production",
    "residue": "Residue_inventory",
    "conversion": "Conversion_parameters",
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
    "pyrolysis_tech": "Pyrolysis_tech",
    "compost_yield": "Compost_yield",
    "composting_tech": "Composting_tech",
}

PROVINCE_ALIASES = {
    "Noord-Brabant": "Noord Brabant",
    "Prov. Oost-Vlaanderen": "East Flanders",
    "Prov. West-Vlaanderen": "West Flanders",
    "Prov. Vlaams-Brabant": "Flemish Brabant",
    "Prov. Antwerpen": "Antwerp Province",
}

PROVINCE_CENTROIDS = {
    "Zeeland": {"lat": 51.49, "lon": 3.90},
    "Noord Brabant": {"lat": 51.55, "lon": 5.20},
    "Limburg (NL)": {"lat": 51.10, "lon": 5.95},
    "East Flanders": {"lat": 51.02, "lon": 3.85},
    "West Flanders": {"lat": 51.02, "lon": 2.95},
    "Flemish Brabant": {"lat": 50.88, "lon": 4.70},
    "Antwerp Province": {"lat": 51.25, "lon": 4.75},
    "Limburg (BE)": {"lat": 50.98, "lon": 5.45},
}

MISSING_DATA_LOG_PATH = "data/user_missing_data_submissions.csv"

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
