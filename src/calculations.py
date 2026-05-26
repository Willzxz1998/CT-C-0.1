from __future__ import annotations

import pandas as pd

from .config import DATA_TYPES, PRODUCTION_VIEW


def add_potential_products(
    df: pd.DataFrame,
    utilization_rate: float = 1.0,
) -> pd.DataFrame:
    df = df.copy()
    df["residue_usable_kt"] = (
        df["residue_kt"] * df.get("residue_usable_fraction", 1.0) * utilization_rate
    )
    df["biochar_potential_kt"] = df["residue_usable_kt"] * df.get("biochar_yield", 0.0)
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
