from typing import List


def average_account_age(ages: List[int]) -> float:
    if not ages:
        return 0.0
    total = 0
    for age in ages:
        total += age
    return total / len(ages)


def total_account_age(ages: List[int]) -> int:
    return sum(ages)


def newest_account_age(ages: List[int]) -> int:
    if not ages:
        return 0
    return ages[len(ages) - 1]
