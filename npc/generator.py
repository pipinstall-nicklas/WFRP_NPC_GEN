"""Orchestrate building an NPC from career selections."""
from .models import NPC, CareerLevel
from .rules import apply_career_levels


def build_npc(name: str, race: str, career_levels: list[CareerLevel]) -> NPC:
    npc = NPC(name=name, race=race)
    npc.careers = career_levels
    apply_career_levels(npc, career_levels)
    return npc
