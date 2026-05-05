from __future__ import annotations

import pandas as pd

from .config import DATA_TYPES


def add_potential_products(
    df: pd.DataFrame,
    utilization_rate: float = 1.0,
) -> pd.DataFrame:
    """
    在原始 DataFrame 基础上增加潜在产品产量列（吨）。

    utilization_rate 为 0–1 之间的小数，表示用户选择的残余物利用率。
    """
    df = df.copy()

    # usable residue (kt)
    df["residue_usable_kt"] = (
        df["residue_kt"]
        * df.get("residue_usable_fraction", 1.0)
        * utilization_rate
    )

    # Biochar potential (kt)
    df["biochar_potential_kt"] = (
        df["residue_usable_kt"] * df.get("biochar_yield", 0.0)
    )

    # Compost potential (kt)
    df["compost_potential_kt"] = (
        df["residue_usable_kt"] * df.get("compost_yield", 0.0)
    )

    return df


def aggregate_for_view(
    df: pd.DataFrame,
    data_type_label: str,
    provinces: list[str] | None = None,
    crops: list[str] | None = None,
    residue_types: list[str] | None = None,
) -> pd.DataFrame:
    """
    根据选择的数据类型、省份和作物进行聚合。

    返回的 DataFrame 至少包含：
    - province
    - crop
    - value（对应所选数据类型的数值）
    """
    if data_type_label not in DATA_TYPES:
        raise ValueError(f"未知的数据类型：{data_type_label}")

    df_sel = df.copy()
    if provinces:
        df_sel = df_sel[df_sel["province"].isin(provinces)]
    if crops:
        df_sel = df_sel[df_sel["crop"].isin(crops)]
    if residue_types and "residue_type" in df_sel.columns:
        df_sel = df_sel[df_sel["residue_type"].isin(residue_types)]

    value_col = DATA_TYPES[data_type_label]

    # 安全处理缺失列
    if value_col not in df_sel.columns:
        df_sel[value_col] = 0.0

    # Province-crop aggregation
    # NOTE: production_kt can be duplicated across residue_type rows (to support residue_type filtering),
    # so we must not sum it across residue types. Taking max is safe because it's constant per (province, crop).
    if value_col == "production_kt" and "residue_type" in df_sel.columns:
        grouped = df_sel.groupby(["province", "crop"], as_index=False)[value_col].max()
    else:
        grouped = df_sel.groupby(["province", "crop"], as_index=False)[value_col].sum()
    grouped = grouped.rename(columns={value_col: "value"})

    return grouped


def summary_by_crop(grouped_df: pd.DataFrame) -> pd.DataFrame:
    """按作物汇总，用于作物排名条形图。"""
    return (
        grouped_df.groupby("crop", as_index=False)["value"]
        .sum()
        .sort_values("value", ascending=False)
    )


def summary_by_province(grouped_df: pd.DataFrame) -> pd.DataFrame:
    """按省汇总，用于省份饼图和地图。"""
    return (
        grouped_df.groupby("province", as_index=False)["value"]
        .sum()
        .sort_values("value", ascending=False)
    )


def stacked_by_province_and_crop(grouped_df: pd.DataFrame) -> pd.DataFrame:
    """返回适合堆叠条形图的长表（保持 province, crop, value 三列）。"""
    return grouped_df.copy()

