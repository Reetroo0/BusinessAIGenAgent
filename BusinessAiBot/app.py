import asyncio
from config import bot, dp ,logger
from handlers import start, query
from misc.keyboards import main_kb

async def main():

    # Подключение хендлеров
    dp.include_router(start.router)
    dp.include_router(query.router)

    # Уведомление бота о запуске 
    await bot.send_message(chat_id=618425933, text='Бот запущен', reply_markup=main_kb)

    # Запуск бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    logger.info("Бот запущен")
    asyncio.run(main())