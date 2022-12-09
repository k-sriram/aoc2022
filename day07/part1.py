from __future__ import annotations

import argparse
import os.path

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")


def compute(s: str) -> int:
    fs = read_dir_structure(s)
    return compute_size(fs)


def read_dir_structure(s: str) -> dict[tuple[str, ...], int]:
    dirs: dict[tuple[str, ...], int] = {}
    current_dir = None
    for line in s.splitlines():
        if line.startswith("$"):
            if line == "$ cd /":
                current_dir = ["/"]
            elif line == "$ cd ..":
                current_dir.pop()  # type: ignore[union-attr]
            elif line.startswith("$ cd "):
                current_dir.append(line[5:].strip())  # type: ignore[union-attr]
        else:
            if current_dir is None:
                raise ValueError("No current directory")
            if not line.startswith("dir"):
                size = int(line.split()[0])
                for i in range(len(current_dir)):
                    dirs.setdefault(tuple(current_dir[: i + 1]), 0)
                    dirs[tuple(current_dir[: i + 1])] += size
    return dirs


def compute_size(fs: dict[tuple[str, ...], int]) -> int:
    return sum(i for i in fs.values() if i <= 100000)


INPUT_S = """$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
"""
EXPECTED = 95437


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
