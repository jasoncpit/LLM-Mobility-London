import os
from langchain_openai import ChatOpenAI
import langgraph 
from backend.model.prompts import SYSTEM_PROMPT
from backend.model.output_classes import *

if os.getenv("OPENAI_API_KEY") is None:
    raise ValueError("OPENAI_API_KEY is not set")

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

daily_schedule_node = llm | StrOutputParser()

if __name__ == "__main__":
    result = llm.invoke({"user_description": "A 30 year old software engineer who loves to travel and explore new places."})
    print(result)

