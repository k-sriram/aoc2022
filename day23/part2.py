from __future__ import annotations

import argparse
import itertools
import os.path

import pytest

import support


Position = tuple[int, int]

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

DIRECTIONS = [
    ((0, -1), [(-1, -1), (0, -1), (1, -1)]),
    ((0, 1), [(-1, 1), (0, 1), (1, 1)]),
    ((-1, 0), [(-1, -1), (-1, 0), (-1, 1)]),
    ((1, 0), [(1, -1), (1, 0), (1, 1)]),
]


def draw_map(elves: list[Position]) -> tuple[list[list[str]], Position]:
    min_x = min(x for x, _ in elves)
    max_x = max(x for x, _ in elves)
    min_y = min(y for _, y in elves)
    max_y = max(y for _, y in elves)

    offset = (min_x - 1, min_y - 1)

    map_ = [["."] * (max_x - min_x + 3) for _ in range(max_y - min_y + 3)]
    for x, y in elves:
        map_[y - offset[1]][x - offset[0]] = "#"

    return map_, offset


def remove_overlaps(intentions: dict[Position, Position]) -> None:
    poplist = []
    for pos, target in intentions.items():
        overlaps = 0
        for (dx, dy) in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if intentions.get((target[0] + dx, target[1] + dy)) == target:
                overlaps += 1
        if overlaps > 1:
            poplist.append(pos)
    for pos in poplist:
        intentions.pop(pos)


def get_intentions(elves: list[Position], time: int) -> dict[Position, Position]:
    map_, (mx, my) = draw_map(elves)

    intentions: dict[Position, Position] = {}

    elves_with_neighbours = []
    for x, y in elves:
        if any(
            map_[y + dy - my][x + dx - mx] != "."
            for dx, dy in [
                (-1, -1),
                (-1, 0),
                (-1, 1),
                (0, -1),
                (0, 1),
                (1, -1),
                (1, 0),
                (1, 1),
            ]
        ):
            elves_with_neighbours.append((x, y))
    for i in range(4):
        direction, adjacents = DIRECTIONS[(time + i) % 4]
        for x, y in elves_with_neighbours:
            if (x, y) in intentions:
                continue
            if all(map_[y + dy - my][x + dx - mx] == "." for dx, dy in adjacents):
                intentions[(x, y)] = (x + direction[0], y + direction[1])

    return intentions


def compute(s: str) -> int:
    elves: list[Position] = []
    for y, line in enumerate(s.splitlines()):
        for x, c in enumerate(line):
            if c == "#":
                elves.append((x, y))

    for time in itertools.count(0):
        intentions = get_intentions(elves, time)
        remove_overlaps(intentions)

        if not intentions:
            return time + 1

        for pos, target in intentions.items():
            elves.remove(pos)
            elves.append(target)

    assert False, "unreachable"


INPUT_S = """\
..............
..............
.......#......
.....###.#....
...#...#.#....
....#...##....
...#.###......
...##.#.##....
....#..#......
..............
..............
..............
"""
EXPECTED = 20


INPUT_S_2 = """\
.....
..##.
..#..
.....
..##.
.....
"""
EXPECTED_2 = 25


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED),),
)
def test(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        print(compute(f.read()))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
