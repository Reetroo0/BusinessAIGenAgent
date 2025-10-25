from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from langchain.tools.base import tool
from langchain.callbacks.manager import CallbackManagerForToolRun

import json
import re
from pathlib import Path
from difflib import SequenceMatcher


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
def load_vacancies_data(path: str | Path = None) -> Dict:
    """Загрузка данных о вакансиях из JSON файла"""
    if path is None:
        path = Path(__file__).parent / 'processed_vacancies.json'
    else:
        path = Path(path)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"vacancies": []}


def load_courses_data(path: str | Path = None) -> Dict:
    """Загрузка данных о курсах из JSON файла"""
    if path is None:
        path = Path(__file__).parent / 'courses_data.json'
    else:
        path = Path(path)
    try:
        with open(path, 'r', encoding='utf-8') as f:
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


# Функция №1: Анализ профиля пользователя
@tool
def analyze_user_profile(user_input: str) -> str:
    """
    Анализирует ввод пользователя и извлекает информацию о навыках, образовании и интересах.
    Используется для первичного знакомства с пользователем и создания профиля.

    Args:
        user_input: Текст от пользователя с описанием его背景, навыков и интересов

    Returns:
        str: Структурированный анализ профиля пользователя
    """
    print("Вызвана функция: analyze_user_profile")

    # Извлечение информации из текста
    education_level = extract_education_level(user_input)
    skills = extract_skills_from_text(user_input)
    interests = extract_interests(user_input)
    experience = extract_experience(user_input)

    # Анализ соответствия направлений
    recommended_directions = recommend_career_directions(skills, interests)

    # Формирование ответа
    response = f"""🎯 Отлично! Я проанализировал ваш профиль:

📊 Ваши текущие навыки:
{format_skills_list(skills)}

🎓 Уровень образования: {education_level}
💼 Опыт: {experience}

🎯 Рекомендуемые направления:
{format_recommendations(recommended_directions)}

Хотите:
🔍 Посмотреть подходящие вакансии для начинающих
📚 Получить учебный план для развития  
💬 Обсудить карьерные возможности"""

    return response


def extract_education_level(text: str) -> str:
    """Извлекает уровень образования из текста"""
    text_lower = text.lower()

    if any(word in text_lower for word in ['студент', 'учусь', 'обучаюсь', 'вуз', 'универ']):
        if '1 курс' in text_lower:
            return "Студент 1 курса"
        elif '2 курс' in text_lower:
            return "Студент 2 курса"
        elif '3 курс' in text_lower:
            return "Студент 3 курса"
        elif '4 курс' in text_lower:
            return "Студент 4 курса"
        else:
            return "Студент"
    elif any(word in text_lower for word in ['выпускник', 'закончил', 'окончил']):
        return "Выпускник"
    elif any(word in text_lower for word in ['школ', 'ученик']):
        return "Школьник"
    else:
        return "Не указано"


def extract_skills_from_text(text: str) -> List[str]:
    """Извлекает навыки из текста"""
    text_lower = text.lower()
    found_skills = set()

    # Поиск навыков по синонимам
    for normalized_skill, synonyms in SKILLS_SYNONYMS.items():
        for synonym in synonyms:
            if synonym in text_lower:
                found_skills.add(normalized_skill)
                break

    # Дополнительные паттерны для извлечения
    skill_patterns = [
        r'\b(python|javascript|java|sql|html|css|react|vue|angular|node|docker|kubernetes|aws|git|linux)\b',
        r'\b(machine learning|data science|data analysis|business intelligence|computer vision)\b',
        r'\b(программирование|разработка|анализ данных|тестирование|автоматизация)\b'
    ]

    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            normalized_skill = normalize_skill(match)
            found_skills.add(normalized_skill)

    return list(found_skills)


