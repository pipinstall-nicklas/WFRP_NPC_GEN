"""Write NPC to a text file using the simple template in templates/npc_text.txt."""
from pathlib import Path
from settings import OUTPUT_DIR
from io_.render import format_characteristics, format_skills, format_talents


TEMPLATE_PATH = Path(__file__).parent.parent / "templates" / "npc_text.txt"


def write_npc(npc, filename: str):
    out_dir = Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / filename
    with open(TEMPLATE_PATH, "r") as t:
        tpl = t.read()

    body = tpl.format(
        name=npc.name,
        race=npc.race,
        latest_career=npc.latest_career(),
        latest_status=npc.latest_status(),
        characteristics=format_characteristics(npc.characteristics),
        skills=format_skills(npc.skills),
        talents=format_talents(npc.talents),
    )

    with open(path, "w") as f:
        f.write(body)

    return path
