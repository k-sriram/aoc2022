from __future__ import annotations

import argparse
import os.path
import sys
from collections import deque
from typing import Deque
from typing import IO

import pytest
from termcolor import colored  # type: ignore

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")
PRINT_DEBUG = False


class BlizzardMap:
    def __init__(self, valleymap: list[list[str]]):
        self.height = len(valleymap) - 2
        self.width = len(valleymap[0]) - 2
        self.horbliz: list[list[tuple[int, int]]] = [[] for _ in range(self.height)]
        self.verbliz: list[list[tuple[int, int]]] = [[] for _ in range(self.width)]
        for y, line in enumerate(valleymap[1:-1], 1):
            for x, c in enumerate(line[1:-1], 1):
                if c in "><":
                    self.horbliz[y - 1].append((x - 1, {">": 1, "<": -1}[c]))
                elif c in "^v":
                    self.verbliz[x - 1].append((y - 1, {"^": -1, "v": 1}[c]))

        self.start = (valleymap[0].index("."), 0)
        self.end = (valleymap[-1].index("."), len(valleymap) - 1)

    def is_blizzard(self, x: int, y: int, t: int) -> bool:
        x, y = x - 1, y - 1
        for blizx, dx in self.horbliz[y]:
            if (blizx + dx * t) % self.width == x:
                return True
        for blizy, dy in self.verbliz[x]:
            if (blizy + dy * t) % self.height == y:
                return True
        return False

    def draw_map(
        self,
        t: int,
        transpose: bool = False,
        glyphpos: list[tuple[int, int]] | None = None,
        glyph: str = colored("o", "cyan"),
        file: IO[str] = sys.stderr,
    ) -> None:
        blizzmap = [["." for _ in range(self.width)] for _ in range(self.height)]
        for y, row in enumerate(self.horbliz):
            for blizx, dx in row:
                x = (blizx + dx * t) % self.width
                if blizzmap[y][x] == ".":
                    blizzmap[y][x] = ">" if dx == 1 else "<"
                else:
                    blizzmap[y][x] = "X"
        for x, col in enumerate(self.verbliz):
            for blizy, dy in col:
                y = (blizy + dy * t) % self.height
                if blizzmap[y][x] == ".":
                    blizzmap[y][x] = "^" if dy == -1 else "v"
                else:
                    blizzmap[y][x] = "X"
        bmap_w_border: list[list[str]] = (
            [["#" for _ in range(self.width + 2)]]
            + [["#"] + line + ["#"] for line in blizzmap]
            + [["#" for _ in range(self.width + 2)]]
        )
        bmap_w_border[self.start[1]][self.start[0]] = "S"
        bmap_w_border[self.end[1]][self.end[0]] = "E"

        if glyphpos is not None:
            for x, y in glyphpos:
                bmap_w_border[y][x] = glyph

        if transpose:
            bmap_w_border = list(map(list, zip(*bmap_w_border)))
            for y, line in enumerate(bmap_w_border):
                for x, c in enumerate(line):
                    if c in "><^v":
                        bmap_w_border[y][x] = {">": "v", "<": "^", "^": "<", "v": ">"}[
                            c
                        ]

        for y, line in enumerate(bmap_w_border):
            print("".join(line), file=file)
        print(end="", flush=True, file=file)


def get_neighbours(
    blizzards: BlizzardMap,
    x: int,
    y: int,
    t: int,
    start: tuple[int, int],
    end: tuple[int, int],
) -> list[tuple[int, int]]:
    neighbours = []
    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)):
        nx, ny = x + dx, y + dy
        if (nx, ny) == end:
            return [(nx, ny)]
        if (nx, ny) == start:
            neighbours.append((nx, ny))
            continue
        if not (0 < nx <= blizzards.width and 0 < ny <= blizzards.height):
            continue
        if not blizzards.is_blizzard(nx, ny, t):
            neighbours.append((nx, ny))
    neighbours.sort(key=lambda p: abs(p[0] - end[0]) + abs(p[1] - end[1]))
    return neighbours


def get_path_bfs(
    blizzards: BlizzardMap, start: tuple[int, int], end: tuple[int, int]
) -> list[tuple[int, int]]:
    queue: Deque[tuple[tuple[int, int], int, list[tuple[int, int]]]] = deque(
        [(start, 1, [start])]
    )
    max_time = 0
    while queue:
        time = queue[0][1]
        if time > max_time:
            max_time = time
            visited = set()
            newqueue: Deque[
                tuple[tuple[int, int], int, list[tuple[int, int]]]
            ] = deque()
            for pos, time, path in queue:
                if pos not in visited:
                    visited.add(pos)
                    newqueue.append((pos, time, path))
            queue = newqueue
            if PRINT_DEBUG:
                print(f"Time: {time}, queue: {len(queue)}", flush=True, file=sys.stderr)
                blizzards.draw_map(
                    time, transpose=False, glyphpos=[pos for pos, _, _ in queue]
                )
        pos, time, path = queue.popleft()
        for nx, ny in get_neighbours(blizzards, *pos, time, start, end):
            if (nx, ny) == end:
                return path + [(nx, ny)]
            queue.append(((nx, ny), time + 1, path + [(nx, ny)]))
    raise ValueError("No path found")


def compute(s: str) -> int:
    valleymap = [list(line) for line in s.splitlines()]
    start = (valleymap[0].index("."), 0)
    end = (valleymap[-1].index("."), len(valleymap) - 1)
    blizzards = BlizzardMap(valleymap)
    path = get_path_bfs(blizzards, start, end)

    return len(path) - 1


INPUT_S = """\
#.######
#>>.<^<#
#.<..<<#
#>v.><>#
#<^v^^>#
######.#
"""
EXPECTED = 18


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED),),
)
def test(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    if args.verbose:
        global PRINT_DEBUG
        PRINT_DEBUG = True

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        print(compute(f.read()))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
