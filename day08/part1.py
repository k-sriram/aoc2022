from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> int:
    heights = []
    for line in s.splitlines():
        heights.append([int(x) for x in line])
        visible = 0
        for i in range(len(heights)):
            for j in range(len(heights[i])):
                if is_visible(heights, i, j):
                    visible += 1
    return visible


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
EXPECTED = 21


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
