from pydantic import BaseModel, Field
from typing import List
from enum import Enum

#########################
# Daily Schedule 
#########################
class ScheduleEntry(BaseModel):
    time: str = Field(description="The time of the activity in 24 hour format")
    action: str = Field(description="The activity to be performed")
    location: str = Field(description="The location of the activity")
    reason: str = Field(description="The reason for the activity")

class DailyPlan(BaseModel):
    entries: List[ScheduleEntry] = Field(description="The activities to be performed on the day")

class WeeklyPlan(BaseModel):
    days: List[DailyPlan] = Field(description="The activities to be performed on each day of the week")

#########################
# Weekly Planner 
#########################
class dayofweek(Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

class DailySummary(BaseModel):
    day: dayofweek = Field(description="The day of the week")
    summary: str = Field(description="A key summary of the day")
class WeeklySummary(BaseModel): 
    days: List[DailySummary] = Field(description="The key summaries of each day of the week")


