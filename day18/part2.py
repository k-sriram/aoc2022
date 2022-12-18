from __future__ import annotations

import argparse
import os.path
from collections import deque
from typing import Iterator

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


D_NEIGHBOUR = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]


def get_neighbours(
    c: tuple[int, int, int], max_dim: int
) -> Iterator[tuple[int, int, int]]:
    for dx, dy, dz in D_NEIGHBOUR:
        x, y, z = c
        x += dx
        y += dy
        z += dz
        if 0 <= x <= max_dim and 0 <= y <= max_dim and 0 <= z <= max_dim:
            yield (x, y, z)


def compute(s: str) -> int:
    cubes = [eval(line) for line in s.splitlines()]
    max_side = max(max(c) for c in zip(*cubes))
    cells = [
        [[0 for _ in range(max_side + 1)] for _ in range(max_side + 1)]
        for _ in range(max_side + 1)
    ]
    cells[0][0][0] = 1
    queue = deque([(0, 0, 0)])
    visited = set(cubes)
    visited.add(queue[0])

    while queue:
        x, y, z = queue.popleft()
        for nx, ny, nz in get_neighbours((x, y, z), max_side):
            if (nx, ny, nz) not in visited:
                visited.add((nx, ny, nz))
                queue.append((nx, ny, nz))
                cells[nx][ny][nz] = 1

    cubes = [
        (x, y, z)
        for x, row in enumerate(cells)
        for y, col in enumerate(row)
        for z, c in enumerate(col)
        if c == 0
    ]

    area = 6 * len(cubes)
    for i, c1 in enumerate(cubes):
        for c2 in cubes[i + 1 :]:
            if sum(abs(a - b) for a, b in zip(c1, c2)) == 1:
                area -= 2
    return area


INPUT_S = """\
2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5
"""
EXPECTED = 58


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
