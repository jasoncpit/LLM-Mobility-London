from langgraph.graph import Graph 
import os
import dotenv
from langgraph.graph import END, START, StateGraph 
from nodes import Nodes
from edges import Edges
from graphstate import WeeklyPlannerState 
from langchain_openai import ChatOpenAI
dotenv.load_dotenv()


class App:
    def __init__(self, llm):
        self.nodes = Nodes(llm)
        self.edges = Edges()
    def setup(self):
        workflow = StateGraph(WeeklyPlannerState)
        #Nodes 
        workflow.add_node('CreateWeeklySummary', self.nodes.create_weekly_summary)
        workflow.add_node('CreateDailyPlan', self.nodes.create_daily_plan)
        workflow.add_node('POIFinder', self.nodes.find_relevant_pois) 

        # Edges
        workflow.add_edge(START, 'CreateWeeklySummary')
        workflow.add_edge('CreateWeeklySummary', 'CreateDailyPlan')
        workflow.add_edge('CreateDailyPlan', 'POIFinder')
        workflow.add_conditional_edges('POIFinder', self.edges.routing_edge)
        app = workflow.compile()
        return app 

    @staticmethod
    def save_plans_to_pandas(traces):
        # Import pandas
        import pandas as pd
        
        # Create empty list to store plan entries
        all_entries = []
        
        # Get the plans from the last trace
        if traces and isinstance(traces[-1], dict) and 'plans' in traces[-1]:
            all_plans = traces[-1]['plans']
            
            # Map plans to days of week 
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # Extract entries from each daily plan
            for plan, day in zip(all_plans, days):
                for entry in plan.entries:
                    entry_dict = {
                        'day': day,
                        'time': entry.time,
                        'action': entry.action,
                        'poi_category': entry.poi_category,
                        'location': entry.location,
                        'travel_mode': entry.travel_mode.value if hasattr(entry.travel_mode, 'value') else entry.travel_mode,
                        'poi_name': entry.poi_output.name if entry.poi_output else None,
                        'latitude': entry.poi_output.latitude if entry.poi_output else None,
                        'longitude': entry.poi_output.longitude if entry.poi_output else None,
                        'address': entry.poi_output.address if entry.poi_output else None
                    }
                    all_entries.append(entry_dict)
        
        # Convert to pandas DataFrame
        df = pd.DataFrame(all_entries)
        return df


    @staticmethod
    def post_process_traces(traces):   
        traces = [trace for trace in traces if 'current_day_index' in trace]
        traces = [trace for trace in traces if 'plans' in trace]
        schedule_df = save_plans_to_pandas(traces)
        routes, time, day, travel_mode = client.compute_routes(traces)

        return schedule_df, routes, time, day, travel_mode