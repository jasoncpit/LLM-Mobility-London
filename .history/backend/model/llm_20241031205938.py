from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from model.prompts import SCHEDULER_SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT 
from model.output_classes import WeeklySchedule, weeklyplanner
import dotenv
import os 
dotenv.load_dotenv()
if os.getenv("OPENAI_API_KEY") is None:
    raise ValueError("OPENAI_API_KEY is not set")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# Weekly Schedule LLM planner -> given user description, generate weekly planner 
weekly_schedule_planner = ChatPromptTemplate.from_messages([
    ("system", PLANNER_SYSTEM_PROMPT)
    ]) | llm.with_structured_output(WeeklySchedule)

weekly_planner = ChatPromptTemplate.from([
 ('system' , SCHEDULER_SYSTEM_PROMPT)
]
)

# Overture POI finders  -> given the weekly planner (Location, Activities), use web to find the most relevant POI points using overture and web? 
 
