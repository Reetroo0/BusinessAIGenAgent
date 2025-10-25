from fastapi import APIRouter, Request, HTTPException, Depends
from typing import Dict

from ..schemas.career import (
    ProfileAnalysisRequest, VacancySearchRequest,
    LearningPlanRequest, CareerAdviceRequest,
    ProfileAnalysisResponse, VacancySearchResponse,
    LearningPlanResponse, CareerAdviceResponse
)
from ..services.career import CareerService

router = APIRouter(prefix="/career", tags=["career"])


def get_career_service() -> CareerService:
    """Dependency для получения сервиса."""
    return CareerService()

# Анализирует профиль пользователя и предлагает карьерные направления
@router.post("/analyze-profile", response_model=ProfileAnalysisResponse)
async def analyze_profile(
    request: Request,
    data: ProfileAnalysisRequest,
    service: CareerService = Depends(get_career_service)
):
    """Анализирует профиль пользователя и предлагает карьерные направления."""
    try:
        result = await service.analyze_profile(request, data.dict())
        return ProfileAnalysisResponse(analysis=result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ищет подходящие вакансии на основе навыков и опыта
@router.post("/find-vacancies", response_model=VacancySearchResponse)
async def find_vacancies(
    request: Request,
    data: VacancySearchRequest,
    service: CareerService = Depends(get_career_service)
):
    """Ищет подходящие вакансии на основе навыков и опыта."""
    try:
        result = await service.find_vacancies(request, data.dict())
        return VacancySearchResponse(vacancies=result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Создает персонализированный план обучения
@router.post("/create-learning-plan", response_model=LearningPlanResponse)
async def create_learning_plan(
    request: Request,
    data: LearningPlanRequest,
    service: CareerService = Depends(get_career_service)
):
    """Создает персонализированный план обучения."""
    try:
        result = await service.create_learning_plan(request, data.dict())
        return LearningPlanResponse(learning_plan=result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Предоставляет карьерные советы и рекомендации
@router.post("/advice", response_model=CareerAdviceResponse)
async def get_career_advice(
    request: Request,
    data: CareerAdviceRequest,
    service: CareerService = Depends(get_career_service)
):
    """Предоставляет карьерные советы и рекомендации."""
    try:
        profile = data.user_profile.dict() if data.user_profile else None
        result = await service.get_career_advice(request, data.question, profile)
        return CareerAdviceResponse(advice=result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))