def extract_interests(text: str) -> List[str]:
    """Извлекает интересы из текста"""
    text_lower = text.lower()
    interests = []

    interest_keywords = {
        'data analysis': ['анализ данных', 'data analysis', 'аналитик'],
        'machine learning': ['машинное обучение', 'machine learning', 'ml'],
        'web development': ['веб-разработка', 'web development', 'frontend', 'backend'],
        'mobile development': ['мобильная разработка', 'mobile development'],
        'devops': ['devops', 'инфраструктура'],
        'data science': ['data science', 'наука о данных'],
    }

    for interest, keywords in interest_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            interests.append(interest)

    return interests


def extract_experience(text: str) -> str:
    """Извлекает информацию об опыте"""
    text_lower = text.lower()

    if any(phrase in text_lower for phrase in ['нет опыта', 'без опыта', 'опыта нет', 'пока нет']):
        return "Без опыта работы"
    elif any(word in text_lower for word in ['стажировка', 'интерн', 'практик']):
        return "Опыт стажировки"
    elif any(word in text_lower for word in ['опыт работы', 'работал', 'работаю']):
        return "Есть опыт работы"
    else:
        return "Не указан"


def normalize_skill(skill: str) -> str:
    """Нормализует название навыка"""
    skill = skill.lower().strip()

    for normalized_skill, synonyms in SKILLS_SYNONYMS.items():
        if skill in synonyms:
            return normalized_skill

    return skill


def recommend_career_directions(skills: List[str], interests: List[str]) -> List[Dict[str, Any]]:
    """Рекомендует карьерные направления на основе навыков и интересов"""
    directions = [
        {
            "name": "Data Analyst",
            "required_skills": ["python", "sql", "data analysis"],
            "match_score": 0
        },
        {
            "name": "Data Scientist",
            "required_skills": ["python", "machine learning", "data science"],
            "match_score": 0
        },
        {
            "name": "Business Intelligence Analyst",
            "required_skills": ["sql", "business intelligence", "data analysis"],
            "match_score": 0
        },
        {
            "name": "Backend Developer",
            "required_skills": ["python", "java", "sql", "node"],
            "match_score": 0
        },
        {
            "name": "Frontend Developer",
            "required_skills": ["javascript", "html", "css", "react"],
            "match_score": 0
        }
    ]

    # Расчет соответствия для каждого направления
    for direction in directions:
        required = direction["required_skills"]
        matched_skills = 0

        for req_skill in required:
            for user_skill in skills:
                if calculate_skill_similarity(user_skill, req_skill) > 0.7:
                    matched_skills += 1
                    break

        direction["match_score"] = matched_skills / len(required) if required else 0

    # Сортировка по убыванию соответствия
    directions.sort(key=lambda x: x["match_score"], reverse=True)

    return directions[:3]  # Возвращаем топ-3 направления


def calculate_skill_similarity(skill1: str, skill2: str) -> float:
    """Рассчитывает схожесть между двумя навыками"""
    return SequenceMatcher(None, skill1.lower(), skill2.lower()).ratio()


def format_skills_list(skills: List[str]) -> str:
    """Форматирует список навыков для вывода"""
    if not skills:
        return "• Навыки не обнаружены"

    return "\n".join([f"• {skill.capitalize()}" for skill in skills])


def format_recommendations(recommendations: List[Dict]) -> str:
    """Форматирует рекомендации для вывода"""
    result = []
    for rec in recommendations:
        score = rec["match_score"]
        if score >= 0.7:
            level = "высокое соответствие"
        elif score >= 0.4:
            level = "среднее соответствие"
        else:
            level = "низкое соответствие"

        result.append(f"{len(result) + 1}. {rec['name']} - {level}")

    return "\n".join(result)


