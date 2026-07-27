# User Manual — Circular Cultivation and Chemistry SusTool

## 1. Purpose

### Purpose of the tool
SusTool is an informational and decision-support portal for exploring horticultural biomass flows, residue inventories, and circular valorisation pathways in the **Southern Netherlands and Flanders (SNF)** region.

### Main functions
- Visualise **horticultural production**, **residue inventory**, and **potential biochar and compost production**.
- Filter by province, crop, and residue type.
- Explore rankings, provincial contributions, stacked overviews, and an interactive SNF map.
- Contribute missing or updated data via **Data Contribution**.

### Target users
Researchers, policymakers, growers, bioeconomy stakeholders, and students interested in circular horticulture and biomass valorisation.

### Workflow overview
1. Open **Homepage** for context and valorisation products.
2. Go to **Circular horticultural cultivation value chain** and set filters.
3. Choose a data view (production, residue, biochar, or compost).
4. Explore charts and the SNF map.
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
| **Horticultural residues** | Residues from open-field and protected horticulture in the SNF region. |
| **Residue inventory** | Quantified residues by crop, province, and type. |
| **Residue utilization** | Assumed share of residue entering a valorisation pathway. |
| **Coumaric acid** | Phenolic compound recoverable via biorefinery; a project valorisation product. |
| **SNF region** | Southern Netherlands and Flanders (eight NUTS2 provinces). |

---

## 3. Data conventions

| Data type | Mass basis |
|-----------|------------|
| **Residue inventory** | **Wet mass** (kt) |
| **Compost production (potential)** | **Wet mass** (kt) |
| **Biochar production (potential)** | **Dry mass** (kt) |

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
5. **Geographical coverage** — SNF provinces only, or clearly flagged if wider.
6. **Crop information** — align with the 23 vegetables and 10 fruit crops in the study where possible.
7. **Reproducibility** — enough detail for independent verification.
8. **Consistency** — compatible with wet/dry conventions above.
9. **Citation / reference** — full bibliographic reference in standard format (see Data Contribution page).
10. **Preferred formats** — structured spreadsheet (`.xlsx`) or CSV; PDF only as supplementary evidence.

Contributors whose data are accepted will receive an **acknowledgement email**.

---

## 7. Application availability

On **Streamlit Community Cloud (free tier)**, the app may sleep after inactivity. The first visit after sleep can show *“Get this app back”* while the server restarts. This is a **platform limitation**. Recommended access: via the group website at [lcatraining.nl/sustool](https://www.lcatraining.nl/index.php/sustool/). For 24/7 uptime, use paid hosting or self-deployment (see **Methods & Data** for maintainers).

---

## 8. Citation, license, and contact

**Suggested citation:** Circular Cultivation and Chemistry Sustainability Tool (SusTool), Maastricht University / Interreg Circulaire Teelt en Chemie.

**License:** Creative Commons Attribution 4.0 International (CC BY 4.0) for tool documentation and shared outputs, unless otherwise stated.

**Contact:** xinzhi.zhong@maastrichtuniversity.nl
