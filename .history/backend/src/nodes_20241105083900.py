import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.graphstate import WeeklyPlannerState 
from model.agents import agent_creator 


class nodes:
    def __init__(self, llm):
        self.agent_creator = agent_creator(llm) 
        self.weekly_planner = self.agent_creator.create_weekly_planner()
        self.daily_scheduler = self.agent_creator.create_daily_scheduler()  
    #Step 1: Create the weekly summary 
    async def create_weekly_summary(self, WeeklyPlannerState):
        return {current_day_plan: None, weekly_plan: None}

    #Step 2: Create the daily plan  
    async def create_daily_plan(self, WeeklyPlannerState): 
        return {current_day_plan: None}

    #Step 3: Find the most relevant POIs and append to the daily plan 
    async def find_relevant_pois(self, WeeklyPlannerState):
        return {current_day_plan: None}  


if __name__ == "__main__":
    print(state)

