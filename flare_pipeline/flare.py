"""
Module:
    flare.py

Purpose:
    Flare event characterization — background, onset/peak times, fluence, qf.

Project:
    HXR-rich Weak Solar Flares
"""

import pandas as pd
from flare_pipeline.config import STIX_BANDS, SXR_BAND

def estimate_background(
    lightcurve_df,
    flare_df,                        # full flare catalog — needed to check for contamination from neighboring flares
    flare_row,                       # the single flare this call is estimating background for
    window_minutes = 5,                # width of each quiet-time window, in minutes
    bands = tuple(STIX_BANDS.keys()),  # energy bands to compute stats for
):
    """
    Purpose
    -------
    Estimate background mean and standard deviation per energy band,
    using local quiet-time windows immediately before and after a flare.
    (Background is estimated locally rather than globally, since quiet-Sun levels 
    drift over the course of an observation.)
    
    Each of the two candidate windows is only used if no other cataloged flare overlaps it 
    (since a window contaminated by a neighboring flare would bias the background estimate).

    Parameters
    ----------
    lightcurve_df : pandas.DataFrame
        Full parsed lightcurve covering at least flare_start - window_minutes
        to flare_end + window_minutes (output of parse_lightcurve).
    flare_df : pandas.DataFrame
        Full flare catalog — used to check for contamination from neighboring flares.
    flare_row : pandas.Series
        A single row from flare_df representing the flare being characterized.
        Must have start_UTC, end_UTC, and flare_id fields.
    window_minutes : int
        Width of each quiet-time window in minutes. Default is 5.
    bands : tuple of str
        Energy band column names to compute background stats for.
        Defaults to all bands defined in config.STIX_BANDS.

    Returns
    -------
    dict
        {
            band: {
                "mean"   : float,               # mean background count rate
                "std"    : float,               # standard deviation (sample, ddof=1)
                "source" : "pre"/"post"/"pre+post",  # which window(s) contributed
            }
        }
        One entry per band. Raises ValueError if no clean window is available.
    """
    pad = pd.Timedelta(minutes = window_minutes)

    # Pre-window is anchored to flare start and extends backward — it's the quiet stretch
    # leading up to the flare, so sampling should stop exactly where the flare begins.
    pre_start = flare_row["start_UTC"] - pad
    pre_end = flare_row["start_UTC"]

    # Post-window is anchored to flare end and extends forward — mirrors the pre-window,
    # sampling should only begin once the flare itself is over.
    post_start = flare_row["end_UTC"]
    post_end = flare_row["end_UTC"] + pad

    #   ←── pre_window ──→ |══ FLARE ══| ←── post_window ──→
    # start-pad         start         end                end+pad
    pre_window = (pre_start, pre_end)
    post_window = (post_start, post_end)

    def is_clean(window):
        # Checks whether a candidate window is contaminated by some OTHER flare in the
        # catalog — a window can't be trusted as "background" if another flare's own
        # emission falls inside it.
        a, b = window

        # Drop the current flare from the catalog before checking overlaps — we only
        # care about interference from *other* events.
        others = flare_df[flare_df["flare_id"] != flare_row["flare_id"]]

        # Test whether an other-flare's [start_UTC, end_UTC] intersects
        # our [a, b] window whenever it starts early enough AND ends late enough to reach
        # into it.
        overlap = others[(others["start_UTC"] <= b) & (others["end_UTC"] >= a)]

        # No overlapping rows survived the filter => window is quiet and safe to treat as background.
        # => overlap.empty returns true => is_clean() returns true.
        return overlap.empty        

    # Pre and post are tested independently. A flare can end up with
    # zero, one, or both windows usable, depending on how crowded its neighbors are.
    usable_windows = []
    if is_clean(pre_window):
        usable_windows.append(("pre", pre_window))
    if is_clean(post_window):
        usable_windows.append(("post", post_window))
    if not usable_windows:
        # In case both sides came back contaminated — there's no quiet data to build a background
        # from, so explicitly fail output here rather than let a NaN slip into fluence/qf calculations.
        raise ValueError(
            f"No clean background window found for flare {flare_row['flare_id']}"
        )

    # Blank selection mask spanning the full light curve, with same index but nothing selected yet.
    # This gets built up window by window below rather than slicing lightcurve_df directly,
    # so the flare's own rows are excluded automatically by never being marked True.
    mask = pd.Series(False, index=lightcurve_df.index)

    for _, (a, b) in usable_windows:
        # Marks True every light curve row whose timestamp falls inside this window.
        window_mask = (lightcurve_df["time"] >= a) & (lightcurve_df["time"] <= b)

        # OR-accumulate into the running mask — combining pre and post into one selection
        mask |= window_mask

    # Filtered down to just the quiet-time rows — either one continuous burst (pre-only or post-only) or two (pre and post)
    bg_data = lightcurve_df[mask]

    # Provenance tag recording which window(s) actually contributed — "pre", "post", or
    # "pre+post" — useful later for weighting background quality per flare.
    labels = []
    for label, _ in usable_windows:
        labels.append(label)
    source = "+".join(labels)

    # Per-band background stats:
    # Mean/std are computed independently per band (since each energy channel has its own count-rate values),
    # but reuse the same source label for all of them (since its been defined once for the particular flare_row and doesn't depend on energy band).
    result = {}
    for band in bands:
        result[band] = {
            "mean": bg_data[band].mean(),
            "std": bg_data[band].std(),
            "source": source,
        }
    return result


