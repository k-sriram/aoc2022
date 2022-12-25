from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


class OrigIDList:
    def __init__(self, list_: list[int]) -> None:
        self.list_ = list_
        self.n = len(list_)
        self.orig_id = list(range(self.n))

    def swap(self, i: int, j: int) -> int:
        i %= self.n
        j %= self.n
        if i == 0 and j == self.n - 1:
            self.list_ = self.list_[1:-1] + self.list_[:1] + self.list_[-1:]
            self.orig_id = self.orig_id[1:-1] + self.orig_id[:1] + self.orig_id[-1:]
            return self.n - 2
        elif j == 0 and i == self.n - 1:
            self.list_ = self.list_[:1] + self.list_[-1:] + self.list_[1:-1]
            self.orig_id = self.orig_id[:1] + self.orig_id[-1:] + self.orig_id[1:-1]
            return 1
        else:
            self.list_[i], self.list_[j] = self.list_[j], self.list_[i]
            self.orig_id[i], self.orig_id[j] = self.orig_id[j], self.orig_id[i]
            return j

    def __getitem__(self, i: int) -> int:
        return self.list_[i % self.n]

    def oid(self, i: int) -> int:
        return self.orig_id.index(i)

    def move_forward(self, i: int, n: int) -> None:
        j = i
        n = n % (self.n - 1)
        for _ in range(n):
            j = self.swap(j, j + 1)


def compute(s: str) -> int:
    vals = OrigIDList([811589153 * int(line) for line in s.splitlines()])
    for _ in range(10):
        for i in range(vals.n):
            oi = vals.oid(i)
            vals.move_forward(oi, vals[oi])

    i0 = vals.list_.index(0)
    coors = 1000, 2000, 3000
    sum = 0
    for i in coors:
        sum += vals[i0 + i]

    return sum


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
