from __future__ import annotations

import argparse
import os.path
from collections import deque
from typing import Iterator

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> int:
    heightmap, start, end = parse(s)
    return dijkstra(heightmap, start, end)


def get_neighbors(
    heightmap: list[list[int]], pos: tuple[int, int]
) -> Iterator[tuple[int, int]]:
    xi, yi = pos
    for xj, yj in ((xi - 1, yi), (xi + 1, yi), (xi, yi - 1), (xi, yi + 1)):
        if 0 <= xj < len(heightmap[0]) and 0 <= yj < len(heightmap):
            if heightmap[yi][xi] + 1 >= heightmap[yj][xj]:
                yield (xj, yj)


def dijkstra(
    heightmap: list[list[int]], start: tuple[int, int], end: tuple[int, int]
) -> int:
    length = {start: 0}
    queue = deque([start])
    while queue:
        current = queue.popleft()
        for neighbor in get_neighbors(heightmap, current):
            if neighbor not in length:
                if neighbor == end:
                    return length[current] + 1
                length[neighbor] = length[current] + 1
                queue.append(neighbor)
    raise ValueError("No path found")


def parse(s: str) -> tuple[list[list[int]], tuple[int, int], tuple[int, int]]:
    heightmap = []
    for j, line in enumerate(s.splitlines()):
        if "S" in line:
            start = (line.index("S"), j)
            line = line.replace("S", "a")
        if "E" in line:
            end = (line.index("E"), j)
            line = line.replace("E", "z")
        heightmap.append([ord(c) for c in line])
    return heightmap, start, end


INPUT_S = """Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi
"""
EXPECTED = 31


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