# Функция №2: Подбор вакансий по профилю
@tool
def find_matching_vacancies(user_skills: str, experience_level: str = "beginner") -> str:
    """
    Подбирает подходящие вакансии на основе навыков пользователя и уровня опыта.

    Args:
        user_skills: Строка с навыками пользователя (через запятую или в свободной форме)
        experience_level: Уровень опыта (beginner, junior, middle)

    Returns:
        str: Отформатированный список подходящих вакансий
    """
    print("Вызвана функция: find_matching_vacancies")

    # Извлекаем навыки из входной строки
    skills_list = extract_skills_from_text(user_skills)
    vacancies_data = load_vacancies_data()

    if not vacancies_data.get("vacancies"):
        return "К сожалению, база вакансий временно недоступна. Попробуйте позже."

    matching_vacancies = []

    for vacancy in vacancies_data["vacancies"]:
        # Проверяем соответствие уровню опыта
        vacancy_exp = vacancy.get("experience", "").lower()
        if experience_level == "beginner" and "senior" in vacancy_exp:
            continue

        # Расчет соответствия навыков
        vacancy_skills = vacancy.get("skills", [])
        match_score = calculate_vacancy_match(skills_list, vacancy_skills)

        if match_score > 0.3:  # Пороговое значение
            matching_vacancies.append({
                "vacancy": vacancy,
                "match_score": match_score
            })

    # Сортировка по релевантности
    matching_vacancies.sort(key=lambda x: x["match_score"], reverse=True)

    if not matching_vacancies:
        return "К сожалению, по вашему запросу не найдено подходящих вакансий. Попробуйте расширить список навыков."

    return format_vacancies_response(matching_vacancies[:5])


def calculate_vacancy_match(user_skills: List[str], vacancy_skills: List[str]) -> float:
    """Рассчитывает соответствие между навыками пользователя и вакансии"""
    if not user_skills or not vacancy_skills:
        return 0.0

    matched_skills = 0
    for vacancy_skill in vacancy_skills:
        for user_skill in user_skills:
            if calculate_skill_similarity(user_skill, vacancy_skill) > 0.7:
                matched_skills += 1
                break

    return matched_skills / len(vacancy_skills)


def format_vacancies_response(vacancies: List[Dict]) -> str:
    """Форматирует ответ с вакансиями"""
    response = "🔍 Найдены подходящие вакансии:\n\n"

    for i, vac_data in enumerate(vacancies, 1):
        vacancy = vac_data["vacancy"]
        match_score = vac_data["match_score"]

        response += f"{i}. **{vacancy.get('name', 'Название не указано')}**\n"
        response += f"   🏢 {vacancy.get('company', 'Компания не указана')}\n"
        response += f"   💰 {vacancy.get('salary', 'Зарплата не указана')}\n"
        response += f"   🎯 Совпадение: {match_score:.0%}\n"
        response += f"   📍 {vacancy.get('experience', 'Опыт не указан')}\n\n"

    response += "Хотите увидеть больше вакансий или получить детали по конкретной позиции?"
    return response


# Функция №3: Создание учебного плана
@tool
def create_learning_plan(target_position: str, current_skills: str) -> str:
    """
    Создает персонализированный учебный план для достижения целевой должности.

    Args:
        target_position: Целевая должность (например, "Data Analyst")
        current_skills: Текущие навыки пользователя

    Returns:
        str: Структурированный учебный план
    """
    print("Вызвана функция: create_learning_plan")

    current_skills_list = extract_skills_from_text(current_skills)
    courses_data = load_courses_data()

    # Определяем требуемые навыки для целевой позиции
    required_skills_map = {
        "data analyst": ["sql", "python", "data analysis", "excel", "tableau"],
        "data scientist": ["python", "machine learning", "sql", "statistics", "data science"],
        "frontend developer": ["javascript", "html", "css", "react", "git"],
        "backend developer": ["python", "sql", "docker", "linux", "git"]
    }

    target_skills = required_skills_map.get(target_position.lower(), [])
    missing_skills = [skill for skill in target_skills
                      if not any(calculate_skill_similarity(skill, user_skill) > 0.7
                                 for user_skill in current_skills_list)]

    if not missing_skills:
        return f"Отлично! Ваши текущие навыки уже соответствуют требованиям для {target_position}. Рекомендуется сосредоточиться на практике и создании проектов для портфолио."

    # Подбираем курсы для недостающих навыков
    recommended_courses = []
    for skill in missing_skills:
        matching_courses = find_courses_for_skill(skill, courses_data)
        if matching_courses:
            recommended_courses.extend(matching_courses[:2])  # Берем до 2 курсов на навык

    return format_learning_plan_response(target_position, missing_skills, recommended_courses)


