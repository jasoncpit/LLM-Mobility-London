import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
from model.llm import weekly_schedule_planner
if __name__ == "__main__":
    import json
    result = weekly_schedule_planner.invoke(
        {'user_description': "A 30 year old married software engineer lives in Stratford and works in "
        "West Kensignton. He loves to travel and explore new places."}
    )
    # Save the result to json file with indent 4
    with open("result.json", "w") as f:
        json.dump(result.model_dump(), f, indent=4)
