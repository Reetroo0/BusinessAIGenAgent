from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import psycopg2.pool
import logging
import os



# Настройка логирования
logging.basicConfig(
    level=logging.INFO,                                             # Минимальный уровень логов
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # Формат логов
    handlers=[logging.StreamHandler()]                              # Вывод логов в консоль
)
logger = logging.getLogger(__name__)
logging.getLogger('aiogram.event').setLevel(logging.WARNING) 

load_dotenv()

# Инициализация бота и диспетчера
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())
dsn = os.getenv('DSN')


# Парсим список ID администраторов
admin_ids = os.getenv('ADMIN_IDS')
# if admin_ids:
#     admin_ids = [int(id.strip()) for id in admin_ids.split(',')]
# else:
#     admin_ids = []
# logger.info(f"Admin IDs: {admin_ids}")


# Создание пула соединений
# try:
#     connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=dsn)
#     logger.info("Connection pool created successfully")
# except psycopg2.OperationalError as e:
#     logger.error(f"Failed to connect to database: {e}")
#     raise