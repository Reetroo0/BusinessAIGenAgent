from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from langchain.tools.base import tool
from langchain.callbacks.manager import CallbackManagerForToolRun

import json
import re
from difflib import SequenceMatcher
from ..utils.paths import COURSES_DATA_PATH, VACANCIES_DATA_PATH


# Модели данных для профиля пользователя
class UserProfile(BaseModel):
    education_level: str = Field(description="Уровень образования пользователя")
    known_technologies: List[str] = Field(description="Список известных технологий и языков программирования")
    interests: List[str] = Field(description="Направления ИТ, которые интересуют пользователя")
    experience: str = Field(description="Опыт работы (если есть)")
    career_goals: Optional[str] = Field(description="Карьерные цели")


class Vacancy(BaseModel):
    id: str
    title: str
    company: str
    required_skills: List[str]
    preferred_skills: List[str]
    salary_range: Optional[Dict[str, int]]
    experience_level: str
    description: str


class Course(BaseModel):
    id: str
    title: str
    platform: str
    skills_covered: List[str]
    duration: str
    level: str
    url: str


# Загрузка данных о вакансиях и курсах
def load_vacancies_data() -> Dict:
    """Загрузка данных о вакансиях из JSON файла"""
    try:
        with open(VACANCIES_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"vacancies": []}


def load_courses_data() -> Dict:
    """Загрузка данных о курсах из JSON файла"""
    try:
        with open(COURSES_DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"courses": []}


# Синонимы навыков для нормализации
SKILLS_SYNONYMS = {
    "python": ["python", "python3", "питон"],
    "javascript": ["javascript", "js", "ecmascript"],
    "java": ["java", "джава"],
    "sql": ["sql", "mysql", "postgresql", "базы данных"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "react": ["react", "react.js", "reactjs"],
    "vue": ["vue", "vue.js", "vuejs"],
    "angular": ["angular", "angular.js", "angularjs"],
    "node": ["node", "node.js", "nodejs"],
    "docker": ["docker", "докер"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services"],
    "git": ["git", "гит"],
    "linux": ["linux", "unix"],
    "machine learning": ["machine learning", "ml", "машинное обучение"],
    "data science": ["data science", "data analysis", "анализ данных"],
    "data analysis": ["data analysis", "анализ данных", "data analytics"],
    "business intelligence": ["business intelligence", "bi", "бизнес-аналитика"],
}


# Функции-инструменты для агента
@tool
def analyze_user_profile(user_input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """Анализирует профиль пользователя для определения карьерных возможностей"""
    try:
        profile = UserProfile(**json.loads(user_input))
        # Анализ профиля и генерация рекомендаций...
        return "Анализ профиля проведен успешно"
    except Exception as e:
        return f"Ошибка при анализе профиля: {str(e)}"


@tool
def find_matching_vacancies(skills_json: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """Находит подходящие вакансии на основе навыков"""
    try:
        skills = json.loads(skills_json)
        vacancies = load_vacancies_data().get("vacancies", [])
        # Поиск и фильтрация вакансий...
        return "Найдены подходящие вакансии"
    except Exception as e:
        return f"Ошибка при поиске вакансий: {str(e)}"


@tool
def create_learning_plan(plan_json: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """Создает план обучения на основе текущих и целевых навыков"""
    try:
        plan_data = json.loads(plan_json)
        courses = load_courses_data().get("courses", [])
        # Создание плана обучения...
        return "План обучения создан"
    except Exception as e:
        return f"Ошибка при создании плана: {str(e)}"


@tool
def provide_career_advice(query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
    """Предоставляет карьерные советы на основе запроса"""
    try:
        # Генерация карьерного совета...
        return "Карьерный совет предоставлен"
    except Exception as e:
        return f"Ошибка при генерации совета: {str(e)}"