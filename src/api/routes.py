from fastapi import APIRouter, HTTPException
from api.schemas import UserSessionResponse, CareerQueryRequest, CareerQueryResponse
from api.utils import save_json, load_json
from core.stepik_courses_collector import StepikCourseCollector
from core.vacancy_data_collector import HHDataCollector
import uuid
import os

router = APIRouter()

DATA_DIR = "data"
COURSES_FILE = os.path.join(DATA_DIR, "courses.json")
VACANCIES_FILE = os.path.join(DATA_DIR, "vacancies.json")

os.makedirs(DATA_DIR, exist_ok=True)

@router.post("/initialize_user_session", response_model=UserSessionResponse)
def initialize_user_session():
    """Создает новую пользовательскую сессию"""
    session_id = str(uuid.uuid4())
    return UserSessionResponse(session_id=session_id, message="Сессия успешно инициализирована.")

@router.post("/process_career_query", response_model=CareerQueryResponse)
def process_career_query(request: CareerQueryRequest):
    """Обрабатывает карьерный запрос: получает курсы и вакансии"""
    try:
        # --- Получаем вакансии с HH.ru ---
        hh_collector = HHDataCollector()
        vacancies = hh_collector.fetch_vacancies(queries=[request.query], per_page=10, pages_per_query=1)
        processed_vacancies = [hh_collector.process_vacancy(v) for v in vacancies]
        save_json(processed_vacancies, VACANCIES_FILE)

        # --- Получаем курсы с Stepik ---
        stepik_collector = StepikCourseCollector()
        courses = stepik_collector.fetch_stepik_courses(request.query, limit=5)
        save_json(courses, COURSES_FILE)

        return CareerQueryResponse(
            query=request.query,
            vacancies_count=len(processed_vacancies),
            courses_count=len(courses),
            message="Данные успешно собраны",
            saved_files={"vacancies": VACANCIES_FILE, "courses": COURSES_FILE}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке запроса: {e}")
