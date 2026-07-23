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
- GOES_flux = 0 corresponds to GOES_class = NaN (9 flares). These are not errors — GOES simply had no reliable flux estimate for those events. Retained in catalog.

---

## 30 June 2026

**Infrastructure**
- Finalized modular architecture: `flare_pipeline/` for reusable code, numbered notebooks for scientific narrative.
- Implemented `config.py`, `data.py`, `lightcurves.py` (get_lightcurve, parse_lightcurve, extract_flare_window).
- Converted STIX relative time offsets to absolute UTC; rounded to whole seconds.

**Scientific progress**
- STIX API currently returns 215 flare detections vs. paper's 217. Discrepancy noted, likely due to catalog updates since paper publication. Proceeding with 215.
- Attempted timestamp-based matching of first paper event (SOL2021-09-21T09:46:22) to STIX catalog. Found two candidates within 5-minute tolerance; neither timestamp aligns cleanly. Concluded that timestamp matching alone is insufficient.

**Decision: paper event cross-identification parked.**
Attempting to identify individual paper events before the pipeline exists is blocking progress on the main deliverable. The real task is building a generic per-flare pipeline and running it across all 215 flares. Individual event matching will be revisited as an optional validation step once the pipeline produces qf values.

---

## 11 July 2026

**Bug fixes**
- `flare_id` dtype mismatch: CSV round-trip coerces flare_id to int64; all notebooks now cast to str immediately after pd.read_csv(). Affected notebooks 02 and 03 silently.
- Column naming inconsistency: `parse_lightcurve()` was building columns with hyphens (4-10) while config.py defined band keys with underscores (4_10). Fixed in lightcurves.py. Canonical convention: underscores everywhere.

**Rename**
- `events.py` → `flare.py`. Follows module naming convention (config, data, lightcurves, flare).

**Implemented and validated: `estimate_background()`**
- Method: local quiet-time windows (5 min pre + 5 min post) anchored to catalog start_UTC / end_UTC. Both windows cross-checked against full catalog to reject contamination from neighboring flares. Raises ValueError if no clean window available.
- Rationale for local over global: background drifts slowly over the observation; local estimation is more accurate per-flare.
- Validated on row 50 (flare 2109241944, 2021-09-24): both windows clean (pre+post), means consistent with catalog LC*_BKG_COUNTS_4S reference values (4_10: 250.8 vs 247).
- The catalog's LC*_BKG_COUNTS_4S columns have only 2 unique values across 215 flares — confirmed unsuitable as per-flare background estimates. Used as sanity check only.

