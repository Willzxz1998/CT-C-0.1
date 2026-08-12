from __future__ import annotations

import pandas as pd

from .config import DATA_TYPES, PRODUCTION_VIEW


def compute_gwp_per_kg_crop(
    *,
    crop: str,
    production_emission_kgco2eq_per_kg_crop: float,
    residue_kg_per_kg_crop: float,
    utilization_emission_kgco2eq_per_kg_residue: dict[str, float],
    utilization_ratios_percent: dict[str, float],
) -> dict:
    """
    Compute overall GWP per kg crop production.

    overall = production_emission
              + sum_i (residue_mass_per_kg_crop * ratio_i * emission_i_per_kg_residue)

    where ratio_i is in [0, 1].
    """
    ratios_fraction = {
        k: float(v) / 100.0 for k, v in utilization_ratios_percent.items()
    }

    residue_components: dict[str, float] = {}
    for util, emis_per_kg_res in utilization_emission_kgco2eq_per_kg_residue.items():
        share = ratios_fraction.get(util, 0.0)
        residue_components[util] = (
            float(residue_kg_per_kg_crop) * share * float(emis_per_kg_res)
        )

    overall = float(production_emission_kgco2eq_per_kg_crop) + sum(
        residue_components.values()
    )

    return {
        "crop": crop,
        "production_emission": float(production_emission_kgco2eq_per_kg_crop),
        "residue_components": residue_components,
        "overall_emission": overall,
    }


def moisture_correction_factor(
    initial_moisture: pd.Series,
    final_moisture: pd.Series,
) -> pd.Series:
    """
    (100 - initial moisture) / (100 - final moisture).

    Excel stores moisture as fractions (e.g. 0.9 = 90%); values > 1 are treated as %.
    """
    initial = pd.to_numeric(initial_moisture, errors="coerce")
    final = pd.to_numeric(final_moisture, errors="coerce")
    initial_pct = initial.where(initial > 1, initial * 100)
    final_pct = final.where(final > 1, final * 100)
    denom = 100 - final_pct
    factor = (100 - initial_pct) / denom
    valid = initial.notna() & final.notna() & (denom > 0)
    return factor.where(valid, 1.0)


def add_potential_products(
    df: pd.DataFrame,
    utilization_rate: float = 1.0,
) -> pd.DataFrame:
    df = df.copy()
    df["residue_usable_kt"] = (
        df["residue_kt"] * df.get("residue_usable_fraction", 1.0) * utilization_rate
    )
    moisture_factor = moisture_correction_factor(
        df.get("initial_moisture", pd.Series(dtype=float)),
        df.get("final_moisture", pd.Series(dtype=float)),
    )
    df["biochar_potential_kt"] = (
        df["residue_usable_kt"] * df.get("biochar_yield", 0.0) * moisture_factor
    )
    df["compost_potential_kt"] = df["residue_usable_kt"] * df.get("compost_yield", 0.0)
    return df


def aggregate_production_for_view(
    prod_df: pd.DataFrame,
    provinces: list[str] | None = None,
    crops: list[str] | None = None,
) -> pd.DataFrame:
    """Aggregate production from Crop_production sheet only (kt)."""
    df_sel = prod_df.copy()
    if provinces:
        df_sel = df_sel[df_sel["province"].isin(provinces)]
    if crops:
        df_sel = df_sel[df_sel["crop"].isin(crops)]

    grouped = (
        df_sel.groupby(["province", "crop"], as_index=False)["production_kt"]
        .sum()
        .rename(columns={"production_kt": "value"})
    )
    return grouped


def aggregate_for_view(
    df: pd.DataFrame,
    data_type_label: str,
    provinces: list[str] | None = None,
    crops: list[str] | None = None,
    residue_types: list[str] | None = None,
) -> pd.DataFrame:
    if data_type_label == PRODUCTION_VIEW:
        raise ValueError("Use aggregate_production_for_view() for production overview.")

    if data_type_label not in DATA_TYPES:
        raise ValueError(f"Unknown data type: {data_type_label}")

    df_sel = df.copy()
    if provinces:
        df_sel = df_sel[df_sel["province"].isin(provinces)]
    if crops:
        df_sel = df_sel[df_sel["crop"].isin(crops)]
    if residue_types and "residue_type" in df_sel.columns:
        df_sel = df_sel[df_sel["residue_type"].isin(residue_types)]

    value_col = DATA_TYPES[data_type_label]
    if value_col not in df_sel.columns:
        df_sel[value_col] = 0.0

    grouped = df_sel.groupby(["province", "crop"], as_index=False)[value_col].sum()
    grouped = grouped.rename(columns={value_col: "value"})
    return grouped


def summary_by_crop(grouped_df: pd.DataFrame) -> pd.DataFrame:
    return (
        grouped_df.groupby("crop", as_index=False)["value"]
        .sum()
        .sort_values("value", ascending=False)
    )


def summary_by_province(grouped_df: pd.DataFrame) -> pd.DataFrame:
    return (
        grouped_df.groupby("province", as_index=False)["value"]
        .sum()
        .sort_values("value", ascending=False)
    )


def stacked_by_province_and_crop(grouped_df: pd.DataFrame) -> pd.DataFrame:
    return grouped_df.copy()
