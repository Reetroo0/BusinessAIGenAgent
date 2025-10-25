from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from misc.keyboards import main_kb, cancel_kb
from misc.functions import ask_question

router = Router()

class QuestionStates(StatesGroup):
    waiting_for_question = State()

@router.message(F.text == "Задать вопрос")
async def handle_question_start(message: Message, state: FSMContext):
    await state.set_state(QuestionStates.waiting_for_question)
    await message.answer("Пожалуйста, введите ваш вопрос.", reply_markup=cancel_kb)

@router.message(QuestionStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    question_text = message.text.strip()
    if not question_text:
        await message.answer("Вопрос не может быть пустым. Пожалуйста, введите вопрос.", reply_markup=cancel_kb)
        return
    
    try:
        # Отправляем вопрос на сервер
        response_text = await ask_question(question_text)
        await message.answer(response_text, parse_mode="Markdown", reply_markup=main_kb)
    except Exception as e:
        await message.answer(f"Ошибка при запросе: {str(e)}", reply_markup=main_kb)
    await state.clear()

@router.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_kb)