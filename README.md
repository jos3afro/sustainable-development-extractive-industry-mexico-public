# Sustainable Development & The Extractive Industry: The Mexican Case

**Published in *Ecological Economics* (2026)**

> Lead co-author: José Riascos · [jos3riascos@gmail.com](mailto:jos3riascos@gmail.com)

---

## Data you need to download

All raw data must be placed in the folder structure below before running any script.
The data are not included in this repository due to size and licensing.

### 1. INEGI Census microdata (1990 · 2000 · 2010 · 2020)

| Year | URL | Place files in |
|------|-----|----------------|
| 1990 | [inegi.org.mx — CPVH 1990](https://www.inegi.org.mx/programas/ccpv/1990/) | `Censo1990/` |
| 2000 | [inegi.org.mx — CPVH 2000](https://www.inegi.org.mx/programas/ccpv/2000/) | `Censo2000/` |
| 2010 | [inegi.org.mx — CPVH 2010](https://www.inegi.org.mx/programas/ccpv/2010/) | `Censo2010/` |
| 2020 | [inegi.org.mx — CPVH 2020](https://www.inegi.org.mx/programas/ccpv/2020/) | `Censo2020/` |

Download the **microdata files** (`.dbf` for 1990–2010, `.CSV` for 2020, one file per state).

### 2. MINEX mining concessions database

- Source: **SNL / S&P Global Commodity Insights** (institutional subscription required)
- Filter: Country = `Mexico`
- Save as: `Censo2020/Minex_data.csv`

### 3. NASA MODIS NDVI (MOD13Q1 v6.1)

- Register for a free account at [urs.earthdata.nasa.gov](https://urs.earthdata.nasa.gov)
- Set your token as an environment variable:
  ```
  # Windows PowerShell
  $env:NASA_EARTHDATA_TOKEN = "your-token-here"
  # Linux / Mac
  export NASA_EARTHDATA_TOKEN="your-token-here"
  ```
- Run `scripts-cleaning/nasa_data_fetching.py` — it downloads all tiles covering Mexico (2000–2020) via the LP DAAC API
- Output goes to `NDVI/`

### 4. Land use data

- Source: [INEGI Marco Geoestadístico](https://www.inegi.org.mx/temas/mg/)
- Place processed files in `LandUse/`
- Or run `scripts-cleaning/land_use_fetch.py` (requires the same `NASA_EARTHDATA_TOKEN`)

### 5. Additional municipality-level controls

| File | Source | Place in |
|------|--------|----------|
| `Municipalities info.csv` | INEGI ITER | `Censo2020/` |
| `Inegi Fiscal income.xls` | INEGI Finanzas Públicas | `Censo2020/` |
| `Maps_data/Intersection_N.xlsx` (N = 5, 10 … 100) | QGIS output from `scripts-cleaning/mexicoqgis.py` | `Censo2020/Maps_data/` |

---

## Repository structure

```
mexico-mining-paper/            <- repo root
|-- config.py                   <- Python path config (auto-detects root)
|-- config.do                   <- Stata path config (sets $root, $core, etc.)
|
|-- scripts-cleaning/           <- data cleaning and construction
|   |-- data_cleaning_I.py      # merge all municipality-level variables into panel
|   |-- data_cleaning_II.py     # clean MINEX mining records -> treatment variable
|   |-- Census_cleanin.py       # census .dbf -> aggregated CSV per year
|   |-- nasa_data_fetching.py   # download NASA MODIS NDVI tiles via LP DAAC API
|   |-- nasa_qgis.py            # merge NDVI tiles with municipal shapefiles (QGIS)
|   |-- land_use_fetch.py       # fetch land use rasters from NASA LP DAAC
|   |-- LandUse_qgis.py         # spatial merge land use x municipalities (QGIS)
|   |-- Mexico_landuse_merge.py # aggregate land use files into municipality table
|   |-- mexicoqgis.py           # buffer/intersection for spatial rings (QGIS)
|   |-- Censo_cleanin.do        # Stata cleaning for 2020 census microdata
|   `-- Cleanin_gini.do         # Gini coefficient construction from 2020 microdata
|
|-- scripts-analysis/           <- econometric analysis (Stata)
|   |-- Municipality_analysis.do # merge cleaned datasets and build panel
|   |-- Census Analysis.do      # main DID estimates (income, education, Gini)
|   |-- Census_gini.do          # Gini-specific DID regressions
|   |-- LandUse Analysis.do     # DID estimates for land use outcomes
|   |-- ndvi.do                 # DID estimates for vegetation (NDVI)
|   `-- Water Quality.do        # DID estimates for water-related outcomes
|
|-- Censo1990/                  <- raw census data (not tracked)
|-- Censo2000/                  <- raw census data (not tracked)
|-- Censo2010/                  <- raw census data (not tracked)
|-- Censo2020/                  <- raw census data + MINEX (not tracked)
|-- NDVI/                       <- satellite NDVI tiles (not tracked)
|-- LandUse/                    <- land use files (not tracked)
|-- Core/                       <- intermediate merged datasets (not tracked)
`-- Results/                    <- regression output and figures (not tracked)
```

---

## How to run

### Requirements

**Python 3.9+**
```
pip install pandas numpy pyreadstat scikit-learn geopandas requests
```

**Stata 16+**
```stata
ssc install did_multiplegt
ssc install csdid
ssc install estout
```

**Other:** QGIS 3.x (for the three `_qgis.py` scripts only)

---

### Run order

```bash
# 1 -- Clean MINEX mining records -> treatment variable
python scripts-cleaning/data_cleaning_II.py

# 2 -- Clean census microdata (one CSV per year per municipality)
python scripts-cleaning/Census_cleanin.py

# 3 -- Download and process satellite NDVI data
python scripts-cleaning/nasa_data_fetching.py
# Then open QGIS and run scripts-cleaning/nasa_qgis.py in the Python console

# 4 -- Fetch and spatially merge land use
python scripts-cleaning/land_use_fetch.py
# Then run scripts-cleaning/LandUse_qgis.py in QGIS
python scripts-cleaning/Mexico_landuse_merge.py

# 5 -- Merge all municipality-level variables into panel
python scripts-cleaning/data_cleaning_I.py

# --- all remaining steps are in Stata; run from repo root ---

# 6 -- Build panel dataset and main analysis
stata -b do scripts-analysis/Municipality_analysis.do
stata -b do "scripts-analysis/Census Analysis.do"
stata -b do scripts-analysis/Census_gini.do
stata -b do "scripts-analysis/LandUse Analysis.do"
stata -b do scripts-analysis/ndvi.do
stata -b do "scripts-analysis/Water Quality.do"
```

> **QGIS scripts:** open QGIS, go to *Plugins > Python Console*, and paste the script. Edit the `ROOT` variable at the top of each file to match your local clone path.

> **Stata:** all `.do` files call `do "../config.do"` on line 2, which sets `$root`, `$core`, `$censo1990`, etc. Run Stata with the repo root as the working directory.

---

## Methods

**Main identification strategy:** Staggered Difference-in-Differences (Callaway & Sant'Anna 2021), which accounts for heterogeneous treatment timing across municipalities.

**Additional estimators:** TWFE with municipality x year fixed effects, Propensity Score Matching, Regression Adjustment.

**Outcome variables:** log income, Gini coefficient, school enrollment rate, years of schooling, log local government spending, NDVI, land use shares, water quality indicators.

---

## Citation

> Riascos, J. et al. (2026). Sustainable Development & The Extractive Industry: The Mexican Case. *Ecological Economics*.

---

## License

Code: [MIT License](LICENSE) | Data: subject to original source terms (INEGI open license; MINEX requires institutional access; NASA data is open)
