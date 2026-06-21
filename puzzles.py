"""Definition of puzzles for water sorting.

This file just needs to export PUZZLE_TO_SOLVE which main.py expects to be an
iterable of iterables with up to main.Tube.MAX_TUBE_CAPACITY elements. Each
element should be a hex colour string, i.e. #000000 is black. The iterable can
be empty for an empty tube (and the convenience EMPTY_TUBE exists for this).
"""

EMPTY_TUBE = ()

RED = "#ff0000"
BLUE = "#0000ff"
GREEN = "#00ff00"

SIMPLE_THREE_TUBE = (
    (RED, BLUE, RED, BLUE),
    (BLUE, RED, BLUE, RED),
    EMPTY_TUBE,
)

# Level 4 from https://poki.com/en/g/water-color-sort, purple mapped to blue
POKI_LVL4 = (
    (GREEN, BLUE),
    (RED, RED, GREEN),
    (BLUE, RED, GREEN),
    (GREEN, RED),
    (BLUE, BLUE),
)

del RED, GREEN, BLUE

# Level 114 from the Water Sort app
PALE_GREEN = "#62d67c"
LIME_GREEN = "#78960e"
DARK_GREEN = "#106533"
GREY = "#636465"
PALE_BLUE = "#55a3e5"
DARK_BLUE = "#3a2ec3"
ORANGE = "#e88c42"
PURPLE = "#722b93"
PINK = "#ea5e7b"
YELLOW = "#f1da58"
RED = "#c52a23"
BROWN = "#7e4a07"

WATER_SORT_LVL114 = (
    (ORANGE, PALE_BLUE, GREY, PALE_GREEN),
    (YELLOW, PINK, ORANGE, ORANGE),
    (DARK_GREEN, RED, ORANGE, YELLOW),
    (PALE_BLUE, DARK_BLUE, PURPLE, PURPLE),
    (DARK_BLUE, BROWN, DARK_GREEN, YELLOW),
    (LIME_GREEN, PINK, DARK_BLUE, RED),
    (BROWN, DARK_BLUE, BROWN, PALE_BLUE),
    (PALE_BLUE, GREY, PINK, LIME_GREEN),
    (PURPLE, RED, LIME_GREEN, PINK),
    (RED, LIME_GREEN, PALE_GREEN, YELLOW),
    (PALE_GREEN, BROWN, GREY, GREY),
    (DARK_GREEN, DARK_GREEN, PURPLE, PALE_GREEN),
    EMPTY_TUBE,
    EMPTY_TUBE,
)

PUZZLE_TO_SOLVE = POKI_LVL4
