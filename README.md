# Parallel Forces and Support Reaction Solver

**Course:** Computer Fundamentals and Programming for Civil Engineering
**Author:** [Your Name Here]
**Stub Code:** [Your Stub Code Here]

A Python program that solves parallel-force and support-reaction problems
commonly encountered in Statics. The user enters the beam length and any
number of vertical forces (magnitude, direction and position); the program
calculates the two support reactions using the equations of static
equilibrium, prints every step of the solution, verifies equilibrium and
draws the beam diagram.

Two interfaces are included:

- **Console version** – `main.py` (typed input, printed step-by-step solution)
- **Graphical version** – `gui.py` (tkinter window with the diagram embedded)

Both versions use the _same_ calculation module (`solver.py`) and the _same_
drawing module (`diagram.py`), so they always give identical results.

---

## 1. Features

- Accepts the beam length and the positions of the two supports
  (defaults: supports at 0 m and at the beam length).
- Accepts any number of vertical forces (1–50 in console, 1–10 in GUI).
- Each force has a **magnitude (kN)**, a **direction (upward / downward)**
  and a **position (m)** measured from the left end of the beam.
- Calculates the support reactions using:
  - `Sum M = 0` about the left support -> gives the right reaction
  - `Sum Fy = 0` -> gives the left reaction
- Shows the full calculation (every moment, every equation), not just answers.
- Checks equilibrium: `Sum Fy ≈ 0`, `Sum M_A ≈ 0`, `Sum M_B ≈ 0`
  (tolerance = 0.0001).
- Handles both upward and downward forces, and reports a negative reaction
  (support must hold the beam down).
- Bonus: internal shear force table along the beam.
- Generates a beam diagram with Matplotlib **from the user's real input**:
  beam, pin and roller supports, force arrows with labels and positions,
  reaction arrows, support labels and the overall beam length dimension.
  The picture is saved as `output/beam_diagram.png` (console version) and is
  embedded in the window (GUI version).

---

## 2. Project Structure

```
parallel_forces_solver/
│
├── main.py              ← RUN THIS: console version (program flow)
├── gui.py               ← RUN THIS: graphical version (tkinter + embedded plot)
├── forces.py            ← all user input and validation (console)
├── solver.py            ← all statics calculations (pure math, no printing)
├── report.py            ← formatted step-by-step printout (console)
├── diagram.py           ← Matplotlib beam drawing (figure builder + PNG saver)
│
├── requirements.txt     ← project dependencies (matplotlib)
├── sample_input.txt     ← the 20 m class example for automatic testing
├── README.md            ← this file
│
└── output/              ← created automatically; holds beam_diagram.png
```

---

## 3. Requirements

- Python **3.7 or newer** (tkinter is included with Python)
- Matplotlib

Install the dependency once:

```
pip install matplotlib
```

---

## 4. How to Run

Open a terminal **inside the project folder**, then choose a version:

### 4.1 Console version (typed input)

```
python main.py
```

### 4.2 Automatic test (no typing, uses the class example)

```
python main.py < sample_input.txt
```

### 4.3 Graphical version

```
python gui.py
```

GUI screens:

1. **Start screen** – title, description, `Start` button, author line.
2. **Input screen** – beam length, number of loads, `Set Loads` builds one
   row per load (magnitude + direction dropdown + distance), support
   positions R1/R2 (leave blank for the defaults 0 and L).
3. **Results** – `Calculate Reactions` shows R1 and R2, the equilibrium
   verdict and the beam diagram on the right; `Show Steps` opens the full
   step-by-step calculation; `Back` and `Clear` reset the screen.

---

## 5. Example Input (class problem)

| Item        | Value                   |
| ----------- | ----------------------- |
| Beam length | 20 m                    |
| Supports    | 0 m and 20 m (defaults) |
| Force 1     | 5 kN downward at 4 m    |
| Force 2     | 19 kN downward at 11 m  |
| Force 3     | 8 kN downward at 16 m   |

Console input sequence: `20`, _Enter_, _Enter_, `3`, then for each force
`5 / 2 / 4`, `19 / 2 / 11`, `8 / 2 / 16` (direction `2` = downward),
finally `n` to exit.

### Expected result

