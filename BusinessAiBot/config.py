import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

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
dp = Dispatcher(storage=MemoryStorage())e