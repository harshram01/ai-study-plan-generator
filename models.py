from typing import List, Dict
from pydantic import BaseModel, Field


# --- Input Models ---
class SubjectScore(BaseModel):
    current_score: float = Field(..., description="Current test or assignment score out of 100")
    target_score: float = Field(..., description="Target or passing threshold score out of 100")
    weak_areas: List[str] = Field(default_factory=list, description="Specific topics needing improvement")


class StudentProfile(BaseModel):
    student_id: str
    available_hours_per_week: float
    subjects: Dict[str, SubjectScore]


# Alias for backward compatibility with extractor.py
StudentAcademicData = StudentProfile


# --- Output Models ---
class DailyPlanItem(BaseModel):
    day: str = Field(..., description="e.g., Monday, Tuesday")
    subject: str = Field(..., description="Subject name")
    topic: str = Field(..., description="Target concept to revise")
    duration_hours: float = Field(..., description="Allocated study time in hours")
    recommended_action: str = Field(..., description="Specific activity: problem sets, review, or code practice")


class StudyRecommendation(BaseModel):
    diagnostic_summary: str = Field(..., description="Brief analysis of current academic standing")
    priority_topics: List[str] = Field(..., description="High-priority topics needing immediate remediation")
    weekly_schedule: List[DailyPlanItem] = Field(..., description="Targeted weekly action plan")
    study_tips: List[str] = Field(..., description="Targeted pedagogical guidance or strategies")