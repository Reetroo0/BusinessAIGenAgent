# misc/handlers/career_handlers.py

from aiogram import Router, F
from aiogram.types import Message
from misc.keyboards import main_kb
from misc.functions import send_career_query

router = Router()


@router.message(F.text.lower().strip().in_(["подбор вакансий", "подбор курсов", "составить план обучения"]))
async def handle_career_actions(message: Message):
    user_data = {
        "name": message.from_user.first_name or "Пользователь",
        "age": 0,
        "education": "не указано"
    }

    text = message.text.strip().lower()

    prompts = {
        "подбор вакансий": "Подбери подходящие вакансии для пользователя, учитывая его профиль.",
        "подбор курсов": "Подбери подходящие обучающие курсы по ИТ для пользователя, исходя из его данных.",
        "составить план обучения": "Составь индивидуальный план обучения в сфере ИТ для пользователя."
    }

    prompt = prompts.get(text, "Дай совет по карьере в ИТ.")

    await message.answer("🤖 Думаю над ответом, подождите немного...")
    response = await send_career_query(str(message.from_user.id), user_data, prompt)
    answer_text = response.get("response", "⚠️ Не удалось получить ответ от сервера.")
    await message.answer(answer_text, reply_markup=main_kb)
