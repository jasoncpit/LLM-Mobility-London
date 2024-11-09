from langgraph.graph import END
from typing import Literal
from graphstate import WeeklyPlannerState 
class Edges:
    @staticmethod
    async def routing_edge(state: WeeklyPlannerState) -> Literal[END, 'CreateDailyPlan']:
        if state['current_day_index'] == 6:
            return END
        else:
            return 'CreateDailyPlan'

