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

    