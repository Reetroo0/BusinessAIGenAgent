from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from misc.keyboards import main_kb
from misc.functions import fetch_digital_maturity

router = Router()


class SurveyStates(StatesGroup):
    answering = State()

# Вопросы и ключи для JSON
questions = [
    ("Формализованы ли и задокументированы бизнес-процессы вашей компании (имеются ли действующие регламенты и инструкции)?", "formalization_level"),
    ("Использует ли ваша компания автоматизированные системы (CRM, ERP, СЭД)?", "automation_systems"),
    ("Имеются ли автоматические инструменты сбора и анализа KPI?", "kpi_metrics"),
    ("Часто ли принимаемые вами управленческие решения основаны на анализе данных?", "data_driven_decisions"),
    ("Применяются ли современные ИТ-системы (CRM, ERP, СЭД, облачные решения)?", "it_systems_used"),
    ("Интегрированы ли используемые системы друг с другом (например, CRM → Бухгалтерия → Склад)?", "systems_integration"),
    ("Используется ли облачная инфраструктура (SaaS/PaaS/IaaS) или всё установлено локально?", "cloud_services_usage"),
    ("Обеспечиваете ли вы резервное копирование данных и защиту от угроз информационной безопасности?", "info_security_measures"),
    ("Умеют ли ваши сотрудники эффективно пользоваться современными ИТ-технологиями?", "digital_literacy"),
    ("Проводятся ли мероприятия по повышению цифровизации сотрудников регулярно?", "training_programs"),
    ("Есть ли штатные специалисты по ИТ или эта область передаётся внешним исполнителям?", "it_specialists_in_house"),
    ("Поддерживают ли сотрудники идеи внедрения новых цифровых решений?", "employees_automation_perception"),
    ("Разработана ли стратегия цифровой трансформации вашей компании?", "it_strategy"),
    ("Пользуется ли организация электронными сервисами взаимодействия с государственными органами (Госуслуги, ЭДО, «Честный знак»)?", "state_electronic_services"),
    ("Планируется ли расширение автоматизации в ближайшие годы (CRM, СЭД, ETP и др.)?", "future_implementation_plans"),
]

# Варианты ответов
answer_options = {
    "yes": "Да",
    "mostly_yes": "Скорее Да",
    "mostly_no": "Скорее Нет",
    "no": "Нет",
    "unknown": "Нет информации"
}

def get_inline_kb():
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=label, callback_data=key)]
        for key, label in answer_options.items()
    ])
    return kb

@router.message(F.text == "Отмена")
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.", reply_markup=main_kb)


@router.message(F.text == "Анкета")
async def survey_start(message: Message, state: FSMContext):
    await state.set_state(SurveyStates.answering)
    await state.update_data(current_question=0, answers={})
    await message.answer(questions[0][0], reply_markup=get_inline_kb())


@router.callback_query(SurveyStates.answering)
async def get_answer(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    curQuest = data.get("current_question", 0)
    answers = data.get("answers", {})

    # Записываем ответ
    question_text, question_key = questions[curQuest]
    answers[question_key] = callback.data
    await state.update_data(answers=answers)

    await callback.answer(f"Ответ сохранён: {answer_options[callback.data]}")

    # Следующий вопрос
    nextQuest = curQuest + 1
    if nextQuest < len(questions):
        await state.update_data(current_question=nextQuest)
        await callback.message.answer(questions[nextQuest][0], reply_markup=get_inline_kb())
    else:
        try:
            # # Сохраним локально (опционально)
            # with open("results.json", "w", encoding="utf-8") as f:
            #     json.dump(answers, f, ensure_ascii=False, indent=2)

            # Отправим на API
            response = await fetch_digital_maturity(answers)
            result_text = response.get("result", "Не удалось получить результат.")

            # Покажем пользователю в markdown
            await callback.message.answer(result_text, parse_mode="Markdown", reply_markup=main_kb)

        except Exception as e:
            await callback.message.answer(f"Ошибка при сохранении/запросе: {str(e)}", reply_markup=main_kb)

        await state.clear()