"""Schema: expected column names and light parsing helpers."""
import pandas as pd
CAREER_COLS = [
    "Career",
    "Level",
    "Status",
    "Characteristics",
    "Skills",
    "Talents",
]


def split_list(cell: str):
    if not cell or (isinstance(cell, float) and pd.isna(cell)):
        return []
    # Accept comma separated lists
    return [p.strip() for p in str(cell).split(",") if p.strip()]
