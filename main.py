"""Simulate the water sort game"""
from collections import namedtuple
from copy import deepcopy
from pprint import pprint

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

RED = "#ff0000"
BLUE = "#0000ff"
GREEN = "#00ff00"

Move = namedtuple("Move", ["source", "dest", "count"])


class Tube:

    MAX_TUBE_CAPACITY = 4

    def __init__(self, idx, *colours):
        """Given a list of hex codes."""
        assert len(colours) <= self.MAX_TUBE_CAPACITY
        self._colours = list(colours)
        self.idx = idx

    def draw(self, ax, left_x, bottom_y):
        """Given an axis and the coordinates of the bottom left corner, draw the tube."""
        for (pos, colour) in enumerate(self._colours):
            ax.add_patch(Rectangle((left_x, bottom_y + pos), 1, 1, color=colour))

        tube_outline = (
            (left_x, bottom_y + self.MAX_TUBE_CAPACITY),
            (left_x, bottom_y),
            (left_x + 1, bottom_y),
            (left_x + 1, bottom_y + self.MAX_TUBE_CAPACITY),
        )
        ax.plot([x for (x, _) in tube_outline], [y for (_, y) in tube_outline], color="k", linewidth=2)

    @property
    def is_empty(self):
        return len(self._colours) == 0

    @property
    def top_colour(self):
        return None if self.is_empty else self._colours[-1]
    
    @property
    def top_colour_count(self):
        """Number of top colour on the top of the tube."""
        if self.is_empty:
            return 0

        count = 0
        for col in reversed(self._colours):
            if col == self.top_colour:
                count += 1
            else:
                break
        
        return count

    @property
    def free_spaces(self):
        return self.MAX_TUBE_CAPACITY - len(self._colours)

    def find_moves(self, other_tubes: list[Tube]) -> list[Move]:
        """Return a list of possible moves"""
        if self.is_empty:
            return []

        moves = []
        for tube in other_tubes:
            if tube.is_empty or (tube.top_colour == self.top_colour and tube.free_spaces > 0):
                move_count = min(tube.free_spaces, self.top_colour_count)
                moves.append(Move(source=self.idx, dest=tube.idx, count=move_count))

        return moves

    def remove(self, count):
        """Remove count from this tube."""
        assert 1 <= count <= self.MAX_TUBE_CAPACITY
        assert len(self._colours) >= count
        to_remove = self._colours[-count:]
        assert all([x == to_remove[0] for x in to_remove])
        self._colours = self._colours[:-count]
        return to_remove[0]

    def add(self, colour, count):
        """Add to this tube"""
        assert 1 <= count <= self.MAX_TUBE_CAPACITY
        assert len(self._colours) + count <= self.MAX_TUBE_CAPACITY
        self._colours.extend([colour] * count)

    def __repr__(self):
        """Representation of this object for debugging."""
        return f"{self.__class__.__name__}(idx={self.idx}, colours={self._colours})"
    
    @property
    def is_solved(self):
        return self.is_empty or (self.top_colour_count == 4)

    def __eq__(self, other):
        """True if self equals other."""
        if not isinstance(other, Tube):
            return False
        
        if self.is_empty and other.is_empty:
            return True
        
        if self.is_empty != other.is_empty:
            return False
        
        if len(self._colours) != len(other._colours):
            return False

        return all([x == y for (x, y) in zip(self._colours, other._colours)])


def setup_tubes() -> list[Tube]:
    """Return a list of tube objects."""
    return [
        Tube(0, RED, BLUE, RED, BLUE),
        Tube(1, BLUE, RED, BLUE, RED),
        Tube(2),
    ]


def setup_tubes():
    return [
        Tube(0, GREEN, BLUE),
        Tube(1, RED, RED, GREEN),
        Tube(2, BLUE, RED, GREEN),
        Tube(3, GREEN, RED),
        Tube(4, BLUE, BLUE),
    ]


def show_tubes(tubes: list[Tube]):
    """Given a list of tubes, draw them."""

    fig, ax = plt.subplots(1, 1)

    left_x = 0
    bottom_y = 0
    for tube in tubes:
        left_x += 2
        tube.draw(ax, left_x, bottom_y)

    plt.show()


def calculate_moves(tubes: list[Tube]):
    """Calculate all the possible moves given a list of tubes."""
    moves = []
    for tube in tubes:
        other_tubes = [x for x in tubes if x.idx != tube.idx]
        moves.extend(tube.find_moves(other_tubes))
    return moves


def show_moves(moves: list[Move]):
    pprint(moves)


def apply_one_move(tubes, move):
    """Apply a single move to tubes, in place."""
    colour = tubes[move.source].remove(move.count)
    tubes[move.dest].add(colour, move.count)
    return tubes


def apply_moves(tubes: list[Tube], moves: list[Move]) -> list[list[Tube]]:
    """Given some tubes and some moves, apply each move and return a list of lists of tubes"""
    return [apply_one_move(deepcopy(tubes), move) for move in moves]


def is_solved(tubes: list[Tube]) -> bool:
    """True if the game is over."""
    return all([tube.is_solved for tube in tubes])


def is_in_sequence(sequence: list[list[Tube]], tubes: list[Tube]):
    """True if tubes is already in sequence."""
    return any([all([y == z for (y, z) in zip(tubes, x)]) for x in sequence])


def is_permutation(current_tubes: list[Tube], proposed_tubes: list[Tube]):
    """True if proposed_tubes is just a permutation of current_tubes."""
    return 


def recursive_solve(sequence):
    """Given a sequence, work out all the possible subsequences and call one_step on them."""

    if sequence is None:
        return None

    current_tubes = sequence[-1]

    if is_solved(current_tubes):
        return sequence

    moves = calculate_moves(current_tubes)
    if not moves:
        return None

    new_options = apply_moves(current_tubes, moves)

    for option in new_options:

        if is_in_sequence(sequence, option):
            # Avoid cycles
            continue
        
        if is_permutation(current_tubes, option):
            # Avoid permutations of the current tubes which just move water
            continue

        result = recursive_solve(sequence + [option])
        if result is not None:
            return result


def main():
    """Main"""
    tubes = setup_tubes()
    # show_tubes(tubes)

    sequence = [tubes]
    solution = recursive_solve(sequence)
    pprint(solution)

    for x in solution:
        show_tubes(x)


if __name__ == "__main__":
    main()
