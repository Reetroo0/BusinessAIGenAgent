from typing import Dict, Optional
from ...main import run_agent
from ..tools.career_tools import analyze_user_profile, find_matching_vacancies, create_learning_plan, provide_career_advice


class CareerService:
    def __init__(self):
        pass

    @staticmethod
    def _extract_auth_headers(request) -> Dict:
        """Извлекает заголовки авторизации из запроса."""
        headers = {}
        auth = request.headers.get('authorization') or request.headers.get('Authorization')
        if auth:
            headers['Authorization'] = auth
        return headers

    async def analyze_profile(self, request, profile_data: Dict) -> str:
        """Анализирует профиль пользователя и предлагает карьерные направления."""
        headers = self._extract_auth_headers(request)
        question = (
            "Проанализируй профиль пользователя и предложи подходящие карьерные "
            "направления в ИТ. Укажи сильные стороны и области для развития."
        )
        return run_agent(question, user_profile=profile_data, headers=headers)

    async def find_vacancies(self, request, search_data: Dict) -> str:
        """Ищет подходящие вакансии на основе навыков и опыта."""
        headers = self._extract_auth_headers(request)
        question = (
            "Найди подходящие вакансии для пользователя на основе его навыков "
            "и требований. Предложи конкретные позиции и компании."
        )
        return run_agent(question, user_profile=search_data, headers=headers)

    async def create_learning_plan(self, request, plan_data: Dict) -> str:
        """Создает персонализированный план обучения."""
        headers = self._extract_auth_headers(request)
        question = (
            "Создай план обучения для перехода от текущих навыков к целевым. "
            "Предложи конкретные курсы, проекты и этапы развития."
        )
        return run_agent(question, user_profile=plan_data, headers=headers)

    async def get_career_advice(
        self, request, question: str, profile_data: Optional[Dict] = None
    ) -> str:
        """Предоставляет карьерные советы и рекомендации."""
        headers = self._extract_auth_headers(request)
        return run_agent(question, user_profile=profile_data, headers=headers)