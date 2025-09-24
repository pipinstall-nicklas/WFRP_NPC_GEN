from npc.models import NPC, CareerLevel
from npc.rules import apply_career_levels
from settings import CHAR_BASE, CHAR_PER_LEVEL


def test_apply_career_levels_cumulative():
    """Ensure characteristics and skills accumulate correctly and talents are counted."""
    npc = NPC(name="Test", race="Human")

    # Create three career-levels (levels 1,2,3) that each affect the same char/skill
    cl1 = CareerLevel(career="Engineer", level=1, status="",
                      characteristics=["Ws"], skills=["Climb"], talents=["A"])
    cl2 = CareerLevel(career="Engineer", level=2, status="",
                      characteristics=["Ws"], skills=["Climb"], talents=["A"])
    cl3 = CareerLevel(career="Engineer", level=3, status="",
                      characteristics=["Ws"], skills=["Climb"], talents=["B"])

    apply_career_levels(npc, [cl1, cl2, cl3])

    # Characteristics: starts at CHAR_BASE; rule adds CHAR_PER_LEVEL * level for each CareerLevel
    expected_ws = CHAR_BASE + CHAR_PER_LEVEL * 1 + CHAR_PER_LEVEL * 2 + CHAR_PER_LEVEL * 3
    assert npc.characteristics["Ws"] == expected_ws

    # Skills: start at 0, accumulate level*CHAR_PER_LEVEL per occurrence
    expected_climb = CHAR_PER_LEVEL * (1 + 2 + 3)
    assert npc.skills["Climb"] == expected_climb

    # Talents: duplicates counted
    assert npc.talents["A"] == 2
    assert npc.talents["B"] == 1
