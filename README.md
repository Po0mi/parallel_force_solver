## What is this program?

This program solves a beam problem from Statics.

Think of a beam like a plank. It rests on two supports (left and right).
Forces push the beam down (or up) at different points.
The supports push back. These pushes are called **reactions**.

The program does this:

1. Asks for the length of the beam.
2. Asks for the forces: how big, up or down, and where on the beam.
3. Calculates the two support reactions (R1 and R2).
4. Shows every step of the math, not just the answer.
5. Checks if the beam is balanced (equilibrium).
6. Draws a picture of the beam with all forces and reactions.

---

## Files in this project

| File               | What it does                                          |
| ------------------ | ----------------------------------------------------- |
| `main.py`          | The typed version. **Run this one.**                  |
| `gui.py`           | The window version with buttons. **Or run this one.** |
| `forces.py`        | Asks the questions and reads your answers             |
| `solver.py`        | Does all the math                                     |
| `report.py`        | Prints the steps on the screen                        |
| `diagram.py`       | Draws the beam picture                                |
| `sample_input.txt` | Ready-made answers for a quick test                   |
| `output/`          | Folder where the picture is saved                     |

---

## What you need

- Python 3
- Matplotlib (the drawing library)

Install it once with this command:

```
pip install matplotlib
```

---

## How to run

Open a terminal inside the project folder, then:

**Typed version:**

```
python main.py
```

**Window version:**

```
python gui.py
```

**Quick test (no typing needed):**

```
python main.py < sample_input.txt
```

---

## How to use the window version

1. Click **Start**.
2. Type the beam length, example: `20`.
3. Type the number of loads, example: `3`, then click **Set Loads**.
4. Fill each row: size, direction (down or up), distance.
5. Leave R1 and R2 empty (the program will use 0 and the beam length).
6. Click **Calculate Reactions**.
7. You will see R1, R2 and the beam picture.
8. **Show Steps** = see all the math. **Clear** = erase. **Back** = start screen.

---

## Example and answer

Beam = 20 m long.
Forces: 5 kN down at 4 m, 19 kN down at 11 m, 8 kN down at 16 m.

The program gives:

```
R1 (left support)  = 14.15 kN up
R2 (right support) = 17.85 kN up
All checks = 0.0000  ->  the beam is balanced. Correct.
```

---

## The math, in simple words

Two rules keep the beam still:

- **Rule 1:** total push up = total push down. (Sum Fy = 0)
- **Rule 2:** the beam must not turn. All turning effects must cancel. (Sum M = 0)

A turning effect is called a **moment**:

```
Moment = Force x Distance from the point
```

Steps the program follows:

1. Take moments about the left support. This finds R2 first.
2. Use Rule 1 to find R1.
3. Put the answers back into both rules to check. Everything must be about 0.

Signs used: up = positive, down = negative.

---

## Tests done

- Test 1: the class example above -> R1 = 14.15, R2 = 17.85. Correct.
- Test 2: 10 m beam, 10 kN in the middle -> R1 = 5, R2 = 5. Correct.
- Test 3: 10 m beam, 20 kN down at 3 m and 5 kN up at 8 m -> R1 = 13, R2 = 2. Correct.

In all tests the checks showed 0.0000, so equilibrium was OK.

---

## What the program cannot do

- Only 2 supports (not 3 or more).
- Only vertical forces (no sideways pushes).
- No spread-out loads. Change them into one force first.
- The weight of the beam itself is not added automatically.

---

## Where the picture is saved

- Typed version: `output/beam_diagram.png`
- Window version: shown inside the window.
