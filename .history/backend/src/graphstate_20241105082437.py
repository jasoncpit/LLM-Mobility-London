import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from model.output_classes import WeeklySummary, DailyPlan 

class WeeklyPlannerState(TypedDict):
    user_description: str
    current_day_plan: str 
    weekly_plan: WeeklySchedule
    current_day: dayofweek
    

