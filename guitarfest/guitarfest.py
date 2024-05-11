from dataclasses import dataclass
from typing import Dict, Tuple


RANKING_LENGTH = 6


@dataclass(frozen=True)
class Person:
  id: int
  name: str


@dataclass(frozen=True)
class Guitar:
  id: int
  name: str
  luthier: str


@dataclass(frozen=True)
class Ranking:
  person: Person
  ranking: Tuple[Guitar, ...]

  def __post_init__(self):
    if len(self.ranking) != RANKING_LENGTH:
      raise ValueError(
          f'Incorrect number of guitars for ranking: {self.person}')

  def nth(self, n: int):
    if n < 1 or n > RANKING_LENGTH:
      raise ValueError(f'Index {n} is invalid for ranking list length')
    return self.ranking[n-1]

RankingSet = Dict[Person, Ranking]

# @dataclass(frozen=True)
# class Allocation:
    
    