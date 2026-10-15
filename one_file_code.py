"""
PARALLEL FORCES AND SUPPORT REACTION SOLVER
Computer Fundamentals and Programming for Civil Engineering

Single-file version containing:
- Engineering Math (Solver)
- Matplotlib Drawing (Diagram)
- Console Output (Report & Inputs)
- Graphical User Interface (Tkinter GUI)
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

# Matplotlib setup MUST happen before importing pyplot
import matplotlib
matplotlib.use("TkAgg") 
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# >>> PUT YOUR OWN NAME AND STUB CODE HERE <<<
CREATOR_LINE = "Program Created by: Your Name Here  |  Stub Code: 000"

# ==============================================================================
# 1. SOLVER MODULE (Engineering Math)
# ==============================================================================
TOLERANCE = 0.0001

def clean(value):
    if abs(value) < TOLERANCE: return 0.0
    return value

def signed_force(force):
    label, magnitude, direction, position = force
    return magnitude * direction

def lever_arm(position, pivot):
    return position - pivot

def moment_of_force(force, pivot):
    return signed_force(force) * lever_arm(force[3], pivot)

def total_force(forces):
    return sum(signed_force(f) for f in forces)

def total_moment_about(forces, pivot):
    return sum(moment_of_force(f, pivot) for f in forces)

def solve_reactions(forces, support_a, support_b):
    span = support_b - support_a
    moment_loads_a = total_moment_about(forces, support_a)
    rb = -moment_loads_a / span
    ra = -total_force(forces) - rb
    return ra, rb

def check_equilibrium(forces, ra, rb, support_a, support_b):
    span = support_b - support_a
    sum_fy = total_force(forces) + ra + rb
    sum_ma = total_moment_about(forces, support_a) + rb * span
    sum_mb = total_moment_about(forces, support_b) + ra * (-span)
    return sum_fy, sum_ma, sum_mb

def is_balanced(sum_fy, sum_ma, sum_mb):
    return abs(sum_fy) <= TOLERANCE and abs(sum_ma) <= TOLERANCE and abs(sum_mb) <= TOLERANCE

# ==============================================================================
# 2. DIAGRAM MODULE (Matplotlib Drawing)
# ==============================================================================
OUTPUT_FOLDER = "output"
FILE_NAME = "beam_diagram.png"

def make_output_folder(folder):
    if not os.path.exists(folder): os.makedirs(folder)
    return folder

def tidy(value):
    return 0.0 if abs(value) < 0.0001 else value

def arrow_length(magnitude, biggest_magnitude, scale):
    if biggest_magnitude <= 0: return 2.0 * scale
    return (1.2 + 2.0 * (magnitude / biggest_magnitude)) * scale

def draw_support(ax, x, top_y, height, kind):
    half_width = height * 0.6
    triangle = Polygon([(x, top_y), (x - half_width, top_y - height), (x + half_width, top_y - height)],
                       closed=True, facecolor="white", edgecolor="black", linewidth=1.5)
    ax.add_patch(triangle)
    ground_y = top_y - height
    if kind == "roller":
        radius = height * 0.17
        for wheel_x in (x - half_width * 0.55, x + half_width * 0.55):
            ax.add_patch(Circle((wheel_x, ground_y - radius), radius, facecolor="white", edgecolor="black", linewidth=1.2))
        ground_y -= 2 * radius
    line_half = half_width * 1.9
    ax.plot([x - line_half, x + line_half], [ground_y, ground_y], color="black", linewidth=1.6)
    for i in range(7):
        hx = x - line_half + (2 * line_half) * i / 6
        ax.plot([hx, hx - height * 0.30], [ground_y, ground_y - height * 0.30], color="black", linewidth=0.8)
    return ground_y

def draw_applied_force(ax, x, beam_top, magnitude, direction, length, scale, text, text_lift):
    start_y = beam_top + 0.15 * scale
    tip_y = start_y + length
    if direction < 0:
        ax.annotate("", xy=(x, start_y), xytext=(x, tip_y), arrowprops=dict(arrowstyle="-|>", color="crimson", lw=2.2, mutation_scale=20))
    else:
        ax.annotate("", xy=(x, tip_y), xytext=(x, start_y), arrowprops=dict(arrowstyle="-|>", color="green", lw=2.2, mutation_scale=20))
    label_y = tip_y + 0.25 * scale + text_lift
    ax.text(x, label_y, text, ha="center", va="bottom", fontsize=9.5, linespacing=1.5)
    return label_y + 1.0 * scale

def draw_reaction(ax, x, ground_y, value, length, scale, text):
    gap = 0.55 * scale
    bottom_y = ground_y - gap - length
    top_y = ground_y - gap
    colour = "navy" if value >= 0 else "darkorange"
    if value >= 0:
        ax.annotate("", xy=(x, top_y), xytext=(x, bottom_y), arrowprops=dict(arrowstyle="-|>", color=colour, lw=2.4, mutation_scale=22))
    else:
        ax.annotate("", xy=(x, bottom_y), xytext=(x, top_y), arrowprops=dict(arrowstyle="-|>", color=colour, lw=2.4, mutation_scale=22))
    ax.text(x, bottom_y - 0.30 * scale, text, ha="center", va="top", fontsize=10, fontweight="bold", color=colour, linespacing=1.4)
    return bottom_y - 1.5 * scale

def draw_dimension(ax, x1, x2, y, text, scale):
    ax.annotate("", xy=(x1, y), xytext=(x2, y), arrowprops=dict(arrowstyle="<|-|>", color="dimgray", lw=1.2, mutation_scale=14))
    ax.text((x1 + x2) / 2.0, y - 0.35 * scale, text, ha="center", va="top", fontsize=10, color="dimgray")

def create_beam_figure(beam_length, forces, ra, rb, support_a, support_b, sum_fy, sum_ma, sum_mb, balanced, figsize=(12, 7.5)):
    scale = max(beam_length / 20.0, 0.35)
    beam_h = 0.55 * scale
    beam_top = beam_h / 2.0
    beam_bottom = -beam_h / 2.0
    support_h = 1.7 * scale
    biggest_load = max((f[1] for f in forces), default=0.0)
    biggest_reaction = max(abs(ra), abs(rb))
    
    fig, ax = plt.subplots(figsize=figsize)
    ax.add_patch(Rectangle((0, beam_bottom), beam_length, beam_h, facecolor="#dcdcdc", edgecolor="black", linewidth=1.6))
    ax.text(beam_length / 2.0, 0.0, "BEAM", ha="center", va="center", fontsize=9, color="#555555")
    
    ground_a = draw_support(ax, support_a, beam_bottom, support_h, "pin")
    ground_b = draw_support(ax, support_b, beam_bottom, support_h, "roller")
    half = support_h * 0.6
    ax.text(support_a - 1.15 * half, beam_bottom - support_h / 2.0, f"A (pin)\nx = {support_a:.2f} m", ha="right", va="center", fontsize=9.5)
    ax.text(support_b + 1.15 * half, beam_bottom - support_h / 2.0, f"B (roller)\nx = {support_b:.2f} m", ha="left", va="center", fontsize=9.5)
    
    highest = beam_top
    for index, (label, magnitude, direction, position) in enumerate(forces, 1):
        length = arrow_length(magnitude, biggest_load, scale)
        sense = "(down)" if direction < 0 else "(up)"
        text = f"{label} = {magnitude:.2f} kN {sense}\nat x = {position:.2f} m"
        lift = 0.9 * scale if index % 2 == 0 else 0.0
        used = draw_applied_force(ax, position, beam_top, magnitude, direction, length, scale, text, lift)
        if used > highest: highest = used
        
    text_a = f"RA = {abs(ra):.2f} kN\n({'up' if ra >= 0 else 'down'})"
    text_b = f"RB = {abs(rb):.2f} kN\n({'up' if rb >= 0 else 'down'})"
    low_a = draw_reaction(ax, support_a, ground_a, ra, arrow_length(abs(ra), biggest_reaction, scale), scale, text_a)
    low_b = draw_reaction(ax, support_b, ground_b, rb, arrow_length(abs(rb), biggest_reaction, scale), scale, text_b)
    lowest = min(low_a, low_b, ground_a - support_h, ground_b - support_h)
    
    dim_y = lowest - 1.2 * scale
    ax.plot([0, 0], [beam_bottom, dim_y], color="dimgray", lw=0.8, linestyle=":")
    ax.plot([beam_length, beam_length], [beam_bottom, dim_y], color="dimgray", lw=0.8, linestyle=":")
    draw_dimension(ax, 0, beam_length, dim_y, f"L = {beam_length:.2f} m", scale)
    
    margin_x = max(2.2 * scale, beam_length * 0.09)
    ax.set_xlim(-margin_x, beam_length + margin_x)
    ax.set_ylim(dim_y - 2.4 * scale, highest + 2.0 * scale)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Beam Diagram - Parallel Forces and Support Reactions", fontsize=13, fontweight="bold")
    
    verdict = "EQUILIBRIUM OK" if balanced else "NOT IN EQUILIBRIUM"
    summary = (f"RA = {ra:+.2f} kN at x = {support_a:.2f} m        RB = {rb:+.2f} kN at x = {support_b:.2f} m\n"
               f"Check :  Sum Fy = {tidy(sum_fy):+.4f} kN     Sum M_A = {tidy(sum_ma):+.4f} kN.m     Sum M_B = {tidy(sum_mb):+.4f} kN.m     -->  {verdict}")
    fig.subplots_adjust(left=0.03, right=0.97, top=0.92, bottom=0.15)
    fig.text(0.5, 0.035, summary, ha="center", va="bottom", fontsize=9.5, family="monospace")
    return fig

def draw_beam_console(beam_length, forces, ra, rb, support_a, support_b, sum_fy, sum_ma, sum_mb, balanced):
    make_output_folder(OUTPUT_FOLDER)
    fig = create_beam_figure(beam_length, forces, ra, rb, support_a, support_b, sum_fy, sum_ma, sum_mb, balanced)
    file_path = os.path.join(OUTPUT_FOLDER, FILE_NAME)
    fig.savefig(file_path, dpi=160)
    print(f"  Beam diagram saved as : {file_path}")
    try: plt.show()
    except Exception: print("  Window could not be opened, but PNG is saved.")
    plt.close(fig)

# ==============================================================================
# 3. GUI MODULE (Tkinter Interface)
# ==============================================================================
BG_COLOR, CARD_BG, CARD_BORDER = "#e8f4f0", "#ffffff", "#bcd8cd"
TITLE_BG, TITLE_FG, BOX_COLOR = "#2e8b57", "white", "#dcefe2"
BUTTON_BG, BUTTON_FG = "#2e8b57", "white"
LABEL_FONT, BOLD_FONT = ("Arial", 10), ("Arial", 10, "bold")
MAX_LOADS = 10

root = tk.Tk()
root.title("Reaction Solver with Diagram")
root.geometry("1280x760")
root.minsize(1100, 640)
root.configure(bg=BG_COLOR)

screens, load_entries, steps_string, current_canvas, current_fig = {}, [], None, None, None
beam_len_entry, num_loads_entry, r1_entry, r2_entry = None, None, None, None
load_area, result_label, diagram_panel = None, None, None

def make_button(parent, text, command):
    return tk.Button(parent, text=text, command=command, bg=BUTTON_BG, fg=BUTTON_FG, font=BOLD_FONT, padx=10, pady=6, bd=0, activebackground="#256e46", cursor="hand2")

def make_card(parent):
    return tk.Frame(parent, bg=CARD_BG, highlightbackground=CARD_BORDER, highlightthickness=1, padx=22, pady=16)

def make_row(parent):
    row = tk.Frame(parent, bg=CARD_BG); row.pack(fill="x", pady=3); return row

def make_label(parent, text, width=16):
    return tk.Label(parent, text=text, bg=CARD_BG, fg="#333333", font=LABEL_FONT, width=width, anchor="e")

def make_entry(parent, width=10):
    return tk.Entry(parent, width=width, font=LABEL_FONT, relief="solid", bd=1)

def separator(parent):
    tk.Frame(parent, bg=CARD_BORDER, height=1).pack(fill="x", pady=8)

def show_screen(name):
    for frame in screens.values(): frame.pack_forget()
    screens[name].pack(fill="both", expand=True)

def text_to_number(text):
    try: return float(text.strip())
    except ValueError: return None

def build_start_screen():
    frame = tk.Frame(root, bg=BG_COLOR)
    card = make_card(frame); card.pack(expand=True)
    tk.Label(card, text="PARALLEL FORCES", font=("Arial", 26, "bold"), bg=TITLE_BG, fg=TITLE_FG, padx=26, pady=8).pack(pady=(4, 12))
    tk.Label(card, text="Support Reaction Solver", font=("Arial", 13, "bold"), bg=CARD_BG, fg="#1b4d2e").pack(pady=(0, 10))
    desc = "This tool helps you calculate reactions for beams with loads.\nYou can input the beam details, loads, and distances\nto visualize the reactions."
    tk.Label(card, text=desc, font=LABEL_FONT, bg=BOX_COLOR, fg="#123f24", justify="center", padx=16, pady=10).pack(pady=(0, 16))
    make_button(card, "S T A R T", lambda: show_screen("input")).pack(pady=(0, 4))
    tk.Label(frame, text=CREATOR_LINE, font=("Arial", 10), bg=BG_COLOR, fg="#4a6b5c").pack(side="bottom", pady=10)
    screens["start"] = frame

def show_diagram_placeholder():
    tk.Label(diagram_panel, text="The beam diagram will appear here\nafter you press Calculate Reactions.", font=("Arial", 11, "italic"), bg="white", fg="#9aa5a0", justify="center").pack(expand=True)

def build_input_screen():
    global beam_len_entry, num_loads_entry, r1_entry, r2_entry, load_area, result_label, diagram_panel
    frame = tk.Frame(root, bg=BG_COLOR)
    holder = tk.Frame(frame, bg=BG_COLOR); holder.pack(side="left", fill="y", padx=(60, 12), pady=18)
    card = make_card(holder); card.pack(expand=True)
    tk.Label(card, text="BEAM DATA", font=BOLD_FONT, bg=CARD_BG, fg="#1b4d2e").pack(anchor="w", pady=(0, 6))
    
    row = make_row(card); make_label(row, "Beam Length (m):").pack(side="left")
    beam_len_entry = make_entry(row); beam_len_entry.pack(side="left", padx=6)
    
    row = make_row(card); make_label(row, "Number of Loads:").pack(side="left")
    num_loads_entry = make_entry(row); num_loads_entry.pack(side="left", padx=6); num_loads_entry.insert(0, "0")
    make_button(row, "Set Loads", set_loads).pack(side="left", padx=6)
    
    load_area = tk.Frame(card, bg=CARD_BG); load_area.pack(fill="x", pady=4)
    separator(card)
    
    row = make_row(card); make_label(row, "R1 Position (m):").pack(side="left")
    r1_entry = make_entry(row); r1_entry.pack(side="left", padx=6)
    row = make_row(card); make_label(row, "R2 Position (m):").pack(side="left")
    r2_entry = make_entry(row); r2_entry.pack(side="left", padx=6)
    tk.Label(card, text="leave R1 / R2 blank to use 0 and the beam length", font=("Arial", 8, "italic"), bg=CARD_BG, fg="#777777").pack(anchor="w", pady=(2, 8))
    
    buttons = tk.Frame(card, bg=CARD_BG); buttons.pack(fill="x", pady=4)
    buttons.columnconfigure(0, weight=1); buttons.columnconfigure(1, weight=1)
    make_button(buttons, "Calculate Reactions", calculate_reactions).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=2)
    make_button(buttons, "Show Steps", show_steps).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=2)
    make_button(buttons, "Clear", clear_all).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=2)
    make_button(buttons, "Back", lambda: show_screen("start")).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=2)
    
    separator(card)
    result_label = tk.Label(card, text="", bg=CARD_BG, fg="#0b3d91", font=("Arial", 13, "bold"), justify="center"); result_label.pack(pady=(6, 2))
    
    diagram_panel = tk.Frame(frame, bg="white", highlightbackground=CARD_BORDER, highlightthickness=1)
    diagram_panel.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=14)
    show_diagram_placeholder()
    screens["input"] = frame

def set_loads():
    global load_entries
    for widget in load_area.winfo_children(): widget.destroy()
    load_entries = []
    number = text_to_number(num_loads_entry.get())
    if number is None or number != int(number):
        messagebox.showerror("Input error", "Number of loads must be a whole number."); return
    number = int(number)
    if number < 1 or number > MAX_LOADS:
        messagebox.showerror("Input error", f"Please enter between 1 and {MAX_LOADS} loads."); return
    for index in range(1, number + 1):
        row = tk.Frame(load_area, bg=CARD_BG); row.pack(fill="x", pady=2)
        tk.Label(row, text=f"Load {index} (kN):", bg=CARD_BG, fg="#333333", font=LABEL_FONT, width=12, anchor="e").pack(side="left")
        magnitude = make_entry(row, width=8); magnitude.pack(side="left", padx=(6, 8))
        direction = ttk.Combobox(row, values=["down", "up"], width=5, state="readonly", font=LABEL_FONT); direction.set("down"); direction.pack(side="left")
        tk.Label(row, text=f"Dist {index} (m):", bg=CARD_BG, fg="#333333", font=LABEL_FONT).pack(side="left", padx=(10, 0))
        position = make_entry(row, width=8); position.pack(side="left", padx=6)
        load_entries.append((magnitude, direction, position))

def calculate_reactions():
    global steps_string, current_canvas, current_fig
    beam_length = text_to_number(beam_len_entry.get())
    if beam_length is None or beam_length <= 0:
        messagebox.showerror("Input error", "Beam length must be a number greater than 0."); return
    support_a = text_to_number(r1_entry.get())
    if support_a is None: support_a = 0.0
    support_b = text_to_number(r2_entry.get())
    if support_b is None: support_b = beam_length
    if not (0 <= support_a <= beam_length) or not (0 <= support_b <= beam_length):
        messagebox.showerror("Input error", "Support positions must be between 0 and the beam length."); return
    if support_a == support_b:
        messagebox.showerror("Input error", "The two supports cannot be at the same position."); return
    if support_a > support_b: support_a, support_b = support_b, support_a
    if not load_entries:
        messagebox.showerror("Input error", "Press 'Set Loads' first and fill in the load table."); return
        
    forces = []
    for index, (mag_entry, dir_combo, pos_entry) in enumerate(load_entries, start=1):
        magnitude = text_to_number(mag_entry.get())
        position = text_to_number(pos_entry.get())
        if magnitude is None or magnitude <= 0:
            messagebox.showerror("Input error", f"Load {index} must be a number greater than 0."); return
        if position is None or position < 0 or position > beam_length:
            messagebox.showerror("Input error", f"Distance {index} must be between 0 and {beam_length:g} m."); return
        direction = 1 if dir_combo.get() == "up" else -1
        forces.append((f"F{index}", magnitude, direction, position))
        
    ra, rb = solve_reactions(forces, support_a, support_b)
    sum_fy, sum_ma, sum_mb = check_equilibrium(forces, ra, rb, support_a, support_b)
    balanced = is_balanced(sum_fy, sum_ma, sum_mb)
    verdict = "EQUILIBRIUM OK" if balanced else "NOT IN EQUILIBRIUM"
    result_label.config(text=(f"R1 = {abs(ra):.2f} kN ({'up' if ra >= 0 else 'down'})\nR2 = {abs(rb):.2f} kN ({'up' if rb >= 0 else 'down'})\n{verdict}"), fg="#0b3d91" if balanced else "#b00000")
    steps_string = build_steps_string(beam_length, forces, support_a, support_b, ra, rb, sum_fy, sum_ma, sum_mb)
    
    fig = create_beam_figure(beam_length, forces, ra, rb, support_a, support_b, sum_fy, sum_ma, sum_mb, balanced, figsize=(9.5, 6.2))
    current_fig = fig
    for widget in diagram_panel.winfo_children(): widget.destroy()
    current_canvas = FigureCanvasTkAgg(fig, master=diagram_panel)
    current_canvas.draw()
    current_canvas.get_tk_widget().pack(fill="both", expand=True)

def build_steps_string(beam_length, forces, support_a, support_b, ra, rb, sum_fy, sum_ma, sum_mb):
    lines, span, loads, ma = [], support_b - support_a, total_force(forces), total_moment_about(forces, support_a)
    lines.append("STEP 1 : INPUT SUMMARY")
    lines.append(f"  Beam length L        = {beam_length:.2f} m")
    lines.append(f"  Support R1 (A) at x  = {support_a:.2f} m")
    lines.append(f"  Support R2 (B) at x  = {support_b:.2f} m\n  Span                 = {span:.2f} m")
    lines.append("  Applied forces (up = +, down = -):")
    for label, magnitude, direction, position in forces:
        fy = magnitude * direction
        lines.append(f"    {label}: {magnitude:.2f} kN {'up' if direction > 0 else 'down'} at x = {position:.2f} m   ->   Fy = {fy:+.2f} kN")
    lines.append(f"  Sum of applied forces = {loads:+.2f} kN\n\nSTEP 2 : MOMENTS ABOUT R1")
    for label, magnitude, direction, position in forces:
        fy, arm = magnitude * direction, position - support_a
        lines.append(f"    {label}: M = ({fy:+.2f}) * ({arm:+.2f}) = {fy * arm:+.2f} kN.m")
    lines.append(f"  Sum of moments about R1 = {ma:+.2f} kN.m\n\nSTEP 3 : FIND R2")
    lines.append(f"  {ma:+.2f} + R2 * ({span:.2f}) = 0  =>  R2 = {-ma:+.2f} / {span:.2f} = {rb:.2f} kN\n\nSTEP 4 : FIND R1")
    lines.append(f"  R1 + ({rb:+.2f}) + ({loads:+.2f}) = 0  =>  R1 = {ra:.2f} kN\n\nSTEP 5 : EQUILIBRIUM CHECK")
    lines.append(f"  Sum Fy   = {clean(sum_fy):.4f} kN\n  Sum M_R1 = {clean(sum_ma):.4f} kN.m\n  Sum M_R2 = {clean(sum_mb):.4f} kN.m")
    lines.append("  --> The system IS in equilibrium." if is_balanced(sum_fy, sum_ma, sum_mb) else "  --> WARNING : NOT in equilibrium.")
    return "\n".join(lines)

def show_steps():
    if steps_string is None: messagebox.showinfo("Calculation Steps", "Press 'Calculate Reactions' first."); return
    window = tk.Toplevel(root); window.title("Calculation Steps"); window.geometry("640x520"); window.configure(bg=BG_COLOR)
    text_box = tk.Text(window, font=("Consolas", 10), bg="#f7fbf9", relief="solid", bd=1)
    text_box.pack(fill="both", expand=True, padx=12, pady=12); text_box.insert("1.0", steps_string); text_box.config(state="disabled")

def clear_all():
    global load_entries, steps_string, current_canvas, current_fig
    beam_len_entry.delete(0, "end"); num_loads_entry.delete(0, "end"); num_loads_entry.insert(0, "0")
    r1_entry.delete(0, "end"); r2_entry.delete(0, "end")
    for widget in load_area.winfo_children(): widget.destroy()
    load_entries, steps_string, current_canvas, current_fig = [], None, None, None
    result_label.config(text="")
    for widget in diagram_panel.winfo_children(): widget.destroy()
    show_diagram_placeholder()

def run_gui():
    build_start_screen(); build_input_screen(); show_screen("start"); root.mainloop()

# ==============================================================================
# 4. CONSOLE MODULE (Text-based Interface)
# ==============================================================================
def get_float(prompt):
    while True:
        try: return float(input(prompt).strip())
        except ValueError: print("      Please type a number.")

def get_positive_float(prompt):
    while True:
        val = get_float(prompt)
        if val > 0: return val
        print("      Must be > 0.")

def run_console():
    print("="*60 + "\n   PARALLEL FORCES SOLVER (CONSOLE MODE)\n" + "="*60)
    L = get_positive_float("Beam length (m): ")
    xA, xB = 0.0, L
    n = int(get_positive_float("How many forces? "))
    forces = []
    for i in range(1, n + 1):
        mag = get_positive_float(f"  Force {i} magnitude (kN): ")
        dir_sign = 1 if input(f"  Force {i} direction (1=up, 2=down): ").strip() == '1' else -1
        pos = get_float(f"  Force {i} position (m): ")
        forces.append((f"F{i}", mag, dir_sign, pos))
        
    ra, rb = solve_reactions(forces, xA, xB)
    sum_fy, sum_ma, sum_mb = check_equilibrium(forces, ra, rb, xA, xB)
    balanced = is_balanced(sum_fy, sum_ma, sum_mb)
    
    print(f"\nRESULTS:\n  RA = {ra:.2f} kN\n  RB = {rb:.2f} kN\n  Equilibrium: {'OK' if balanced else 'FAILED'}")
    draw_beam_console(L, forces, ra, rb, xA, xB, sum_fy, sum_ma, sum_mb, balanced)

# ==============================================================================
# 5. MAIN ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("  PARALLEL FORCES AND SUPPORT REACTION SOLVER")
    print("="*50)
    print("  1. Run Graphical Version (GUI)")
    print("  2. Run Console Version (Text)")
    print("="*50)
    
    # If running in an IDE like Spyder where input() might be annoying, 
    # you can just hardcode `choice = "1"` here.
    try:
        choice = input("\nChoose 1 or 2: ").strip()
    except EOFError:
        choice = "1" # Default to GUI if input fails
        
    if choice == "2":
        run_console()
    else:
        run_gui()

# === END OF FILE ===