"""
gui.py
GRAPHICAL version of the Parallel Forces and Support Reaction Solver.
Computer Fundamentals and Programming for Civil Engineering.

It uses tkinter (already included in Python) and embeds the SAME beam
diagram produced by diagram.py inside the window.

Screens (same style as the class example):
    1. START  : title, description, Start button, creator line
    2. INPUT  : beam length, number of loads, load table, support positions
    3. RESULT : R1 and R2 values, equilibrium verdict and the beam diagram

Run with:     python gui.py
(The console version is still available:  python main.py)
"""

import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")     # must be set BEFORE pyplot is imported by diagram.py
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import solver
import diagram

# ------------------------------------------------------------------ appearance
WINDOW_TITLE = "Reaction Solver with Diagram"
BG_COLOR    = "#e8f4f0"     # soft mint page background
CARD_BG     = "#ffffff"     # white card that holds the controls
CARD_BORDER = "#bcd8cd"     # thin green-gray border around cards
TITLE_BG    = "#2e8b57"     # dark green title band
TITLE_FG    = "white"
BOX_COLOR   = "#dcefe2"     # light green info box
BUTTON_BG   = "#2e8b57"
BUTTON_FG   = "white"
LABEL_FONT  = ("Arial", 10)
BOLD_FONT   = ("Arial", 10, "bold")

# >>> PUT YOUR OWN NAME AND STUB CODE HERE (like the example screenshot) <<<
CREATOR_LINE = "Program Created by: Your Name Here  |  Stub Code: 000"

DESCRIPTION = ("This tool helps you calculate reactions for beams with loads.\n"
               "You can input the beam details, loads, and distances\n"
               "to visualize the reactions.")

MAX_LOADS = 10

# ------------------------------------------------------------------ window
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry("1280x760")
root.minsize(1100, 640)
root.configure(bg=BG_COLOR)

screens = {}            # "start" / "input"  ->  frame
load_entries = []       # one (magnitude, direction, position) triple per row
steps_string = None     # text shown by the "Show Steps" button
current_canvas = None   # keeps the matplotlib canvas alive
current_fig = None


# ------------------------------------------------------------------ small tools
def make_button(parent, text, command):
    return tk.Button(parent, text=text, command=command, bg=BUTTON_BG,
                     fg=BUTTON_FG, font=BOLD_FONT, padx=10, pady=6, bd=0,
                     activebackground="#256e46", activeforeground="white",
                     cursor="hand2")


def make_card(parent):
    """A white panel with a thin border and inner padding."""
    return tk.Frame(parent, bg=CARD_BG, highlightbackground=CARD_BORDER,
                    highlightthickness=1, padx=22, pady=16)


def make_row(parent):
    """One horizontal line inside a card."""
    row = tk.Frame(parent, bg=CARD_BG)
    row.pack(fill="x", pady=3)
    return row


def make_label(parent, text, width=16):
    return tk.Label(parent, text=text, bg=CARD_BG, fg="#333333",
                    font=LABEL_FONT, width=width, anchor="e")


def make_entry(parent, width=10):
    return tk.Entry(parent, width=width, font=LABEL_FONT, relief="solid", bd=1)


def separator(parent):
    tk.Frame(parent, bg=CARD_BORDER, height=1).pack(fill="x", pady=8)


def show_screen(name):
    """Hides every screen and shows only the one asked for."""
    for frame in screens.values():
        frame.pack_forget()
    screens[name].pack(fill="both", expand=True)


def text_to_number(text):
    """Converts the content of an entry box to float, or None if invalid."""
    try:
        return float(text.strip())
    except ValueError:
        return None


# ------------------------------------------------------------------ screen 1
def build_start_screen():
    frame = tk.Frame(root, bg=BG_COLOR)

    card = make_card(frame)
    card.pack(expand=True)                  # whole card sits in the middle

    tk.Label(card, text="PARALLEL FORCES", font=("Arial", 26, "bold"),
             bg=TITLE_BG, fg=TITLE_FG, padx=26, pady=8).pack(pady=(4, 12))

    tk.Label(card, text="Support Reaction Solver", font=("Arial", 13, "bold"),
             bg=CARD_BG, fg="#1b4d2e").pack(pady=(0, 10))

    tk.Label(card, text=DESCRIPTION, font=LABEL_FONT, bg=BOX_COLOR,
             fg="#123f24", justify="center", padx=16, pady=10).pack(pady=(0, 16))

    make_button(card, "S T A R T", lambda: show_screen("input")).pack(pady=(0, 4))

    tk.Label(frame, text=CREATOR_LINE, font=("Arial", 10),
             bg=BG_COLOR, fg="#4a6b5c").pack(side="bottom", pady=10)

    screens["start"] = frame


