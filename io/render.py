"""Convert NPC dataclass to string components for export."""
from typing import List


def format_characteristics(chars: dict) -> str:
    return ", ".join(f"{k}: {v}" for k, v in chars.items())


def format_skills(skills: dict) -> str:
    items = sorted(skills.items(), key=lambda x: x[0].lower())
    return ", ".join(f"{k} {v}" for k, v in items)


def format_talents(talents: dict) -> str:
    items = sorted(talents.items(), key=lambda x: x[0].lower())
    return ", ".join(f"{k} {v}" if v > 1 else k for k, v in items)
