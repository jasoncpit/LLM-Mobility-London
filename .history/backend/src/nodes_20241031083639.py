import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from langchain_openai import ChatOpenAI
import langgraph
from model.prompts import SYSTEM_PROMPT
from model.output_classes import *
import dotenv
from langchain_core.prompts import ChatPromptTemplate

dotenv.load_dotenv()
if os.getenv("OPENAI_API_KEY") is None:
    raise ValueError("OPENAI_API_KEY is not set")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

input_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT)
    ])

daily_schedule_node = input_template | llm.with_structured_output(WeeklySchedule)

if __name__ == "__main__":
    result = daily_schedule_node.invoke(
        {'user_description': "A 30 year old married software engineer lives in Stratford and works in "
        "West Kensignton. He loves to travel and explore new places."}
    )
    print(result)
