"""
forces.py
INPUT module of the Parallel Forces and Support Reaction Solver.
Computer Fundamentals and Programming for Civil Engineering.

Every function here talks to the user with input() and returns clean numbers.
No engineering math happens in this file.

A force is stored as a tuple with 4 items:
        (label, magnitude, direction, position)
    label      -> "F1", "F2", "F3", ...
    magnitude  -> size of the force in kN (always a positive number)
    direction  -> +1 = upward ,  -1 = downward
    position   -> distance in meters from the LEFT end of the beam
"""

UPWARD = 1
DOWNWARD = -1


# ---------------------------------------------------------------- basic input
def get_float(prompt):
    """Keep asking until the user types a real number."""
    while True:
        answer = input(prompt).strip()
        try:
            return float(answer)
        except ValueError:
            print("      Please type a number, for example 12.5")


def get_positive_float(prompt):
    """Keep asking until the user types a number bigger than zero."""
    while True:
        value = get_float(prompt)
        if value > 0:
            return value
        print("      The value must be greater than zero.")


def get_direction():
    """Ask if the force acts upward or downward. Returns +1 or -1."""
    while True:
        answer = input("   Direction (1 = upward, 2 = downward): ").strip().lower()
        if answer in ("1", "u", "up", "upward"):
            return UPWARD
        if answer in ("2", "d", "dn", "down", "downward"):
            return DOWNWARD
        print("      Please type 1 for upward or 2 for downward.")


# ------------------------------------------------------------ beam and supports
def get_beam_length():
    """REQUIREMENT 1 : accept the beam length."""
    print()
    return get_positive_float("Enter the beam length in meters: ")


def get_position_or_default(prompt, default, beam_length):
    """Reads a support position. An empty line (just ENTER) uses the default."""
    while True:
        answer = input(prompt).strip()
        if answer == "":
            return default
        try:
            value = float(answer)
        except ValueError:
            print("      Type a number, or just press ENTER for the default.")
            continue
        if value < 0 or value > beam_length:
            print(f"      The support must be between 0 and {beam_length:g} m.")
            continue
        return value


def get_support_positions(beam_length):
    """Returns (xA, xB). Default = 0 m and L m. A is always the left support."""
    print()
    print("Position of the two supports (press ENTER to accept the default).")
    while True:
        left = get_position_or_default("  Left  support A at x = ? m [0]: ",
                                       0.0, beam_length)
        right = get_position_or_default(f"  Right support B at x = ? m [{beam_length:g}]: ",
                                        beam_length, beam_length)
        if left == right:
            print("      The two supports cannot be at the same place. Try again.")
            continue
        if left > right:
            left, right = right, left
            print("      The supports were swapped so that A is the left one.")
        return left, right


# ---------------------------------------------------------------------- forces
def get_number_of_forces():
    """REQUIREMENT 2 : accept how many vertical forces will be entered."""
    print()
    while True:
        answer = input("How many vertical forces will you enter? ").strip()
        try:
            number = int(answer)
        except ValueError:
            print("      Please type a whole number, for example 3")
            continue
        if number < 1:
            print("      You must enter at least one force.")
            continue
        if number > 50:
            print("      Please enter 50 forces or fewer.")
            continue
        return number


def get_force_position(prompt, beam_length):
    """REQUIREMENT 5 : the position must be somewhere on the beam."""
    while True:
        value = get_float(prompt)
        if 0 <= value <= beam_length:
            return value
        print(f"      The force must be between 0 and {beam_length:g} m.")


def get_forces(number_of_forces, beam_length):
    """REQUIREMENTS 3, 4 and 5 : the loop that reads every force."""
    force_list = []
    for index in range(1, number_of_forces + 1):
        print()
        print(f"--- Force {index} of {number_of_forces} ---")
        magnitude = get_positive_float("   Magnitude in kN: ")
        direction = get_direction()
        position = get_force_position("   Position from the left end in m: ",
                                      beam_length)
        label = "F" + str(index)
        force_list.append((label, magnitude, direction, position))
    return force_list


def describe_force(force):
    """Returns one force as a readable sentence."""
    label, magnitude, direction, position = force
    word = "upward" if direction == UPWARD else "downward"
    return f"{label} = {magnitude:.2f} kN {word} at x = {position:.2f} m"