from __future__ import annotations

import argparse
import os.path
import re

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

movere = re.compile(r"move (\d+) from (\d+) to (\d+)")


def compute(s: str) -> str:
    stacks, moves = parse(s)
    for move in moves:
        applymove(stacks, move)

    return "".join(stack[-1] for stack in stacks)


def applymove(stacks: list[list[str]], move: tuple[int, int, int]) -> None:
    n, fromstack, tostack = move
    stacks[tostack - 1].extend(stacks[fromstack - 1][-n:])
    del stacks[fromstack - 1][-n:]


def parse(s: str) -> tuple[list[list[str]], list[tuple[int, int, int]]]:
    stacklines = []
    moves: list[tuple[int, int, int]] = []
    phase = "stacks"
    for line in s.splitlines():
        if line == "":
            phase = "moves"
            continue

        if phase == "stacks":
            stacklines.append(line)
        elif phase == "moves":
            moves.append(tuple(map(int, movere.match(line).groups())))  # type: ignore
    return parsestacks(stacklines), moves


def parsestacks(stacklines: list[str]) -> list[list[str]]:
    indices = []
    for i, c in enumerate(stacklines.pop()):
        if c != " ":
            indices.append(i)

    stacks: list[list[str]] = [[] for _ in indices]
    for line in stacklines[-1::-1]:
        for si, i in enumerate(indices):
            if line[i] != " ":
                stacks[si].append(line[i])

    return stacks


INPUT_S = """\
    [D]    \n\
[N] [C]    \n\
[Z] [M] [P]
 1   2   3 \n\

move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2
"""
EXPECTED = "MCD"


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED),),
)
def test(input_s: str, expected: int) -> None:
    assert compute(input_s) == expected


EXPECTED_PARSE = (
    [["Z", "N"], ["M", "C", "D"], ["P"]],
    [(1, 2, 1), (3, 1, 3), (2, 2, 1), (1, 1, 2)],
)


@pytest.mark.parametrize(
    ("input_s", "expected"),
    ((INPUT_S, EXPECTED_PARSE),),
)
def test_parse(
    input_s: str, expected: tuple[list[list[str]], list[tuple[int, int, int]]]
) -> None:
    assert parse(input_s) == expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("data_file", nargs="?", default=INPUT_TXT)
    args = parser.parse_args()

    with open(args.data_file) as f, support.timing():  # type: ignore[attr-defined]
        print(compute(f.read()))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
