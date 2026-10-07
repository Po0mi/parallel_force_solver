"""
diagram.py
DRAWING module of the Parallel Forces and Support Reaction Solver.
It builds the beam picture with Matplotlib from the user's real input
(no fixed image is ever used).

Two ways to use it:
    create_beam_figure(...)  -> builds the picture and RETURNS the figure
                                (used by gui.py to embed it in the window)
    draw_beam(...)           -> builds the picture, SAVES it as a PNG and
                                opens a window (used by main.py, console version)
"""

import os
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle

OUTPUT_FOLDER = "output"
FILE_NAME = "beam_diagram.png"


# ------------------------------------------------------------------ small tools
def make_output_folder(folder):
    """Creates the output folder the first time the program runs."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder


def tidy(value):
    """Avoids printing '-0.0000' inside the picture."""
    if abs(value) < 0.0001:
        return 0.0
    return value


def arrow_length(magnitude, biggest_magnitude, scale):
    """A bigger force gets a longer arrow, so the picture is meaningful."""
    if biggest_magnitude <= 0:
        return 2.0 * scale
    return (1.2 + 2.0 * (magnitude / biggest_magnitude)) * scale


# ------------------------------------------------------------------ the pieces
def draw_support(ax, x, top_y, height, kind):
    """
    Draws a pin (triangle) or a roller (triangle + two wheels) with hatched
    ground underneath.  Returns the y level of the ground line.
    """
    half_width = height * 0.6
    triangle = Polygon([(x, top_y),
                        (x - half_width, top_y - height),
                        (x + half_width, top_y - height)],
                       closed=True, facecolor="white", edgecolor="black", linewidth=1.5)
    ax.add_patch(triangle)

    ground_y = top_y - height

    if kind == "roller":
        radius = height * 0.17
        for wheel_x in (x - half_width * 0.55, x + half_width * 0.55):
            ax.add_patch(Circle((wheel_x, ground_y - radius), radius,
                                facecolor="white", edgecolor="black", linewidth=1.2))
        ground_y = ground_y - 2 * radius

    # ground line + hatching
    line_half = half_width * 1.9
    ax.plot([x - line_half, x + line_half], [ground_y, ground_y],
            color="black", linewidth=1.6)
    steps = 6
    for i in range(steps + 1):
        hx = x - line_half + (2 * line_half) * i / steps
        ax.plot([hx, hx - height * 0.30], [ground_y, ground_y - height * 0.30],
                color="black", linewidth=0.8)
    return ground_y


def draw_applied_force(ax, x, beam_top, magnitude, direction, length, scale, text, text_lift):
    """Red arrow pointing DOWN for a downward load, green arrow UP for an upward load."""
    start_y = beam_top + 0.15 * scale
    tip_y = start_y + length

    if direction < 0:                       # downward : head touches the beam
        ax.annotate("", xy=(x, start_y), xytext=(x, tip_y),
                    arrowprops=dict(arrowstyle="-|>", color="crimson",
                                    lw=2.2, mutation_scale=20))
    else:                                   # upward : head points away from the beam
        ax.annotate("", xy=(x, tip_y), xytext=(x, start_y),
                    arrowprops=dict(arrowstyle="-|>", color="green",
                                    lw=2.2, mutation_scale=20))

    label_y = tip_y + 0.25 * scale + text_lift
    ax.text(x, label_y, text, ha="center", va="bottom",
            fontsize=9.5, linespacing=1.5)
    return label_y + 1.0 * scale            # highest point used by this force


def draw_reaction(ax, x, ground_y, value, length, scale, text):
    """Reaction arrow drawn below the support. Navy = up, orange = down."""
    gap = 0.55 * scale
    bottom_y = ground_y - gap - length
    top_y = ground_y - gap
    colour = "navy" if value >= 0 else "darkorange"

    if value >= 0:                          # upward reaction, head toward the support
        ax.annotate("", xy=(x, top_y), xytext=(x, bottom_y),
                    arrowprops=dict(arrowstyle="-|>", color=colour,
                                    lw=2.4, mutation_scale=22))
    else:                                   # downward reaction, head pointing away
        ax.annotate("", xy=(x, bottom_y), xytext=(x, top_y),
                    arrowprops=dict(arrowstyle="-|>", color=colour,
                                    lw=2.4, mutation_scale=22))

    ax.text(x, bottom_y - 0.30 * scale, text, ha="center", va="top",
            fontsize=10, fontweight="bold", color=colour, linespacing=1.4)
    return bottom_y - 1.5 * scale           # lowest point used


def draw_dimension(ax, x1, x2, y, text, scale):
    """Dimension line with an arrowhead on both ends."""
    ax.annotate("", xy=(x1, y), xytext=(x2, y),
                arrowprops=dict(arrowstyle="<|-|>", color="dimgray",
                                lw=1.2, mutation_scale=14))
    ax.text((x1 + x2) / 2.0, y - 0.35 * scale, text,
            ha="center", va="top", fontsize=10, color="dimgray")


# ------------------------------------------------------------------ main drawing
def create_beam_figure(beam_length, forces, ra, rb, support_a, support_b,
                       sum_fy, sum_ma, sum_mb, balanced, figsize=(12, 7.5)):
    """
    Builds the whole picture and RETURNS the Matplotlib figure.
    It does NOT save a file and does NOT open a window, so the GUI can
    embed this figure inside its own window.
    """
    # ---- scale: everything is sized from the real beam length -------------
    scale = max(beam_length / 20.0, 0.35)
    beam_h = 0.55 * scale
    beam_top = beam_h / 2.0
    beam_bottom = -beam_h / 2.0
    support_h = 1.7 * scale

    biggest_load = 0.0
    for label, magnitude, direction, position in forces:
        if magnitude > biggest_load:
            biggest_load = magnitude
    biggest_reaction = max(abs(ra), abs(rb))

    fig, ax = plt.subplots(figsize=figsize)

    # ---- 1. the beam -------------------------------------------------------
    ax.add_patch(Rectangle((0, beam_bottom), beam_length, beam_h,
                           facecolor="#dcdcdc", edgecolor="black", linewidth=1.6))
    ax.text(beam_length / 2.0, 0.0, "BEAM", ha="center", va="center",
            fontsize=9, color="#555555")

    # ---- 2. the supports ---------------------------------------------------
    ground_a = draw_support(ax, support_a, beam_bottom, support_h, "pin")
    ground_b = draw_support(ax, support_b, beam_bottom, support_h, "roller")
    half = support_h * 0.6
    ax.text(support_a - 1.15 * half, beam_bottom - support_h / 2.0,
            f"A (pin)\nx = {support_a:.2f} m", ha="right", va="center", fontsize=9.5)
    ax.text(support_b + 1.15 * half, beam_bottom - support_h / 2.0,
            f"B (roller)\nx = {support_b:.2f} m", ha="left", va="center", fontsize=9.5)

    # ---- 3. the applied forces (labels staggered so they do not overlap) ----
    highest = beam_top
    index = 0
    for label, magnitude, direction, position in forces:
        index = index + 1
        length = arrow_length(magnitude, biggest_load, scale)
        sense = "(down)" if direction < 0 else "(up)"
        text = f"{label} = {magnitude:.2f} kN {sense}\nat x = {position:.2f} m"
        lift = 0.9 * scale if index % 2 == 0 else 0.0
        used = draw_applied_force(ax, position, beam_top, magnitude, direction,
                                  length, scale, text, lift)
        if used > highest:
            highest = used

    # ---- 4. the calculated support reactions -------------------------------
    text_a = f"RA = {abs(ra):.2f} kN\n({'up' if ra >= 0 else 'down'})"
    text_b = f"RB = {abs(rb):.2f} kN\n({'up' if rb >= 0 else 'down'})"
    low_a = draw_reaction(ax, support_a, ground_a, ra,
                          arrow_length(abs(ra), biggest_reaction, scale), scale, text_a)
    low_b = draw_reaction(ax, support_b, ground_b, rb,
                          arrow_length(abs(rb), biggest_reaction, scale), scale, text_b)
    lowest = min(low_a, low_b, ground_a - support_h, ground_b - support_h)

    # ---- 5. beam length dimension -----------------------------------------
    dim_y = lowest - 1.2 * scale
    ax.plot([0, 0], [beam_bottom, dim_y], color="dimgray", lw=0.8, linestyle=":")
    ax.plot([beam_length, beam_length], [beam_bottom, dim_y],
            color="dimgray", lw=0.8, linestyle=":")
    draw_dimension(ax, 0, beam_length, dim_y, f"L = {beam_length:.2f} m", scale)

    # ---- 6. picture limits and title --------------------------------------
    margin_x = max(2.2 * scale, beam_length * 0.09)
    ax.set_xlim(-margin_x, beam_length + margin_x)
    ax.set_ylim(dim_y - 2.4 * scale, highest + 2.0 * scale)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Beam Diagram - Parallel Forces and Support Reactions",
                 fontsize=13, fontweight="bold")

    # ---- 7. result summary under the picture ------------------------------
    verdict = "EQUILIBRIUM OK" if balanced else "NOT IN EQUILIBRIUM"
    summary = (f"RA = {ra:+.2f} kN at x = {support_a:.2f} m        "
               f"RB = {rb:+.2f} kN at x = {support_b:.2f} m\n"
               f"Check :  Sum Fy = {tidy(sum_fy):+.4f} kN     "
               f"Sum M_A = {tidy(sum_ma):+.4f} kN.m     "
               f"Sum M_B = {tidy(sum_mb):+.4f} kN.m     -->  {verdict}")
    fig.subplots_adjust(left=0.03, right=0.97, top=0.92, bottom=0.15)
    fig.text(0.5, 0.035, summary, ha="center", va="bottom",
             fontsize=9.5, family="monospace")

    # ---- 8. hand the figure back to the caller -----------------------------
    return fig


def draw_beam(beam_length, forces, ra, rb, support_a, support_b,
              sum_fy, sum_ma, sum_mb, balanced,
              folder=OUTPUT_FOLDER, show_window=True):
    """
    Console version (used by main.py): builds the picture with
    create_beam_figure, saves it as a PNG and opens a window.
    """
    make_output_folder(folder)
    fig = create_beam_figure(beam_length, forces, ra, rb, support_a, support_b,
                             sum_fy, sum_ma, sum_mb, balanced)

    file_path = os.path.join(folder, FILE_NAME)
    fig.savefig(file_path, dpi=160)
    print(f"  Beam diagram saved as : {file_path}")

    if show_window:
        try:
            plt.show()
        except Exception:
            print("  The diagram window could not be opened, but the PNG file is saved.")
    plt.close(fig)
    return file_path