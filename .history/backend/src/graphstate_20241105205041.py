
import os
import sys
# Go to the root of the project
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict

class WeeklyPlannerState(TypedDict):
    user_description: str
