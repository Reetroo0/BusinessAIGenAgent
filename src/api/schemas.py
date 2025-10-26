from pydantic import BaseModel
from typing import Dict, Optional

class UserSessionResponse(BaseModel):
    session_id: str
    message: str

class CareerQueryRequest(BaseModel):
    query: str

class CareerQueryResponse(BaseModel):
    query: str
    vacancies_count: int
    courses_count: int
    message: str
    saved_files: Dict[str, str]
