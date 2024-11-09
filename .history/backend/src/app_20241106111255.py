from langgraph.graph import Graph 
import os
import dotenv
from langgraph.graph import END, START, StateGraph 
from nodes import Nodes
from edges import Edges
from langchain_openai import ChatOpenAI
dotenv.load_dotenv()


class FullGraph:
    def __init__(self, llm):
        self.llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
        self.nodes = Nodes(self.llm)
        self.edges = Edges() 
