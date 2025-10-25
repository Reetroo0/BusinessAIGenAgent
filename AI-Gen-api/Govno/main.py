import sys

sys.path.append('..')

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_gigachat.chat_models import GigaChat
from langchain.schema.messages import HumanMessage
from tools import analyze_user_profile, find_matching_vacancies, create_learning_plan, provide_career_advice
from typing import Dict, Optional, List
import json

from dotenv import find_dotenv, load_dotenv
import os
import threading

# Загрузка переменных окружения
load_dotenv(find_dotenv())

# Ленивая инициализация агента
_AGENT_LOCK = threading.Lock()
_AGENT = None
_AGENT_TOKEN = None

system_prompt = (
    "Ты являешься ИИ-агентом «Карьерный навигатор в ИТ», работающим в рамках Департамента цифрового развития, "
    "информационных технологий и связи. "
    "Основная цель твоего существования — помощь студентам, выпускникам и молодым специалистам 18-25 лет "
    "в карьерном ориентировании и развитии в ИТ-сфере. "
    "Ты помогаешь пользователям: "
    "анализировать их навыки и подбирать подходящие карьерные направления, "
    "находить вакансии на основе их компетенций, "
    "создавать персонализированные учебные планы для развития, "
    "оказывать консультационную поддержку по карьерным вопросам. "
    "Будь дружелюбным, поддерживающим и мотивирующим помощником. "
    "Используй эмодзи для создания позитивной атмосферы. "
    "Всегда предлагай следующие шаги и варианты развития."
)

TOOLS = [analyze_user_profile, find_matching_vacancies, create_learning_plan, provide_career_advice]


def _init_agent(token: str):
    """Создает и возвращает нового агента с предоставленным токеном"""
    # Устанавливаем переменную окружения для GigaChat
    os.environ["GIGACHAT_CREDENTIALS"] = token
    # Инициализируем модель и агента
    model = GigaChat(model="GigaChat-2", verify_ssl_certs=False)
    agent = create_react_agent(model, tools=TOOLS, checkpointer=MemorySaver(), prompt=system_prompt)
    return agent


def _get_agent(headers: Optional[Dict] = None):
    """Возвращает кэшированного агента; инициализирует если отсутствует или токен изменился"""
    global _AGENT, _AGENT_TOKEN

    # Извлекаем токен: предпочтительно из заголовка Authorization, иначе из env
    token = None
    if headers:
        auth = headers.get("Authorization") or headers.get("authorization")
        if auth and isinstance(auth, str) and auth.lower().startswith("bearer "):
            token = auth.split(None, 1)[1].strip()

    if not token:
        token = os.getenv("GIGACHAT_ACCESS_TOKEN")

    if token is None or len(token.strip()) == 0:
        raise ValueError("Переменная GIGACHAT_ACCESS_TOKEN отсутствует или пуста")

    with _AGENT_LOCK:
        if _AGENT is None or _AGENT_TOKEN != token:
            # Убеждаемся, что переменная окружения установлена для библиотеки GigaChat
            os.environ["GIGACHAT_CREDENTIALS"] = token
            _AGENT = _init_agent(token)
            _AGENT_TOKEN = token
    return _AGENT


def run_agent(question: str, user_profile: Optional[Dict] = None, headers: Optional[Dict] = None) -> str:
    """Запускает агента с вопросом и опциональными данными профиля пользователя"""
    agent = _get_agent(headers)

    # Если предоставлены данные профиля пользователя, добавляем их к вопросу
    if user_profile is not None:
        try:
            # Создаем удобочитаемый блок из словаря
            pairs = [f"{k}: {v}" for k, v in user_profile.items()]
            profile_block = "\n".join(pairs)
            full_question = f"{question}\n\nПрофиль пользователя:\n{profile_block}"
        except Exception:
            # Резервный вариант - сырая JSON строка
            full_question = f"{question}\n\nПрофиль пользователя:\n{json.dumps(user_profile, ensure_ascii=False)}"
        messages = [HumanMessage(content=full_question)]
    else:
        messages = [HumanMessage(content=question)]

    config = {"configurable": {"thread_id": 1}}

    # Отладочный вывод сообщений если запрошено через env
    if os.getenv("DEBUG_AGENT_PAYLOAD"):
        print("DEBUG: исходящие сообщения:")
        for m in messages:
            print("---")
            print(m.content)

    try:
        resp = agent.invoke({"messages": messages}, config=config)
        answer = resp["messages"][-1].content
        return answer
    except Exception as e:
        return f"Произошла ошибка при обработке запроса: {str(e)}"


