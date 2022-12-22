from __future__ import annotations

import argparse
import os.path

import pytest

import support

Position = tuple[int, int]

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

# Coordinates are (x,y) tuples, and a point is addressed as m[y][x].

DIR = {0: (1, 0), 1: (0, 1), 2: (-1, 0), 3: (0, -1)}


def turn(dir: int, rot: str) -> int:
    if rot == "L":
        return (dir - 1) % 4
    elif rot == "R":
        return (dir + 1) % 4
    else:
        raise ValueError(f"Invalid rotation {rot}")


def parse(
    s: str,
) -> tuple[list[list[str]], list[int | str]]:
    boardmap = []
    for line in s.splitlines()[:-2]:
        boardmap.append(list(line))

    width = max(len(row) for row in boardmap)
    for row in boardmap:
        row.extend([" "] * (width - len(row)))

    instructions: list[int | str] = []
    line = s.splitlines()[-1]
    token = ""
    for c in line:
        if c in "LR":
            instructions.append(int(token))
            token = ""
            instructions.append(c)
        else:
            token += c
    if token:
        instructions.append(int(token))

    return boardmap, instructions


def calc_neighbours(boardmap: list[list[str]]) -> list[list[list[Position]]]:
    neighbors: list[list[list[Position]]] = []
    for y, row in enumerate(boardmap):
        neighbors.append([])
        for x, _ in enumerate(row):
            neighbors[y].append([])
            for dx, dy in DIR.values():
                nx, ny = x + dx, y + dy
                if (
                    0 <= nx < len(row)
                    and 0 <= ny < len(boardmap)
                    and boardmap[ny][nx] != " "
                ):
                    neighbors[y][x].append((nx, ny))
                else:
                    odx, ody = -dx, -dy
                    i = 1
                    nx, ny = x + odx * i, y + ody * i
                    while (
                        0 <= nx < len(row)
                        and 0 <= ny < len(boardmap)
                        and boardmap[ny][nx] != " "
                    ):
                        i += 1
                        nx, ny = x + odx * i, y + ody * i
                    nx, ny = x + odx * (i - 1), y + ody * (i - 1)
                    neighbors[y][x].append((nx, ny))
    return neighbors


def get_init_pos(boardmap: list[list[str]]) -> Position:
    for y, row in enumerate(boardmap):
        for x, c in enumerate(row):
            if c == ".":
                return x, y
    raise ValueError("No starting position found")


def compute(s: str) -> int:
    boardmap, instructions = parse(s)
    neighbors = calc_neighbours(boardmap)
    pos, dir = get_init_pos(boardmap), 0

    for ins in instructions:
        if isinstance(ins, int):
            for _ in range(ins):
                nx, ny = neighbors[pos[1]][pos[0]][dir]
                if boardmap[ny][nx] == "#":
                    break
                pos = nx, ny
        else:
            dir = turn(dir, ins)

    return 1000 * (pos[1] + 1) + 4 * (pos[0] + 1) + dir


INPUT_S = """\
        ...#
        .#..
        #...
        ....
...#.......#
........#...
..#....#....
..........#.
        ...#....
        .....#..
        .#......
        ......#.

10R5L5R10L4R5L5
"""
EXPECTED = 6032


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
