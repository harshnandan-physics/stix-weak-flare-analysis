# PROJECT ROADMAP
## Extreme Thermal and Non-Thermal Solar Flares
## Reproduction and Extension of Awasthi et al. (2021)

---

## Project Objective

Reproduce the main observational result of Awasthi et al. (2021) — the statistical
characterization of relative HXR/SXR yield (qf) across ~200 weak solar flares observed
by STIX during September 20–25, 2021 — and build a scalable automated pipeline capable
of extending the analysis to thousands of future STIX flare detections.

The immediate deliverable is a reproduction of Figure 2 of the paper.

---

## Data Source

> ⚠️ **ARCHITECTURAL TRANSITION IN PROGRESS (as of 16 July 2026)**
>
> The pipeline is transitioning from **STIX quicklook lightcurve data** to
> **STIX spectrogram science data**. The transition is not yet complete in code.
> See the section "Pipeline Modules" for exact status per file.

| Property | Quicklook (old) | Spectrogram (new) |
|----------|----------------|-------------------|
| Cadence | 4 seconds | 0.5 seconds |
| Energy bands | 5 fixed bands (4–84 keV) | User-defined from ~32 channels |
| HXR proxy | 15–25 keV (fixed) | 12–25 keV (user-selected, closer to paper) |
| Coverage | All 215 flares | 175 / 215 flares (40 have no science data) |
| Access | `stixdcpy.quicklook.LightCurves` | `stixdcpy.spectrogram.Spectrogram` |

**Why the switch:** Higher cadence improves onset/peak time precision and fluence
integration accuracy. User-defined bands allow a closer match to the paper's
12–20 keV HXR band. Directed by supervisor July 2026.

---

## Known Methodological Caveats

**HXR band substitution (partially resolved).**
The paper uses 12–20 keV as the HXR band. With spectrogram data we can approximate
12–25 keV by summing appropriate channels — much closer than the quicklook proxy of
15–25 keV. However, 7 spectrogram files are capped at 18 keV and cannot support
12–25 keV. Fallback strategy for those flares is pending.

**Fluence integration window — methodology resolved, implementation pending.**
Two methods to be implemented:
- **Method 2 (primary):** Integrate HXR from t_1e_rise (where SXR first crosses
  SXR_peak/e on the rise) to tp. Adaptive and physically motivated.
- **Method 1 (cross-check):** Fixed 2-minute window [tp − 2 min, tp].
Both will be implemented and compared before scaling to all flares.

**Catalog data quality flags.**
- Row 116 (flare 2109221943): ~4-hour catalog duration — likely catalog error. Excluded.
- Row 78 (flare 2109231524): ~79-minute duration — suspicious. Excluded.

**Spectrogram coverage.**
40 / 215 flares have no spectrogram science data available. These will be excluded
from the spectrogram pipeline. Working dataset: 175 flares (minus 2 quality flags = 173).

---

# Scientific Roadmap

## Phase I — Paper Reproduction

- [x] Retrieve STIX flare catalog (215 events)
- [x] Inspect and export processed catalog
- [~] Paper event cross-identification (parked — see archive/)
- [x] Assess spectrogram data coverage (175 / 215 flares covered)
- [ ] Extract and standardize spectrogram light curves ← **CURRENT STAGE**
- [ ] Estimate per-flare background (mean + σ per band)
- [ ] Determine flare onset time (t0) and SXR peak time (tp) from data
- [ ] Compute HXR fluence (Method 2 primary, Method 1 cross-check)
- [ ] Compute qf per flare
- [ ] Run pipeline across all 175 covered flares
- [ ] Reproduce Figure 2

## Phase II — Physical Interpretation

- [ ] Thermal parameter extraction (temperature, emission measure)
- [ ] Non-thermal parameter extraction (spectral slope)
- [ ] Plasma density estimation
- [ ] Correlation analysis (qf vs EM, qf vs T, qf vs density)
- [ ] HXR-rich flare identification and characterization

## Phase III — Extension and Scaling

- [ ] Restructure data acquisition (fetch-once-per-day caching)
- [ ] Optimise catalog overlap scan for large N (sorted/windowed search)
- [ ] Scale pipeline to large flare datasets (thousands of events)
- [ ] Feature engineering for ML
- [ ] Statistical and machine learning analysis
- [ ] Physical interpretation of extended results

---

# Notebook Roadmap

