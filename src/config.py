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

# 示例：可以在实际数据中替换/扩展为 23 种作物
DEFAULT_CROPS = [
    "Asparagus",
    "Blueberry",
    "Grape",
]


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


# Main Excel dataset (keep this modifiable).
# Recommended: use the repo-relative path `data/CTCdata.xlsx` for deployment.
EXCEL_PATH = "data/CTCdata.xlsx"

# NUTS2 boundaries GeoJSON for the 8 SNF provinces (generated from GISCO NUTS2).
GEOJSON_PATH = "data/geo/snf_nuts2.geojson"

# Excel sheet names and column names (as provided in your dataset).
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

# Province name normalization (to match SNF_PROVINCES and GeoJSON `properties.name`)
PROVINCE_ALIASES = {
    "Noord-Brabant": "Noord Brabant",
    "Prov. Oost-Vlaanderen": "East Flanders",
    "Prov. West-Vlaanderen": "West Flanders",
    "Prov. Vlaams-Brabant": "Flemish Brabant",
    "Prov. Antwerpen": "Antwerp Province",
}

# Approximate province centroids for map value labels.
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