def find_onset_peak(
    flare_window,
    bg,
    bands = tuple(STIX_BANDS.keys())
):
    """
    Purpose
    -------
    Find flare onset time (t0) per energy band and SXR peak time (tp).

    Parameters
    ----------
    flare_window : pandas.DataFrame
        Lightcurve trimmed to the flare interval (output of extract_flare_window).
    bg : dict
        Background stats per band (output of estimate_background).
    bands : tuple of str
        Energy bands to find onset times for.
        
    Returns
    -------
    dict
        {
            "t0": dict{band: pandas.Timestamp or None},
            "tp": pandas.Timestamp,
            "flux_subtracted": pandas.DataFrame,
        }
    """
    # --- Step 1: Background subtraction ---
        # Subtract the per-band background mean from the raw counts.
        # This gives us the flare's own emission, isolated from the quiet-Sun baseline.
        # We build a new DataFrame rather than modifying flare_window:
    flux_sub = flare_window[["time"]].copy()        # Initialising the new dataframe with a single column "time"
    for band in bands:                              # Filling the "band" columns into the bg subtracted new dataframe 
        flux_sub[band] = flare_window[band] - bg[band]["mean"]

    # --- Step 2: Onset time t0 per band ---
        # The paper defines t0 as the first moment flux exceeds background by 1σ.
        # "Exceeds by 1σ" means: background-subtracted flux > 1 × bg_std.
        # We search forward from the beginning of the flare window.
    t0_per_band = {}
    for band in bands:
        # True where this band's flux clears the 1σ threshold
        above_threshold = flux_sub[band] > bg[band]["std"]

        if above_threshold.any():
            # .idxmax() on a boolean Series returns the index label of the first True
            # (because True(1) > False(0), so the "maximum" is the first True encountered)
            first_idx = above_threshold.idxmax()
            t0_per_band[band] = flux_sub.loc[first_idx, "time"]         # Looks up the first true row index and converts it to a timestamp
        else:
            # Flux never cleared 1σ in this band — flare was undetected here
            t0_per_band[band] = None
    
    # --- Step 3: Peak time tp — SXR band only ---
        # tp is defined as the time of maximum SXR flux within the flare window.
        # qf is evaluated at tp, so this is the single most important timestamp
        # in the whole pipeline.
    peak_idx = flux_sub[SXR_BAND].idxmax()
    tp = flux_sub.loc[peak_idx, "time"]

    return {
        "t0": t0_per_band,
        "tp": tp,
        "flux_subtracted": flux_sub,
    }
