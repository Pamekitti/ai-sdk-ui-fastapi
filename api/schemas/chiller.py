from pydantic import BaseModel
from typing import List

class ScheduleTime(BaseModel):
    """Schema for a single schedule time slot"""
    start: str | None
    stop: str | None

class ScheduleChangeRequest(BaseModel):
    """Schema for chiller schedule change request"""
    chiller_id: str
    profile_type: str
    old_schedule: List[ScheduleTime]
    new_schedule: List[ScheduleTime]

class ScheduleChangeResponse(BaseModel):
    """Schema for chiller schedule change response"""
    success: bool
    message: str
    data: dict | None = None 