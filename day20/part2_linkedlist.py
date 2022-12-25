from __future__ import annotations

import argparse
import os.path
from dataclasses import dataclass

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


@dataclass
class Node:
    value: int
    next: Node
    prev: Node


def swap_adjacent_nodes(first: Node, second: Node) -> None:
    if first.next is not second or second.prev is not first:
        raise ValueError("Nodes are not adjacent")
    if second.next is not None:
        second.next.prev = first
    if first.prev is not None:
        first.prev.next = second
    first.next = second.next
    second.prev = first.prev
    first.prev = second
    second.next = first


def move_forward(node: Node, n: int) -> None:
    if n > 0:
        for _ in range(n):
            swap_adjacent_nodes(node, node.next)
    elif n < 0:
        for _ in range(-n):
            swap_adjacent_nodes(node.prev, node)


def print_list(first: Node) -> None:
    node = first
    while node.next != first:
        print(node.value, end=", ")
        node = node.next
    print(node.value)


def compute(s: str) -> int:
    vals = [811589153 * int(line) for line in s.splitlines()]
    numvals = len(vals)
    first = Node(vals[0], None, None)  # type: ignore
    prev = first
    nodelist = [first]
    for val in vals[1:]:
        node = Node(val, None, prev=prev)  # type: ignore
        prev.next = node
        prev = node
        nodelist.append(node)
    first.prev = prev
    prev.next = first

    for _ in range(10):
        for node in nodelist:
            move_forward(node, node.value % (numvals - 1))

    node = first
    while node.next != first:
        node = node.next

    xcoor, ycoor, zcoor = 1000 % numvals, 2000 % numvals, 3000 % numvals

    x, y, z = None, None, None

    node = first
    while node.value != 0:
        node = node.next

    count = 0

    while x is None or y is None or z is None:
        if count == xcoor:
            x = node.value
        if count == ycoor:
            y = node.value
        if count == zcoor:
            z = node.value
        node = node.next
        count += 1

    return x + y + z


INPUT_S = """\
1
2
-3
3
-2
0
4
"""
EXPECTED = 1623178306


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
