from langchain_core.prompts import ChatPromptTemplate
from prompts import SCHEDULER_SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT 
from output_classes import WeeklySummary,DailyPlan 
import dotenv
import os 
class agent:
    def __init__(self,llm):
        self.llm = llm    
    def create_weekly_planner(self):
        # Weekly Schedule LLM planner -> given user description, generate weekly planner 
       return ChatPromptTemplate.from_messages([
            ("system", PLANNER_SYSTEM_PROMPT)]) | self.llm.with_structured_output(WeeklySummary)

    def create_daily_scheduler(self):
        return ChatPromptTemplate.from_messages([
        ('system' , SCHEDULER_SYSTEM_PROMPT)]) | self.llm.with_structured_output(DailyPlan) 

# Overture POI finders  -> given the weekly planner (Location, Activities), use web to find the most relevant POI points using overture and web? 

if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    import dotenv
    dotenv.load_dotenv() 
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    agent = agent(llm)
    result = agent.create_weekly_planner().invoke(
        {'user_description': "A 30 year old married software engineer lives in Stratford and works in "
        "West Kensignton. He loves to travel and explore new places. He works from home three times a week."}
    )
    print(result)
    example_schedule  = result.days[-2].summary 
    daily_planner = agent.create_daily_scheduler().invoke(
        {'user_description': "A 30 year old married software engineer lives in Stratford and works in "
        "West Kensignton. He loves to travel and explore new places. He works from home three times a week.",
        'daily_agenda': example_schedule}
    )
    print(daily_planner)
