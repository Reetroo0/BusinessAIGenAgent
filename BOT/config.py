import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import psycopg2.pool


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,                                          
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]                              
)
logger = logging.getLogger(__name__)
logging.getLogger('aiogram.event').setLevel(logging.WARNING) 

load_dotenv()

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(storage=MemoryStorage())
dsn = os.getenv('DSN')

# Создание пула соединений
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=dsn)
    logger.info("Connection pool created successfully")

    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            logger.info("Database connection is OK")
            conn.commit()
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        
except psycopg2.OperationalError as e:
    logger.error(f"Failed to connect to database: {e}")
    raise
