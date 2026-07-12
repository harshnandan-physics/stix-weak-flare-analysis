"""
Central configuration for the project.

Purpose
-------
Store project-wide constants and conventions in one place.
Changing a value here updates the behaviour everywhere.
"""

# -----------------------------------------------------------------------
# STIX Energy Bands (For better readability in accessing lightcurve data)
# -----------------------------------------------------------------------

STIX_BANDS = {
    "4_10": 0,
    "10_15": 1,
    "15_25": 2,
    "25_50": 3,
    "50_84": 4,
}

# --------------------------------------------------
# Energy bands adopted in Awasthi et al. (2021)
# --------------------------------------------------

SXR_BAND = "4_10"
HXR_BAND = "15_25"
