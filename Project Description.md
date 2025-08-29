

A lightweight desktop application for quickly creating  **NPCs for Warhammer Fantasy Roleplay 4th Edition (WFRP4E)** .

The tool streamlines NPC creation by loading career and skill data from a spreadsheet and presenting it in a simple **Tkinter-based GUI** — so you don’t need to touch the terminal.

## Features (MVP)

* **Spreadsheet-driven data** : Careers, skills, and characteristics are pulled from a structured Excel/CSV file. (WFRP_NPC_GEN_DF_final folder at the moment)
* **Career-based NPC creation** : Type in a career name and level, and the program will:
* Automatically add all relevant skills.
* Apply the correct characteristic advances.
* Prompt the user to select at least one talent.
* **Multi-career progression** : Stack multiple careers and levels to build more advanced characters.
* **GUI interface** : Simple Tkinter interface — no command line required.

## Planned Features (Future Roadmap)

* **Race integration** : Automatically apply racial traits and modifiers.
* **Random stats** : Generate characteristics using dice formulas (e.g. 20 + 2d10).
* **Quick NPC generation** : Randomly roll complete NPCs with less than five clicks.
* **PC generation** : Expand functionality for creating full Player Characters.

## Intended Audience

Originally designed for a private WFRP4E campaign, this tool may also serve GMs and fans of the system who want a fast, no-frills NPC generator.

## Tech Stack (Expected, not required)

* **Python 3** (Preferably the only language required)
* **Tkinter** (GUI)
* **Pandas** (spreadshet integration)

## File Structure

wfrp-npc-gen/
├─ main.py                     # Tiny entrypoint: launches Tkinter UI
├─ settings.py                 # Paths & app settings (e.g., OUTPUT_DIR)
├─ data/
│  ├─ loader.py                # Read/validate spreadsheet -> in-memory models
│  └─ schema.py                # Column names, parsers, light validators
├─ npc/
│  ├─ models.py                # Dataclasses: Career, CareerLevel, NPC, etc.
│  ├─ rules.py                 # Pure “rules” funcs (merge careers, apply advances)
│  ├─ generator.py             # Orchestrates: careers in -> NPC out
│  └─ validators.py            # Business rules (≥1 talent, valid levels, etc.)
├─ pc/                         # (empty for now) future Player Character logic
│  └─ __init__.py
├─ app/
│  ├─ ui_tk.py                 # Tkinter screens/widgets (View)
│  └─ viewmodel.py             # Glue between UI and pure logic (ViewModel)
├─ io/
│  ├─ writer.py                # TXT exporter to WFRP_NPC_OUTPUT/
│  └─ render.py                # Converts NPC dataclass -> strings (no I/O)
├─ templates/
│  └─ npc_text.txt             # Simple format string for the TXT export
├─ tests/                      # (optional) tiny pytest sanity checks
│  ├─ test_rules.py
│  └─ test_loader.py
└─ WFRP_NPC_OUTPUT/            # (existing) generated .txt files land here

* **Pure core** (models/rules/generator) is independent of UI & disk → easy to test and reuse (later CLI/web).
* **UI = thin** : Tkinter only collects input and displays output. No rules in callbacks.
* **I/O isolated** : One small writer module. Easy to swap TXT → Markdown/HTML later.
* **Data layer** is a single choke point (loader) so your spreadsheet can evolve without touching rules/GUI.


## Abstract

On execution GUI opens up that allows user to see names of NPCs in WFRP_NPC_ouput, as well as create new NPCs and some basic configs. On click new it should present options NPC, Quick NPC, PC (but we will only work on NPC for now!). Pressing NPC takes us into the main creation workflow. The app should read from the data, and allow User to Give a name and a Race for the NPC, as well as searching in 'Career'. On selection of any given career it should give 5(+5 for every level) in the associated characteristics and Skills. Users should also be presented with an option to choose at least 1 of the associated talents. If selecting a Career in a higher level, it should complete the same logic for previous levels, So selecting Engineer 3 should give +5 to characteristics and skills in Engineer 1, and +10 in the associated statistics in engineer 2, and +15 in engineer 3, all the while asking to pick talents at every tier. If possible, make the interface intuitive enough such that users can see the choices they've made so far. When the user is done, allow them to save the character and export it to WFRP_NPC_ouput.


### Character formatting

Name: Display the Written Name

Race: Display the Race (perhaps integrated from Race_and_Origin in Races-Table.csv)

Latest Career: Display the name of the last career

Latest Status: Display the Status of the last career

Characteristics: the characteristics are Ws Bs S T I Agi Dex Int Wp Fel. For now, have all get a base value of 30. They should increase cumulatively with career choices!

Skills: Display a list of total associated comma seperated skills in alphabetical order. Every skill should be formatted like ' [Name][Value],' //No duplicates and no overwrites! They should increase cumulatively with career choices!

Talents: Display a list of total associated comma seperated talents in alphabetical order. No Overwrites! If there are duplicates, instead delete potential copies and display a value on the original, such that a list like 'A, B, B, C' becomes 'A, B 2, C'.
