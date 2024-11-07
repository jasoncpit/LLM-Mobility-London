
import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict
from model.output_classes import WeeklySummary, dayofweek, DailyPlan

class WeeklyPlannerState(TypedDict):
    user_description: str
    weekly_plan: WeeklySummary
    current_day_index: int = 0
    daily_agenda: str 
    plans: list[DailyPlan] 
