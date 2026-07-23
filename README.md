# STIX Weak Flare Analysis

Reproduction and extension of **Awasthi et al. (2021)** — *"Relative yield of thermal
and nonthermal emission during weak flares observed by STIX during September 20–25, 2021"*

---

## Overview

This project builds an automated pipeline to characterize the relative hard X-ray (HXR)
and soft X-ray (SXR) yield across ~200 weak solar flares detected by the Spectrometer
Telescope for Imaging X-rays (STIX) aboard Solar Orbiter. The core scientific quantity
is the quotient factor:

```
qf = HXR_fluence / F_SXR(tp)
```

where HXR fluence is the time-integrated hard X-ray flux over the flare rise phase
and F_SXR(tp) is the soft X-ray flux at the SXR peak time tp.

The immediate goal is to reproduce Figure 2 of the paper. The longer-term goal is a
scalable pipeline for statistical and machine-learning analysis of thousands of STIX flares.

---

## Data

> ⚠️ **Pipeline currently transitioning from quicklook to spectrogram data.**
> See PROJECT_ROADMAP.md for full transition status.

| Property | Value |
|----------|-------|
| Instrument | STIX / Solar Orbiter |
| Observation period | 2021-09-20 to 2021-09-25 |
| Total catalog flares | 215 |
| Flares with spectrogram coverage | 175 (173 after quality flags) |
| SXR band | 4–10 keV |
| HXR band | 12–25 keV (spectrogram; previously 15–25 keV quicklook proxy) |
| Spectrogram cadence | 0.5 seconds |
| Data source | STIX Data Center via `stixdcpy` |

---

## Project Structure

```
├── flare_pipeline/              # Reusable pipeline modules
│   ├── config.py                # Global constants and energy band definitions
│   ├── data.py                  # STIX catalog retrieval
│   ├── lightcurves.py           # ⚠️ Quicklook-based — to be replaced by spectrogram.py
│   ├── spectrogram.py           # ⬜ Not yet built — will replace lightcurves.py
│   ├── flare.py                 # Flare characterization (background, onset, peak, fluence, qf)
│   └── plotting.py              # ⬜ Standardized visualizations (not yet implemented)
│
├── notebooks/
│   ├── 01_STIX_Catalog.ipynb            # ✅ Catalog retrieval and export
│   ├── 02_Lightcurve_Extraction.ipynb   # ⚠️ Quicklook-based — will be rebuilt
│   ├── 03_Event_Characterization.ipynb  # ⚠️ Quicklook-based — will be rebuilt
│   └── [04–11 not yet created]
│
├── data/
│   └── processed/
│       └── stix_flare_catalog_sep20_25_2021.csv   # Canonical flare catalog (215 events)
│
├── archive/
│   └── ARCHIVED_Paper_Event_Matching_Attempt.ipynb
│
├── PROJECT_ROADMAP.md
├── RESEARCH_LOG.md
└── README.md
```

---

## Pipeline Modules

### `config.py`
Central configuration. Defines energy band names and SXR/HXR band assignments.
> ⚠️ Currently reflects quicklook 5-band structure. Will be updated with spectrogram
> channel indices once confirmed.

### `data.py`
Retrieves the STIX flare catalog via `stixdcpy`. Unaffected by spectrogram transition.

### `lightcurves.py` ⚠️
Quicklook lightcurve retrieval and parsing. **Will be replaced by `spectrogram.py`.**

### `flare.py`
Flare characterization functions:
- `estimate_background()` — local 5-minute pre/post quiet-time windows, contamination-checked
- `find_onset_peak()` — 1σ onset detection per band, SXR peak time
- `compute_fluence()` — ⬜ not yet implemented (pending spectrogram transition)
- `compute_qf()` — ⬜ not yet implemented

---

## Conventions

- `flare_id` is always a string (cast after `pd.read_csv`)
- Column names use underscores (`4_10`, not `4-10`)
- Never mutate input DataFrames; always use `.copy()`
- All reusable logic in `flare_pipeline/`; notebooks contain scientific workflow only
- Use keyword arguments at call sites with 3+ parameters
- Build and validate on a single test flare before scaling

**Current test flare:** `2109250916` (B2.9, 2021-09-25 09:12–09:19 UTC, row 23 in catalog)

---

## Setup

```bash
conda activate astrophysics
pip install stixdcpy
```

### Key dependencies
- `stixdcpy` — STIX Data Center access
- `pandas`, `numpy`, `matplotlib`

---

## Current Status

**Phase I — Paper Reproduction, in progress.**

The data layer is being transitioned from quicklook to spectrogram. Background estimation
and onset/peak detection are implemented in `flare.py`; fluence and qf are pending.

See `PROJECT_ROADMAP.md` for the full task list and `RESEARCH_LOG.md` for decision history.

---

## Reference

Awasthi, A. K., Mrozek, T., Kołomański, S., Litwicka, M., Stęślicki, M., & Kułaga, K.
(2021). *Relative yield of thermal and nonthermal emission during weak flares observed by
STIX during September 20–25, 2021.* arXiv:2402.01936

