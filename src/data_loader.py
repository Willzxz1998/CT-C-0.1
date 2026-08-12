from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import (
    COLS,
    SHEETS,
    DEFAULT_YEAR,
    EXCEL_PATH,
    NUTS2_TO_PROVINCE,
    PROVINCE_ALIASES,
    SNF_PROVINCES,
)


def _ensure_path(path_str: str | Path) -> Path:
    return Path(path_str).expanduser().resolve()


def _normalize_provinces(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["province"] = out["province"].replace(PROVINCE_ALIASES)
    out["province"] = out.apply(
        lambda r: NUTS2_TO_PROVINCE.get(str(r.get("nuts_id", "")), r["province"]),
        axis=1,
    )
    return out


def read_production_data(path: str | Path = EXCEL_PATH, year: int = DEFAULT_YEAR) -> pd.DataFrame:
    """Load horticultural production directly from the Crop_production sheet."""
    excel_path = _ensure_path(path)
    prod = pd.read_excel(excel_path, sheet_name=SHEETS["production"])

    required = [COLS["year"], COLS["nuts_id"], COLS["province"], COLS["crop"], COLS["production_kt"]]
    missing = [c for c in required if c not in prod.columns]
    if missing:
        raise ValueError(f"Missing required columns in {SHEETS['production']}: {missing}")

    prod_std = prod.rename(
        columns={
            COLS["year"]: "year",
            COLS["nuts_id"]: "nuts_id",
            COLS["province"]: "province",
            COLS["crop"]: "crop",
            COLS["production_kt"]: "production_kt",
        }
    )
    prod_std = _normalize_provinces(prod_std)
    prod_std["production_kt"] = pd.to_numeric(prod_std["production_kt"], errors="coerce").fillna(0.0)
    prod_std["year"] = pd.to_numeric(prod_std["year"], errors="coerce").fillna(DEFAULT_YEAR).astype(int)

    prod_std = prod_std[prod_std["province"].isin(SNF_PROVINCES)]
    prod_std = prod_std[prod_std["year"] == year]
    prod_std = prod_std.dropna(subset=["province", "crop"])
    return prod_std.reset_index(drop=True)


def read_excel_data(path: str | Path = EXCEL_PATH) -> pd.DataFrame:
    """Read residue + conversion data merged with production for non-production views."""
    excel_path = _ensure_path(path)
    if not excel_path.exists():
        raise FileNotFoundError(f"Data file not found: {excel_path}")

    prod = pd.read_excel(excel_path, sheet_name=SHEETS["production"])
    residue = pd.read_excel(excel_path, sheet_name=SHEETS["residue"])
    conv = pd.read_excel(excel_path, sheet_name=SHEETS["conversion"])

    required_prod = [COLS["year"], COLS["nuts_id"], COLS["province"], COLS["crop"], COLS["production_kt"]]
    required_residue = [
        COLS["year"],
        COLS["nuts_id"],
        COLS["province"],
        COLS["crop_residue"],
        COLS["residue_type"],
        COLS["residue_kt"],
    ]
    required_conv = [
        COLS["crop_residue"],
        COLS["residue_type"],
        COLS["biochar_yield"],
        COLS["pyrolysis_tech"],
        COLS["compost_yield"],
        COLS["composting_tech"],
    ]

    for req, sheet_name, df_ in [
        (required_prod, SHEETS["production"], prod),
        (required_residue, SHEETS["residue"], residue),
        (required_conv, SHEETS["conversion"], conv),
    ]:
        missing = [c for c in req if c not in df_.columns]
        if missing:
            raise ValueError(f"Missing required columns in sheet '{sheet_name}': {missing}")

    prod_std = prod.rename(
        columns={
            COLS["year"]: "year",
            COLS["nuts_id"]: "nuts_id",
            COLS["province"]: "province",
            COLS["crop"]: "crop",
            COLS["production_kt"]: "production_kt",
        }
    )
    residue_std = residue.rename(
        columns={
            COLS["year"]: "year",
            COLS["nuts_id"]: "nuts_id",
            COLS["province"]: "province",
            COLS["crop_residue"]: "crop",
            COLS["residue_type"]: "residue_type",
            COLS["residue_kt"]: "residue_kt",
        }
    )
    conv_std = conv.rename(
        columns={
            COLS["crop_residue"]: "crop",
            COLS["residue_type"]: "residue_type",
            COLS["biochar_yield"]: "biochar_yield",
            COLS["initial_moisture"]: "initial_moisture",
            COLS["final_moisture"]: "final_moisture",
            COLS["pyrolysis_tech"]: "pyrolysis_tech",
            COLS["compost_yield"]: "compost_yield",
            COLS["composting_tech"]: "composting_tech",
        }
    )

    residue_merged = residue_std.merge(conv_std, on=["crop", "residue_type"], how="left")

    allowed_residue_types = {"Resid", "Farm food loss"}
    residue_merged["residue_type"] = residue_merged["residue_type"].astype(str).str.strip()
    residue_merged = residue_merged[residue_merged["residue_type"].isin(allowed_residue_types)]

    prod_std = _normalize_provinces(prod_std)
    residue_merged = _normalize_provinces(residue_merged)

    prod_std["production_kt"] = pd.to_numeric(prod_std["production_kt"], errors="coerce").fillna(0.0)
    residue_merged["residue_kt"] = pd.to_numeric(residue_merged["residue_kt"], errors="coerce").fillna(0.0)
    residue_merged["biochar_yield"] = pd.to_numeric(residue_merged["biochar_yield"], errors="coerce")
    residue_merged["initial_moisture"] = pd.to_numeric(
        residue_merged.get("initial_moisture"), errors="coerce"
    )
    residue_merged["final_moisture"] = pd.to_numeric(
        residue_merged.get("final_moisture"), errors="coerce"
    )
    residue_merged["compost_yield"] = pd.to_numeric(residue_merged["compost_yield"], errors="coerce")
    residue_merged["pyrolysis_tech"] = residue_merged["pyrolysis_tech"].fillna("Data unavailable")
    residue_merged["composting_tech"] = residue_merged["composting_tech"].fillna("Data unavailable")

    residue_by_type = (
        residue_merged.groupby(["year", "nuts_id", "province", "crop", "residue_type"], as_index=False)
        .agg(
            residue_kt=("residue_kt", "sum"),
            biochar_yield=("biochar_yield", "mean"),
            initial_moisture=("initial_moisture", "first"),
            final_moisture=("final_moisture", "first"),
            compost_yield=("compost_yield", "mean"),
            pyrolysis_tech=("pyrolysis_tech", "first"),
            composting_tech=("composting_tech", "first"),
        )
    )

    production_agg = (
        prod_std.groupby(["year", "nuts_id", "province", "crop"], as_index=False)["production_kt"].sum()
    )
    df_out = residue_by_type.merge(production_agg, on=["year", "nuts_id", "province", "crop"], how="left")

    df_out["year"] = pd.to_numeric(df_out["year"], errors="coerce").fillna(DEFAULT_YEAR).astype(int)
    df_out["residue_type"] = df_out["residue_type"].fillna("")
    for c in ["production_kt", "residue_kt", "biochar_yield", "compost_yield"]:
        df_out[c] = pd.to_numeric(df_out.get(c, 0.0), errors="coerce")

    df_out["missing_production"] = df_out["production_kt"].isna()
    df_out["missing_residue"] = df_out["residue_kt"].isna()
    df_out["missing_biochar_yield"] = df_out["biochar_yield"].isna()
    df_out["missing_compost_yield"] = df_out["compost_yield"].isna()

    for c in ["production_kt", "residue_kt", "biochar_yield", "compost_yield"]:
        df_out[c] = df_out[c].fillna(0.0)

    df_out["residue_usable_fraction"] = 1.0
    df_out = df_out[df_out["province"].isin(SNF_PROVINCES)]
    df_out = df_out.dropna(subset=["province", "crop"])
    df_out = df_out[df_out["residue_type"] != ""]

    return df_out


def filter_by_year(df: pd.DataFrame, year: int = DEFAULT_YEAR) -> pd.DataFrame:
    if "year" not in df.columns:
        return df.copy()
    return df[df["year"] == year].copy()


def get_available_filters(df: pd.DataFrame) -> Tuple[list[str], list[str]]:
    provinces = sorted(df["province"].dropna().unique().tolist())
    crops = sorted(df["crop"].dropna().unique().tolist())
    return provinces, crops


def get_production_summary(year: int = DEFAULT_YEAR) -> dict:
    prod = read_production_data(year=year)
    return {
        "total_production_kt": float(prod["production_kt"].sum()),
        "crop_count": int(prod["crop"].nunique()),
        "province_count": int(prod["province"].nunique()),
        "record_count": int(len(prod)),
    }


def _parse_numeric_cell(x) -> float:
    """
    Parse numeric values from Excel cells that may contain comma decimals and units.
    Examples:
      "0,370064 kg CO2eq" -> 0.370064
      "0,7 kg residue per kg production" -> 0.7
      -0,027 -> -0.027
    """
    import re

    if x is None:
        return float("nan")
    s = str(x).strip()
    if not s:
        return float("nan")
    # Replace comma decimal separator to dot, keep minus sign and digits/points.
    s = s.replace(",", ".")
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if not m:
        return float("nan")
    return float(m.group(0))


def read_gwp_input_data(path: str | Path = EXCEL_PATH) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Read GWP factors:
    - Crop_pro_emi: production emission per kg crop and residue mass per kg crop
    - Resi_uti_emission: emission per kg residue for each residue utilization
    """
    excel_path = _ensure_path(path)
    crop_emi = pd.read_excel(excel_path, sheet_name=SHEETS["crop_emi"])
    resi_uti = pd.read_excel(excel_path, sheet_name=SHEETS["resi_uti_emi"])

    # Standardize columns.
    crop_emi = crop_emi.rename(
        columns={
            "Crop": "crop",
            "Emission": "production_emission_kgco2eq_per_kg_crop",
            "Residue": "residue_kg_per_kg_crop",
        }
    )
    if "crop" not in crop_emi.columns:
        raise ValueError(f"Missing column 'Crop' in sheet '{SHEETS['crop_emi']}'")

    crop_emi["production_emission_kgco2eq_per_kg_crop"] = crop_emi[
        "production_emission_kgco2eq_per_kg_crop"
    ].apply(_parse_numeric_cell)
    crop_emi["residue_kg_per_kg_crop"] = crop_emi["residue_kg_per_kg_crop"].apply(_parse_numeric_cell)

    # Resi utilization factors.
    resi_uti = resi_uti.rename(
        columns={
            "Utilization": "utilization",
            "Emission": "utilization_emission_kgco2eq_per_kg_residue",
        }
    )
    if "utilization" not in resi_uti.columns:
        raise ValueError(f"Missing column 'Utilization' in sheet '{SHEETS['resi_uti_emi']}'")

    resi_uti["utilization_emission_kgco2eq_per_kg_residue"] = resi_uti[
        "utilization_emission_kgco2eq_per_kg_residue"
    ].apply(_parse_numeric_cell)

    resi_uti["utilization"] = resi_uti["utilization"].astype(str).str.strip()

    # Units column kept as raw text (for UI/reference).
    return crop_emi, resi_uti
