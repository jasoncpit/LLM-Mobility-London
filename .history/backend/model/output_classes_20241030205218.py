from pydantic import BaseModel
from typing import List

class ScheduleEntry(BaseModel):
    time: str
    action: str
    location: str

class DailySchedule(BaseModel):
    day: str
    entries: List[ScheduleEntry]

class WeeklySchedule(BaseModel):
    days: List[DailySchedule]


