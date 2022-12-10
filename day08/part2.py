from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> int:
    heights = get_heights(s)
    max_scene = None
    for i in range(len(heights)):
        for j in range(len(heights[i])):
            if max_scene is None or scene(heights, i, j) > max_scene:
                max_scene = scene(heights, i, j)
    assert max_scene is not None
    return max_scene


def get_heights(s: str) -> list[list[int]]:
    heights = []
    for line in s.splitlines():
        heights.append([int(x) for x in line])
    return heights


def scene(heights: list[list[int]], i: int, j: int, show: bool = False) -> int:
    t, r, L, b = 0, 0, 0, 0
    height = heights[i][j]
    for c, xi in enumerate(range(i + 1, len(heights))):
        if heights[xi][j] >= height:
            b = c + 1
            break
    else:
        b = len(heights) - i - 1
    for c, xj in enumerate(range(j + 1, len(heights[i]))):
        if heights[i][xj] >= height:
            r = c + 1
            break
    else:
        r = len(heights[i]) - j - 1
    for c, xi in enumerate(range(i - 1, -1, -1)):
        if heights[xi][j] >= height:
            t = c + 1
            break
    else:
        t = i
    for c, xj in enumerate(range(j - 1, -1, -1)):
        if heights[i][xj] >= height:
            L = c + 1
            break
    else:
        L = j
    return t * r * L * b


def is_visible(heights: list[list[int]], i: int, j: int) -> bool:
    if i == 0 or j == 0 or i == len(heights) - 1 or j == len(heights[i]) - 1:
        return True
    if all(heights[i][j] > heights[xi][j] for xi in range(i)):
        return True
    if all(heights[i][j] > heights[xi][j] for xi in range(i + 1, len(heights))):
        return True
    if all(heights[i][j] > heights[i][xj] for xj in range(j)):
        return True
    if all(heights[i][j] > heights[i][xj] for xj in range(j + 1, len(heights[i]))):
        return True
    return False


INPUT_S = """30373
25512
65332
33549
35390
"""
EXPECTED = 8


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED),),
)
def test(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


@pytest.mark.parametrize(
    ("input_s", "i", "j", "expected"),
    (
        (INPUT_S, 1, 2, 4),
        (INPUT_S, 3, 2, 8),
        (INPUT_S, 2, 0, 0),
    ),
)
def test_scene(input_s: str, i: int, j: int, expected: int) -> None:
    heights = get_heights(input_s)
    assert scene(heights, i, j) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        print(compute(f.read()))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
