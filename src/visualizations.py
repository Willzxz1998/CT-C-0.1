from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .config import CHART_COLORS, GEOJSON_PATH, PROVINCE_CENTROIDS


def _load_geojson(path: str | Path = GEOJSON_PATH) -> dict:
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"GeoJSON file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def apply_chart_theme(fig: go.Figure, *, height: int | None = None) -> go.Figure:
    layout_kwargs: dict = {
        "template": "plotly_white",
        "font": {"family": "Inter, Segoe UI, Helvetica, Arial, sans-serif", "size": 13, "color": "#1B4332"},
        "title_font": {"size": 18, "color": "#1B4332"},
        "margin": {"l": 48, "r": 28, "t": 56, "b": 48},
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "#F8FBF8",
        "legend": {
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
            "font": {"size": 11},
        },
    }
    if height is not None:
        layout_kwargs["height"] = height
    fig.update_layout(**layout_kwargs)
    fig.update_xaxes(gridcolor="#E8F0E8", zerolinecolor="#C8E6C9")
    fig.update_yaxes(gridcolor="#E8F0E8", zerolinecolor="#C8E6C9")
    return fig


def bar_chart_rank_by_crop(
    df: pd.DataFrame,
    value_label: str,
    *,
    title: str = "Crop ranking",
    unit: str = "kt",
    hover_col: str | None = None,
) -> go.Figure:
    if df.empty:
        fig = px.bar(title="No data to display")
        return apply_chart_theme(fig, height=320)

    crop_count = max(len(df), 1)
    dynamic_height = max(360, min(1400, 58 * crop_count))

    fig = px.bar(
        df,
        x="value",
        y="crop",
        orientation="h",
        title=title,
        labels={"value": f"{value_label} ({unit})", "crop": "Crop"},
        color_discrete_sequence=[CHART_COLORS[0]],
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
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return apply_chart_theme(fig, height=dynamic_height)


def pie_chart_by_province(
    df: pd.DataFrame,
    value_label: str,
    *,
    title: str = "Province contribution",
    unit: str = "kt",
) -> go.Figure:
    if df.empty:
        fig = px.pie(title="No data to display")
        return apply_chart_theme(fig, height=420)

    fig = px.pie(
        df,
        names="province",
        values="value",
        title=title,
        color_discrete_sequence=CHART_COLORS,
        hole=0.38,
    )
    fig.update_traces(
        textposition="inside",
        texttemplate="%{label}<br>%{value:.2f} " + unit,
        hovertemplate="<b>%{label}</b><br>%{value:.3f} " + unit + "<br>%{percent}<extra></extra>",
    )
    return apply_chart_theme(fig, height=480)


def stacked_bar_by_province_and_crop(
    df: pd.DataFrame,
    value_label: str,
    *,
    title: str = "Overview",
    unit: str = "kt",
) -> go.Figure:
    if df.empty:
        fig = px.bar(title="No data to display")
        return apply_chart_theme(fig, height=420)

    fig = px.bar(
        df,
        x="province",
        y="value",
        color="crop",
        title=title,
        labels={"value": f"{value_label} ({unit})", "province": "Province", "crop": "Crop"},
        color_discrete_sequence=CHART_COLORS,
        barmode="stack",
    )
    fig.update_traces(hovertemplate="%{x}<br>%{fullData.name}: %{y:.3f} " + unit + "<extra></extra>")
    fig.update_layout(xaxis_tickangle=-28)
    return apply_chart_theme(fig, height=520)


def choropleth_snf(
    df: pd.DataFrame,
    value_label: str,
    geojson_path: str | Path = GEOJSON_PATH,
    province_field_geojson: str = "name",
) -> go.Figure:
    if df.empty:
        fig = px.choropleth(title="No data to display")
        return apply_chart_theme(fig, height=520)

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
        color_continuous_scale=["#E8F5E9", "#A5D6A7", "#43A047", "#1B5E20"],
        labels={"value": value_label, "province": "Province"},
        title=f"{value_label} — SNF map (province level)",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(coloraxis_colorbar={"title": {"text": f"{value_label} (kt)"}})
    fig.update_traces(hovertemplate="<b>%{location}</b><br>%{z:.3f} kt<extra></extra>")

    label_df = map_df.dropna(subset=["label_lat", "label_lon"])
    if not label_df.empty:
        fig.add_trace(
            go.Scattergeo(
                lat=label_df["label_lat"],
                lon=label_df["label_lon"],
                text=label_df["value"].map(lambda x: f"{x:.2f}"),
                mode="text",
                showlegend=False,
                hoverinfo="skip",
                textfont={"size": 11, "color": "#1B4332"},
            )
        )
    return apply_chart_theme(fig, height=560)


def gwp_stacked_bar_by_components(
    components_df: pd.DataFrame,
    *,
    title: str = "GWP breakdown per kg crop production",
    unit: str = "kg CO2eq",
) -> go.Figure:
    """
    components_df columns:
      - crop
      - component (e.g. Production emission, Animal feed, ...)
      - value
    Uses barmode='relative' so negative credits stack correctly.
    """
    if components_df.empty:
        return apply_chart_theme(px.bar(title="No data to display"), height=360)

    fig = px.bar(
        components_df,
        x="crop",
        y="value",
        color="component",
        barmode="relative",
        title=title,
        labels={"value": unit, "crop": "Crop", "component": "Component"},
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>%{fullData.name}: %{y:.6f}<extra></extra>"
    )
    fig.update_layout(xaxis_tickangle=0)
    return apply_chart_theme(fig, height=480)
