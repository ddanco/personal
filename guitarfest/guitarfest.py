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


Ranking = Tuple[Guitar, ...]
Rankings = Dict[Person, Ranking]
Ordering = Tuple[Person, ...]
Choices = Tuple[Choice, ...]
Choicess = Tuple[Choices, ...]
Allocation = Dict[Person, Guitar]


def remove_guitar_and_person(
    all_choices: Choicess, guitar: Guitar, person: Person) -> Choicess:
  choice_filter = lambda c: c.person != person and c.guitar != guitar
  return tuple(tuple(filter(choice_filter, choices)) for choices in all_choices)


def order_choices(choicess: Choicess, ordering: Ordering) -> Choicess:
  return tuple(tuple(sorted(choices, key=lambda c: ordering.index(c.person)))
      for choices in choicess)


def build_choices_from_rankings(
    rankings: Rankings, ordering: Ordering) -> Choicess:

  def get_ith_choices(i: int) -> Choices:
    return tuple(Choice(person, ranking[i])
        for person, ranking in rankings.items() if len(ranking) > i)

  return tuple(get_ith_choices(i)
      for i in range(max(len(ranking) for ranking in rankings.values())))


def allocate_guitars(choices: Choicess,
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


def guitar_fest(rankings: Rankings, ordering: Ordering) -> Tuple[Allocation, Allocation]:

  choicess = build_choices_from_rankings(rankings, ordering)
  first_allocation = allocate_guitars(choicess, {})

  def reduce_helper(acc: Choicess, pair: Tuple[Person, Guitar]) -> Choicess:
    return remove_guitar_and_person(choicess, pair[1], pair[0])

  updated_choices: Choicess = reduce(reduce_helper, first_allocation.items(), choicess)

  def choice_level_in_first_round(person: Person) -> int: ## Todo: combine this with ordering function
    if person not in first_allocation:
      # Did not get guitar in first allocation, give highest priority next round
      return 100
    return rankings[person].index(first_allocation[person])

  reordered_choices = tuple(tuple(sorted(choices,
      key=lambda c: choice_level_in_first_round(c.person), reverse=True))
      for choices in updated_choices)

  second_allocation = allocate_guitars(reordered_choices, {})

  return (first_allocation, second_allocation)



##### EXAMPLE #####

ordering = ('ty', 'helene', 'alex', 'dominique')

rankings: Rankings = {'ty': ('guitar_1', 'guitar_2', 'guitar_3'),
              'helene': ('guitar_1', 'guitar_2', 'guitar_4'),
              'alex': ('guitar_2', 'guitar_3', 'guitar_4'),
              'dominique': ('guitar_4', 'guitar_1', 'guitar_2')}

# Expected result: Ty:1, Alex:2, Dominique:4, Helene:X


##################



if __name__ == '__main__':

  allocation_1, allocation_2 = guitar_fest(rankings, ordering)

  print('Allocation 1:')
  for (person, guitar) in allocation_1.items():
    print(f'{person}: {guitar}')

  print('\nAllocation 2:')
  for (person, guitar) in allocation_2.items():
    print(f'{person}: {guitar}')



