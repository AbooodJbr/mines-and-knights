# CS50 AI Knowledge Projects

This workspace contains two small logic-based projects from Harvard's CS50 AI course.

## Projects
- **Knights**: Propositional logic engine for solving knights-and-knaves puzzles. See `knights/logic.py` for the sentence primitives and `knights/puzzle.py` for sample puzzles.
- **Minesweeper**: Minesweeper game with a knowledge-based AI. Core logic lives in `minesweeper/minesweeper.py`; a Pygame GUI is provided in `minesweeper/runner.py`.

## Running
- Knights puzzles (CLI):
  1. Navigate to the `knights` directory.
  2. Run `python puzzle.py` to print the truths inferred for each puzzle.
- Minesweeper GUI:
  1. Install Pygame (`pip install pygame`).
  2. From the `minesweeper` directory run `python runner.py` to start the game.
  3. Left-click to reveal, right-click to flag, or press the AI Move button to let the agent choose.

## Notes
- GUI: The Minesweeper project already includes a GUI; the Knights project remains CLI-oriented. If you want a small GUI for Knights, we can add a simple visualization or web front-end on request.
- Notebooks: No notebooks are present in this workspace. If you add any, we can populate them with markdown context and narration.
- Docstrings: Functions across the codebase now include docstrings for quick reference.
