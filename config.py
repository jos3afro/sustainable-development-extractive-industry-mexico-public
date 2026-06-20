"""
Project root configuration — set ROOT to your local clone path.
Import this at the top of every Python script:
    from config import ROOT
Then replace hardcoded paths like:
    r'C:/Users/Jos3/Documents/Mexico/Censo2020/Minex_data.csv'
with:
    ROOT / 'Censo2020' / 'Minex_data.csv'
"""
from pathlib import Path

# ── Set this to wherever you cloned the repo ──────────────────────────────────
ROOT = Path(__file__).resolve().parent
# ──────────────────────────────────────────────────────────────────────────────

# Convenience sub-paths
CENSO1990  = ROOT / "Censo1990"
CENSO2000  = ROOT / "Censo2000"
CENSO2010  = ROOT / "Censo2010"
CENSO2020  = ROOT / "Censo2020"
CLEANIN    = ROOT / "Cleanin"
CORE       = ROOT / "Core"
NDVI_DIR   = ROOT / "NDVI"
LANDUSE    = ROOT / "LandUse"
RESULTS    = ROOT / "Results"
