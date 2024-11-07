import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from src.graphstate import WeeklyPlannerState 
from model.agents import agent_creator 
from utils.agent_tools import GoogleAPIClient

class Nodes:
    def __init__(self, llm) -> None:
        self.agent_creator = agent_creator(llm)
        self.weekly_planner = self.agent_creator.create_weekly_planner()
        self.daily_scheduler = self.agent_creator.create_daily_scheduler()
        self.google_api_client = GoogleAPIClient(os.getenv('GOOGLE_API_KEY'))

    async def create_weekly_summary(self, state: WeeklyPlannerState) -> dict:
        weekly_plan = self.weekly_planner.ainvoke(state)
        current_day_index = state['current_day_index']
        daily_agenda = weekly_plan.days[current_day_index].summary
        current_day = weekly_plan.days[current_day_index].day
        return {
            "daily_agenda": daily_agenda,
            "weekly_plan": weekly_plan,
            "current_day": current_day
        }

    async def create_daily_plan(self, state: WeeklyPlannerState) -> dict:
        daily_plan = self.daily_scheduler.ainvoke(state)
        return {"daily_plan": daily_plan}

    async def find_relevant_pois(self, WeeklyPlannerState):
        pass 
    
    async def find_route(self, WeeklyPlannerState):
        pass 

if __name__ == "__main__":
    from model.llm import LLM
    
    llm = LLM()
    nodes = Nodes(llm)
    state = WeeklyPlannerState()  # Initialize with proper parameters

