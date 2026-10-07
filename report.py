"""
report.py
PRINTING module of the Parallel Forces and Support Reaction Solver.
It only shows the calculations on the screen with formatted print statements.
All the numbers come from solver.py.
"""

import solver

WIDTH = 68
LINE = "=" * WIDTH
THIN = "-" * WIDTH
SMALL = "-" * 58


# ------------------------------------------------------------------ small tools
def direction_word(direction):
    if direction > 0:
        return "upward"
    return "downward"


def reaction_word(value):
    if value >= 0:
        return "UPWARD"
    return "DOWNWARD"


def mark(value):
    """Short verdict used in the equilibrium check."""
    if abs(value) <= solver.TOLERANCE:
        return "OK"
    return "NOT OK"


# ---------------------------------------------------------------- title / step 1
def print_title():
    print(LINE)
    print("         PARALLEL FORCES AND SUPPORT REACTION SOLVER")
    print("         Vertical (parallel) loads on a simply supported beam")
    print(LINE)
    print("Sign convention used in this program:")
    print("     upward force              = positive (+)")
    print("     downward force            = negative (-)")
    print("     counter-clockwise moment  = positive (+)")
    print()
    print("Equilibrium equations used :   Sum Fy = 0    and    Sum M = 0")
    print(LINE)


def print_input_summary(beam_length, force_list, support_a, support_b):
    print()
    print("STEP 1 : INPUT SUMMARY")
    print(THIN)
    print(f"  Beam length L            : {beam_length:.2f} m")
    print(f"  Support A (pin)          : x = {support_a:.2f} m")
    print(f"  Support B (roller)       : x = {support_b:.2f} m")
    print(f"  Span between supports    : {support_b - support_a:.2f} m")
    print(f"  Number of applied forces : {len(force_list)}")
    print()
    print("  Applied forces (a force is stored as magnitude + sign):")
    for label, magnitude, direction, position in force_list:
        fy = magnitude * direction
        print(f"    {label} : {magnitude:>7.2f} kN  {direction_word(direction):<9}"
              f" at x = {position:>6.2f} m   ->   Fy = {fy:+.2f} kN")
    print(SMALL)
    print(f"  Sum of the applied vertical forces  =  {solver.total_force(force_list):+.2f} kN")


# ----------------------------------------------------------------------- step 2
def print_moment_step(force_list, pivot, pivot_name):
    """Shows Moment = Force x Distance for EVERY force, then the total."""
    print()
    print(f"STEP 2 : MOMENTS OF THE APPLIED FORCES ABOUT {pivot_name}  (x = {pivot:.2f} m)")
    print(THIN)
    print("  Formula :  Moment = Fy * (x_force - x_pivot)     counter-clockwise = +")
    print("  RA is not listed because it acts AT point A, so its lever arm is 0.")
    print()
    for label, magnitude, direction, position in force_list:
        fy = magnitude * direction
        arm = position - pivot
        moment = fy * arm
        print(f"    {label} : M = ({fy:+.2f}) * ({position:.2f} - {pivot:.2f})"
              f" = ({fy:+.2f}) * ({arm:+.2f}) = {moment:+.2f} kN.m")
    print(SMALL)
    total = solver.total_moment_about(force_list, pivot)
    print(f"  Sum of the moments of the loads about {pivot_name}  =  {total:+.2f} kN.m")
    return total


# ----------------------------------------------------------------------- step 3
def print_solve_rb(moment_loads_a, support_a, support_b, rb):
    span = support_b - support_a
    print()
    print("STEP 3 : FIND RB USING  Sum M_A = 0   (moment equation about support A)")
    print(THIN)
    print("  Taking moments about A removes RA from the equation,")
    print("  so RB is the only unknown left.")
    print()
    print("  Sum M_A = 0")
    print("  (moment of the loads about A) + RB * (xB - xA) = 0")
    print(f"  {moment_loads_a:+.2f} + RB * ({support_b:.2f} - {support_a:.2f}) = 0")
    print(f"  RB * {span:.2f} = {-moment_loads_a:+.2f}")
    print(f"  RB = {-moment_loads_a:+.2f} / {span:.2f}")
    print(f"  RB = {rb:.2f} kN     -> the reaction acts {reaction_word(rb)}")


