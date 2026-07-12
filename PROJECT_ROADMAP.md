# PROJECT ROADMAP
## Extreme Thermal and Non-Thermal Solar Flares

---

## Project Objective

Reproduce the main observational results of Awasthi et al. (2021) and build a scalable analysis pipeline for thousands of STIX solar flares.

The immediate goal is to reproduce the paper's Figure 2 before extending the analysis with additional physical parameters and machine learning.

---

# Scientific Roadmap

## Phase I — Paper Reproduction

- [x] Retrieve STIX flare catalog  
- [x] Extract STIX light curves
- [x] Estimate the background flux
- [x] Characterize flare events
- [ ] Compute HXR fluence
- [ ] Compute qf
- [ ] Reproduce Figure 2

---

## Phase II — Physical Interpretation

- [ ] Thermal parameters
- [ ] Non-thermal parameters
- [ ] Plasma diagnostics
- [ ] HXR-rich flare identification

---

## Phase III — Extension

- [ ] Scale to large flare datasets
- [ ] Automated pipeline
- [ ] Feature engineering
- [ ] Statistical analysis
- [ ] Machine Learning
- [ ] Physical interpretation

---

# Notebook Roadmap

| Notebook | Purpose | Status |
|-----------|---------|--------|
| 01_STIX_Catalog          | Retrieve and inspect STIX flare catalog   | ✅ Complete |
| 02_Lightcurve_Extraction | Download, standardize and isolate flare light curves | 🟡 In Progress |
| 03_Event_Characterization| Background estimation (✅), onset/peak detection (✅), fluence pending supervisor confirmation | 🟡 In Progress |
| 04_Fluence_Calculation   | Compute HXR fluence                       | ⬜ Not Started |
| 05_qf_Calculation        | Compute qf for each flare                 | ⬜ Not Started |
| 06_Reproduce_Figure2     | Reproduce paper's main statistical result | ⬜ Not Started |
| 07_HXR_Rich_Flares       | Identify and investigate HXR-rich flares  | ⬜ Not Started |
| 08_Extended_Analysis     | Beyond the paper                          | ⬜ Not Started |
|-----------|---------|--------|
| ARCHIVED_Paper_Event_Matching_Attempt | Reconstruct the paper event sample        | 🟥 ARCHIVED |
> **Archived:** `archive/ARCHIVED_Paper_Event_Matching_Attempt.ipynb` —
> paper event timestamp-matching attempt; concluded insufficient, parked for
> optional future validation.

---

# Pipeline Modules

| Module | Purpose | Status |
|----------|---------|--------|
| config.py      | Global project configuration (energy bands, constants, etc.) | ✅ |
| data.py        | STIX catalog acquisition | ✅ |
| lightcurves.py | Light curve retrieval and preprocessing | ✅ |
| flare.py       | Flare event characterization (background, onset, peak, etc.) | 🟡 |
| plotting.py    | Relevent plotting | ⬜ |

---

## Project Conventions

- Processed CSV is the canonical flare catalog.
- Every notebook loads the processed catalog instead of querying the STIX Data Center again.
- All reusable logic belongs in `flare_pipeline/`.
- Notebooks perform scientific workflows only.
- Every notebook begins with:
  - Objective
  - Inputs
  - Outputs
  - Scientific Milestone
- Permanent exploratory code belongs in the appropriate notebook.
- Temporary exploration belongs in `Preliminary STIX Data Access.ipynb`.
- Preserve all five STIX energy bands in the standardized DataFrame.
- Primary scientific analysis will use the 4–10 keV and 15–25 keV bands unless explicitly required otherwise.
- Comments should explain *why* something is done rather than *how* Python performs it.
- Develop and validate the pipeline on one flare before scaling to all flares.

---

# Current Status

## Current Phase

**Phase I — Paper Reproduction**

---

## Completed

### Notebook 01
- Retrieved STIX flare catalog.
- Inspected catalog structure.
- Exported processed catalog as CSV.

### Notebook 02
- Established correspondence between paper timestamps and STIX catalog.
- Identified candidate flare IDs for the first paper event.
- Confirmed that timestamp matching alone is insufficient; final identification will rely on light-curve comparison.

### Notebook 03
- Implemented `get_lightcurve()`.
- Implemented `parse_lightcurve()`.
- Converted STIX ResponseDict into a standardized pandas DataFrame.
- Converted relative time offsets into absolute UTC timestamps.
- Rounded timestamps to one-second precision.
- Implemented `extract_flare_window()`.

---

## Current Objective

Validate the complete light-curve extraction pipeline by reproducing the first flare analysed in the paper.

Workflow:

Processed Catalog
→ Select flare
→ Download STIX light curve
→ Parse to DataFrame
→ Extract flare window
→ Verify against paper

---

## Next Objective

Begin event characterization:

- Background estimation
- Peak identification
- Start/end time verification
- Preparation for HXR fluence calculation