from pydantic import BaseModel
from typing import List, Dict, Optional

class ProfileAnalysisRequest(BaseModel):
    education_level: str
    known_technologies: List[str]
    interests: List[str]
    experience: Optional[str] = None
    career_goals: Optional[str] = None


class VacancySearchRequest(BaseModel):
    skills: List[str]
    experience_level: Optional[str] = None
    preferred_salary_range: Optional[Dict[str, int]] = None


class LearningPlanRequest(BaseModel):
    current_skills: List[str]
    target_skills: List[str]
    preferred_duration: Optional[str] = None
    learning_style: Optional[str] = None


class CareerAdviceRequest(BaseModel):
    question: str
    user_profile: Optional[ProfileAnalysisRequest] = None


# Модели ответов
class ProfileAnalysisResponse(BaseModel):
    analysis: str


class VacancySearchResponse(BaseModel):
    vacancies: str


class LearningPlanResponse(BaseModel):
    learning_plan: str


class CareerAdviceResponse(BaseModel):
    advice: str