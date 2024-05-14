import csv

from dataclasses import dataclass
from functools import reduce
from os import path
from random import sample
from typing import Dict, FrozenSet, Tuple


Person = str
Guitar = str
Ranking = Tuple[Guitar, ...]
Rankings = Dict[Person, Ranking]
Ordering = Tuple[Person, ...]

@dataclass(frozen=True)
class Choice:
  person: Person
  guitar: Guitar

# For example, all the first-choice picks for all participants
ChoiceLevel = Tuple[Choice, ...]
Choices = Tuple[ChoiceLevel, ...]
Allocation = Dict[Person, Guitar]


def get_rankings_from_file(filepath: str) -> Rankings:
  csvreader = csv.reader(open(path.expanduser(filepath)))
  next(csvreader) # Skip header
  return {row[0]: tuple(filter(lambda i: i != '', row[1:])) for row in csvreader}


def order_choices(choices: Choices, ordering: Ordering) -> Choices:
  return tuple(tuple(sorted(choice_level, key=lambda c: ordering.index(c.person)))
      for choice_level in choices)


def build_choices_from_rankings(
    rankings: Rankings, ordering: Ordering) -> Choices:

  def get_ith_choice_level(i: int) -> ChoiceLevel:
    return tuple(Choice(person, ranking[i])
        for person, ranking in rankings.items() if len(ranking) > i)

  return order_choices(tuple(get_ith_choice_level(i)
      for i in range(max(len(ranking) for ranking in rankings.values()))), ordering)


def remove_guitar_and_person(
    choices: Choices, guitar: Guitar, person: Person) -> Choices:
  choice_filter = lambda c: c.person != person and c.guitar != guitar
  return tuple(tuple(filter(choice_filter, choice_level)) for choice_level in choices)


def make_starting_ordering(
    participants: Tuple[Person, ...], vips: Tuple[Person, ...]) -> Ordering:
  non_vips = tuple(filter(lambda p: p not in vips, participants))
  return vips + tuple(sample(non_vips, len(non_vips))) # sample shuffles list


def allocate_guitars(choices: Choices,
                      allocation: Allocation) -> Allocation:

  # All possible guitars allocated
  if len(choices) == 0:
    return allocation

  # No more valid allocations left at current choice level
  if len(choices[0]) == 0:
    return allocate_guitars(choices[1:], allocation)

  selection = choices[0][0]
  allocation[selection.person] = selection.guitar

  updated_choices = remove_guitar_and_person(
      choices, selection.guitar, selection.person)

  return allocate_guitars(updated_choices, allocation)


def guitar_fest(rankings: Rankings, ordering: Ordering) -> Tuple[Allocation, Allocation]:

  choices = build_choices_from_rankings(rankings, ordering)
  first_allocation = allocate_guitars(choices, {})

  allocated_pairs = tuple(Choice(person, guitar) for person, guitar in first_allocation.items())
  updated_choices = tuple(tuple(filter(lambda c: c not in allocated_pairs, choice_level))
      for choice_level in choices)

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


# ##### EXAMPLE #####

# ordering = ('ty', 'helene', 'alex', 'dominique')

rankings: Rankings = {
  'ty': ('guitar_1', 'guitar_2', 'guitar_3'),
  'helene': ('guitar_1', 'guitar_2', 'guitar_4'),
  'alex': ('guitar_2', 'guitar_3', 'guitar_4'),
  'dominique': ('guitar_4', 'guitar_1', 'guitar_2')}

# # Expected result: Ty:1, Alex:2, Dominique:4, Helene:X

# ##################


if __name__ == '__main__':

  # rankings = get_rankings_from_file('~/Downloads/rankings.csv')
  vips = ('ty',)
  ordering = make_starting_ordering(tuple(rankings.keys()), vips)

  allocation_1, allocation_2 = guitar_fest(rankings, ordering)

  print('Allocation 1:')
  for (person, guitar) in allocation_1.items():
    print(f'{person}: {guitar}')

  print('\nAllocation 2:')
  for (person, guitar) in allocation_2.items():
    print(f'{person}: {guitar}')
