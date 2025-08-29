"""Glue layer between UI and generator.

Provides an incremental API used by the Tk UI: start a new NPC, add careers one
by one (expands from CSV), and obtain live formatted summary. Supports undoing
last group of career additions.
"""
from typing import List

from npc.generator import build_npc
from npc.models import CareerLevel, NPC
from data.loader import get_career_levels
from io_.render import format_characteristics, format_skills, format_talents


class ViewModel:
    def __init__(self):
        self.reset()

    def reset(self):
        self.name = ""
        self.race = ""
        self.career_levels: List[CareerLevel] = []
        # history stores groups of CareerLevel objects added together
        self._history: List[List[CareerLevel]] = []

    def start_new_npc(self, name: str, race: str):
        if not name:
            raise ValueError("Name required")
        self.name = name
        self.race = race
        self.career_levels = []
        self._history = []

    def add_career_str(self, career_input: str) -> List[CareerLevel]:
        """Add a career string like 'Engineer:2' or 'Smith' and return the added rows.

        Multiple comma-separated entries are allowed and all of them are recorded
        as a single history group for undo.
        """
        parts = [p.strip() for p in career_input.split(",") if p.strip()]
        added: List[CareerLevel] = []
        for p in parts:
            if ":" in p:
                career, lvl = [x.strip() for x in p.split(":", 1)]
                try:
                    lvl = int(lvl)
                except ValueError:
                    lvl = 1
            else:
                career = p
                lvl = 1

            expanded = get_career_levels(career, lvl)
            if not expanded:
                cl = CareerLevel(career=career, level=lvl, status="")
                self.career_levels.append(cl)
                added.append(cl)
            else:
                self.career_levels.extend(expanded)
                added.extend(expanded)

        if added:
            self._history.append(added.copy())
        return added

    def undo_last_career(self) -> List[CareerLevel]:
        """Undo the last group of career-level additions and return the removed list."""
        if not self._history:
            return []
        last_group = self._history.pop()
        # remove the same number of items from the end
        for _ in range(len(last_group)):
            if self.career_levels:
                self.career_levels.pop()
        return last_group

    def undo_history_index(self, index: int) -> List[CareerLevel]:
        """Undo a history group at a specific index (0-based).

        Removes those exact CareerLevel objects from the current career_levels
        list and deletes the history entry. Returns the removed group.
        """
        if index < 0 or index >= len(self._history):
            return []
        group = self._history.pop(index)
        # remove each object by identity from career_levels
        for cl in group:
            try:
                self.career_levels.remove(cl)
            except ValueError:
                # already removed or not present; ignore
                pass
        return group

    def get_current_npc(self) -> NPC:
        return build_npc(self.name or "", self.race or "", self.career_levels)

    def get_summary(self):
        npc = self.get_current_npc()
        return {
            "name": npc.name,
            "race": npc.race,
            "latest_career": npc.latest_career(),
            "latest_status": npc.latest_status(),
            "characteristics": format_characteristics(npc.characteristics),
            "skills": format_skills(npc.skills),
            "talents": format_talents(npc.talents),
            "careers": [(c.career, c.level) for c in npc.careers],
        }
