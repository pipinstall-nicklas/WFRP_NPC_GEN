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
import settings
from settings import OUTPUT_DIR, DEFAULT_THEME, ACCENT_COLOR
from io_.writer import write_npc
import json


def run_app():
    vm = ViewModel()
    root = tk.Tk()
    root.title("WFRP NPC Gen (minimal)")
    # sensible minimum size to keep layout usable
    try:
        root.minsize(800, 600)
    except Exception:
        pass

    # apply theme and basic styling
    style = ttk.Style(root)
    # load persisted config if present
    cfg_path = settings.ROOT / 'app_config.json'
    if cfg_path.exists():
        try:
            with open(cfg_path, 'r', encoding='utf-8') as fh:
                cfg = json.load(fh)
            # apply persisted output dir
            if 'output_dir' in cfg:
                try:
                    settings.OUTPUT_DIR = cfg['output_dir']
                except Exception:
                    pass
            # apply persisted theme
            if 'theme' in cfg:
                try:
                    style.theme_use(cfg['theme'])
                except Exception:
                    pass
            else:
                try:
                    style.theme_use(DEFAULT_THEME)
                except Exception:
                    pass
            # apply persisted accent
            if 'accent' in cfg:
                try:
                    style.configure('Accent.TLabel', background=cfg['accent'])
                    style.configure('Accent.TButton', foreground='white', background=cfg['accent'])
                except Exception:
                    pass
        except Exception:
            try:
                style.theme_use(DEFAULT_THEME)
            except Exception:
                pass
    else:
        try:
            style.theme_use(DEFAULT_THEME)
        except Exception:
            pass

    frm = ttk.Frame(root, padding=10)
    frm.grid(sticky='nsew', padx=8, pady=8)
    # allow the main window to resize and let the frame expand
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # --- Front page frame ---
    front = ttk.Frame(root, padding=12)
    def show_front():
        builder_frame.grid_remove()
        front.grid()

    def show_builder():
        front.grid_remove()
        builder_frame.grid()

    # Big buttons with simple styling
    ttk.Label(front, text="WFRP NPC Generator", font="Helvetica 18 bold").grid(column=0, row=0, pady=8)
    ttk.Button(front, text="Create NPC", command=show_builder, width=30).grid(column=0, row=1, pady=6)
    
    def open_output():
        out = Path(OUTPUT_DIR)
        out.mkdir(parents=True, exist_ok=True)
        try:
            subprocess.run(["open", str(out)])
        except Exception:
            messagebox.showinfo("Output Folder", f"Output: {out}")
    ttk.Button(front, text="Open Output Folder", command=open_output, width=30).grid(column=0, row=2, pady=6)

    def open_config():
        dlg = tk.Toplevel(root)
        dlg.title('Config')
        dlg.transient(root)
        ttk.Label(dlg, text='Output folder:').grid(column=0, row=0, sticky='w')
        outvar = tk.StringVar(value=str(Path(OUTPUT_DIR)))
        ttk.Entry(dlg, textvariable=outvar, width=60).grid(column=0, row=1, sticky='w')

        # Theme selection
        ttk.Label(dlg, text='Theme:').grid(column=0, row=2, sticky='w', pady=(8,0))
        theme_var = tk.StringVar(value=style.theme_use())
        themes = style.theme_names()
        theme_combo = ttk.Combobox(dlg, textvariable=theme_var, values=themes, state='readonly')
        theme_combo.grid(column=0, row=3, sticky='w')

        # Accent color (used for some widget highlights)
        ttk.Label(dlg, text='Accent color (hex):').grid(column=0, row=4, sticky='w', pady=(8,0))
        accent_var = tk.StringVar(value=str(ACCENT_COLOR))
        ttk.Entry(dlg, textvariable=accent_var, width=20).grid(column=0, row=5, sticky='w')

        def save():
            try:
                import settings as _s
                _s.OUTPUT_DIR = outvar.get()
                # apply theme immediately
                try:
                    style.theme_use(theme_var.get())
                except Exception:
                    pass
                # update simple accent style for Labels and Buttons
                try:
                    accent = accent_var.get()
                    style.configure('Accent.TLabel', background=accent)
                    style.configure('Accent.TButton', foreground='white', background=accent)
                except Exception:
                    pass
                # persist configuration to disk
                try:
                    cfg = {
                        'output_dir': outvar.get(),
                        'theme': theme_var.get(),
                        'accent': accent_var.get(),
                    }
                    with open(cfg_path, 'w', encoding='utf-8') as fh:
                        json.dump(cfg, fh, indent=2)
                except Exception:
                    # non-fatal; continue
                    pass
                dlg.destroy()
            except Exception as e:
                messagebox.showerror('Config', f'Could not set output: {e}')

        ttk.Button(dlg, text='Save', command=save).grid(column=0, row=6, pady=6)
    ttk.Button(front, text="Config", command=open_config, width=30).grid(column=0, row=3, pady=6)
    ttk.Button(front, text="Exit", command=root.destroy, width=30).grid(column=0, row=4, pady=6)

    front.grid()

    # --- Builder frame (the previous main UI) ---
    builder_frame = ttk.Frame(root, padding=10)
    # make builder_frame expand when shown
    builder_frame.grid(sticky='nsew')
    builder_frame.columnconfigure(0, weight=0)
    builder_frame.columnconfigure(1, weight=1)
    builder_frame.columnconfigure(2, weight=0)
    # rows that can expand when window is resized
    builder_frame.rowconfigure(5, weight=1)   # listbox
    builder_frame.rowconfigure(8, weight=1)   # characteristics text
    builder_frame.rowconfigure(9, weight=1)   # skills text

    ttk.Label(builder_frame, text="Name").grid(column=0, row=0)
    name = tk.StringVar()
    ttk.Entry(builder_frame, textvariable=name).grid(column=1, row=0)

    # Return to front page (top-right)
    ttk.Button(builder_frame, text="Return", command=show_front).grid(column=2, row=0, padx=6, sticky=tk.E)

    ttk.Label(builder_frame, text="Race").grid(column=0, row=1)
    race = tk.StringVar()
    ttk.Entry(builder_frame, textvariable=race).grid(column=1, row=1)

    ttk.Label(builder_frame, text="Career (name:level)").grid(column=0, row=2)
    career_input = tk.StringVar()

    # Searchable combobox: suggestions supplied from data.loader.get_career_names()
    try:
        from tkinter import StringVar
        from tkinter.ttk import Combobox
        from data.loader import get_career_names

        all_careers = []
        try:
            all_careers = get_career_names()
        except Exception:
            all_careers = []

        combo = Combobox(builder_frame, textvariable=career_input, values=all_careers, width=40)
        combo.grid(column=1, row=2)

        def update_career_suggestions(event=None):
            q = career_input.get().strip()
            if not q:
                combo['values'] = all_careers
                return
            qlow = q.lower()
            # word-start matches first, then substring matches
            word_start = [c for c in all_careers if any(part.lower().startswith(qlow) for part in c.split())]
            substr = [c for c in all_careers if qlow in c.lower() and c not in word_start]
            results = word_start + substr
            # if the user included a numeric level like 'Watchman 3', keep that string in the box
            combo['values'] = results

        # update suggestions while typing
        combo.bind('<KeyRelease>', update_career_suggestions)
    except Exception:
        # fallback to plain Entry if Combobox or loader not available
        ttk.Entry(builder_frame, textvariable=career_input, width=40).grid(column=1, row=2)

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

            # Open a combined multi-level dialog to select talents for each added level
            selections = ask_talents_multi_dialog(root, added)
            if selections is None:
                # user cancelled the multi-level talent selection -> undo the added career levels
                vm.undo_last_career()
                lbl_status.config(text="Career addition cancelled")
            else:
                # assign chosen talents for each career level and display
                for c, chosen in zip(added, selections):
                    c.talents = chosen
                    display = f"{c.career} {c.level}"
                    if c.talents:
                        display += f" - Talents: {', '.join(c.talents)}"
                    else:
                        display += " - Talents: (none)"
                    lb_careers.insert(tk.END, display)
                career_input.set("")
                refresh_summary()
                lbl_status.config(text=f"Added: {', '.join(f'{c.career} {c.level}' for c in added)}")
        except Exception as e:
            lbl_status.config(text=f"Error: {e}")

    ttk.Button(builder_frame, text="Start NPC", command=on_start).grid(column=0, row=3, pady=4)
    ttk.Button(builder_frame, text="Add Career", command=on_add_career).grid(column=1, row=3, sticky=tk.W, pady=4)

    # Listbox to show added careers (expandable)
    lb_careers = tk.Listbox(builder_frame, height=6, exportselection=False)
    lb_careers.grid(column=0, row=5, columnspan=3, sticky='nsew', padx=4, pady=4)
    # horizontal scrollbar for long career entries (attached to builder_frame)
    hscroll = tk.Scrollbar(builder_frame, orient=tk.HORIZONTAL, command=lb_careers.xview)
    lb_careers.configure(xscrollcommand=hscroll.set)
    hscroll.grid(column=0, row=6, columnspan=3, sticky='we')

    # Status and summary labels
    lbl_status = ttk.Label(builder_frame, text="")
    # apply accent style if available
    try:
        style.configure('Accent.TLabel')
        lbl_status = ttk.Label(builder_frame, text="", style='Accent.TLabel')
    except Exception:
        lbl_status = ttk.Label(builder_frame, text="")
    lbl_status.grid(column=0, row=7, columnspan=3, sticky='we', pady=(4,2))

    # Use small read-only Text widgets with wrapping for long summaries
    txt_chars = tk.Text(builder_frame, height=3, width=60, wrap='word')
    txt_chars.grid(column=0, row=8, columnspan=3, sticky='nsew')
    txt_chars.configure(state='disabled')

    txt_skills = tk.Text(builder_frame, height=3, width=60, wrap='word')
    txt_skills.grid(column=0, row=9, columnspan=3, sticky='nsew')
    txt_skills.configure(state='disabled')

    txt_talents = tk.Text(builder_frame, height=2, width=60, wrap='word')
    txt_talents.grid(column=0, row=10, columnspan=3, sticky='nsew')
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

    # Controls frame placeholder (created later when callbacks exist)

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

    # legacy placement removed; buttons are in controls frame
    def on_open_output():
        out = Path(OUTPUT_DIR)
        out.mkdir(parents=True, exist_ok=True)
        try:
            # macOS open command
            subprocess.run(["open", str(out)])
        except Exception:
            messagebox.showinfo("Open Folder", f"Output folder: {out}")

    # legacy placement removed; buttons are in controls frame

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

    # Details button moved to controls frame
    # Create controls frame now that callbacks exist so commands are bound correctly
    controls = ttk.Frame(builder_frame)
    controls.grid(column=0, row=11, columnspan=3, sticky='we', pady=(8,4))
    controls.columnconfigure(0, weight=1)
    # place buttons inside controls (left-aligned)
    btn_export = ttk.Button(controls, text="Export NPC", command=on_export)
    btn_export.pack(side='left', padx=6)
    btn_open = ttk.Button(controls, text="Open Output Folder", command=on_open_output)
    btn_open.pack(side='left', padx=6)
    btn_undo = ttk.Button(controls, text="Undo Last", command=on_undo)
    btn_undo.pack(side='left', padx=6)
    btn_history = ttk.Button(controls, text="History", command=on_history)
    btn_history.pack(side='left', padx=6)
    btn_details = ttk.Button(controls, text="Details", command=on_details)
    btn_details.pack(side='left', padx=6)

    # Start with front page visible
    builder_frame.grid_remove()
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

    lb = tk.Listbox(dlg, selectmode=tk.MULTIPLE, width=50, height=8, exportselection=False)
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
            # auto-select the newly added custom talent so OK will pick it
            lb.selection_clear(0, tk.END)
            lb.selection_set(tk.END)
            entry.set("")

    def on_ok():
        selections = [lb.get(i) for i in lb.curselection()]
        # If there are no explicit selections and there are available options,
        # require the user to select at least one talent. If the options list is
        # empty (career level has no talents), allow the user to explicitly
        # confirm proceeding without talents.
        has_options = lb.size() > 0
        if not selections:
            if has_options:
                messagebox.showwarning("No talents selected",
                                       "Please select at least one talent or add a custom one for this career level.")
                return
            else:
                # No options available; ask explicit confirmation to proceed
                proceed = messagebox.askyesno("No talents available",
                                              "This career level has no listed talents. Proceed without talents?")
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


