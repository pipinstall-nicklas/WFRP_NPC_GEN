"""Pure rules for merging careers into NPC stats."""
from typing import Iterable
from collections import Counter
from settings import CHAR_BASE, CHAR_PER_LEVEL

CHAR_ORDER = ["Ws", "Bs", "S", "T", "I", "Agi", "Dex", "Int", "Wp", "Fel"]


def apply_career_levels(npc, career_levels: Iterable):
    # ensure base characteristics
    for c in CHAR_ORDER:
        npc.characteristics.setdefault(c, CHAR_BASE)

    for cl in career_levels:
        # apply characteristic increases
        for c in cl.characteristics:
            npc.characteristics[c] = npc.characteristics.get(c, CHAR_BASE) + CHAR_PER_LEVEL * cl.level

        # apply skills
        for s in cl.skills:
            npc.skills[s] = npc.skills.get(s, 0) + CHAR_PER_LEVEL * cl.level

        # apply talents (count duplicates)
        for t in cl.talents:
            npc.talents[t] = npc.talents.get(t, 0) + 1

    # normalize talents to show counts; skills and characteristics remain numeric values
    return npc
