from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from misc.functions import send_career_query, addUserData
from misc.keyboards import choice_inl_kb

router = Router()


# === Машина состояний ===
class CareerForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_education = State()
    waiting_for_skills = State()
    waiting_for_experience = State()
    waiting_for_target_position = State()
    waiting_for_query = State()


# === 1. Старт ===
@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(
        "👋 Привет! Добро пожаловать в *«Карьерный навигатор в ИТ»*! 💼\n\n"
        "Я помогу тебе определить, как развиваться в сфере информационных технологий.\n"
        "Для начала давай познакомимся!\n\n"
        "Как тебя зовут?",
        parse_mode="Markdown"
    )
    await state.set_state(CareerForm.waiting_for_name)


# === 2. Имя ===
@router.message(CareerForm.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()
    await state.update_data(name=name)

    await message.answer("Отлично! 😊 А сколько тебе лет?")
    await state.set_state(CareerForm.waiting_for_age)


# === 3. Возраст ===
@router.message(CareerForm.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    age_text = message.text.strip()
    if not age_text.isdigit():
        await message.answer("❗️Пожалуйста, введи возраст числом.")
        return

    await state.update_data(age=int(age_text))
    await message.answer(
        "Спасибо! 🎓 Теперь расскажи, какое у тебя образование, "
        "где и по какой специальности ты учился."
    )
    await state.set_state(CareerForm.waiting_for_education)


# === 4. Образование ===
@router.message(CareerForm.waiting_for_education)
async def process_education(message: Message, state: FSMContext):
    education = message.text.strip()
    await state.update_data(education=education)

    await message.answer(
        "Хорошо! 💡 Расскажи теперь, какими языками программирования или инструментами ты владеешь? "
        "Например: Python, JavaScript, Linux, Git, Docker и т.д."
    )
    await state.set_state(CareerForm.waiting_for_skills)


# === 5. Навыки ===
@router.message(CareerForm.waiting_for_skills)
async def process_skills(message: Message, state: FSMContext):
    # Берём текст и превращаем его в список навыков
    raw_skills = message.text.strip()

    # Разделяем по запятым и/или пробелам
    skills = [s.strip() for s in raw_skills.replace(',', ' ').split() if s.strip()]

    # Сохраняем уже список (массив)
    await state.update_data(skills=skills)

    await message.answer(
        "Отлично! 💼 Есть ли у тебя опыт работы в ИТ (например, стажировки, фриланс, проекты)? "
        "Если нет — просто напиши «нет»."
    )
    await state.set_state(CareerForm.waiting_for_experience)



# === 6. Опыт работы ===
@router.message(CareerForm.waiting_for_experience)
async def process_experience(message: Message, state: FSMContext):
    experience = message.text.strip()
    await state.update_data(experience=experience)

    await message.answer(
        "Понял! 🚀 И наконец, какая должность или направление тебя интересует? "
        "Например: backend-разработчик, UX/UI дизайнер, DevOps-инженер, аналитик данных и т.д."
    )
    await state.set_state(CareerForm.waiting_for_target_position)


# === 7. Цель (направление в ИТ) ===
@router.message(CareerForm.waiting_for_target_position)
async def process_target_position(message: Message, state: FSMContext):
    target_position = message.text.strip()
    await state.update_data(target_position=target_position)

    # Сохраняем все данные пользователя
    data = await state.get_data()
    user_data = {
        "tg_id": message.from_user.id,   # <-- вот так правильно
        "name": data["name"],
        "age": data["age"],
        "education": data["education"],
        "skills": data["skills"],
        "experience": data["experience"],
        "target_position": data["target_position"]
    }


    success = addUserData(user_data)

    if not success:
        await message.answer("❗️Произошла ошибка при сохранении твоих данных. Попробуй ещё раз позже.")
        await state.clear()
        return

    await state.update_data(user_data=user_data)

    await message.answer(
        "✅ Отлично! Я запомнил твои данные.\n"
        "Теперь можешь выбрать, что тебя интересует — я помогу тебе разобраться! 💬",
        reply_markup=choice_inl_kb
    )

    await state.set_state(CareerForm.waiting_for_query)


# === 8. Универсальный хендлер для общения после анкеты ===
@router.message(CareerForm.waiting_for_query)
async def handle_user_query(message: Message, state: FSMContext):
    user_text = message.text.strip()
    data = await state.get_data()
    user_data = data.get("user_data")

    if not user_data:
        await message.answer("⚠️ Не удалось найти твои данные. Начни заново командой /start.")
        await state.clear()
        return

    await message.answer("💭 Думаю над ответом...")

    # Формируем промпт для API
    prompt = (
        f"Пользователь {user_data['name']}, {user_data['age']} лет.\n"
        f"Образование: {user_data['education']}.\n"
        f"Навыки: {user_data['skills']}.\n"
        f"Опыт работы: {user_data['experience']}.\n"
        f"Целевая позиция: {user_data['target_position']}.\n"
        f"Вопрос: {user_text}"
    )

    response = await send_career_query(str(message.from_user.id), user_data, prompt)

    answer_text = response.get("response", "⚠️ Не удалось получить ответ от сервера.")
    await message.answer(answer_text)
