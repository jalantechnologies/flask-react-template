from typing import List


def average_account_age(ages: List[int]) -> float:
    if not ages:
        return 0.0
    total = 0
    for age in ages:
        total += age
    return total / len(ages)
