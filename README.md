# HXR-rich Weak Solar Flares — STIX Pipeline

Reproduction and extension of **Awasthi et al. (2021)**, analysing HXR-rich weak solar flares
using data from the **Spectrometer/Telescope for Imaging X-rays (STIX)** aboard Solar Orbiter.

---

## Project Objective

Reproduce the main observational results of Awasthi et al. (2021) — starting with the paper's
Figure 2 — and build a scalable, modular analysis pipeline for characterizing thousands of
STIX solar flares. The pipeline will later be extended with additional physical parameters
and machine learning for large-scale statistical analysis.

---

## Repository Structure

```
.
├── data/                  # Raw and processed STIX catalog data (gitignored)
├── docs/                  # Project documentation
├── figures/                # Output plots (e.g. Figure 2 reproduction)
├── flare_pipeline/         # Reusable pipeline modules
│   ├── config.py           # Global constants (STIX energy bands, SXR/HXR band definitions)
│   ├── data.py              # STIX flare catalog acquisition
│   ├── lightcurves.py       # Light curve retrieval, parsing, flare-window extraction
│   └── flare.py             # Flare event characterization (background, onset, peak)
├── notebooks/               # Numbered notebooks for the scientific narrative
│   ├── 01_STIX_Catalog.ipynb
│   ├── 02_Lightcurve_Extraction.ipynb
│   ├── 03_Event_Characterization.ipynb
│   └── archive/              # Parked/exploratory work (e.g. paper event matching attempt)
├── papers/                   # Reference papers (gitignored — not committed publicly)
├── PROJECT_ROADMAP.md         # Phased scientific roadmap and current status
├── RESEARCH_LOG.md             # Dated research log of progress, decisions, and bug fixes
└── pyproject.toml               # Project dependencies
```

---

## Pipeline Overview

```
Processed Catalog
   → Select flare
   → Download STIX light curve
   → Parse to DataFrame
   → Extract flare window
   → Estimate background
   → Find onset (t0) and peak (tp)
   → [Next] Compute HXR fluence
   → [Next] Compute qf
```

---

## Current Status

**Phase I — Paper Reproduction** (in progress)

- [x] Retrieve STIX flare catalog (215 events, Sep 20–25 2021)
- [x] Extract and standardize STIX light curves
- [x] Estimate per-flare local background (`estimate_background()`)
- [x] Characterize flare onset/peak times (`find_onset_peak()`)
- [ ] Compute HXR fluence — *pending supervisor confirmation on integration window*
- [ ] Compute qf
- [ ] Reproduce paper's Figure 2

See [`PROJECT_ROADMAP.md`](./PROJECT_ROADMAP.md) for the full phased roadmap and
[`RESEARCH_LOG.md`](./RESEARCH_LOG.md) for a dated log of decisions and progress.

---

## Project Conventions

- The processed CSV catalog is canonical — notebooks load it rather than re-querying STIX.
- All reusable logic lives in `flare_pipeline/`; notebooks handle scientific workflow only.
- Background is estimated **locally** (per-flare quiet-time windows), not globally, since
  quiet-Sun levels drift over an observation.
- Energy band naming uses underscores (e.g. `4_10`, not `4-10`) throughout.
- `flare_id` is cast to `str` immediately after any `pd.read_csv()` to avoid dtype drift.
- Comments explain *why*, not *how*.

---

## Setup

```bash
git clone <repo-url>
cd <repo-name>
pip install -e .
```

Dependencies are managed via `pyproject.toml`.

---

## Reference

Awasthi, A. K., et al. (2021). *[Paper title]*. Reference paper for this reproduction —
see `papers/` (not tracked in this repository; obtain via journal access).
