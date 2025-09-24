"""Load CSV data into simple Python structures using pandas.

This loader understands the semicolon-delimited CSV found in the project
(`Careers-...csv`) and exposes a small helper to get CareerLevel objects
for a career up to a requested level.
"""
from pathlib import Path
import pandas as pd
from typing import Dict, List

from settings import DATA_DIR, CAREERS_CSV, RACES_CSV, TALENTS_CSV
from npc.models import CareerLevel


def _read_csv(name: str, sep=",") -> pd.DataFrame:
    path = Path(DATA_DIR) / name
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")
    return pd.read_csv(path, sep=sep)


def load_careers() -> pd.DataFrame:
    # the careers CSV in the repo uses semicolons as separators
    df = _read_csv(CAREERS_CSV, sep=";")
    # Normalize column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    return df


def load_races() -> pd.DataFrame:
    return _read_csv(RACES_CSV, sep=";")


def load_talents() -> pd.DataFrame:
    return _read_csv(TALENTS_CSV, sep=";")


def get_career_levels(career_name: str, upto_level: int) -> List[CareerLevel]:
    """Return a list of CareerLevel objects for `career_name` for levels 1..upto_level.

    The CSV stores each career-level on a separate row like "Engineer 1", "Engineer 2".
    This helper will match rows whose 'Career' starts with the given name and extract
    Characteristics, Skills and Talents columns (splitting comma lists).
    """
    df = load_careers()
    # career_name could be like 'Engineer' and CSV has 'Engineer 1' etc.
    matched = df[df['Career'].str.startswith(career_name)]
    results: List[CareerLevel] = []
    for _, row in matched.iterrows():
        # attempt to parse level from the career string e.g. 'Engineer 2'
        parts = str(row['Career']).rsplit(' ', 1)
        lvl = 1
        if len(parts) == 2 and parts[1].isdigit():
            lvl = int(parts[1])
        if lvl <= upto_level:
            # split semicolon CSV fields (they themselves use commas to separate lists)
            chars = [c.strip() for c in str(row.get('Characteristics', '')).split(',') if c.strip()]
            skills = [s.strip() for s in str(row.get('Skills', '')).split(',') if s.strip()]
            talents = [t.strip() for t in str(row.get('Talents', '')).split(',') if t.strip()]
            status = str(row.get('Status', '')).strip()
            results.append(CareerLevel(career=career_name, level=lvl, status=status,
                                       characteristics=chars, skills=skills, talents=talents))
    # sort by level
    results.sort(key=lambda c: c.level)
    return results


def get_career_names() -> List[str]:
    """Return a sorted list of unique base career names (without numeric level suffix).

    Example: if CSV contains 'Watchman 1', 'Watchman 2', this will return ['Watchman'].
    """
    df = load_careers()
    names = []
    for val in df['Career'].astype(str).tolist():
        # split off trailing level if present
        base = val.rsplit(' ', 1)[0] if val.rsplit(' ', 1)[-1].isdigit() else val
        names.append(base.strip())
    # unique + sort
    unique = sorted(set([n for n in names if n]))
    return unique
