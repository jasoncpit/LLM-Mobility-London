import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict


class WeeklyPlannerState(TypedDict):
    user_description: str
    weekly_plan: WeeklySchedule
    current_day: dayofweek
    current_day_plan: DailySchedule
    

