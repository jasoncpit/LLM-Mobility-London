import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
#from model.agents import weekly_schedule_planner, daily_schedule_planner
from src.graphstate import WeeklyPlannerState 

#Step 1: Create the weekly summary 
async def create_weekly_summary(WeeklyPlannerState):
    return {current_day_plan: None, weekly_plan: None}

#Step 2: Create the daily plan  
async def create_daily_plan(WeeklyPlannerState): 
    return {current_day_plan: None}

#Step 3: Find the most relevant POIs and append to the daily plan 
async def find_relevant_pois(WeeklyPlannerState):
    return {current_day_plan: None}  


if __name__ == "__main__":
    print(state)

