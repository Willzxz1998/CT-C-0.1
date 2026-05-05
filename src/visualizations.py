from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import GEOJSON_PATH, PROVINCE_CENTROIDS


def _load_geojson(path: str | Path = GEOJSON_PATH) -> dict:
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        geo = json.load(f)

    return geo


def bar_chart_rank_by_crop(
    df: pd.DataFrame,
    value_label: str,
    *,
    title: str = "Crop ranking",
    unit: str = "kt",
    hover_col: str | None = None,
) -> "px.Figure":
    """Horizontal bar chart for crop ranking (descending)."""
    if df.empty:
        return px.bar(title="No data to display")

    crop_count = max(len(df), 1)
    dynamic_height = max(320, min(1400, 55 * crop_count))

    fig = px.bar(
        df,
        x="value",
        y="crop",
        orientation="h",
        title=title,
        labels={"value": f"{value_label} ({unit})", "crop": "Crop"},
    )
    if hover_col and hover_col in df.columns:
        fig.update_traces(
            customdata=df[[hover_col]],
            hovertemplate="<b>%{y}</b><br>%{x:.3f} "
            + unit
            + "<br>%{customdata[0]}<extra></extra>",
        )
    else:
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>%{x:.3f} " + unit + "<extra></extra>"
        )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=dynamic_height)
    return fig


def pie_chart_by_province(
    df: pd.DataFrame, value_label: str, *, title: str = "Province contribution", unit: str = "kt"
) -> "px.Figure":
    """Province contribution pie chart."""
    if df.empty:
        return px.pie(title="No data to display")

    fig = px.pie(
        df,
        names="province",
        values="value",
        title=title,
    )
    fig.update_traces(
        texttemplate="%{label}<br>%{value:.3f} " + unit,
        hovertemplate="<b>%{label}</b><br>%{value:.3f} " + unit + "<br>%{percent}<extra></extra>",
    )
    return fig


def stacked_bar_by_province_and_crop(
    df: pd.DataFrame,
    value_label: str,
    *,
    title: str = "Overview",
    unit: str = "kt",
) -> "px.Figure":
    """Stacked bar chart by province and crop."""
    if df.empty:
        return px.bar(title="No data to display")

    fig = px.bar(
        df,
        x="province",
        y="value",
        color="crop",
        title=title,
        labels={"value": f"{value_label} ({unit})", "province": "Province", "crop": "Crop"},
    )
    fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y:.3f} " + unit + "<extra></extra>")
    return fig


def choropleth_snf(
    df: pd.DataFrame,
    value_label: str,
    geojson_path: str | Path = GEOJSON_PATH,
    province_field_geojson: str = "name",
) -> "px.Figure":
    """
    SNF region choropleth map at provincial level.

    Requirements:
    - df contains: province, value
    - GeoJSON attribute (e.g. 'name') matches df['province']
    """
    if df.empty:
        return px.choropleth(title="No data to display")

    geojson = _load_geojson(geojson_path)

    map_df = df.copy()
    map_df["label_lat"] = map_df["province"].map(
        lambda p: PROVINCE_CENTROIDS.get(p, {}).get("lat")
    )
    map_df["label_lon"] = map_df["province"].map(
        lambda p: PROVINCE_CENTROIDS.get(p, {}).get("lon")
    )

    fig = px.choropleth(
        df,
        geojson=geojson,
        locations="province",
        featureidkey=f"properties.{province_field_geojson}",
        color="value",
        color_continuous_scale="YlGnBu",
        labels={"value": value_label, "province": "Province"},
        title=f"{value_label} — SNF map (province level)",
    )
    fig.update_geos(
        fitbounds="locations",
        visible=False,
    )
    fig.update_layout(
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
        coloraxis_colorbar={"title": {"text": f"{value_label} (kt)"}},
    )
    fig.update_traces(hovertemplate="<b>%{location}</b><br>%{z:.3f} kt<extra></extra>")

    label_df = map_df.dropna(subset=["label_lat", "label_lon"])
    if not label_df.empty:
        fig.add_trace(
            go.Scattergeo(
                lat=label_df["label_lat"],
                lon=label_df["label_lon"],
                text=label_df["value"].map(lambda x: f"{x:.2f} kt"),
                mode="text",
                showlegend=False,
                hoverinfo="skip",
                textfont={"size": 11},
            )
        )
    return fig

