"""Very small Tkinter UI to create a single NPC using minimal inputs."""
import tkinter as tk
from tkinter import ttk
from app.viewmodel import ViewModel
from io_.writer import write_npc


def run_app():
    vm = ViewModel()
    root = tk.Tk()
    root.title("WFRP NPC Gen (minimal)")

    frm = ttk.Frame(root, padding=10)
    frm.grid()

    ttk.Label(frm, text="Name").grid(column=0, row=0)
    name = tk.StringVar()
    ttk.Entry(frm, textvariable=name).grid(column=1, row=0)

    ttk.Label(frm, text="Race").grid(column=0, row=1)
    race = tk.StringVar()
    ttk.Entry(frm, textvariable=race).grid(column=1, row=1)

    ttk.Label(frm, text="Career (name:level)").grid(column=0, row=2)
    career_input = tk.StringVar()
    ttk.Entry(frm, textvariable=career_input, width=40).grid(column=1, row=2)

    # Buttons: start NPC and add career
    def on_start():
        try:
            vm.start_new_npc(name.get(), race.get())
            refresh_summary()
        except Exception as e:
            lbl_status.config(text=f"Error: {e}")

    def on_add_career():
        try:
            added = vm.add_career_str(career_input.get())
            for c in added:
                lb_careers.insert(tk.END, f"{c.career} {c.level}")
            career_input.set("")
            refresh_summary()
        except Exception as e:
            lbl_status.config(text=f"Error: {e}")

    ttk.Button(frm, text="Start NPC", command=on_start).grid(column=0, row=3)
    ttk.Button(frm, text="Add Career", command=on_add_career).grid(column=1, row=3, sticky=tk.W)

    # Listbox to show added careers
    lb_careers = tk.Listbox(frm, height=6, width=40)
    lb_careers.grid(column=0, row=5, columnspan=2)

    # Status and summary labels
    lbl_status = ttk.Label(frm, text="")
    lbl_status.grid(column=0, row=6, columnspan=2)

    lbl_chars = ttk.Label(frm, text="Characteristics: ")
    lbl_chars.grid(column=0, row=7, columnspan=2, sticky=tk.W)

    lbl_skills = ttk.Label(frm, text="Skills: ")
    lbl_skills.grid(column=0, row=8, columnspan=2, sticky=tk.W)

    lbl_talents = ttk.Label(frm, text="Talents: ")
    lbl_talents.grid(column=0, row=9, columnspan=2, sticky=tk.W)

    def refresh_summary():
        s = vm.get_summary()
        lbl_status.config(text=f"NPC: {s['name']} ({s['race']}) Latest: {s['latest_career']} {s['latest_status']}")
        lbl_chars.config(text=f"Characteristics: {s['characteristics'][:200]}")
        lbl_skills.config(text=f"Skills: {s['skills'][:200]}")
        lbl_talents.config(text=f"Talents: {s['talents'][:200]}")

    def on_export():
        try:
            npc = vm.get_current_npc()
            if not npc.name:
                lbl_status.config(text="Error: NPC has no name. Start a new NPC first.")
                return
            # simple filename sanitisation
            filename = f"{npc.name.strip().replace(' ', '_')}.txt"
            path = write_npc(npc, filename)
            lbl_status.config(text=f"Saved: {path}")
        except Exception as e:
            lbl_status.config(text=f"Export error: {e}")

    ttk.Button(frm, text="Export NPC", command=on_export).grid(column=0, row=10)

    root.mainloop()
