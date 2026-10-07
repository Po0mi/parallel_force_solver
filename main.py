"""
main.py
PARALLEL FORCES AND SUPPORT REACTION SOLVER
Computer Fundamentals and Programming for Civil Engineering

This file only controls the PROGRAM FLOW:

    USER INPUT  ->  ENGINEERING CALCULATIONS  ->  SHOW CALCULATIONS
                ->  EQUILIBRIUM CHECK  ->  FINAL REACTIONS  ->  BEAM DIAGRAM

    forces.py   reads the input
    solver.py   does the statics math
    report.py   prints the step-by-step solution
    diagram.py  draws the beam picture

Run with:   python main.py
"""

import forces
import solver
import report
import diagram


def solve_one_beam():
    """Runs one complete problem from input to diagram."""

    # ---------------- INPUT (requirements 1 to 5) ----------------
    beam_length = forces.get_beam_length()
    support_a, support_b = forces.get_support_positions(beam_length)
    number_of_forces = forces.get_number_of_forces()
    force_list = forces.get_forces(number_of_forces, beam_length)

    # ---------------- CALCULATIONS (requirement 6) ----------------
    ra, rb = solver.solve_reactions(force_list, support_a, support_b)
    sum_fy, sum_ma, sum_mb = solver.check_equilibrium(force_list, ra, rb,
                                                      support_a, support_b)
    balanced = solver.is_balanced(sum_fy, sum_ma, sum_mb)
    shear_rows = solver.build_shear_table(force_list, ra, rb,
                                          support_a, support_b)

    # ---------------- SHOW THE SOLUTION (requirement 7) ----------------
    report.print_input_summary(beam_length, force_list, support_a, support_b)

    moment_loads_a = report.print_moment_step(force_list, support_a, "A")
    report.print_solve_rb(moment_loads_a, support_a, support_b, rb)
    report.print_solve_ra(solver.total_force(force_list), rb, ra)

    # ---------------- EQUILIBRIUM CHECK (requirement 8) ----------------
    report.print_equilibrium_check(force_list, ra, rb, support_a, support_b)

    # ---------------- FINAL ANSWERS ----------------
    report.print_final_answers(ra, rb, support_a, support_b, force_list)

    # ---------------- BONUS : shear along the beam ----------------
    report.print_shear_table(shear_rows)

    # ---------------- BEAM DIAGRAM (requirement 9) ----------------
    report.print_diagram_message()
    diagram.draw_beam(beam_length, force_list, ra, rb, support_a, support_b,
                      sum_fy, sum_ma, sum_mb, balanced)


def main():
    report.print_title()
    while True:
        solve_one_beam()
        print()
        again = input("Solve another beam? (y = yes, anything else = exit): ")
        if again.strip().lower() != "y":
            break
    report.print_goodbye()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by the user (Ctrl + C).")