# ------------------------------------------------------------------ screen 2
def build_input_screen():
    global beam_len_entry, num_loads_entry, r1_entry, r2_entry
    global load_area, result_label, diagram_panel

    frame = tk.Frame(root, bg=BG_COLOR)

    # ---------- left : control card, centered in its column ----------
    holder = tk.Frame(frame, bg=BG_COLOR)
    holder.pack(side="left", fill="y", padx=(60, 12), pady=18)

    card = make_card(holder)
    card.pack(expand=True)                  # card centered vertically

    tk.Label(card, text="BEAM DATA", font=BOLD_FONT,
             bg=CARD_BG, fg="#1b4d2e").pack(anchor="w", pady=(0, 6))

    row = make_row(card)
    make_label(row, "Beam Length (m):").pack(side="left")
    beam_len_entry = make_entry(row); beam_len_entry.pack(side="left", padx=6)

    row = make_row(card)
    make_label(row, "Number of Loads:").pack(side="left")
    num_loads_entry = make_entry(row); num_loads_entry.pack(side="left", padx=6)
    num_loads_entry.insert(0, "0")
    make_button(row, "Set Loads", set_loads).pack(side="left", padx=6)

    load_area = tk.Frame(card, bg=CARD_BG)   # load rows appear here
    load_area.pack(fill="x", pady=4)

    separator(card)

    row = make_row(card)
    make_label(row, "R1 Position (m):").pack(side="left")
    r1_entry = make_entry(row); r1_entry.pack(side="left", padx=6)

    row = make_row(card)
    make_label(row, "R2 Position (m):").pack(side="left")
    r2_entry = make_entry(row); r2_entry.pack(side="left", padx=6)

    tk.Label(card, text="leave R1 / R2 blank to use 0 and the beam length",
             font=("Arial", 8, "italic"), bg=CARD_BG,
             fg="#777777").pack(anchor="w", pady=(2, 8))

    # buttons in a tidy 2 x 2 grid
    buttons = tk.Frame(card, bg=CARD_BG)
    buttons.pack(fill="x", pady=4)
    buttons.columnconfigure(0, weight=1)
    buttons.columnconfigure(1, weight=1)
    make_button(buttons, "Calculate Reactions",
                calculate_reactions).grid(row=0, column=0, sticky="ew",
                                          padx=(0, 4), pady=2)
    make_button(buttons, "Show Steps", show_steps).grid(row=0, column=1,
                                                        sticky="ew",
                                                        padx=(4, 0), pady=2)
    make_button(buttons, "Clear", clear_all).grid(row=1, column=0, sticky="ew",
                                                  padx=(0, 4), pady=2)
    make_button(buttons, "Back",
                lambda: show_screen("start")).grid(row=1, column=1, sticky="ew",
                                                   padx=(4, 0), pady=2)

    separator(card)

    result_label = tk.Label(card, text="", bg=CARD_BG, fg="#0b3d91",
                            font=("Arial", 13, "bold"), justify="center")
    result_label.pack(pady=(6, 2))

    # ---------- right : diagram panel ----------
    diagram_panel = tk.Frame(frame, bg="white", highlightbackground=CARD_BORDER,
                             highlightthickness=1)
    diagram_panel.pack(side="left", fill="both", expand=True,
                       padx=(0, 16), pady=14)
    show_diagram_placeholder()

    screens["input"] = frame


def show_diagram_placeholder():
    """Nice message instead of an empty white area."""
    tk.Label(diagram_panel,
             text="The beam diagram will appear here\nafter you press Calculate Reactions.",
             font=("Arial", 11, "italic"), bg="white", fg="#9aa5a0",
             justify="center").pack(expand=True)


