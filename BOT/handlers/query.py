from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from misc.functions import send_career_query
from misc.keyboards import choice_inl_kb

router = Router()


# === Общий хендлер для любых сообщений ===
@router.message(StateFilter(None))  # <-- сработает ТОЛЬКО если пользователь не в состоянии
async def handle_any_message(message: Message, state: FSMContext):
    await message.answer(
        "🤖 Я тебя понял! Но если хочешь начать карьерный тест — напиши /start 🙂"
    )



@router.callback_query(F.data.in_(["view_vacancies", "discuss_career", "get_study_plan"]))
async def handle_career_callback(callback: CallbackQuery, state: FSMContext):
    # Загружаем данные состояния (если пользователь прошёл анкету)
    data = await state.get_data()
    user_data = data.get("user_data")

    if not user_data:
        await callback.answer("❗ Пожалуйста, сначала пройди анкету командой /start", show_alert=True)
        return
    
    # Выбираем промпт по типу кнопки
    prompts = {
        "view_vacancies": "Подбери подходящие вакансии для меня, учитывая мой профиль. Используй функцию find_matching_vacancies",
        "discuss_career": "Какие вопросы я могу задать тебе по карьере в айти?. Для ответов на вопросы пользователя используй функцию provide_career_advice",
        "get_study_plan": "Составь индивидуальный план обучения в сфере ИТ для меня. Используй функцию create_learning_plan"
    }

    # Добавляем контекст профиля к промпту
    full_prompt = (
        f"Пользователь {user_data['name']}, {user_data['age']} лет.\n"
        f"Образование: {user_data['education']}.\n"
        f"Интересы: {user_data.get('interests', 'не указаны')}.\n\n"
        f"{prompts.get(callback.data, "Дай совет по карьере в ИТ.")}"
    )

    await callback.answer()
    await callback.message.answer("🤖 Думаю над ответом, подождите немного...")

    # Отправляем запрос в API
    response = await send_career_query(str(callback.from_user.id), user_data, full_prompt)
    answer_text = response.get("response", "⚠️ Не удалось получить ответ от сервера.")

    # Отправляем ответ пользователю с клавиатурой
    await callback.message.answer(answer_text, reply_markup=choice_inl_kb)





