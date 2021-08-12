from datetime import datetime
from typing import Any, Dict, List


def recommend(budget: int, spent: int, restrs: List[Dict],
              dislikes: List[str],
              mess_menu: List[str]) -> Dict[str, Any]:
    """Recommend restaurant based on budget and the time of the month"""
    # Some constants (To be tweaked)
    DISLIKE_ERROR = 3
    LIKE_ERROR = 3
    THRESHHOLD_MOD = 6.6

    days = datetime.today().day
    perc_days = days / 31 * 100
    perc_budget = spent / budget * 100

    does_dislike = False
    for dish in mess_menu:
        if dish in dislikes:
            does_dislike = True
            break

    if does_dislike:
        mod_perc_budget = perc_budget - DISLIKE_ERROR
    else:
        mod_perc_budget = perc_budget + LIKE_ERROR

    print(mod_perc_budget)

    if mod_perc_budget < perc_days:
        # Rich buuooy, do recommend something
        restr_budget = ((perc_days + THRESHHOLD_MOD) - mod_perc_budget) * (budget - spent) / 100
        for restr in restrs:
            if restr["price"] <= restr_budget:
                return {"flag": True, "restr": restr}

        # Nope, false alarm, you're still poor, go home
        return {"flag": False, "restr": None}
    else:
        # You're poor, go home
        return {"flag": False, "restr": None}


if __name__ == "__main__":
    res = recommend(
        5000, 4000, [{"name": "abc", "price": 120},
                     {"name": "def", "price": 300}],
        ["tinda", "lauki"],
        ["chole", "raita"])
    print(res)
