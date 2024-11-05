import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from model.output_classes import WeeklySummary, dayofweek, DailyPlan, DailyPlan

class WeeklyPlannerState(TypedDict):
    user_description: str
    weekly_plan: WeeklySummary
    current_day: dayofweek
    current_day_plan_summary: str 
    current_day_plan: DailyPlan 
    

if __name__ == '__main__':
    print(next(dayofweek))