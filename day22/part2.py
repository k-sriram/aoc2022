from __future__ import annotations

import argparse
import os.path
from collections import deque
from itertools import product
from typing import Literal

import pytest

import support

Position = tuple[int, int]
Dir = int
Face = Literal[0, 1, 2, 3, 4, 5, 6]

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

# Coordinates are (x,y) tuples, and a point is addressed as m[y][x].
RIGHT, DOWN, LEFT, UP = range(4)
DIRECTION_DELTA: list[Position] = [(1, 0), (0, 1), (-1, 0), (0, -1)]
BLOCK_SIZE: int = 50

CUBE_FACES: tuple[tuple[tuple[Face, Dir], ...], ...] = (
    ((0, 0), (0, 0), (0, 0), (0, 0)),
    ((3, 1), (5, 1), (4, 1), (2, 1)),
    ((3, 2), (1, 3), (4, 0), (6, 1)),
    ((5, 2), (1, 0), (2, 0), (6, 0)),
    ((2, 2), (1, 2), (5, 0), (6, 2)),
    ((4, 2), (1, 1), (3, 0), (6, 3)),
    ((3, 3), (2, 3), (4, 3), (5, 3)),
)


def get_adjacent_face(
    face: Face, orientation: Dir, direction: Dir
) -> tuple[tuple[Face, Dir], Dir]:
    corrected_direction = (direction - orientation) % 4
    adjacent_face = CUBE_FACES[face][corrected_direction]
    return (
        (adjacent_face[0], (2 - adjacent_face[1] + direction) % 4),
        CUBE_FACES[face][corrected_direction][1],
    )


def turn(dir: Dir, rot: str) -> Dir:
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


def cubemap_from_boardmap(boardmap: list[list[str]]) -> list[list[tuple[Face, Dir]]]:
    # Make a map of the cube faces
    blockwidth = len(boardmap[0]) // BLOCK_SIZE
    blockheight = len(boardmap) // BLOCK_SIZE
    cubemap: list[list[tuple[Face, Dir]]] = []
    for j in range(blockheight):
        cubemap.append([])
        for i in range(blockwidth):
            if boardmap[j * BLOCK_SIZE][i * BLOCK_SIZE] == " ":
                cubemap[-1].append((0, 0))
            else:
                cubemap[-1].append((1, 0))

    # Find the first block
    for j, i in product(range(blockheight), range(blockwidth)):
        if cubemap[j][i][0] == 1:
            first_block = (i, j)
            break

    # Use an exhaustive search to find the orientation of the each block
    queue = deque([first_block])
    visited = set(queue)
    while queue:
        x, y = queue.popleft()
        for di, (dx, dy) in enumerate(DIRECTION_DELTA):
            nx, ny = x + dx, y + dy
            if 0 <= nx < blockwidth and 0 <= ny < blockheight:
                if cubemap[ny][nx][0] == 0:
                    continue
                if (nx, ny) in visited:
                    continue
                visited.add((nx, ny))
                queue.append((nx, ny))
                face, orientation = cubemap[y][x]
                cubemap[ny][nx], _ = get_adjacent_face(face, orientation, di)
    return cubemap


def get_edge_cells(direction: Dir, *, is_clockwise: bool) -> list[Position]:
    if direction == RIGHT:
        edge_cells = [(BLOCK_SIZE - 1, y) for y in range(BLOCK_SIZE)]
    elif direction == DOWN:
        edge_cells = [(x, BLOCK_SIZE - 1) for x in range(BLOCK_SIZE - 1, -1, -1)]
    elif direction == LEFT:
        edge_cells = [(0, y) for y in range(BLOCK_SIZE - 1, -1, -1)]
    elif direction == UP:
        edge_cells = [(x, 0) for x in range(BLOCK_SIZE)]
    else:
        raise ValueError(f"Invalid direction {direction}")
    if not is_clockwise:
        edge_cells.reverse()
    return edge_cells


def calc_neighbours(
    boardmap: list[list[str]],
) -> list[list[list[tuple[Position, Dir]]]]:
    cubemap = cubemap_from_boardmap(boardmap)
    cubepos: dict[Face, Position] = {}
    for y, row in enumerate(cubemap):
        for x, (face, _) in enumerate(row):
            if face != 0:
                cubepos[face] = (x, y)
    neighbors: list[list[list[tuple[Position, Dir]]]] = [
        [[((0, 0), 0) for _ in range(4)] for _ in row] for row in boardmap
    ]

    for face, (cx, cy) in cubepos.items():
        for direction, (dx, dy) in enumerate(DIRECTION_DELTA):
            for px, py in product(range(BLOCK_SIZE), repeat=2):
                if 0 <= px + dx < BLOCK_SIZE and 0 <= py + dy < BLOCK_SIZE:
                    neighbors[cy * BLOCK_SIZE + py][cx * BLOCK_SIZE + px][direction] = (
                        (
                            cx * BLOCK_SIZE + px + dx,
                            cy * BLOCK_SIZE + py + dy,
                        ),
                        direction,
                    )
            edge_cells = get_edge_cells(direction, is_clockwise=True)
            orient = cubemap[cy][cx][1]
            (nface, _), n_dir_to_us_rel = get_adjacent_face(face, orient, direction)
            ncx, ncy = cubepos[nface]
            norient = cubemap[ncy][ncx][1]
            ndirection = (norient + n_dir_to_us_rel) % 4
            new_direction = (ndirection + 2) % 4
            n_edge_cells = get_edge_cells(ndirection, is_clockwise=False)
            for (px, py), (npx, npy) in zip(edge_cells, n_edge_cells):
                neighbors[cy * BLOCK_SIZE + py][cx * BLOCK_SIZE + px][direction] = (
                    (
                        ncx * BLOCK_SIZE + npx,
                        ncy * BLOCK_SIZE + npy,
                    ),
                    new_direction,
                )
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
    pos, dir = get_init_pos(boardmap), RIGHT

    for ins in instructions:
        if isinstance(ins, int):
            for _ in range(ins):
                (nx, ny), nd = neighbors[pos[1]][pos[0]][dir]
                if boardmap[ny][nx] == "#":
                    break
                pos = nx, ny
                dir = nd
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
EXPECTED = 5031


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED),),
)
def test(input_s: str, expected: int) -> None:
    global BLOCK_SIZE
    BLOCK_SIZE = 4
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
