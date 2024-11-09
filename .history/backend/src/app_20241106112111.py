from langgraph.graph import Graph 
import os
import dotenv
from langgraph.graph import END, START, StateGraph 
from nodes import Nodes
from edges import Edges
from graphstate import WeeklyPlannerState 
from langchain_openai import ChatOpenAI
dotenv.load_dotenv()


class FullGraph:
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


if __name__ == "__main__":
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
    app = FullGraph(llm)
    app = app.setup()
    for event in app.astream({
        "user_description": "I am a 30 year old male who loves to travel and explore new places. I am looking for a week long trip to a city with a lot of culture and history."
    }):
        print(event)