def run_career_navigator_interactive():
    """Интерактивный режим для тестирования карьерного навигатора"""
    print("🚀 Запуск Карьерного навигатора в ИТ")
    print("=" * 50)
    print("Доступные команды:")
    print("- 'выход' - завершить работу")
    print("- 'сброс' - начать новый диалог")
    print("=" * 50)

    user_profile = {}

    while True:
        try:
            user_input = input("\n👤 Ваш вопрос: ").strip()

            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("До свидания! Удачи в карьерном развитии! 🎯")
                break

            if user_input.lower() in ['сброс', 'reset']:
                user_profile = {}
                print("🔄 Начинаем новый диалог!")
                continue

            if not user_input:
                print("Пожалуйста, введите ваш вопрос")
                continue

            # Если это первое сообщение, сохраняем его как начальный профиль
            if not user_profile and len(user_input) > 20:
                user_profile["initial_description"] = user_input

            response = run_agent(user_input, user_profile)
            print(f"\n🤖 Навигатор: {response}")

        except KeyboardInterrupt:
            print("\n\nДо свидания! Удачи в карьерном развитии! 🎯")
            break
        except Exception as e:
            print(f"\n❌ Произошла ошибка: {e}")
            print("Попробуйте еще раз или введите 'сброс' для начала нового диалога")


# Функции для интеграции с веб-интерфейсом
def initialize_user_session(user_id: str, initial_data: Optional[Dict] = None) -> Dict:
    """Инициализирует сессию пользователя с начальными данными"""
    session_data = {
        "user_id": user_id,
        "profile": initial_data or {},
        "conversation_history": [],
        "created_at": json.dumps({"timestamp": "2024-01-01T00:00:00Z"})  # В реальности использовать datetime
    }
    return session_data


def process_career_query(user_id: str, query: str, session_data: Optional[Dict] = None,
                         headers: Optional[Dict] = None) -> Dict:
    """Обрабатывает карьерный запрос пользователя и возвращает структурированный ответ"""

    if session_data is None:
        session_data = initialize_user_session(user_id)

    # Добавляем контекст из истории сессии
    enhanced_query = query
    if session_data.get("profile"):
        profile_context = f"Контекст пользователя: {json.dumps(session_data['profile'], ensure_ascii=False)}"
        enhanced_query = f"{query}\n\n{profile_context}"

    try:
        response = run_agent(enhanced_query, session_data.get("profile"), headers)

        # Обновляем историю сессии
        session_data["conversation_history"].append({
            "query": query,
            "response": response,
            "timestamp": json.dumps({"timestamp": "2024-01-01T00:00:00Z"})  # В реальности использовать datetime
        })

        # Пытаемся извлечь навыки из ответа для обновления профиля
        if "навыки" in response.lower() and not session_data["profile"].get("skills_extracted"):
            session_data["profile"]["skills_extracted"] = True

        return {
            "success": True,
            "response": response,
            "session_data": session_data,
            "suggested_actions": extract_suggested_actions(response)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "response": "Извините, произошла ошибка при обработке вашего запроса. Пожалуйста, попробуйте еще раз.",
            "session_data": session_data
        }


def extract_suggested_actions(response: str) -> List[str]:
    """Извлекает предложенные действия из ответа агента"""
    actions = []

    if "ваканс" in response.lower():
        actions.append("find_vacancies")
    if "курс" in response.lower() or "обучен" in response.lower() or "план" in response.lower():
        actions.append("create_learning_plan")
    if "консульт" in response.lower() or "совет" in response.lower():
        actions.append("career_advice")
    if "профиль" in response.lower() or "навык" in response.lower():
        actions.append("analyze_profile")

    return actions if actions else ["general_help"]


__all__ = ["run_agent", "run_career_navigator_interactive", "process_career_query", "initialize_user_session"]

if __name__ == "__main__":
    # Запуск интерактивного режима если файл запущен напрямую
    run_career_navigator_interactive()