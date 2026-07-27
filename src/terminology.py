"""Shared terminology definitions and lightweight tooltip helpers."""

from __future__ import annotations

# Key terms used in filters, charts, and forms.
TERMS: dict[str, str] = {
    "Food loss": (
        "Edible horticultural biomass that leaves the primary production or supply chain "
        "without being consumed, including on-farm and post-harvest losses."
    ),
    "Farm food loss": (
        "Horticultural biomass lost on the farm or immediately after harvest, "
        "reported separately from field residues in this tool."
    ),
    "Green residues": (
        "Fresh, moist plant material such as leaves, stems, or trimmings removed during "
        "harvest or processing; typically high in moisture."
    ),
    "Crop residues": (
        "Biomass remaining after crop harvest, including field residues and processing residues."
    ),
    "Resid": (
        "Field or processing residues (excluding farm food loss) as classified in the residue inventory."
    ),
    "Compost": (
        "Stabilised organic material produced by aerobic decomposition of organic feedstock; "
        "reported in wet mass in this tool."
    ),
    "Biochar": (
        "Carbon-rich solid produced by pyrolysis of biomass; reported in dry mass in this tool."
    ),
    "Pyrolysis": (
        "Thermal conversion of biomass with limited oxygen to produce biochar, gases, and liquids."
    ),
    "Biochar yield": (
        "Mass of biochar produced divided by the mass of dried feedstock "
        "(dry mass basis)."
    ),
    "Wet biomass": (
        "Biomass mass including its natural moisture content, as typically measured in the field."
    ),
    "Dry biomass": (
        "Biomass mass after moisture has been removed or corrected to a dry basis."
    ),
    "Residual biomass": (
        "Biomass that remains after the main horticultural product has been harvested or processed."
    ),
    "Horticultural residues": (
        "Residues generated in open-field and protected horticultural production in the SNF region."
    ),
    "Residue inventory": (
        "Quantified amounts of horticultural residues by crop, province, and residue type; "
        "reported in wet mass (kt)."
    ),
    "Residue utilization": (
        "Share of available residue assumed to enter a valorisation pathway (biochar or compost)."
    ),
    "Coumaric acid": (
        "A phenolic compound that can be recovered from certain horticultural residues "
        "through biorefinery routes; highlighted as a valorisation product in the project."
    ),
    "SNF region": (
        "Southern Netherlands and Flanders: eight NUTS2 provinces covered by this tool."
    ),
    "NUTS2": (
        "Nomenclature of Territorial Units for Statistics, level 2 — provincial regions used for mapping."
    ),
    "Initial moisture": (
        "Moisture content of residue feedstock before drying or pyrolysis (used in biochar calculations)."
    ),
    "Final moisture": (
        "Target moisture content after pre-treatment or drying before pyrolysis."
    ),
}


def term_label(name: str, display: str | None = None) -> str:
    """Return HTML span with native browser tooltip for a defined term."""
    text = display or name
    tip = TERMS.get(name, TERMS.get(text, ""))
    if not tip:
        return text
    safe_tip = tip.replace('"', "&quot;")
    return (
        f'<span title="{safe_tip}" '
        f'style="border-bottom:1px dotted #2e7d32;cursor:help;">{text}</span>'
    )


def help_text(name: str) -> str | None:
    """Return help string for Streamlit widget `help=` parameter."""
    return TERMS.get(name)
