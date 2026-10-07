"""
solver.py
ENGINEERING module of the Parallel Forces and Support Reaction Solver.
Only math lives here: no input(), no print(), no drawing.

SIGN CONVENTION
    upward force             = positive (+)
    downward force           = negative (-)
    counter-clockwise moment = positive (+)

EQUATIONS OF STATIC EQUILIBRIUM
    (1)  Sum Fy = 0
    (2)  Sum M  = 0
    Moment of a force about a pivot P = Fy * (x_force - x_pivot)

SOLUTION STRATEGY
    Sum M about A  ->  RA has zero lever arm  ->  solve for RB
    Sum Fy = 0     ->  solve for RA
    Then verify with Sum Fy, Sum M_A and Sum M_B.
"""

TOLERANCE = 0.0001        # a result smaller than this is treated as zero


def clean(value):
    """Turns round-off junk like -3.5e-15 into exactly 0.0"""
    if abs(value) < TOLERANCE:
        return 0.0
    return value


# ------------------------------------------------------------- single force math
def signed_force(force):
    """Converts (magnitude, direction) into one signed number Fy."""
    label, magnitude, direction, position = force
    return magnitude * direction


def lever_arm(position, pivot):
    """Distance from the pivot to the force, WITH its sign."""
    return position - pivot


def moment_of_force(force, pivot):
    """Moment = Force * Distance  (requirement of the project)."""
    label, magnitude, direction, position = force
    return signed_force(force) * lever_arm(position, pivot)


# ------------------------------------------------------------------ group math
def total_force(forces):
    """Sum Fy of the APPLIED forces only (reactions not included)."""
    total = 0.0
    for force in forces:
        total = total + signed_force(force)
    return total


def total_moment_about(forces, pivot):
    """Sum M of the APPLIED forces about any pivot point."""
    total = 0.0
    for force in forces:
        total = total + moment_of_force(force, pivot)
    return total


# ------------------------------------------------------------------ the solver
def solve_reactions(forces, support_a, support_b):
    """
    Returns (RA, RB) as signed numbers (positive = acting upward).

    Step 1 : Sum M_A = 0
             moment_loads_A + RB * (xB - xA) = 0
             RB = -moment_loads_A / (xB - xA)
    Step 2 : Sum Fy = 0
             RA + RB + total_load = 0
             RA = -total_load - RB
    """
    span = support_b - support_a
    moment_loads_a = total_moment_about(forces, support_a)

    rb = -moment_loads_a / span
    ra = -total_force(forces) - rb
    return ra, rb


def check_equilibrium(forces, ra, rb, support_a, support_b):
    """Recomputes the three equilibrium sums WITH the reactions included."""
    span = support_b - support_a
    sum_fy = total_force(forces) + ra + rb
    sum_ma = total_moment_about(forces, support_a) + rb * span
    sum_mb = total_moment_about(forces, support_b) + ra * (-span)
    return sum_fy, sum_ma, sum_mb


def is_balanced(sum_fy, sum_ma, sum_mb):
    """True only when all three sums are (practically) zero."""
    if abs(sum_fy) <= TOLERANCE and abs(sum_ma) <= TOLERANCE and abs(sum_mb) <= TOLERANCE:
        return True
    return False


# ------------------------------------------------------------------ bonus part
def build_shear_table(forces, ra, rb, support_a, support_b):
    """
    Walks from the left end to the right end and adds every force on the way.
    The running total is the SHEAR FORCE just to the right of that point.
    The last value must be 0.00 (one more proof that the answers are right).

    Returns a list of rows: (position, label, force_value, shear_after)
    """
    points = []
    for force in forces:
        label, magnitude, direction, position = force
        points.append((position, label, magnitude * direction))
    points.append((support_a, "RA", ra))
    points.append((support_b, "RB", rb))
    points.sort()                     # sort by x position

    rows = []
    shear = 0.0
    for position, label, value in points:
        shear = shear + value
        rows.append((position, label, value, clean(shear)))
    return rows