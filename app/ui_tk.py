"""Very small Tkinter UI to create a single NPC using minimal inputs.

Includes a talent-selection dialog (user may pick from career talents or write
their own) and an Open Output Folder button.
"""
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from app.viewmodel import ViewModel
from npc.validators import require_at_least_one_talent
from settings import OUTPUT_DIR
from io_.writer import write_npc


def run_app():
    vm = ViewModel()
    root = tk.Tk()
    root.title("WFRP NPC Gen (minimal)")

    frm = ttk.Frame(root, padding=10)
    frm.grid(padx=8, pady=8)

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
            # For each added career level, prompt user to choose talents
            for c in added:
                chosen = ask_talents_dialog(root, c.career, c.level, c.talents)
                # allow user-provided talents (append)
                c.talents = chosen
                display = f"{c.career} {c.level}"
                if c.talents:
                    display += f" - Talents: {', '.join(c.talents)}"
                else:
                    display += " - Talents: (none)"
                lb_careers.insert(tk.END, display)
            career_input.set("")
            refresh_summary()
        except Exception as e:
            lbl_status.config(text=f"Error: {e}")

    ttk.Button(frm, text="Start NPC", command=on_start).grid(column=0, row=3, pady=4)
    ttk.Button(frm, text="Add Career", command=on_add_career).grid(column=1, row=3, sticky=tk.W, pady=4)

    # Listbox to show added careers
    lb_careers = tk.Listbox(frm, height=6, width=40)
    lb_careers.grid(column=0, row=5, columnspan=2)
    # horizontal scrollbar for long career entries
    hscroll = tk.Scrollbar(frm, orient=tk.HORIZONTAL, command=lb_careers.xview)
    lb_careers.configure(xscrollcommand=hscroll.set)
    hscroll.grid(column=0, row=6, columnspan=2, sticky='we')

    # Status and summary labels
    lbl_status = ttk.Label(frm, text="")
    lbl_status.grid(column=0, row=7, columnspan=2)

    # Use small read-only Text widgets with wrapping for long summaries
    txt_chars = tk.Text(frm, height=3, width=60, wrap='word')
    txt_chars.grid(column=0, row=8, columnspan=2, sticky='we')
    txt_chars.configure(state='disabled')

    txt_skills = tk.Text(frm, height=3, width=60, wrap='word')
    txt_skills.grid(column=0, row=9, columnspan=2, sticky='we')
    txt_skills.configure(state='disabled')

    txt_talents = tk.Text(frm, height=2, width=60, wrap='word')
    txt_talents.grid(column=0, row=10, columnspan=2, sticky='we')
    txt_talents.configure(state='disabled')

    def refresh_summary():
        s = vm.get_summary()
        lbl_status.config(text=f"NPC: {s['name']} ({s['race']}) Latest: {s['latest_career']} {s['latest_status']}")
        # update text widgets
        txt_chars.configure(state='normal')
        txt_chars.delete('1.0', tk.END)
        txt_chars.insert(tk.END, s['characteristics'])
        txt_chars.configure(state='disabled')

        txt_skills.configure(state='normal')
        txt_skills.delete('1.0', tk.END)
        txt_skills.insert(tk.END, s['skills'])
        txt_skills.configure(state='disabled')

        txt_talents.configure(state='normal')
        txt_talents.delete('1.0', tk.END)
        txt_talents.insert(tk.END, s['talents'])
        txt_talents.configure(state='disabled')

    def on_export():
        try:
            npc = vm.get_current_npc()
            if not npc.name:
                lbl_status.config(text="Error: NPC has no name. Start a new NPC first.")
                return
            # Ensure each career level has at least one talent
            missing = [f"{cl.career} {cl.level}" for cl in npc.careers if not require_at_least_one_talent(cl)]
            if missing:
                proceed = messagebox.askyesno("Missing talents",
                                              f"The following career levels have no talents:\n{', '.join(missing)}\n\nProceed with export anyway?")
                if not proceed:
                    lbl_status.config(text="Export cancelled: missing talents")
                    return
            # simple filename sanitisation
            filename = f"{npc.name.strip().replace(' ', '_')}.txt"
            path = write_npc(npc, filename)
            lbl_status.config(text=f"Saved: {path}")
        except Exception as e:
            lbl_status.config(text=f"Export error: {e}")

    ttk.Button(frm, text="Export NPC", command=on_export).grid(column=0, row=10, pady=6)
    def on_open_output():
        out = Path(OUTPUT_DIR)
        out.mkdir(parents=True, exist_ok=True)
        try:
            # macOS open command
            subprocess.run(["open", str(out)])
        except Exception:
            messagebox.showinfo("Open Folder", f"Output folder: {out}")

    ttk.Button(frm, text="Open Output Folder", command=on_open_output).grid(column=1, row=10, pady=6)

    def on_undo():
        removed = vm.undo_last_career()
        if not removed:
            lbl_status.config(text="Nothing to undo")
            return
        # remove items from listbox equal to number removed
        for _ in range(len(removed)):
            if lb_careers.size() > 0:
                lb_careers.delete(tk.END)
        refresh_summary()
        lbl_status.config(text=f"Undid: {', '.join(f'{c.career} {c.level}' for c in removed)}")

    def on_history():
        # show history groups with Undo buttons
        dlg = tk.Toplevel(root)
        dlg.title("History")
        frame = ttk.Frame(dlg, padding=8)
        frame.pack(fill='both', expand=True)
        for i, group in enumerate(list(vm._history)):
            row = i
            lbl = ttk.Label(frame, text=f"Group {i+1}: " + ", ".join(f"{c.career} {c.level}" for c in group))
            lbl.grid(column=0, row=row, sticky='w', pady=2)
            def make_undo(idx):
                def _undo():
                    removed = vm.undo_history_index(idx)
                    # refresh careers listbox to reflect current career_levels
                    lb_careers.delete(0, tk.END)
                    for c in vm.career_levels:
                        display = f"{c.career} {c.level}"
                        if c.talents:
                            display += f" - Talents: {', '.join(c.talents)}"
                        else:
                            display += " - Talents: (none)"
                        lb_careers.insert(tk.END, display)
                    refresh_summary()
                    messagebox.showinfo("Undo", f"Undid: {', '.join(f'{c.career} {c.level}' for c in removed)}")
                return _undo
            btn = ttk.Button(frame, text="Undo Group", command=make_undo(i))
            btn.grid(column=1, row=row, padx=6)

    ttk.Button(frm, text="Undo Last", command=on_undo).grid(column=0, row=11, pady=4)
    ttk.Button(frm, text="History", command=on_history).grid(column=1, row=11, pady=4)

    def on_details():
        s = vm.get_summary()
        dlg = tk.Toplevel(root)
        dlg.title("NPC Details")
        dlg.geometry('700x400')
        txt = tk.Text(dlg, wrap='word')
        txt.pack(fill='both', expand=True)
        txt.insert(tk.END, f"Name: {s['name']}\n")
        txt.insert(tk.END, f"Race: {s['race']}\n")
        txt.insert(tk.END, f"Latest: {s['latest_career']} {s['latest_status']}\n\n")
        txt.insert(tk.END, "Characteristics:\n" + s['characteristics'] + "\n\n")
        txt.insert(tk.END, "Skills:\n" + s['skills'] + "\n\n")
        txt.insert(tk.END, "Talents:\n" + s['talents'] + "\n\n")
        txt.insert(tk.END, "Careers:\n" + "\n".join(f"{c[0]} {c[1]}" for c in s['careers']))
        txt.configure(state='disabled')

    ttk.Button(frm, text="Details", command=on_details).grid(column=0, row=11)

    root.mainloop()


