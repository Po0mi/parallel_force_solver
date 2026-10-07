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
BG_COLOR   = "#dff0ee"      # light mint background (like the example)
BOX_COLOR  = "#a9d7b8"      # light green boxes on the start screen
BUTTON_BG  = "#2e8b57"      # green buttons
BUTTON_FG  = "white"

# >>> PUT YOUR OWN NAME AND STUB CODE HERE (like the example screenshot) <<<
CREATOR_LINE = "Program Created by: Your Name Here\nStub Code: 000"

DESCRIPTION = ("This tool helps you calculate reactions for beams with loads.\n"
               "You can input the beam details, loads, and distances\n"
               "to visualize the reactions.")

MAX_LOADS = 10

# ------------------------------------------------------------------ window
root = tk.Tk()
root.title(WINDOW_TITLE)
root.geometry("1350x780")
root.configure(bg=BG_COLOR)

screens = {}            # "start" / "input"  ->  frame
load_entries = []       # one (magnitude, direction, position) triple per row
steps_string = None     # text shown by the "Show Steps" button
current_canvas = None   # keeps the matplotlib canvas alive
current_fig = None


# ------------------------------------------------------------------ small tools
def make_button(parent, text, command):
    return tk.Button(parent, text=text, command=command, bg=BUTTON_BG,
                     fg=BUTTON_FG, font=("Arial", 10, "bold"),
                     padx=8, pady=3, activebackground="#256e46")


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

    tk.Label(frame, text="Parallel Forces", font=("Arial", 30, "bold"),
             bg=BOX_COLOR, fg="#1b4d2e", padx=20, pady=6).pack(pady=(70, 25))

    tk.Label(frame, text=DESCRIPTION, font=("Arial", 13), bg=BOX_COLOR,
             fg="#123f24", justify="center", padx=18, pady=10).pack(pady=(0, 30))

    make_button(frame, "Start", lambda: show_screen("input")).pack()

    tk.Label(frame, text=CREATOR_LINE, font=("Arial", 16), bg=BOX_COLOR,
             fg="#1b4d2e", justify="center", padx=16, pady=8).pack(side="bottom", pady=30)

    screens["start"] = frame


# ------------------------------------------------------------------ screen 2
def build_input_screen():
    global beam_len_entry, num_loads_entry, r1_entry, r2_entry
    global load_area, result_label, diagram_panel

    frame = tk.Frame(root, bg=BG_COLOR)

    # ---------------- left panel : all the inputs ----------------
    left = tk.Frame(frame, bg=BG_COLOR)
    left.pack(side="left", fill="y", padx=25, pady=20)

    row = tk.Frame(left, bg=BG_COLOR); row.pack(fill="x", pady=3)
    tk.Label(row, text="Beam Length (m):", bg=BG_COLOR, width=16,
             anchor="e").pack(side="left")
    beam_len_entry = tk.Entry(row, width=10); beam_len_entry.pack(side="left", padx=6)

    row = tk.Frame(left, bg=BG_COLOR); row.pack(fill="x", pady=3)
    tk.Label(row, text="Number of Loads:", bg=BG_COLOR, width=16,
             anchor="e").pack(side="left")
    num_loads_entry = tk.Entry(row, width=10); num_loads_entry.pack(side="left", padx=6)
    num_loads_entry.insert(0, "0")
    make_button(row, "Set Loads", set_loads).pack(side="left", padx=6)

    load_area = tk.Frame(left, bg=BG_COLOR)      # the load rows appear here
    load_area.pack(fill="x", pady=6)

    row = tk.Frame(left, bg=BG_COLOR); row.pack(fill="x", pady=3)
    tk.Label(row, text="R1 Position (m):", bg=BG_COLOR, width=16,
             anchor="e").pack(side="left")
    r1_entry = tk.Entry(row, width=10); r1_entry.pack(side="left", padx=6)

    row = tk.Frame(left, bg=BG_COLOR); row.pack(fill="x", pady=3)
    tk.Label(row, text="R2 Position (m):", bg=BG_COLOR, width=16,
             anchor="e").pack(side="left")
    r2_entry = tk.Entry(row, width=10); r2_entry.pack(side="left", padx=6)

    tk.Label(left, text="(leave R1 / R2 blank to use 0 and the beam length)",
             bg=BG_COLOR, fg="#555555", font=("Arial", 9)).pack(anchor="w", pady=(0, 8))

    buttons = tk.Frame(left, bg=BG_COLOR); buttons.pack(pady=4)
    make_button(buttons, "Calculate Reactions", calculate_reactions).pack(side="left", padx=4)
    make_button(buttons, "Show Steps", show_steps).pack(side="left", padx=4)
    make_button(buttons, "Back", lambda: show_screen("start")).pack(side="left", padx=4)
    make_button(buttons, "Clear", clear_all).pack(side="left", padx=4)

    result_label = tk.Label(left, text="", bg=BG_COLOR, fg="#0b3d91",
                            font=("Arial", 14, "bold"), justify="center")
    result_label.pack(pady=(12, 4))

    # ---------------- right panel : the diagram ----------------
    diagram_panel = tk.Frame(frame, bg="white")
    diagram_panel.pack(side="left", fill="both", expand=True, padx=(0, 15), pady=15)

    screens["input"] = frame


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
        row = tk.Frame(load_area, bg=BG_COLOR)
        row.pack(fill="x", pady=2)

        tk.Label(row, text=f"Load {index} (kN):", bg=BG_COLOR, width=12,
                 anchor="e").pack(side="left")
        magnitude = tk.Entry(row, width=8)
        magnitude.pack(side="left", padx=(6, 10))

        direction = ttk.Combobox(row, values=["down", "up"], width=5, state="readonly")
        direction.set("down")
        direction.pack(side="left")

        tk.Label(row, text=f"Dist {index} (m):", bg=BG_COLOR).pack(side="left", padx=(10, 0))
        position = tk.Entry(row, width=8)
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
    text_box = tk.Text(window, font=("Consolas", 10), bg="#f7fbf9")
    text_box.pack(fill="both", expand=True, padx=10, pady=10)
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


# ------------------------------------------------------------------ run
def main():
    build_start_screen()
    build_input_screen()
    show_screen("start")
    root.mainloop()


if __name__ == "__main__":
    main()