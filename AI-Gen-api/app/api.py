from fastapi import FastAPI
from app.routers import career

# Создание экземпляра FastAPI
app = FastAPI(
    title="Career Navigator API",
    description="API для карьерного навигатора в ИТ",
    version="1.0.0"
)

# Подключение роутеров
# Роутер сам объявляет префикс "/career" — не указываем префикс повторно при include_router
app.include_router(career.router)
