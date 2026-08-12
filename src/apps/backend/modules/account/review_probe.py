from typing import List


def average_account_age(ages: List[int]) -> float:
    total = 0
    for age in ages:
        total += age
    return total / len(ages)
