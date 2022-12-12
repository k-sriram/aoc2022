from __future__ import annotations

import argparse
import math
import os.path
import re
from collections import deque
from typing import Iterable

import pytest
from tqdm import tqdm

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


monkey_re = re.compile(
    r"""Monkey (?P<id>\d+):
  Starting items: (?P<start>[\d, ]+)
  Operation: new = old (?P<op>[\+\-\*\/]) (?P<val>[\d\w]+)
  Test: divisible by (?P<test>\d+)
    If true: throw to monkey (?P<true>\d+)
    If false: throw to monkey (?P<false>\d+)
"""
)


class Monkey:
    def __init__(self, monkey_dict: dict[str, str]) -> None:
        self.id = int(monkey_dict["id"])
        self.items = deque(map(int, monkey_dict["start"].split(", ")))
        self.inspects = 0
        try:
            val = int(monkey_dict["val"])
        except ValueError:
            if monkey_dict["val"] == "old" and monkey_dict["op"] == "*":

                def op(x: int) -> int:
                    return x * x

            else:
                raise NotImplementedError

        else:
            if monkey_dict["op"] == "+":

                def op(x: int) -> int:
                    return x + val

            elif monkey_dict["op"] == "*":

                def op(x: int) -> int:
                    return x * val

            else:
                raise NotImplementedError
        test = int(monkey_dict["test"])
        self.divisor = test
        returnval = {True: int(monkey_dict["true"]), False: int(monkey_dict["false"])}

        def process(self: Monkey, lcm: int) -> tuple[int, int]:
            self.inspects += 1
            item = self.items.popleft()
            new_item = op(item)
            new_item = new_item % lcm
            # new_item = new_item // 3
            return returnval[new_item % test == 0], new_item

        self.process_one = process

    def process(self, lcm: int) -> tuple[int, int]:
        return self.process_one(self, lcm)

    def receive(self, item: int) -> None:
        self.items.append(item)


class MonkeyKeepAway:
    def __init__(self, s: str) -> None:
        self.monkeys = {
            m.id: m
            for m in map(lambda match: Monkey(match.groupdict()), monkey_re.finditer(s))
        }
        self.lcm = math.lcm(*[m.divisor for m in self.monkeys.values()])

    def play_round(self) -> None:
        for monkey in self.monkeys.values():
            while len(monkey.items) > 0:
                monkey_id, new_item = monkey.process(self.lcm)
                self.monkeys[monkey_id].receive(new_item)


def compute(s: str) -> int:
    game = MonkeyKeepAway(s)
    for _ in tqdm(range(10000)):
        game.play_round()
    inspects = (m.inspects for m in game.monkeys.values())
    topinspects = topn(inspects, 2)
    return topinspects[0] * topinspects[1]


def topn(L: Iterable[int], n: int) -> list[int]:
    toplist: list[int] = []
    for i in L:
        if len(toplist) < n:
            reverse_insort(toplist, i)
        elif i > toplist[-1]:
            reverse_insort(toplist, i)
            toplist = toplist[:n]
    return toplist


def reverse_insort(a: list[int], x: int, lo: int = 0, hi: int | None = None) -> None:
    """Insert item x in list a, and keep it reverse-sorted assuming a
    is reverse-sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    if lo < 0:
        raise ValueError("lo must be non-negative")
    if hi is None:
        hi = len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if x > a[mid]:
            hi = mid
        else:
            lo = mid + 1
    a.insert(lo, x)


INPUT_S = """Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1
"""
EXPECTED = 2713310158


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
