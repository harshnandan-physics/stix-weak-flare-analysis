"""
Module:
    data.py

Purpose:
    Data acquisition utilities for STIX observations.

Responsibilities:
    - Retrieve flare catalogs
    - Download STIX products

Project:
    HXR-rich Weak Solar Flares
"""

from stixdcpy.net import Request
from stixdcpy.quicklook import LightCurves


def get_flare_catalog(start_time: str, end_time: str) -> list:
    """
    Retrieve the STIX flare catalog for a given time interval.

    Args:
        start_time: Observation start time in ISO UTC format.
        end_time: Observation end time in ISO UTC format.

    Returns:
        List of flare records from the STIX Data Center.
    """

    if not isinstance(start_time, str):
        raise TypeError("start_time must be a string.")

    if not isinstance(end_time, str):
        raise TypeError("end_time must be a string.")

    flares = Request.fetch_flare_list(start_time, end_time)

    return flares
