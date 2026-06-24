"""Simulate the water sort game"""
from collections import Counter, namedtuple
from copy import deepcopy
from functools import partial, total_ordering
from pprint import pprint
from time import sleep

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Wedge
import numpy as np

from puzzles import PUZZLE_TO_SOLVE

Move = namedtuple("Move", ["source", "dest", "count"])


@total_ordering
class Tube:

    MAX_TUBE_CAPACITY = 4

    def __init__(self, idx, *colours):
        """Given a list of hex codes."""
        assert len(colours) <= self.MAX_TUBE_CAPACITY
        self._colours = list(colours) if colours else []
        self.idx = idx

    def draw(self, ax, left_x, bottom_y):
        """Given an axis and the coordinates of the bottom left corner, draw the tube."""
        for (pos, colour) in enumerate(self._colours):
            if pos == 0:
                ax.add_patch(Rectangle((left_x, bottom_y + 0.5), 1, 0.5, color=colour))
                ax.add_patch(Wedge((left_x + 0.5, bottom_y + 0.5), 0.5, 180, 360, color=colour))
            else:
                ax.add_patch(Rectangle((left_x, bottom_y + pos), 1, 1, color=colour))

        theta = np.linspace(np.pi, np.pi * 2, 100)
        semicircle_x = np.cos(theta) * 0.5
        semicircle_y = np.sin(theta) * 0.5
        semicircle_points = [(x + left_x + 0.5, y + bottom_y + 0.5) for (x, y) in zip(semicircle_x, semicircle_y)]

        tube_outline = (
            # LHS
            (left_x, bottom_y + self.MAX_TUBE_CAPACITY),
            (left_x, bottom_y + 0.5),

            # Points making a semicircle
            *semicircle_points,

            # RHS
            (left_x + 1, bottom_y + 0.5),
            (left_x + 1, bottom_y + self.MAX_TUBE_CAPACITY),
        )
        ax.plot(
            [x for (x, _) in tube_outline], [y for (_, y) in tube_outline],
            color="k",
            linewidth=2,
            solid_capstyle="round",
        )

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
            if tube.is_empty or (tube.top_colour == self.top_colour and tube.free_spaces >= self.top_colour_count):
                moves.append(Move(source=self.idx, dest=tube.idx, count=self.top_colour_count))

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

    @property
    def string(self):
        """Create a sortable string repr of this tube."""
        if self.is_empty:
            return ""
        return "".join(self._colours)

    def __eq__(self, other):
        """True if this tube is the same as other."""
        if not isinstance(other, Tube):
            return NotImplemented

        return self.string == other.string

    def __lt__(self, other):
        """True if self is less than other."""
        if not isinstance(other, Tube):
            return NotImplemented

        return self.string < other.string


def show_tubes(ax, tubes: list[Tube]):
    """Given a list of tubes, draw them."""

    rows = 2 if len(tubes) >= 8 else 1
    per_row = np.ceil(len(tubes) / rows)

    ax.clear()
    ax.set_axis_off()

    left_x = 0
    bottom_y = 0
    for tube in tubes:
        row_idx, col_idx = divmod(tube.idx, per_row)
        left_x = col_idx * 2
        bottom_y = -row_idx * 5
        tube.draw(ax, left_x, bottom_y)


def calculate_moves(tubes: list[Tube]):
    """Calculate all the possible moves given a list of tubes."""
    moves = []
    for tube in tubes:
        other_tubes = [x for x in tubes if x.idx != tube.idx]
        moves.extend(tube.find_moves(other_tubes))
    return moves


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
    return sorted(current_tubes) == sorted(proposed_tubes)


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
            # TODO incorporate this into find_moves()
            continue

        result = recursive_solve(sequence + [option])
        if result is not None:
            return result


def make_tubes(colour_lists):
    """Turn iterables of colours into tubes, with indices."""

    # Quick sanity check, every colour should have a count of 4 else we'll never reach the exit condition
    count_dict = Counter([x for y in colour_lists for x in y])
    for colour, count in count_dict.items():
        if isinstance(colour, str):
            assert count == 4, f"Colour '{colour}' should feature 4 times, actually features {count}"

    return [Tube(idx, *cols) for (idx, cols) in enumerate(colour_lists)]


def animate_fig(ax, solution, fig_idx):
    """Update the figure to show tubes at index i."""
    show_tubes(ax, solution[fig_idx])


def plot_and_save_video(solution):
    """Save a video of the solution then render it to the screen in a figure."""
    plt.rcParams["toolbar"] = "None"
    fig = plt.figure()
    fig.canvas.manager.set_window_title("Water Sort Solver")
    fig.set_facecolor("#efefef")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_aspect("equal")

    video_frame_rate_fps = 30
    each_frame_duration_s = 0.8
    frames_per_solution = round(video_frame_rate_fps * each_frame_duration_s)

    ani = animation.FuncAnimation(
        fig,
        partial(animate_fig, ax, solution),
        frames=len(solution),
        interval=each_frame_duration_s * 1000,  # In milliseconds
        repeat_delay=2000,
    )
    writer = animation.FFMpegWriter(
        fps=video_frame_rate_fps,
        codec="libx264",
        bitrate=500,
    )

    with writer.saving(fig, "output.mp4", dpi=100):
        for state_idx in range(len(solution)):
            animate_fig(ax, solution, state_idx)

            for _ in range(frames_per_solution):
                writer.grab_frame()

    # print("Showing!")
    plt.show()


def main(colour_lists):
    """Main"""
    tubes = make_tubes(colour_lists)

    sequence = [tubes]
    solution = recursive_solve(sequence)
    pprint(solution)
    print(f"\n    *** SOLVED in {len(solution)} steps ***\n")

    plot_and_save_video(solution)


if __name__ == "__main__":
    main(PUZZLE_TO_SOLVE)
