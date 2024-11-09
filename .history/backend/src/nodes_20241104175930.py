import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from model.agents import weekly_schedule_planner, daily_schedule_planner
from src.graphstate import WeeklyPlannerState 

if __name__ == "__main__":
    state = WeeklyPlannerState()
    print(state)

