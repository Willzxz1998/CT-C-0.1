from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

from .config import (
    COLS,
    DEFAULT_YEAR,
    EXCEL_PATH,
    NUTS2_TO_PROVINCE,
    PROVINCE_ALIASES,
    SHEETS,
    SNF_PROVINCES,
)


def _ensure_path(path_str: str | Path) -> Path:
    return Path(path_str).expanduser().resolve()


def read_excel_data(path: str | Path = EXCEL_PATH) -> pd.DataFrame:
    """Read the 3-sheet CTCdata workbook and return the app dataset."""
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
            COLS["pyrolysis_tech"]: "pyrolysis_tech",
            COLS["compost_yield"]: "compost_yield",
            COLS["composting_tech"]: "composting_tech",
        }
    )

    residue_merged = residue_std.merge(conv_std, on=["crop", "residue_type"], how="left")

    # Keep only supported residue types in this version.
    allowed_residue_types = {"Resid", "Farm food loss"}
    residue_merged["residue_type"] = residue_merged["residue_type"].astype(str).str.strip()
    residue_merged = residue_merged[residue_merged["residue_type"].isin(allowed_residue_types)]

    for frame in [prod_std, residue_merged]:
        frame["province"] = frame["province"].replace(PROVINCE_ALIASES)
        frame["province"] = frame.apply(
            lambda r: NUTS2_TO_PROVINCE.get(str(r.get("nuts_id", "")), r["province"]),
            axis=1,
        )

    prod_std["production_kt"] = pd.to_numeric(prod_std["production_kt"], errors="coerce").fillna(0.0)
    residue_merged["residue_kt"] = pd.to_numeric(residue_merged["residue_kt"], errors="coerce").fillna(0.0)
    residue_merged["biochar_yield"] = pd.to_numeric(residue_merged["biochar_yield"], errors="coerce")
    residue_merged["compost_yield"] = pd.to_numeric(residue_merged["compost_yield"], errors="coerce")
    residue_merged["pyrolysis_tech"] = residue_merged["pyrolysis_tech"].fillna("Data unavailable")
    residue_merged["composting_tech"] = residue_merged["composting_tech"].fillna("Data unavailable")

    residue_by_type = (
        residue_merged.groupby(["year", "nuts_id", "province", "crop", "residue_type"], as_index=False)
        .agg(
            residue_kt=("residue_kt", "sum"),
            biochar_yield=("biochar_yield", "mean"),
            compost_yield=("compost_yield", "mean"),
            pyrolysis_tech=("pyrolysis_tech", "first"),
            composting_tech=("composting_tech", "first"),
        )
    )

    production_agg = (
        prod_std.groupby(["year", "nuts_id", "province", "crop"], as_index=False)["production_kt"].sum()
    )
    df_out = residue_by_type.merge(production_agg, on=["year", "nuts_id", "province", "crop"], how="outer")

    df_out["year"] = pd.to_numeric(df_out["year"], errors="coerce").fillna(DEFAULT_YEAR).astype(int)
    # Do not create synthetic residue types; keep only valid input categories.
    df_out["residue_type"] = df_out["residue_type"].fillna("")
    for c in ["production_kt", "residue_kt", "biochar_yield", "compost_yield"]:
        df_out[c] = pd.to_numeric(df_out.get(c, 0.0), errors="coerce")

    # Flags for missing-data panel
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
    """Filter by year if a year column exists; otherwise return the input."""
    if "year" not in df.columns:
        return df.copy()
    return df[df["year"] == year].copy()


def get_available_filters(df: pd.DataFrame) -> Tuple[list[str], list[str]]:
    """
    Return available provinces and crops (alphabetical).
    """
    provinces = sorted(df["province"].dropna().unique().tolist())
    crops = sorted(df["crop"].dropna().unique().tolist())
    return provinces, crops