def set_loads():
    """Builds one row (magnitude + direction + distance) per load."""
    global load_entries
    for widget in load_area.winfo_children():
        widget.destroy()
    load_entries = []

    number = text_to_number(num_loads_entry.get())
    if number is None or number != int(number):
        messagebox.showerror("Input error", "Number of loads must be a whole number.")
        return
    number = int(number)
    if number < 1 or number > MAX_LOADS:
        messagebox.showerror("Input error", f"Please enter between 1 and {MAX_LOADS} loads.")
        return

    for index in range(1, number + 1):
        row = tk.Frame(load_area, bg=CARD_BG)
        row.pack(fill="x", pady=2)

        tk.Label(row, text=f"Load {index} (kN):", bg=CARD_BG, fg="#333333",
                 font=LABEL_FONT, width=12, anchor="e").pack(side="left")
        magnitude = make_entry(row, width=8)
        magnitude.pack(side="left", padx=(6, 8))

        direction = ttk.Combobox(row, values=["down", "up"], width=5,
                                 state="readonly", font=LABEL_FONT)
        direction.set("down")
        direction.pack(side="left")

        tk.Label(row, text=f"Dist {index} (m):", bg=CARD_BG, fg="#333333",
                 font=LABEL_FONT).pack(side="left", padx=(10, 0))
        position = make_entry(row, width=8)
        position.pack(side="left", padx=6)

        load_entries.append((magnitude, direction, position))


# ------------------------------------------------------------------ calculate
def calculate_reactions():
    global steps_string, current_canvas, current_fig

    # ---- beam length ----
    beam_length = text_to_number(beam_len_entry.get())
    if beam_length is None or beam_length <= 0:
        messagebox.showerror("Input error", "Beam length must be a number greater than 0.")
        return

    # ---- support positions (blank = default) ----
    support_a = text_to_number(r1_entry.get())
    if support_a is None:
        support_a = 0.0
    support_b = text_to_number(r2_entry.get())
    if support_b is None:
        support_b = beam_length
    if not (0 <= support_a <= beam_length) or not (0 <= support_b <= beam_length):
        messagebox.showerror("Input error",
                             "Support positions must be between 0 and the beam length.")
        return
    if support_a == support_b:
        messagebox.showerror("Input error", "The two supports cannot be at the same position.")
        return
    if support_a > support_b:
        support_a, support_b = support_b, support_a

    # ---- loads ----
    if not load_entries:
        messagebox.showerror("Input error",
                             "Press 'Set Loads' first and fill in the load table.")
        return

    forces = []
    for index, (mag_entry, dir_combo, pos_entry) in enumerate(load_entries, start=1):
        magnitude = text_to_number(mag_entry.get())
        position = text_to_number(pos_entry.get())
        if magnitude is None or magnitude <= 0:
            messagebox.showerror("Input error", f"Load {index} must be a number greater than 0.")
            return
        if position is None or position < 0 or position > beam_length:
            messagebox.showerror("Input error",
                                 f"Distance {index} must be between 0 and {beam_length:g} m.")
            return
        direction = 1 if dir_combo.get() == "up" else -1
        forces.append((f"F{index}", magnitude, direction, position))

    # ---- the SAME math functions used by the console version ----
    ra, rb = solver.solve_reactions(forces, support_a, support_b)
    sum_fy, sum_ma, sum_mb = solver.check_equilibrium(forces, ra, rb,
                                                      support_a, support_b)
    balanced = solver.is_balanced(sum_fy, sum_ma, sum_mb)

    # ---- results on screen ----
    verdict = "EQUILIBRIUM OK" if balanced else "NOT IN EQUILIBRIUM"
    result_label.config(
        text=(f"R1 = {abs(ra):.2f} kN ({'up' if ra >= 0 else 'down'})\n"
              f"R2 = {abs(rb):.2f} kN ({'up' if rb >= 0 else 'down'})\n"
              f"{verdict}"),
        fg="#0b3d91" if balanced else "#b00000")

    steps_string = build_steps_string(beam_length, forces, support_a, support_b,
                                      ra, rb, sum_fy, sum_ma, sum_mb)

    # ---- diagram embedded in the window ----
    fig = diagram.create_beam_figure(beam_length, forces, ra, rb,
                                     support_a, support_b,
                                     sum_fy, sum_ma, sum_mb, balanced,
                                     figsize=(9.5, 6.2))
    current_fig = fig
    for widget in diagram_panel.winfo_children():
        widget.destroy()
    current_canvas = FigureCanvasTkAgg(fig, master=diagram_panel)
    current_canvas.draw()
    current_canvas.get_tk_widget().pack(fill="both", expand=True)


