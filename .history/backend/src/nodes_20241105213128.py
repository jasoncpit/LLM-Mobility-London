from typing import Dict, Any
import logging
import os
import sys
from pathlib import Path

# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from graphstate import WeeklyPlannerState 
from model.agents import agent_creator 
from utils.agent_tools import GoogleAPIClient
import dotenv
import asyncio
dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Nodes:
    def __init__(self, llm) -> None:
        """Initialize Nodes with language model and required agents.
        
        Args:
            llm: Language model instance
        """
        try:
            self.agent_creator = agent_creator(llm)
            self.weekly_planner = self.agent_creator.create_weekly_planner()
            self.daily_scheduler = self.agent_creator.create_daily_scheduler()
            self.google_api_client = GoogleAPIClient(os.getenv('GOOGLE_API_KEY'))
        except Exception as e:
            logger.error(f"Failed to initialize Nodes: {str(e)}")
            raise

    async def create_weekly_summary(self, state: WeeklyPlannerState) -> Dict[str, Any]:
        try:
            return {
                "weekly_plan": await self.weekly_planner.ainvoke(state)
            }
        except Exception as e:
            logger.error(f"Error creating weekly summary: {str(e)}")
            raise

    async def create_daily_plan(self, state: WeeklyPlannerState) -> Dict[str, Any]:
        try:
            current_day_index = state['current_day_index']
            current_day_agenda = state['weekly_plan'].days[current_day_index].summary 
            daily_plan = await self.daily_scheduler.ainvoke({"daily_agenda": current_day_agenda,"user_description": state['user_description']})
            plans = daily_plan if state['plans'] is None else state['plans'] + [daily_plan]
            return {
                "plans": plans,
                "current_day_index": current_day_index + 1,
                "daily_agenda": current_day_agenda
            }

        except Exception as e:
            logger.error(f"Error creating daily plan: {str(e)}")
            raise

    async def find_relevant_pois(self, state: WeeklyPlannerState) -> Dict[str, Any]:
        """Find points of interest relevant to the weekly plan.
        
        Args:
            state: Current weekly planner state
            
        Returns:
            Dictionary containing relevant POIs
        """
        try: 
            return None 
        except Exception as e:
            logger.error(f"Error finding POIs: {str(e)}")
            raise
    
    async def find_route(self, state: WeeklyPlannerState) -> Dict[str, Any]:
        """Find optimal route based on the plan.
        
        Args:
            state: Current weekly planner state
            
        Returns:
            Dictionary containing route information
        """
        try:
            # Implementation needed
            return {"route": []}
        except Exception as e:
            logger.error(f"Error finding route: {str(e)}")
            raise

if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    
    async def main():
        try:
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
            nodes = Nodes(llm)
            state = WeeklyPlannerState(
                user_description="I am a software engineer who wants to plan my week who lives in Stratford, London and works in West Kensington, London",
                current_day_index=0
            )
            weekly_summary = await nodes.create_weekly_summary(state)
            logger.info(f"Weekly summary created: {weekly_summary}")
            # Update sate 
            new_state = state.copy()
            new_state['weekly_plan'] = weekly_summary['weekly_plan']
            new_state['plans'] = None 
            daily_plan = await nodes.create_daily_plan(new_state)
            logger.info(f"Daily plan created: {daily_plan}")
        except Exception as e:
            logger.error(f"Main execution failed: {str(e)}")
            sys.exit(1)

    asyncio.run(main())
