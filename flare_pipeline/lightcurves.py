"""
Utilities for retrieving STIX quick-look light curves.
"""

from stixdcpy.quicklook import LightCurves
import pandas as pd
from flare_pipeline.config import STIX_BANDS


def get_lightcurve(start_time: str, end_time: str):
    """
    Purpose
    -------
    Download STIX quick-look light curves for a given time interval.

    Parameters
    ----------
    start_time : str
        Start time in ISO UTC format.

    end_time : str
        End time in ISO UTC format.

    returns
    -------
    LightCurves
        STIX LightCurves object.
    """

    return LightCurves.from_sdc(start_time, end_time)


def parse_lightcurve(lightcurve):
    """
    Purpose
    -------
    Convert a STIX lightcurve object into an analysable dataframe.

    Parameters
    ----------
    lightcurve : stixdcpy.quicklook.LightCurves object

    Returns
    -------
    pandas.DataFrame
        (Standardized light curve with UTC timestamps and one column
        for each STIX energy band.)
    """ 
    data = lightcurve.get_data() 
    
    # Reference observation time
    start_time = pd.to_datetime(data["start_utc"])

    # Convert offsets (of 4 sec cadence) into absolute UTC timestamps by adding delta_time to start_utc
    time = start_time + pd.to_timedelta(data["delta_time"], unit="s")
    time = time.floor("s")

    # Construct standard dataframe
    lightcurve_df = pd.DataFrame({
        "time": time,
        "4_10": data["counts"][STIX_BANDS["4_10"]],
        "10_15": data["counts"][STIX_BANDS["10_15"]],
        "15_25": data["counts"][STIX_BANDS["15_25"]],
        "25_50": data["counts"][STIX_BANDS["25_50"]],
        "50_84": data["counts"][STIX_BANDS["50_84"]],
    })
    
    return lightcurve_df


def extract_flare_window(
    lightcurve_df,
    start_time,
    end_time
):
    """
    Purpose
    -------
    Extract the portion of lightcurve corresponding to a flare.

    Parameters
    ----------
    lightcurve_df : pandas.DataFrame
        Parsed STIX light curve.

    start_time : pandas.Timestamp
        Flare start time.

    end_time : pandas.Timestamp
        Flare end time.

    Returns
    -------
    pandas.DataFrame
        Trimmed lightcurve_df restricted to the requested flare window.
    """

    start_time = pd.to_datetime(start_time)
    end_time = pd.to_datetime(end_time)

    flare_window = lightcurve_df[
        (lightcurve_df["time"] >= start_time) &     # Keep only observations between the flare start and end time (Boolean masking).
        (lightcurve_df["time"] <= end_time)
    ].copy()                                        # .copy() creates an independent DataFrame to avoid modifying the original light curve.

    return flare_window