| Notebook | Purpose | Status |
|----------|---------|--------|
| 01_STIX_Catalog | Retrieve, inspect, and export the STIX flare catalog | ✅ Complete |
| 02_Lightcurve_Extraction | ⚠️ Built on quicklook data — will be rebuilt for spectrogram | 🔄 Needs rebuild |
| 03_Event_Characterization | ⚠️ Built on quicklook data — will be rebuilt for spectrogram | 🔄 Needs rebuild |
| 04_Spectrogram_Coverage | Assess spectrogram file coverage vs. catalog; identify covered flares | ⬜ Not started |
| 05_Spectrogram_Extraction | Fetch spectrogram, parse to DataFrame, inspect energy channels | ⬜ Not started |
| 06_Event_Characterization | Background, onset, peak on spectrogram data | ⬜ Not started |
| 07_Fluence_and_qf | Compute HXR fluence (Method 2 + Method 1) and quality factor | ⬜ Not started |
| 08_Full_Pipeline_Run | Run complete pipeline across all 175 covered flares | ⬜ Not started |
| 09_Reproduce_Figure2 | Reproduce paper's main statistical result | ⬜ Not started |
| 10_HXR_Rich_Flares | Identify and investigate HXR-rich weak flares | ⬜ Not started |
| 11_Extended_Analysis | Beyond the paper | ⬜ Not started |

> **Archived:** `archive/ARCHIVED_Paper_Event_Matching_Attempt.ipynb` —
> paper event timestamp-matching attempt; concluded insufficient, parked for
> optional future validation.

---

# Pipeline Modules

| Module | Purpose | Status | Notes |
|--------|---------|--------|-------|
| config.py | Global constants — energy bands, SXR/HXR assignments | ⚠️ Needs update | STIX_BANDS reflects quicklook 5-band structure; must be updated to spectrogram channel indices once confirmed |
| data.py | STIX flare catalog retrieval | ✅ Complete | Unaffected by spectrogram switch |
| lightcurves.py | Quicklook light curve fetch, parse, window extraction | ⚠️ To be replaced | Will be superseded by spectrogram.py |
| spectrogram.py | Spectrogram fetch, parse, window extraction | ⬜ Not built | New module to replace lightcurves.py |
| flare.py | Flare characterization — background, onset/peak, fluence, qf | 🟡 Partial | estimate_background() and find_onset_peak() implemented and validated on quicklook; need re-testing on spectrogram data. compute_fluence() and compute_qf() not yet written. |
| plotting.py | Standardized visualizations | ⬜ Not started | |

---

# Project Conventions

### Data
- The processed CSV (`stix_flare_catalog_sep20_25_2021.csv`) is the canonical flare catalog.
- Every notebook loads the processed catalog from disk — no re-querying the STIX Data Center.
- Working dataset for spectrogram pipeline: 175 covered flares, minus rows 116 and 78
  (data quality flags) = **173 usable flares**.
- SXR band: 4–10 keV. HXR band: 12–25 keV (spectrogram; subject to channel inspection).

### Code
- All reusable logic belongs in `flare_pipeline/`. Notebooks contain scientific workflow only.
- `flare_id` is always treated as a string throughout the pipeline.
- Column names use underscores: `4_10`, `10_15`, `15_25`, `25_50`, `50_84` (quicklook);
  spectrogram band naming convention to be established once channels are confirmed.
- Use keyword arguments at call sites with 3+ parameters to prevent silent positional swaps.
- Never mutate input DataFrames — always work on `.copy()`.
- Comments explain *why*, not *what Python is doing*.

### Development
- Build and validate on a single flare before scaling to all flares.
- **New test flare: row 23, flare_id `2109250916` (B2.9, Sep 25 09:12–09:19, ~424 s).**
  Previous test flare (row 50) has no spectrogram coverage.
- Raise explicitly on bad inputs rather than returning NaN silently.
- Every new function in `flare.py` is tested in the corresponding notebook before the
  next function is written.

### Notebooks
- Every notebook begins with: Objective, Inputs, Outputs, Scientific Milestone.
- Temporary exploration belongs in the Preliminary scratch notebook only.

---

# Current Status

**Phase I — Paper Reproduction**

### Completed
- STIX catalog retrieved and exported (215 events).
- Spectrogram coverage assessed: 175/215 flares covered.
- Data quality flags identified (rows 78, 116).
- New test flare selected: `2109250916`.
- `estimate_background()` and `find_onset_peak()` implemented in `flare.py`
  (validated on quicklook data; spectrogram re-validation pending).
- Fluence methodology resolved: Method 2 (t_1e_rise → tp) primary,
  Method 1 (2 min window) as cross-check.
- Notebooks 01, 02, 03 polished (note: 02 and 03 will be rebuilt for spectrogram).
- GitHub repo live.

### Immediate next step
Fetch spectrogram for flare `2109250916`, inspect energy channel structure
(bin names, keV boundaries, channel indices for SXR and HXR), confirm 0.5s cadence.
Then build `spectrogram.py` and update `config.py`.

### Parked
Paper event cross-identification (archived). Revisit after pipeline produces qf values.