def ask_talents_multi_dialog(parent, career_levels: list):
    """Show a combined modal dialog allowing talent selection for multiple career levels.

    Returns a list of lists of chosen talents (same order as career_levels), or
    None if the user cancels the whole operation.
    """
    dlg = tk.Toplevel(parent)
    dlg.title("Choose talents for career levels")
    dlg.transient(parent)
    dlg.grab_set()

    frame = ttk.Frame(dlg, padding=10)
    frame.grid(sticky='nsew')
    dlg.columnconfigure(0, weight=1)
    dlg.rowconfigure(0, weight=1)

    # Canvas+scrollbar to host many collapsible sections
    canvas = tk.Canvas(frame, borderwidth=0, highlightthickness=0)
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
    scrollable = ttk.Frame(canvas)
    inner_id = canvas.create_window((0, 0), window=scrollable, anchor='nw')

    def _on_frame_config(event):
        canvas.configure(scrollregion=canvas.bbox('all'))

    scrollable.bind('<Configure>', _on_frame_config)

    def _on_mousewheel(event):
        # cross-platform delta
        delta = 0
        if event.num == 5 or event.delta < 0:
            delta = 1
        elif event.num == 4 or event.delta > 0:
            delta = -1
        canvas.yview_scroll(delta, 'units')

    # bind mousewheel both at canvas and on the scrollable frame
    canvas.bind_all('<MouseWheel>', _on_mousewheel)
    canvas.bind_all('<Button-4>', _on_mousewheel)
    canvas.bind_all('<Button-5>', _on_mousewheel)

    canvas.grid(column=0, row=0, sticky='nsew')
    scrollbar.grid(column=1, row=0, sticky='ns')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    # Collapsible section helper
    class CollapsibleSection(ttk.Frame):
        def __init__(self, parent, title):
            super().__init__(parent)
            self.columnconfigure(0, weight=1)
            hdr = ttk.Frame(self)
            hdr.grid(column=0, row=0, sticky='we')
            self._open = tk.BooleanVar(value=True)
            btn = ttk.Checkbutton(hdr, text=title, variable=self._open, style='Toolbutton')
            btn.pack(side='left', fill='x', expand=True)
            self.body = ttk.Frame(self)
            self.body.grid(column=0, row=1, sticky='we', pady=(4, 8))

        def is_open(self):
            return self._open.get()

    # For each career level create a collapsible section containing Listbox and custom entry
    listboxes = []
    entries = []
    for idx, cl in enumerate(career_levels):
        sec = CollapsibleSection(scrollable, f"{cl.career} {cl.level}  ({cl.status})")
        sec.grid(column=0, row=idx, sticky='we', pady=(2, 6), padx=4)

        lb = tk.Listbox(sec.body, selectmode=tk.MULTIPLE, width=72, height=6, exportselection=False)
        lb.grid(column=0, row=0, sticky='we', padx=6, pady=(2, 6))
        for t in cl.talents:
            if t:
                lb.insert(tk.END, t)

        # custom entry + button aligned horizontally
        entry_var = tk.StringVar()
        entry_fr = ttk.Frame(sec.body)
        entry_fr.grid(column=0, row=1, sticky='we', padx=6)
        ent = ttk.Entry(entry_fr, textvariable=entry_var, width=50)
        ent.pack(side='left', fill='x', expand=True)

        def make_add(lb_ref, ent_var):
            def _add():
                v = ent_var.get().strip()
                if v:
                    lb_ref.insert(tk.END, v)
                    lb_ref.selection_clear(0, tk.END)
                    lb_ref.selection_set(tk.END)
                    ent_var.set("")
            return _add

        btn = ttk.Button(entry_fr, text='Add', command=make_add(lb, entry_var))
        btn.pack(side='left', padx=(6, 0))

        listboxes.append((sec, lb))
        entries.append(entry_var)

    # Buttons
    btn_frame = ttk.Frame(dlg)
    btn_frame.grid(column=0, row=1, columnspan=2, pady=(8, 12))

    result = [None]

    def on_ok():
        selections_all = []
        for (sec, lb), cl in zip(listboxes, career_levels):
            # if section collapsed, treat as no selection but require user confirm
            if not sec.is_open():
                proceed = messagebox.askyesno("Section collapsed",
                                              f"You collapsed {cl.career} {cl.level}. Proceed without selecting talents for this level?")
                if not proceed:
                    return
                selections_all.append([])
                continue

            selections = [lb.get(i) for i in lb.curselection()]
            if not selections and lb.size() > 0:
                messagebox.showwarning("No talents selected",
                                       f"Please select at least one talent for {cl.career} {cl.level} or add a custom one.")
                return
            selections_all.append(selections)
        result[0] = selections_all
        dlg.destroy()

    def on_cancel():
        dlg.destroy()

    ttk.Button(btn_frame, text='OK', command=on_ok).pack(side='left', padx=6)
    ttk.Button(btn_frame, text='Cancel', command=on_cancel).pack(side='left', padx=6)

    parent.wait_window(dlg)
    return result[0]
