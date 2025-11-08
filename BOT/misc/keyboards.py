from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Подбор вакансий"),
            KeyboardButton(text="Подбор курсов"),
        ],
        [
            KeyboardButton(text="Составить план обучения")
        ]
    ],
    resize_keyboard=True
)

choice_inl_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔍 Посмотреть подходящие вакансии", callback_data="view_vacancies"),
        ],
        [
            InlineKeyboardButton(text="💬 Обсудить карьерные возможности", callback_data="discuss_career"),
        ],
        [
            InlineKeyboardButton(text="📚 Получить учебный план для развития", callback_data="get_study_plan")
        ]
    ]
)