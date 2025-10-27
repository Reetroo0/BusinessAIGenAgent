from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
from main import process_career_query, initialize_user_session
from Token.set_token import set_gigachat_access_token
import uvicorn
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler

app = FastAPI()

# Словарь для хранения сессий пользователей (в памяти)
sessions = {}  # Ключ: tg_id, Значение: сессия

# Модель для входящего запроса от бота
class UserQuery(BaseModel):
    tg_id: str
    user_data: Dict[str, str | int]  # Данные пользователя: name, age, education
    prompt: str  # Запрос к нейросети

# Модель для ответа боту
class QueryResponse(BaseModel):
    tg_id: str
    response: str  # Ответ от process_career_query
    user_data: Dict[str, str | int]  # Подтверждение полученных данных

# Эндпоинт для обработки запроса от бота
@app.post("/career_query", response_model=QueryResponse)
async def handle_career_query(query: UserQuery):
    try:
        # Проверяем, есть ли сессия для данного tg_id
        if query.tg_id not in sessions:
            # Если сессии нет, инициализируем новую
            sessions[query.tg_id] = initialize_user_session(query.tg_id, query.user_data)
        
        # Получаем сессию
        session = sessions[query.tg_id]

        # Обрабатываем запрос к нейросети
        result = process_career_query(query.tg_id, query.prompt, session)

        # Формируем ответ
        response = QueryResponse(
            tg_id=query.tg_id,
            response=result["response"],
            user_data=query.user_data
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки запроса: {str(e)}")

# Планировщик для периодического запуска функции
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    scheduler.add_job(set_gigachat_access_token, 'interval', minutes=20)
    set_gigachat_access_token()
    try:
        yield
    finally:
        scheduler.shutdown()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)