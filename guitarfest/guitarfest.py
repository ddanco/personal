from dataclasses import dataclass
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


@dataclass(frozen=True)
class Rankings:
  rankings: FrozenSet[Ranking]
  ordering: Tuple[Person, ...]


Choices = Tuple[Choice, ...]
AllChoices = Tuple[Choices, ...]
Allocation = Dict[Person, Guitar]


def remove_guitar_and_person(
    all_choices: AllChoices, guitar: Guitar, person: Person) -> AllChoices:
  choice_filter = lambda c: c.person != person and c.guitar != guitar
  return tuple(tuple(filter(choice_filter, choices)) for choices in all_choices)


def build_choices_from_rankings(rankings: Rankings) -> AllChoices:
  ordered_rankings = sorted(rankings.rankings,
      key=lambda r: rankings.ordering.index(r.person))

  def get_ith_choices(i: int) -> Tuple[Choice, ...]:
    return tuple(Choice(ranking.person, ranking.ranking[i])
        for ranking in filter(lambda r: len(r.ranking) > i, ordered_rankings))

  return tuple(get_ith_choices(i)for i in range(RANKING_LENGTH))


def allocate_guitars(rankings: Rankings) -> Allocation:
  allocation: Allocation = {}
  choices = build_choices_from_rankings(rankings)
  return allocate_guitars_helper(choices, allocation)


def allocate_guitars_helper(
    choices: AllChoices, allocation: Allocation) -> Allocation:

  # All possible guitars allocated
  if len(choices) == 0:
    return allocation

  # No more valid allocations left at current top choice level
  if len(choices[0]) == 0:
    return allocate_guitars_helper(choices[1:], allocation)

  selection = choices[0][0]
  allocation[selection.person] = selection.guitar
  updated_choices = remove_guitar_and_person(
      choices, selection.guitar, selection.person)

  return allocate_guitars_helper(updated_choices, allocation)


##### EXAMPLE #####

ordering = ('ty', 'helene', 'alex', 'dominique')

ty_ranking = Ranking('ty', ('guitar_1', 'guitar_2', 'guitar_3'))
helene_ranking = Ranking('helene', ('guitar_1', 'guitar_2', 'guitar_4'))
alex_ranking = Ranking('alex', ('guitar_2', 'guitar_3', 'guitar_4'))
dominique_ranking = Ranking('dominique', ('guitar_4', 'guitar_1', 'guitar_2'))

# Expected result: Ty:1, Alex:2, Dominique:4, Helene:X

rankings = Rankings(frozenset({ty_ranking, helene_ranking, alex_ranking,
    dominique_ranking}), ordering)


##################




if __name__ == '__main__':
  for (person, guitar) in allocate_guitars(rankings).items():
    print(f'{person}: {guitar}\n')



