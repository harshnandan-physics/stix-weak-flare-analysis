# Research Log
## HXR-rich Weak Solar Flares — Awasthi et al. (2021) Reproduction

---

## 27 June 2026

**Completed**
- Created project structure.
- Retrieved STIX flare catalog (215 events, September 20–25 2021).
- Saved processed catalog as CSV.
- Investigated GOES_flux = 0 events.

**Observations**
- GOES_flux = 0 corresponds to GOES_class = NaN (9 flares). These are not errors —
  GOES simply had no reliable flux estimate for those events. Retained in catalog.

---

## 30 June 2026

**Infrastructure**
- Finalized modular architecture: `flare_pipeline/` for reusable code, numbered notebooks
  for scientific narrative.
- Implemented `config.py`, `data.py`, `lightcurves.py` (get_lightcurve, parse_lightcurve,
  extract_flare_window).
- Converted STIX relative time offsets to absolute UTC; rounded to whole seconds.

**Scientific progress**
- STIX API currently returns 215 flare detections vs. paper's 217. Discrepancy noted,
  likely due to catalog updates since paper publication. Proceeding with 215.
- Attempted timestamp-based matching of first paper event (SOL2021-09-21T09:46:22) to
  STIX catalog. Found two candidates within 5-minute tolerance; neither timestamp aligns
  cleanly. Concluded that timestamp matching alone is insufficient.

**Decision: paper event cross-identification parked.**
Attempting to identify individual paper events before the pipeline exists is blocking
progress on the main deliverable. The real task is building a generic per-flare pipeline
and running it across all 215 flares. Individual event matching will be revisited as an
optional validation step once the pipeline produces qf values.

---

## 11 July 2026

**Bug fixes**
- `flare_id` dtype mismatch: CSV round-trip coerces flare_id to int64; all notebooks
  now cast to str immediately after pd.read_csv(). Affected notebook 02 and 03 silently.
- Column naming inconsistency: `parse_lightcurve()` was building columns with hyphens
  (4-10) while config.py defined band keys with underscores (4_10). Fixed in lightcurves.py.
  Canonical convention: underscores everywhere.

**Rename**
- `events.py` → `flare.py`. Follows module naming convention (config, data, lightcurves, flare).

**Implemented and validated: `estimate_background()`**
- Method: local quiet-time windows (5 min pre + 5 min post) anchored to catalog
  start_UTC / end_UTC. Both windows cross-checked against full catalog to reject
  contamination from neighboring flares. Raises ValueError if no clean window available.
- Rationale for local over global: background drifts slowly over the observation;
  local estimation is more accurate per-flare.
- Validated on row 50 (flare 2109241944, 2021-09-24): both windows clean (pre+post),
  means consistent with catalog LC*_BKG_COUNTS_4S reference values (4_10: 250.8 vs 247).
- The catalog's LC*_BKG_COUNTS_4S columns have only 2 unique values across 215 flares —
  confirmed unsuitable as per-flare background estimates. Used as sanity check only.

**Implemented and validated: `find_onset_peak()`**
- Background subtraction performed once inside this function; subtracted DataFrame
  passed downstream to avoid recomputing.
- t0: first timestamp where background-subtracted flux exceeds 1σ, per band independently.
- tp: timestamp of maximum SXR (4_10) flux within the flare window.
- Validated on row 50: 50_84 onset = None (physically correct for weak B-class flare),
  rise time ~48 seconds (consistent with paper's reported 2–10 minute flare durations).

**Open decision: fluence integration window.**
Paper defines fluence as integral from t0 to tp. Supervisor's integration plots show
red-highlighted HXR windows that are shorter and self-terminating — not anchored to SXR tp.
Interpretation: integrate HXR only where it is detectably above background (HXR t0 → HXR
decay back below threshold). This avoids integrating noise-dominated stretches, especially
important for weak flares where HXR is marginal. Awaiting supervisor confirmation before
implementing compute_fluence().

**Scaling notes (deferred to Phase III)**
- Current design makes one get_lightcurve() API call per flare. At 215 flares this is
  acceptable; at 10,000+ it is not. Future fix: fetch-once-per-day caching.
- catalog overlap scan in estimate_background() is O(N²). Acceptable at 215; will need
  sorted/windowed search at large N.

---

## 12 July 2026

**Archived**
Notebook 02 paper event cross-identification archived to
`archive/ARCHIVED_Paper_Event_Matching_Attempt.ipynb`. Timestamp matching alone
is insufficient (catalog peak_UTC does not correspond to the paper's manually-identified
tp). Closing conclusion cell added to the archived notebook. Will revisit with
light-curve shape comparison as optional validation after pipeline is complete.