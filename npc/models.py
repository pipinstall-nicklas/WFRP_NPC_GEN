"""Dataclasses for NPC model."""
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class CareerLevel:
    career: str
    level: int
    status: str
    characteristics: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    talents: List[str] = field(default_factory=list)


@dataclass
class NPC:
    name: str
    race: str
    careers: List[CareerLevel] = field(default_factory=list)
    characteristics: Dict[str, int] = field(default_factory=dict)
    skills: Dict[str, int] = field(default_factory=dict)
    talents: Dict[str, int] = field(default_factory=dict)

    def latest_career(self):
        if not self.careers:
            return ""
        return self.careers[-1].career

    def latest_status(self):
        if not self.careers:
            return ""
        return self.careers[-1].status