def find_courses_for_skill(skill: str, courses_data: Dict) -> List[Dict]:
    """Находит курсы для развития конкретного навыка"""
    if not courses_data.get("courses"):
        return []

    matching_courses = []
    for course in courses_data["courses"]:
        course_skills = course.get("skills_covered", [])
        for course_skill in course_skills:
            if calculate_skill_similarity(skill, course_skill) > 0.7:
                matching_courses.append(course)
                break

    return matching_courses


def format_learning_plan_response(target_position: str, missing_skills: List[str], courses: List[Dict]) -> str:
    """Форматирует ответ с учебным планом"""
    response = f"""🎓 Учебный план для подготовки к должности **{target_position}**

📋 Необходимо освоить:
{format_skills_list(missing_skills)}

---

📚 Рекомендуемые курсы:

"""

    for i, course in enumerate(courses, 1):
        response += f"{i}. **{course.get('title', 'Название курса')}**\n"
        response += f"   📺 Платформа: {course.get('platform', 'Не указана')}\n"
        response += f"   ⏱️ Длительность: {course.get('duration', 'Не указана')}\n"
        response += f"   🎯 Уровень: {course.get('level', 'Не указан')}\n"
        response += f"   🔗 Ссылка: {course.get('url', 'Не доступна')}\n\n"

    response += "💡 Совет: Сочетайте обучение на курсах с практическими проектами для лучшего закрепления материала."

    return response


# Функция №4: Карьерная консультация
@tool
def provide_career_advice(question: str) -> str:
    """
    Предоставляет консультацию по карьерным вопросам в ИТ-сфере.

    Args:
        question: Вопрос пользователя о карьере в ИТ

    Returns:
        str: Ответ с рекомендациями и советами
    """
    print("Вызвана функция: provide_career_advice")

    # База знаний по карьерным вопросам
    career_advice_db = {
        "старт карьеры": """
🚀 **С чего начать карьеру в ИТ:**

1. **Определите интересы** - попробуйте разные направления через небольшие проекты
2. **Освойте базовые навыки** - Git, основы программирования, английский язык
3. **Создайте портфолио** - даже учебные проекты имеют значение
4. **Ищите стажировки** - многие компании предлагают программы для начинающих
5. **Участвуйте в комьюнити** - хабр, meetups, открытые источники

Начните с бесплатных курсов и постепенно переходите к более сложным задачам.
""",
        "смена профессии": """
🔄 **Переход в ИТ из другой профессии:**

• Используйте свой предыдущий опыт - многие навыки универсальны
• Начните с смежных ролей (бизнес-аналитик, продакт-менеджер)
• Рассмотрите интенсивные курсы с трудоустройством
• Уделяйте время практике - теория без применения малоэффективна

Помните: средний возраст успешного сменщика профессии - 28-35 лет!
""",
        "повышение квалификации": """
📈 **Повышение квалификации и рост:**

• Определите целевой уровень (Middle, Senior, Lead)
• Изучите требования к целевой позиции
• Составьте план развития на 6-12 месяцев
• Найдите ментора или вступите в профессиональное сообщество
• Участвуйте в сложных проектах и берите на себя ответственность

Регулярно обновляйте резюме и отслеживайте свой прогресс.
"""
    }

    # Поиск наиболее релевантного ответа
    question_lower = question.lower()
    best_match = None
    max_similarity = 0

    for key in career_advice_db.keys():
        similarity = calculate_skill_similarity(question_lower, key)
        if similarity > max_similarity:
            max_similarity = similarity
            best_match = key

    if best_match and max_similarity > 0.3:
        return career_advice_db[best_match]
    else:
        return """
🤔 По вашему вопросу я могу предложить общие рекомендации:

• Изучите востребованные технологии на рынке труда
• Сосредоточьтесь на практических навыках, а не только на теории
• Создайте сильное портфолио с реальными проектами
• Развивайте soft skills - коммуникация, работа в команде, тайм-менеджмент
• Не бойтесь начинать с junior-позиций - это нормальный путь роста

Можете задать более конкретный вопрос о карьере в ИТ?
"""