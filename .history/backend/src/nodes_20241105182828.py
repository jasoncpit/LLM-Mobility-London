import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.graphstate import WeeklyPlannerState 
from model.agents import agent_creator 
from utils.agent_tools import GoogleAPIClient

class nodes:
    def __init__(self, llm):
        self.agent_creator = agent_creator(llm) 
        self.weekly_planner = self.agent_creator.create_weekly_planner()
        self.daily_scheduler = self.agent_creator.create_daily_scheduler()  
    #Step 1: Create the weekly summary 
    async def create_weekly_summary(self, WeeklyPlannerState):
        weekly_plan = self.weekly_planner.ainvoke(WeeklyPlannerState) 
        current_day_plan = weekly_plan.days[0].summary
        current_day = weekly_plan.days[0].day
        return {current_day_plan: current_day_plan, weekly_plan: weekly_plan, current_day: current_day}

    #Step 2: Create the daily plan  
    async def create_daily_plan(self, WeeklyPlannerState): 
        return {current_day_plan: None}

    #Step 3: Find the most relevant POIs and append to the daily plan 
    async def find_relevant_pois(self, WeeklyPlannerState):
        pass 


if __name__ == "__main__":
    print(state)

