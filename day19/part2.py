from __future__ import annotations

import argparse
import copy
import os.path
import re
import sys
from dataclasses import dataclass
from typing import Literal

import pytest

import support

INPUT_TXT = os.path.join(os.path.dirname(__file__), "input.txt")

BLUEPRINT_RE = re.compile(
    r"Blueprint (?P<id>\d+):"
    r"\s*Each ore robot costs (?P<ore>\d+) ore\."
    r"\s*Each clay robot costs (?P<clay>\d+) ore\."
    r"\s*Each obsidian robot costs (?P<obsore>\d+) ore and (?P<obsclay>\d+) clay\."
    r"\s*Each geode robot costs (?P<geore>\d+) ore and (?P<geobs>\d+) obsidian\."
)

RobotType = Literal["ore", "clay", "Obsidian", "geode"]


@dataclass
class Blueprint:
    id: int
    ore: int
    clay: int
    obsidian: tuple[int, int]
    geode: tuple[int, int]

    def __init__(self, matchdict: dict[str, str]) -> None:
        self.id = int(matchdict["id"])
        self.ore = int(matchdict["ore"])
        self.clay = int(matchdict["clay"])
        self.obsidian = (int(matchdict["obsore"]), int(matchdict["obsclay"]))
        self.geode = (int(matchdict["geore"]), int(matchdict["geobs"]))


class GameState:
    def __init__(self, blueprint: Blueprint) -> None:
        self.blueprint = blueprint
        self.ore = 0
        self.clay = 0
        self.obsidian = 0
        self.geode = 0
        self.ore_robots = 1
        self.clay_robots = 0
        self.obsidian_robots = 0
        self.geode_robots = 0
        self.time = 32
        self.production: RobotType | None = None

    def get_options(self) -> list[RobotType]:
        options: list[RobotType] = []
        if (
            self.ore >= self.blueprint.geode[0]
            and self.obsidian >= self.blueprint.geode[1]
        ):
            options.append("geode")
        if (
            self.ore >= self.blueprint.obsidian[0]
            and self.clay >= self.blueprint.obsidian[1]
        ):
            options.append("Obsidian")
        if self.ore >= self.blueprint.clay:
            options.append("clay")
        if self.ore >= self.blueprint.ore:
            options.append("ore")
        return options

    def add_robot(self, robot: RobotType) -> None:
        self.production = robot

    def tick(self) -> None:
        self.ore += self.ore_robots
        self.clay += self.clay_robots
        self.obsidian += self.obsidian_robots
        self.geode += self.geode_robots
        if self.production == "ore":
            self.ore_robots += 1
            self.ore -= self.blueprint.ore
        elif self.production == "clay":
            self.clay_robots += 1
            self.ore -= self.blueprint.clay
        elif self.production == "Obsidian":
            self.obsidian_robots += 1
            self.ore -= self.blueprint.obsidian[0]
            self.clay -= self.blueprint.obsidian[1]
        elif self.production == "geode":
            self.geode_robots += 1
            self.ore -= self.blueprint.geode[0]
            self.obsidian -= self.blueprint.geode[1]
        if self.ore < 0 or self.clay < 0 or self.obsidian < 0:
            raise ValueError("Not enough resources")
        self.production = None
        self.time -= 1


def evaluate_blueprint(blueprint: Blueprint) -> int:
    overall_best = 0

    def evaluate_game(
        game: GameState, moves: str, ignores: list[RobotType] | None = None
    ) -> int:
        if game.time == 0:
            nonlocal overall_best
            if game.geode > overall_best:
                overall_best = game.geode
                print(f"{blueprint.id}: {moves}: {game.geode}", file=sys.stderr)
            return game.geode
        options = game.get_options()
        if "geode" in options:
            game.add_robot("geode")
            game.tick()
            return evaluate_game(game, moves + "G")
        best_score = 0
        for option in options:
            if is_robot_good(option, game) and (
                ignores is None or option not in ignores
            ):
                newgame = copy.copy(game)
                newgame.add_robot(option)
                newgame.tick()
                best_score = max(best_score, evaluate_game(newgame, moves + option[0]))
        newgame = copy.copy(game)
        newgame.tick()
        best_score = max(
            best_score,
            evaluate_game(
                newgame,
                moves + ".",
                ignores=options if ignores is None else ignores + options,
            ),
        )
        return best_score

    state = GameState(blueprint)
    return evaluate_game(state, "")


def is_robot_good(robot: RobotType, game: GameState) -> bool:
    blueprint = game.blueprint
    time = game.time
    if robot == "ore":
        if time - 1 - blueprint.ore * game.ore_robots <= 0:
            return False
        return (
            game.ore_robots
            <= (max(blueprint.clay, blueprint.obsidian[0], blueprint.geode[0]) + 2) // 2
        )

    elif robot == "clay":
        return game.clay_robots <= blueprint.obsidian[1] // 2 + 1
    elif robot == "obsidian":
        return True
    return True


def compute(s: str) -> int:
    blueprints = parse(s)[:3]
    scores = [evaluate_blueprint(blueprint) for blueprint in blueprints]
    for i, score in enumerate(scores, 1):
        print(f"Blueprint {i}: {score}", file=sys.stderr)
    product = 1
    for score in scores:
        product *= score
    return product


def parse(s: str) -> list[Blueprint]:
    return [Blueprint(match.groupdict()) for match in BLUEPRINT_RE.finditer(s)]


INPUT_S = """\
Blueprint 1:
  Each ore robot costs 4 ore.
  Each clay robot costs 2 ore.
  Each obsidian robot costs 3 ore and 14 clay.
  Each geode robot costs 2 ore and 7 obsidian.

Blueprint 2:
  Each ore robot costs 2 ore.
  Each clay robot costs 3 ore.
  Each obsidian robot costs 3 ore and 8 clay.
  Each geode robot costs 3 ore and 12 obsidian.
"""
EXPECTED = 56 * 62


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
