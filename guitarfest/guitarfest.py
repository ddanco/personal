from dataclasses import dataclass
from functools import reduce
from typing import Dict, FrozenSet, Tuple


RANKING_LENGTH = 6

Person = str
Guitar = str


@dataclass(frozen=True)
class Choice:
  person: Person
  guitar: Guitar


@dataclass(frozen=True)
class Ranking:
  person: Person
  ranking: Tuple[Guitar, ...]


Rankings = FrozenSet[Ranking]
Ordering = Tuple[Person, ...]
Choices = Tuple[Choice, ...]
RankedChoices = Tuple[Choices, ...]
Allocation = Dict[Person, Guitar]


def remove_guitar_and_person(
    all_choices: RankedChoices, guitar: Guitar, person: Person) -> RankedChoices:
  choice_filter = lambda c: c.person != person and c.guitar != guitar
  return tuple(tuple(filter(choice_filter, choices)) for choices in all_choices)


def build_choices_from_rankings(
    rankings: Rankings, ordering: Ordering) -> RankedChoices:

  ordered_rankings = sorted(rankings, key=lambda r: ordering.index(r.person))

  def get_ith_choices(i: int) -> Choices:
    return tuple(Choice(ranking.person, ranking.ranking[i])
        for ranking in filter(lambda r: len(r.ranking) > i, ordered_rankings))

  return tuple(get_ith_choices(i)
      for i in range(max(len(ranking.ranking) for ranking in rankings)))


def allocate_guitars(choices: RankedChoices,
                      allocation: Allocation) -> Allocation:

  # All possible guitars allocated
  if len(choices) == 0:
    return allocation

  # No more valid allocations left at current top choice level
  if len(choices[0]) == 0:
    return allocate_guitars(choices[1:], allocation)

  selection = choices[0][0]
  allocation[selection.person] = selection.guitar
  updated_choices = remove_guitar_and_person(
      choices, selection.guitar, selection.person)

  return allocate_guitars(updated_choices, allocation)


def guitar_fest(rankings: Rankings, ordering: Ordering) -> Allocation:

  choices = build_choices_from_rankings(rankings, ordering)
  first_allocation = allocate_guitars(choices, {})

  def reduce_helper(pair: Tuple[Person, Guitar]) -> RankedChoices:
    return remove_guitar_and_person(choices, pair[1], pair[0])

  updated_choices: Choices = reduce(reduce_helper, first_allocation.items())

  second_allocation = allocate_guitars(updated_choices, {})

  return second_allocation



##### EXAMPLE #####

ordering = ('ty', 'helene', 'alex', 'dominique')

ty_ranking = Ranking('ty', ('guitar_1', 'guitar_2', 'guitar_3'))
helene_ranking = Ranking('helene', ('guitar_1', 'guitar_2', 'guitar_4'))
alex_ranking = Ranking('alex', ('guitar_2', 'guitar_3', 'guitar_4'))
dominique_ranking = Ranking('dominique', ('guitar_4', 'guitar_1', 'guitar_2'))

# Expected result: Ty:1, Alex:2, Dominique:4, Helene:X

rankings = frozenset({ty_ranking, helene_ranking,
                      alex_ranking, dominique_ranking})


##################



if __name__ == '__main__':
  for (person, guitar) in guitar_fest(rankings, ordering).items():
    print(f'{person}: {guitar}\n')



