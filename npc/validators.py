"""Simple validators for business rules."""
from typing import List


def require_at_least_one_talent(career_level) -> bool:
    return bool(career_level.talents)


def validate_levels(levels: List[int]) -> bool:
    return all(isinstance(l, int) and l > 0 for l in levels)
