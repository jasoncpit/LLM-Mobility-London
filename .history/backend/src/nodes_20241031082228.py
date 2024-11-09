import os
from langchain_openai import ChatOpenAI
import langgraph 
from backend.model.prompts import SYSTEM_PROMPT
from backend.model.output_classes import *

if os.getenv("OPENAI_API_KEY") is None:
    raise ValueError("OPENAI_API_KEY is not set")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

daily_schedule_node = llm.with_structured_output(WeeklySchedule)

if __name__ == "__main__":
    result = llm.invoke("A 30 year old married software engineer lives in Stratford and works in West Kensignton. He loves to travel and explore new places."})
    print(result)

