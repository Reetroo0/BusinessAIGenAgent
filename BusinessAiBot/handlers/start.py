from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from misc.keyboards import main_kb
from misc.functions import send_career_query

router = Router()

# === Машина состояний ===
class CareerForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_education = State()


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
    await message.answer("Спасибо! 🎓 Теперь расскажи, какое у тебя образование, какие языки программирования ты знаешь, какими инструментами владеешь, напиши всё что знаешь?")
    await state.set_state(CareerForm.waiting_for_education)


# === 4. Образование ===
@router.message(CareerForm.waiting_for_education)
async def process_education(message: Message, state: FSMContext):
    education = message.text.strip()
    await state.update_data(education=education)

    # Получаем все данные пользователя
    data = await state.get_data()
    user_data = {
        "name": data["name"],
        "age": data["age"],
        "education": data["education"]
    }

    # Сообщаем, что начинаем обработку
    await message.answer("⏳ Отлично! Обрабатываю информацию...")

    # Отправляем на API
    prompt = (f"Пользователь {user_data['name']}, {user_data['age']} лет, образование: {user_data['education']}.\n")
    response = await send_career_query(str(message.from_user.id), user_data, prompt)

    # Ответ от API
    answer_text = response.get("response", "⚠️ Не удалось получить ответ от сервера.")
    await message.answer(answer_text, reply_markup=main_kb)

    # Очищаем состояние
    await state.clear()
