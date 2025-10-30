from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from misc.functions import send_career_query

router = Router()


# === Машина состояний ===
class CareerForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_education = State()
    waiting_for_interests = State()
    waiting_for_query = State()  # <-- новое состояние для общения после анкеты


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
        "какие языки программирования ты знаешь, какими инструментами владеешь?"
    )
    await state.set_state(CareerForm.waiting_for_education)


# === 4. Образование ===
@router.message(CareerForm.waiting_for_education)
async def process_education(message: Message, state: FSMContext):
    education = message.text.strip()
    await state.update_data(education=education)

    await message.answer(
        "Отлично! 🔍 Теперь расскажи, какие направления в IT тебе интересны? "
        "Например: веб-разработка, дизайн, кибербезопасность, анализ данных и т.д."
    )
    await state.set_state(CareerForm.waiting_for_interests)


# === 5. Интересы ===
@router.message(CareerForm.waiting_for_interests)
async def process_interests(message: Message, state: FSMContext):
    interests = message.text.strip()
    await state.update_data(interests=interests)

    # Сохраняем все данные пользователя
    data = await state.get_data()
    user_data = {
        "name": data["name"],
        "age": data["age"],
        "education": data["education"],
        "interests": data["interests"]
    }

    await state.update_data(user_data=user_data)  # сохраним словарь в состоянии

    await message.answer(
        "✅ Отлично! Я запомнил твои данные.\n"
        "Теперь можешь задать любой вопрос, связанный с карьерой в IT — я помогу тебе разобраться! 💬"
    )

    # Переходим в режим “ожидания запросов”
    await state.set_state(CareerForm.waiting_for_query)


# === 6. Универсальный хендлер для любых сообщений после анкеты ===
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
        f"Интересы: {user_data['interests']}.\n"
        f"Вопрос: {user_text}"
    )

    # Отправляем запрос в API
    response = await send_career_query(str(message.from_user.id), user_data, prompt)

    # Получаем и отправляем ответ
    answer_text = response.get("response", "⚠️ Не удалось получить ответ от сервера.")
    await message.answer(answer_text)
