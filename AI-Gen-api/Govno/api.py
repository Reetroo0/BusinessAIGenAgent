from fastapi import FastAPI
import uvicorn

from app.routers import career

# Инициализация FastAPI приложения
app = FastAPI(
    title="IT Career Navigator API",
    description="API для карьерного навигатора в ИТ: анализ профиля, поиск вакансий, планирование обучения",
    version="1.0.0"
)


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


app = FastAPI(
    title="IT Career Navigator API",
    description="API для карьерного навигатора в ИТ: анализ профиля, поиск вакансий, планирование обучения",
    version="1.0.0"
)


@app.post("/analyze-profile")
async def analyze_profile(request: Request, data: ProfileAnalysisRequest):
    """Анализирует профиль пользователя и предлагает карьерные направления.
    
    Использует AI-агента для анализа навыков и предоставления рекомендаций по развитию.
    """
    try:
        headers = _extract_auth_headers(request)
        profile_dict = data.dict()
        
        question = (
            "Проанализируй профиль пользователя и предложи подходящие карьерные "
            "направления в ИТ. Укажи сильные стороны и области для развития."
        )
        result = run_agent(question, user_profile=profile_dict, headers=headers)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"analysis": result}


@app.post("/find-vacancies")
async def find_vacancies(request: Request, data: VacancySearchRequest):
    """Ищет подходящие вакансии на основе навыков и опыта.
    
    Использует базу вакансий и AI-агента для поиска и ранжирования результатов.
    """
    try:
        headers = _extract_auth_headers(request)
        search_dict = data.dict()
        
        question = (
            "Найди подходящие вакансии для пользователя на основе его навыков "
            "и требований. Предложи конкретные позиции и компании."
        )
        result = run_agent(question, user_profile=search_dict, headers=headers)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"vacancies": result}


@app.post("/create-learning-plan")
async def create_learning_plan(request: Request, data: LearningPlanRequest):
    """Создает персонализированный план обучения.
    
    Анализирует текущие и целевые навыки, предлагает курсы и этапы обучения.
    """
    try:
        headers = _extract_auth_headers(request)
        plan_dict = data.dict()
        
        question = (
            "Создай план обучения для перехода от текущих навыков к целевым. "
            "Предложи конкретные курсы, проекты и этапы развития."
        )
        result = run_agent(question, user_profile=plan_dict, headers=headers)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"learning_plan": result}


@app.post("/career-advice")
async def get_career_advice(request: Request, data: CareerAdviceRequest):
    """Предоставляет карьерные советы и рекомендации.
    
    Отвечает на вопросы по карьере в ИТ с учетом профиля пользователя.
    """
    try:
        headers = _extract_auth_headers(request)
        question = data.question
        profile = data.user_profile.dict() if data.user_profile else None
        
        result = run_agent(question, user_profile=profile, headers=headers)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"advice": result}


def _extract_auth_headers(request: Request) -> Dict:
    """Извлекает заголовки авторизации из запроса."""
    headers = {}
    auth = request.headers.get('authorization') or request.headers.get('Authorization')
    if auth:
        headers['Authorization'] = auth
    return headers


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)