**Implemented and validated: `find_onset_peak()`**
- Background subtraction performed once inside this function; subtracted DataFrame passed downstream to avoid recomputing.
- t0: first timestamp where background-subtracted flux exceeds 1σ, per band independently.
- tp: timestamp of maximum SXR (4_10) flux within the flare window.
- Validated on row 50: 50_84 onset = None (physically correct for weak B-class flare), rise time ~48 seconds (consistent with paper's reported 2–10 minute flare durations).

**Fluence integration window — methodology resolved.**
Two methods to be implemented and compared:
- Method 2 (primary): integrate HXR from t_1e_rise to tp, where t_1e_rise is the timestamp on the RISE side only where background-subtracted SXR first crosses SXR_peak/e. Adaptive, physically motivated, no free parameters. Rise side 1/e crossing is steep and well-defined even for weak flares.
- Method 1 (cross-check): fixed 2-minute window [tp − 2 min, tp]. Simpler, uniform, but window width is an arbitrary free parameter.

Both will be implemented in compute_fluence() and compared on the test flare before scaling.

**Notebook cleanup and restructuring**
- Notebook 02 (Paper Event Selection) archived to `archive/ARCHIVED_Paper_Event_Matching_Attempt.ipynb`. Closing conclusion cell added. Removed from active pipeline.
- Remaining notebooks renumbered: 03 → 02 (Lightcurve Extraction), 04 → 03 (Event Characterization).
- All three active notebooks fully restructured: proper markdown headers (Objective, Inputs, Outputs, Scientific Milestone), section headings, inline comments, and visualizations added.

**Visualizations added**
- Notebook 02: Raw SXR and HXR lightcurve with flare window highlighted.
- Notebook 03: Background estimation windows overlaid on raw lightcurve.
- Notebook 03: Background-subtracted SXR and HXR flux with t0 and tp marked.

**Documentation**
- PROJECT_ROADMAP.md fully revamped.
- RESEARCH_LOG.md brought up to date.
- GitHub repository initialized and pushed: github.com/harshnandan-physics/stix-weak-flare-analysis

**Scaling notes (deferred to Phase III)**
- Current design makes one get_lightcurve() API call per flare. At 215 flares this is acceptable; at 10,000+ it is not. Future fix: fetch-once-per-day caching.
- Catalog overlap scan in estimate_background() is O(N²). Acceptable at 215; will need sorted/windowed search at large N.

---

## 13 July 2026

**Notebook cleanup committed to GitHub.**
- Repository updated: github.com/harshnandan-physics/stix-weak-flare-analysis

---

## 16 July 2026

**MAJOR ARCHITECTURAL DECISION: Switch from quicklook lightcurve data to spectrogram science data.**

**Why:**
Supervisor directed transition from STIX quicklook lightcurve data (4-second cadence, 5 fixed energy bands) to STIX spectrogram science data (0.5-second cadence, user-defined energy bands). Reasons:
1. Higher temporal resolution (0.5s vs 4s) improves accuracy of integration values, onset/peak time detection, and fluence calculation.
2. User-defined energy bands allow us to approximate the paper's 12–20 keV HXR band more accurately (e.g., 12–25 keV) rather than being locked to the quicklook's fixed 15–25 keV proxy.
3. Better reliability of count statistics at higher cadence for weak flares.

**Spectrogram data coverage assessment:**
- Queried stixdcpy for spectrogram files covering 2021-09-20 to 2021-09-25.
- 56 unique spectrogram FITS files found.
- 175 / 215 catalog flares have full spectrogram coverage.
- 40 flares fall in coverage gaps — no spectrogram data retrievable. These will be excluded from the spectrogram-based pipeline.
- Energy ranges vary across files: [4,28] keV (40 files), [4,50] keV (7 files), [4,18] keV (7 files), [4,40] keV (1 file), [4,∞] keV (1 suspicious file). The 7 files capped at 18 keV cannot support a 12–25 keV HXR band — fallback strategy to be determined.

**Data quality flags:**
- Row 116 (flare 2109221943): catalog duration ~4 hours (15:48–19:50). Almost certainly a catalog error. Flagged for exclusion.
- Row 78 (flare 2109231524): catalog duration ~79 minutes. Suspicious. Flagged for exclusion.

Both are excluded regardless of spectrogram coverage.

**Test flare change:**
- Old test flare (row 50, 2109241944, Sep 24) has NO spectrogram coverage.
- New test flare: row 23, flare_id 2109250916 (B2.9, ~424 s duration, Sep 25 09:12–09:19). Confirmed to have spectrogram coverage.

**stixdcpy spectrogram API investigation:**
- `stixdcpy.spectrogram.Spectrogram.from_sdc(start, end)` exists and is the correct call.
- Data is stored in `spec.data` dict (NOT as top-level attributes).
- Key name for counts array is `'spectrogram'` (NOT `'counts'`).
- Full key list: 'datetime', 'time_bin', 'timedel', 'spectrogram', 'time_bins', 'triggers', 'rcr', 'elow', 'ehigh', 'dmask', 'pmask', 'energy_bins', 'energy_bin_names'.
- Energy channel structure not yet fully inspected on new test flare — this is the immediate next step.

**What has NOT changed yet (code-level):**
- `lightcurves.py` still uses quicklook API — will be replaced by `spectrogram.py`.
- `config.py` STIX_BANDS still maps quicklook 5-band structure — will be updated once spectrogram energy channels are confirmed.
- Notebooks 02 and 03 still use quicklook workflow — will be rebuilt.
- `flare.py` (estimate_background, find_onset_peak) logic is conceptually valid and will be re-tested on spectrogram data rather than rewritten.

**Immediate next step:**
Fetch spectrogram for new test flare, inspect energy bin structure (channel indices and keV boundaries), confirm cadence = 0.5s, then begin building `spectrogram.py` module.

---

## 23 July 2026

**INVESTIGATION: Spectrogram time-binning cadence — is 0.5s cadence real for this catalog?**

Following the discovery (16 July) that `spec.data["spectrogram"]` is shaped `(n_energy_channels, n_time_bins)` and that fluence must integrate per-bin `timedel` rather than a fixed `dt`, we ran a structured investigation into how variable that `timedel` actually is, and whether the promised 0.5s cadence is realistic for our catalog's weak flares.

**(1) Confirmed: `spec.data["spectrogram"]` values are count RATES (counts/sec), not raw counts.**
Multiplying `spectrogram × timedel` (broadcast per-bin) recovers exact integer photon counts across all 17 energy channels and the full day's bins tested (max deviation from nearest integer: 5.68e-14, i.e. floating-point noise only). This is NOT normalized by keV channel width — only by time. Confirmed the earlier `dcr` framing (from prior session notes) was directionally right but imprecise: this is counts/sec, not counts/sec/keV.

Implication for `compute_fluence()`: fluence = Σ(rate_i × timedel_i) over the integration window, using each bin's own timedel — not a global constant.

**(2) Confirmed: test flare `2109250916` gets NO fine time binning, even during the flare itself.**
Of 86 bins fetched around the flare, only 22 fall inside the catalog's official [start_UTC, end_UTC] window. All 22 have timedel in the 17.7–20s range. The 5-minute pre-flare background window is a flat, unbroken 20.0s throughout. STIX's onboard adaptive binning never triggered finer resolution for this flare at any point in its lifetime.

**(3) Confirmed: adaptive binning is real, but flux-gated with a clear threshold.**
Spearman correlation between total flux (summed across 17 channels) and timedel, across a full day (2021-09-25 00:02–23:30): ρ = −0.911 (p ≈ 0). Scatter shows bin width pinned at ~20s (flat ceiling) below roughly 2,000–3,000 counts/sec total flux, then a sharp drop, asymptoting toward 0.5s above roughly 7,000–10,000 counts/sec. Below the threshold, STIX simply does not compress the bin — this is a real onboard trigger behavior, not sensor noise or a fetch artifact.

**(4) Catalog-wide check: how much of the 173-flare working sample falls below this threshold?**
Using quicklook's LC0–LC4_PEAK_COUNTS_4S (summed across bands, divided by 4 to convert to counts/sec) as a proxy for peak total flux, checked against the full 215-flare catalog:
- 209 / 215 flares (97.2%) never reach ~2,500 counts/sec even at their peak moment.
- Test flare 2109250916 sits at the 25th percentile of the catalog by this proxy — i.e. it is not an unusually weak outlier; three-quarters of the catalog is brighter, and the overwhelming majority of those are still below threshold.
- Because bin width is peak-flux-gated, a flare whose peak never crosses the threshold will have NO fine bins anywhere in its duration — not "worse cadence," but uniformly coarse cadence throughout.
- Caveat: this proxy sums quicklook's wider 4–84 keV band range against spectrogram's narrower 4–28 keV channel range, so it is if anything an overestimate of flux — the true fraction below threshold in spectrogram's own units could be higher than 97.2%, not lower.

**Consequence — this changes the calculus of the 16 July architectural decision.**
Spectrogram bins at ~18–20s are ~5x COARSER than quicklook's fixed 4s cadence, for essentially the entire catalog. The primary stated justification for the quicklook → spectrogram switch ("higher cadence improves onset/peak time precision and fluence integration accuracy") does not hold for ~97% of the sample. The switch's remaining, narrower justification — user-defined energy bands enabling a closer 12–25 keV HXR match — still stands independently and is unaffected by this finding.

**Two open questions for Dr. Awasthi drafted (see Preliminary notebook / message to supervisor):**
1. Given quicklook has finer cadence than spectrogram for ~97% of the catalog, should the pipeline keep spectrogram for time-resolved quantities (onset t0, peak tp, fluence integration) at all, or should those revert to quicklook, with spectrogram used only for its custom-band flux values (if that combination is technically viable)?
2. Separately still pending: handling of the 7 files capped at 18 keV (partial HXR coverage) — exclude, or reduced 12–18 keV band for those flares only.

**Not yet resolved / next steps:**
- Await supervisor decision on data-source strategy before writing `spectrogram.py` channel-selection logic or updating `config.py`.
- If quicklook is retained for timing, need to decide whether spectrogram is used at all in Phase I, or deferred to Phase II physical-parameter work where cadence matters less.

---
