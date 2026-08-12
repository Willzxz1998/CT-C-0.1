## 1. Purpose

### Purpose of the tool
The Sustainability Tool is an informational and decision-support portal for exploring horticultural biomass flows, residue inventories, and circular valorisation pathways in the **southern Netherlands and Flanders** region.

### Main functions
- Visualise **horticultural production**, **residue inventory**, and **potential biochar and compost production**.
- Calculate **GWP (kg CO2eq per kg crop production)** for horticultural crops under user-defined residue utilization scenarios.
- Filter by province, crop, and residue type.
- Explore rankings, provincial contributions, stacked overviews, and an interactive regional map.
- Contribute missing or updated data via **Data Contribution**.

### Target users
Researchers, policymakers, growers, bioeconomy stakeholders, and students interested in circular horticulture and biomass valorisation.

### Workflow overview
1. Open **Homepage** for context and valorisation products.
2. Go to **Circular horticultural cultivation value chain** and set filters.
3. Choose a data view (production, residue, biochar, compost, or GWP).
4. Explore charts and the map.
5. Use **Data Contribution** to submit new or improved datasets.
6. Consult **References** and this manual for methods and terminology.

---

## 2. Definitions

| Term | Definition |
|------|------------|
| **Food loss** | Edible horticultural biomass that leaves the production or supply chain without being consumed. |
| **Farm food loss** | Losses on the farm or immediately after harvest (separate residue class in the tool). |
| **Green residues** | Fresh, moist plant material (leaves, stems, trimmings) removed during harvest or processing. |
| **Crop residues** | Biomass remaining after harvest, including field and processing residues. |
| **Compost** | Stabilised organic material from aerobic decomposition of organic feedstock. |
| **Biochar** | Carbon-rich solid from pyrolysis of biomass. |
| **Pyrolysis** | Thermal conversion with limited oxygen to produce biochar, gases, and liquids. |
| **Biochar yield** | Mass of biochar produced ÷ mass of **dried feedstock**. |
| **Wet biomass** | Biomass including natural moisture (as measured in the field). |
| **Dry biomass** | Biomass on a dry-mass basis after moisture removal or correction. |
| **Residual biomass** | Biomass left after the main horticultural product is harvested or processed. |
| **Horticultural residues** | Residues from open-field and protected horticulture in the study region. |
| **Residue inventory** | Quantified residues by crop, province, and type. |
| **Residue utilization** | Assumed share of residue entering a valorisation pathway. |
| **GWP** | Global Warming Potential (expressed here as greenhouse gas emissions, in kg CO2-equivalent). |
| **Coumaric acid** | Phenolic compound recoverable via biorefinery; a project valorisation product. |
| **SNF region** | Southern Netherlands and Flanders (eight NUTS2 provinces). |

---

## 3. Data conventions

| Data type | Mass basis |
|-----------|------------|
| **Residue inventory** | **Wet mass** (kt) |
| **Compost production (potential)** | **Wet mass** (kt) |
| **Biochar production (potential)** | **Dry mass** (kt) |
| **GWP of horticultural production and residue utilization** | **kg CO2eq per kg crop production** |

For the **GWP** view, the tool combines:
- production emission per kg crop production,
- residue mass per kg crop production,
- and user-defined residue utilization shares.

Overall GWP per kg crop production is:

> production emission + residue_mass × Σ (residue_share × utilization_emission)

Any residue share not allocated to the selected utilization routes is assigned to **Left on field** by default.

**Biochar yield** is defined as:

> **Biochar yield = Mass of biochar produced / Mass of dried feedstock**

Potential biochar also applies a moisture correction:

> **Potential biochar ∝ biochar yield × residue inventory × (100 − initial moisture) / (100 − final moisture)**

---

## 4. Database reference year

The current database is based on data from **2022**. The reference year is fixed in the backend; it is not shown in the main interface to keep views uncluttered.

---

## 5. Original data source

Primary background dataset:

> **Residual Biomass Flows from Horticulture in the Southern Netherlands and Flanders and Biorefinery Concepts**

Project data are maintained in `data/CTCdata.xlsx` (production, residue inventory, conversion parameters).

---

## 6. Data quality requirements for user submissions

Contributions should meet the following minimum standards:

1. **Reliable source** — peer-reviewed paper, official statistics, or documented experiment.
2. **Complete metadata** — crop, province/NUTS ID, year, residue type, and method.
3. **Units** — clearly stated (preferably kt for regional inventory).
4. **Measurement methods** — how production, residue, or yield was determined.
5. **Geographical coverage** — study-region provinces only, or clearly flagged if wider.
6. **Crop information** — align with horticultural crops in the study region where possible.
7. **Reproducibility** — enough detail for independent verification.
8. **Consistency** — compatible with wet/dry conventions above.
9. **Citation / reference** — full bibliographic reference in standard format (see Data Contribution page).
10. **Preferred formats** — structured spreadsheet (`.xlsx`) or CSV; PDF only as supplementary evidence.

Contributors whose data are accepted will receive an **acknowledgement email**.

---

## 7. Citation, license, and contact

**Suggested citation:** Circular Cultivation and Chemistry Sustainability Tool, Maastricht University / Interreg Circulaire Teelt en Chemie.

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0) for tool documentation and shared outputs, unless otherwise stated.

**Contact:** xinzhi.zhong@maastrichtuniversity.nl