# ----------------------------------------------------------------------- step 4
def print_solve_ra(load_total, rb, ra):
    print()
    print("STEP 4 : FIND RA USING  Sum Fy = 0   (vertical force equation)")
    print(THIN)
    print("  Sum Fy = 0")
    print("  RA + RB + (sum of the applied forces) = 0")
    print(f"  RA + ({rb:+.2f}) + ({load_total:+.2f}) = 0")
    print(f"  RA = -({load_total:+.2f}) - ({rb:+.2f})")
    print(f"  RA = {ra:.2f} kN     -> the reaction acts {reaction_word(ra)}")


# ----------------------------------------------------------------------- step 5
def print_equilibrium_check(force_list, ra, rb, support_a, support_b):
    """REQUIREMENT 8 : verify that Sum Fy = 0 and Sum M = 0."""
    sum_fy, sum_ma, sum_mb = solver.check_equilibrium(force_list, ra, rb,
                                                      support_a, support_b)
    loads = solver.total_force(force_list)
    ma_loads = solver.total_moment_about(force_list, support_a)
    mb_loads = solver.total_moment_about(force_list, support_b)
    span = support_b - support_a

    print()
    print("STEP 5 : EQUILIBRIUM CHECK  (the answers are put back into the equations)")
    print(THIN)
    print(f"  Tolerance used : {solver.TOLERANCE}")
    print()
    print(f"  Sum Fy  = ({loads:+.2f}) + ({ra:+.2f}) + ({rb:+.2f})"
          f" = {solver.clean(sum_fy):.4f} kN      [{mark(sum_fy)}]")
    print(f"  Sum M_A = ({ma_loads:+.2f}) + ({rb:+.2f}) * ({span:+.2f})"
          f" = {solver.clean(sum_ma):.4f} kN.m   [{mark(sum_ma)}]")
    print(f"  Sum M_B = ({mb_loads:+.2f}) + ({ra:+.2f}) * ({-span:+.2f})"
          f" = {solver.clean(sum_mb):.4f} kN.m   [{mark(sum_mb)}]")
    print()
    if solver.is_balanced(sum_fy, sum_ma, sum_mb):
        print("  --> RESULT : The system IS in equilibrium. The reactions are correct.")
        return True
    print("  --> RESULT : WARNING, the system is NOT in equilibrium. Check the input.")
    return False


# ----------------------------------------------------------------------- step 6
def print_final_answers(ra, rb, support_a, support_b, force_list):
    down_total = 0.0
    up_total = 0.0
    for label, magnitude, direction, position in force_list:
        if direction > 0:
            up_total = up_total + magnitude
        else:
            down_total = down_total + magnitude
    if ra >= 0:
        up_total = up_total + ra
    else:
        down_total = down_total - ra
    if rb >= 0:
        up_total = up_total + rb
    else:
        down_total = down_total - rb

    print()
    print("STEP 6 : FINAL SUPPORT REACTIONS")
    print(THIN)
    print(f"  Reaction at A (x = {support_a:.2f} m) :  RA = {abs(ra):.2f} kN  acting {reaction_word(ra)}")
    print(f"  Reaction at B (x = {support_b:.2f} m) :  RB = {abs(rb):.2f} kN  acting {reaction_word(rb)}")
    print()
    print(f"  Total downward force = {down_total:.2f} kN")
    print(f"  Total upward force   = {up_total:.2f} kN")
    if ra < 0 or rb < 0:
        print()
        print("  NOTE : a negative reaction means that support must hold the beam")
        print("         DOWNWARD (the beam is trying to lift off that support).")


# ----------------------------------------------------------------- bonus (step 7)
def print_shear_table(rows):
    print()
    print("BONUS : INTERNAL SHEAR FORCE ALONG THE BEAM")
    print(THIN)
    print("  Walking from left to right, adding every force we pass.")
    print("  The shear value is the internal force just to the RIGHT of that point.")
    print()
    print(f"      {'x (m)':>8}    {'Item':<6}{'Force (kN)':>13}{'Shear (kN)':>14}")
    print(SMALL)
    for position, label, value, shear in rows:
        print(f"      {position:>8.2f}    {label:<6}{value:>13.2f}{shear:>14.2f}")
    print(SMALL)
    print("  The last shear value is 0.00 -> the beam closes in equilibrium.")


def print_diagram_message():
    print()
    print("STEP 7 : BEAM DIAGRAM")
    print(THIN)
    print("  Drawing the beam with Matplotlib from your real input, please wait...")


def print_goodbye():
    print()
    print(LINE)
    print("  Thank you for using the Parallel Forces and Support Reaction Solver.")
    print(LINE)