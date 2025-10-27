from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