def build_steps_string(beam_length, forces, support_a, support_b,
                       ra, rb, sum_fy, sum_ma, sum_mb):
    """The full step-by-step solution as one text block (Show Steps button)."""
    lines = []
    add = lines.append
    span = support_b - support_a
    loads = solver.total_force(forces)
    ma = solver.total_moment_about(forces, support_a)

    add("STEP 1 : INPUT SUMMARY")
    add(f"  Beam length L        = {beam_length:.2f} m")
    add(f"  Support R1 (A) at x  = {support_a:.2f} m")
    add(f"  Support R2 (B) at x  = {support_b:.2f} m")
    add(f"  Span                 = {span:.2f} m")
    add("  Applied forces (up = +, down = -):")
    for label, magnitude, direction, position in forces:
        fy = magnitude * direction
        word = "up" if direction > 0 else "down"
        add(f"    {label}: {magnitude:.2f} kN {word} at x = {position:.2f} m"
            f"   ->   Fy = {fy:+.2f} kN")
    add(f"  Sum of applied forces = {loads:+.2f} kN")
    add("")
    add("STEP 2 : MOMENTS ABOUT R1   (Moment = Force x Distance)")
    for label, magnitude, direction, position in forces:
        fy = magnitude * direction
        arm = position - support_a
        add(f"    {label}: M = ({fy:+.2f}) * ({arm:+.2f}) = {fy * arm:+.2f} kN.m")
    add(f"  Sum of moments about R1 = {ma:+.2f} kN.m")
    add("")
    add("STEP 3 : FIND R2 FROM  Sum M_R1 = 0")
    add(f"  {ma:+.2f} + R2 * ({span:.2f}) = 0")
    add(f"  R2 = {-ma:+.2f} / {span:.2f} = {rb:.2f} kN ({'up' if rb >= 0 else 'down'})")
    add("")
    add("STEP 4 : FIND R1 FROM  Sum Fy = 0")
    add(f"  R1 + ({rb:+.2f}) + ({loads:+.2f}) = 0")
    add(f"  R1 = {ra:.2f} kN ({'up' if ra >= 0 else 'down'})")
    add("")
    add("STEP 5 : EQUILIBRIUM CHECK")
    add(f"  Sum Fy   = {solver.clean(sum_fy):.4f} kN")
    add(f"  Sum M_R1 = {solver.clean(sum_ma):.4f} kN.m")
    add(f"  Sum M_R2 = {solver.clean(sum_mb):.4f} kN.m")
    if solver.is_balanced(sum_fy, sum_ma, sum_mb):
        add("  --> The system IS in equilibrium.")
    else:
        add("  --> WARNING : NOT in equilibrium.")
    return "\n".join(lines)


def show_steps():
    if steps_string is None:
        messagebox.showinfo("Calculation Steps", "Press 'Calculate Reactions' first.")
        return
    window = tk.Toplevel(root)
    window.title("Calculation Steps")
    window.geometry("640x520")
    window.configure(bg=BG_COLOR)
    text_box = tk.Text(window, font=("Consolas", 10), bg="#f7fbf9",
                       relief="solid", bd=1)
    text_box.pack(fill="both", expand=True, padx=12, pady=12)
    text_box.insert("1.0", steps_string)
    text_box.config(state="disabled")


def clear_all():
    global load_entries, steps_string, current_canvas, current_fig
    beam_len_entry.delete(0, "end")
    num_loads_entry.delete(0, "end")
    num_loads_entry.insert(0, "0")
    r1_entry.delete(0, "end")
    r2_entry.delete(0, "end")
    for widget in load_area.winfo_children():
        widget.destroy()
    load_entries = []
    result_label.config(text="")
    steps_string = None
    current_canvas = None
    current_fig = None
    for widget in diagram_panel.winfo_children():
        widget.destroy()
    show_diagram_placeholder()


# ------------------------------------------------------------------ run
def main():
    build_start_screen()
    build_input_screen()
    show_screen("start")
    root.mainloop()


if __name__ == "__main__":
    main()