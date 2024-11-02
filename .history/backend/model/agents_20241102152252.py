from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from prompts import SCHEDULER_SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT 
from output_classes import WeeklySchedule, WeeklyPlanner
import dotenv
import os 
dotenv.load_dotenv() 
class agent:
    def __init__(self,llm):
        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OPENAI_API_KEY is not set")
        # SET UP LLM 
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

        self.llm = llm    
        # Weekly Schedule LLM planner -> given user description, generate weekly planner 
        self.weekly_scheduler = ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT)]) | llm.with_structured_output(WeeklySchedule)

        self.weekly_planner = ChatPromptTemplate.from_messages([
        ('system' , SCHEDULER_SYSTEM_PROMPT)]) | llm.with_structured_output(WeeklyPlanner) 

# Overture POI finders  -> given the weekly planner (Location, Activities), use web to find the most relevant POI points using overture and web? 

if __name__ == "__main__":
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    agent = agent(llm)
    result = agent.weekly_scheduler.invoke(
        {'user_description': "A 30 year old married software engineer lives in Stratford and works in "
        "West Kensignton. He loves to travel and explore new places."}
    )
    print(result)
