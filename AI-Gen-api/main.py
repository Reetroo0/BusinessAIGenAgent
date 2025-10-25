import sys
import logging
import uvicorn
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корневой каталог в PYTHONPATH
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

def main():
    """
    Функция запуска FastAPI приложения.
    - Инициализирует логирование
    - Загружает переменные окружения
    - Запускает ASGI сервер
    """
    try:
        logger.info("Запуск API сервера...")
        
        # Запуск uvicorn с автоперезагрузкой
        uvicorn.run(
            "app.api:app",  # Путь к приложению в модуле app
            host="0.0.0.0",
            port=8000,
            reload=True,    # Автоперезагрузка для разработки
            reload_dirs=[str(ROOT_DIR / "app")]  # Отслеживаем изменения только в app/
        )
    except Exception as e:
        logger.error(f"Ошибка при запуске сервера: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()