```
Sum of applied forces      = -32.00 kN
Sum of moments about A     = -357.00 kN.m
RB = 357.00 / 20.00        =  17.85 kN (upward)
RA = 32.00 - 17.85         =  14.15 kN (upward)
Sum Fy = 0.0000  |  Sum M_A = 0.0000  |  Sum M_B = 0.0000  ->  EQUILIBRIUM OK
```

---

## 6. Engineering Background

**Sign convention**

| Quantity            | Positive (+)      | Negative (−) |
| ------------------- | ----------------- | ------------ |
| Vertical force `Fy` | upward            | downward     |
| Moment `M`          | counter-clockwise | clockwise    |

**Equations of static equilibrium**

```
Sum Fy = 0
Sum M  = 0
Moment of a force about a pivot P = Fy * (x_force - x_pivot)
```

**Solution strategy**

1. Take moments about support A. The left reaction passes through A
   (lever arm = 0), so the equation contains only one unknown:

   `RB = -(sum of moments of the loads about A) / (xB - xA)`

2. Use vertical equilibrium for the second reaction:

   `RA = -(sum of applied forces) - RB`

3. Verify by substituting the answers back into
   `Sum Fy`, `Sum M_A` and `Sum M_B`; all three must be ≈ 0.

A **negative reaction** means the support must pull the beam downward
(the beam tends to lift off that support).

---

## 7. Testing Performed

| Test                | Input                                                 | Expected                         | Result |
| ------------------- | ----------------------------------------------------- | -------------------------------- | ------ |
| 1. Class example    | L = 20 m; 5 kN ↓ @ 4 m; 19 kN ↓ @ 11 m; 8 kN ↓ @ 16 m | RA = 14.15 kN ↑, RB = 17.85 kN ↑ | PASS   |
| 2. Symmetric load   | L = 10 m; 10 kN ↓ @ 5 m                               | RA = RB = 5.00 kN ↑              | PASS   |
| 3. Mixed directions | L = 10 m; 20 kN ↓ @ 3 m; 5 kN ↑ @ 8 m                 | RA = 13.00 kN ↑, RB = 2.00 kN ↑  | PASS   |

In every test the equilibrium check returned
`Sum Fy = 0.0000`, `Sum M_A = 0.0000`, `Sum M_B = 0.0000`, and the last row
of the shear table closed at 0.00.

---

## 8. Program Flow

1. Display the title and sign convention.
2. Ask for the beam length.
3. Ask for the support positions (defaults available).
4. Ask how many forces will be entered.
5. Loop: read magnitude, direction and position of each force.
6. Calculate the moment of every force about support A.
7. Solve RB from `Sum M_A = 0`, then RA from `Sum Fy = 0`.
8. Check equilibrium (`Sum Fy`, `Sum M_A`, `Sum M_B`).
9. Display the complete calculation and the final reactions.
10. Generate and save/show the beam diagram.

---

## 9. Limitations

- Exactly **two supports** (three or more = statically indeterminate).
- **Vertical point loads only** – no horizontal loads and no applied couples.
- Distributed loads must be converted by the user into an equivalent point
  load (`W = w * length`, placed at the centre of the loaded length).
- Beam self-weight is not added automatically (enter it as one more
  downward force at L/2 if needed).

---

## 10. Possible Extensions

- Automatic conversion of uniform distributed loads.
- Shear force and bending moment diagrams plotted under the beam.
- Export the step-by-step solution to a text file.
- Allow movable supports in the GUI by dragging them with the mouse.

---

## 11. File Description

| File               | Purpose                                                                             |
| ------------------ | ----------------------------------------------------------------------------------- |
| `main.py`          | Program flow of the console version (input → math → print → diagram)                |
| `gui.py`           | Graphical version: start screen, input screen, embedded diagram                     |
| `forces.py`        | All `input()` calls and input validation (console)                                  |
| `solver.py`        | Statics math only: totals, moments, reactions, equilibrium check, shear table       |
| `report.py`        | Formatted step-by-step printing (console)                                           |
| `diagram.py`       | `create_beam_figure()` builds the picture; `draw_beam()` saves the PNG and shows it |
| `requirements.txt` | Lists `matplotlib`                                                                  |
| `sample_input.txt` | Ready-made input file with the 20 m class example                                   |
