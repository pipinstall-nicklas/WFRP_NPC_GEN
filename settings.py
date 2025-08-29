"""
Simple settings for paths and defaults.
"""
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "NPC Gen" / "WFRP_NPC_GEN_DF_final"
OUTPUT_DIR = ROOT / "WFRP_NPC_output"

# Base characteristic value and increment per level
CHAR_BASE = 30
CHAR_PER_LEVEL = 5

# Expected CSV filenames (best-effort)
CAREERS_CSV = "Careers-WFRP_NPC_GEN_DF_Careers.csv"
RACES_CSV = "Races-Table 1.csv"
TALENTS_CSV = "Random_Talents-Table 1.csv"

# UI theming defaults (can be changed at runtime via the Config dialog)
# Theme names can be listed at runtime via ttk.Style().theme_names()
DEFAULT_THEME = "clam"
# Accent color used for enhanced styling (hex string)
ACCENT_COLOR = "#4f94d4"
