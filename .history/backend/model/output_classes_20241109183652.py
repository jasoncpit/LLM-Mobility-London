from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from enum import Enum

#########################
# POI 
#########################
class POI(BaseModel):
    name: str = Field(description="The name of the POI")
    latitude: float = Field(description="The latitude of the POI")
    longitude: float = Field(description="The longitude of the POI")
    address: str = Field(description="The address of the POI")

#########################
# Daily Schedule 
#########################
class TravelMode(Enum):
    BICYCLE = "BICYCLE"
    DRIVE = "DRIVE"
    WALK = "WALK"
    TRANSIT = "TRANSIT"
    TRAVEL_MODE_UNSPECIFIED	 = "TRAVEL_MODE_UNSPECIFIED" 
class ScheduleEntry(BaseModel):
    time: str = Field(description="The time of the activity in 24 hour format")
    action: str = Field(description="The activity to be performed")
    poi_category: str = Field(description="The category of point of interest to be visited")
    location: str = Field(description="The location of the activity")
    travel_mode: TravelMode = Field(description="The mode of transport to be used")
    poi_output: Optional[POI] = Field(description="The point of interest to be visited")

class DailyPlan(BaseModel):
    model_config = ConfigDict(frozen=False)  # Makes the model mutable
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


