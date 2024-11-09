from langgraph.graph import END
from typing import Literal

class Edge:
    def routing_edge(state: WeeklyPlannerState) -> Literal['END', None]:
        if state['current_day_index'] == 6:
        return END
        else:
            return 'DailyPlanner'