def ask_talents_dialog(parent, career: str, level: int, options: list):
    """Modal dialog allowing selection of talents or entering custom ones.

    Returns a list of chosen talent strings (must be at least one).
    """
    sel = []

    dlg = tk.Toplevel(parent)
    dlg.title(f"Choose talents for {career} {level}")
    dlg.transient(parent)
    dlg.grab_set()

    ttk.Label(dlg, text=f"Available talents for {career} {level} (select one or more):").grid(column=0, row=0, columnspan=3, sticky=tk.W)

    lb = tk.Listbox(dlg, selectmode=tk.MULTIPLE, width=50, height=8)
    lb.grid(column=0, row=1, columnspan=3)
    for o in options:
        if o:
            lb.insert(tk.END, o)

    ttk.Label(dlg, text="Or write your own:").grid(column=0, row=2, sticky=tk.W)
    entry = tk.StringVar()
    ttk.Entry(dlg, textvariable=entry, width=40).grid(column=0, row=3, columnspan=2, sticky=tk.W)

    def on_add_custom():
        v = entry.get().strip()
        if v:
            lb.insert(tk.END, v)
            entry.set("")

    def on_ok():
        selections = [lb.get(i) for i in lb.curselection()]
        if not selections:
            proceed = messagebox.askyesno("No talents selected",
                                          "You have not selected any talents for this career level. Proceed without talents?")
            if not proceed:
                return
        nonlocal sel
        sel = selections
        dlg.destroy()

    def on_cancel():
        dlg.destroy()

    ttk.Button(dlg, text="Add", command=on_add_custom).grid(column=2, row=3)
    ttk.Button(dlg, text="OK", command=on_ok).grid(column=0, row=4)
    ttk.Button(dlg, text="Cancel", command=on_cancel).grid(column=1, row=4)

    parent.wait_window(dlg)
    return sel

    root.mainloop()
