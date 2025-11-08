from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Optional, Any
from main import process_career_query, initialize_user_session
from Token.set_token import set_gigachat_access_token
import uvicorn
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
import os
import psycopg2.pool
from psycopg2.extras import RealDictCursor
import logging

logger = logging.getLogger(__name__)

# Создание пула соединений
DSN = "host=localhost port=54321 dbname=aigovnodb user=postgres password=4268 sslmode=disable"
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=DSN)
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


def get_user_data_by_tg_id(tg_id: int) -> Optional[Dict]:
    """
    Возвращает данные пользователя из таблицы user_data по tg_id.
    Если пользователя нет — возвращает None.
    """
    conn = None
    try:
        # Получаем соединение из пула
        conn = connection_pool.getconn()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    tg_id, 
                    name, 
                    age, 
                    education, 
                    skills, 
                    experience, 
                    target_position
                FROM user_data
                WHERE tg_id = %s
            """, (tg_id,))
            
            result = cur.fetchone()
            if result:
                logger.debug(f"User data fetched for tg_id={tg_id}: {result}")
            else:
                logger.debug(f"No user found for tg_id={tg_id}")
            return result
    except psycopg2.Error as e:
        logger.error(f"Database error while fetching user_data for tg_id={tg_id}: {e}")
        return None
    finally:
            connection_pool.putconn(conn)




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


app = FastAPI(lifespan=lifespan)


# Обработчик ошибок валидации запросов (Возвращает тело запроса и ошибки для дебага)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body_bytes = await request.body()
        body_text = body_bytes.decode("utf-8", errors="replace")
    except Exception:
        body_text = "<could not read body>"

    # Логируем подробности
    logger.error(f"Request validation error on {request.url.path}: {exc}")
    logger.error(f"Request body: {body_text}")

    # Возвращаем подробный ответ (для разработки). В продакшн можно убрать тело из ответа
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": body_text
        },
    )

# Словарь для хранения сессий пользователей (в памяти)
sessions = {}  # Ключ: tg_id, Значение: сессия

# Модель для входящего запроса от бота
class UserQuery(BaseModel):
    tg_id: str
    user_data: Optional[Dict[str, Any]] = None  # Данные пользователя: name, age, education
    prompt: str  # Запрос к нейросети

# Модель для ответа боту
class QueryResponse(BaseModel):
    tg_id: str
    response: str  # Ответ от process_career_query
    user_data: Optional[Dict[str, Any]] = None  # Подтверждение полученных данных

# Эндпоинт для обработки запроса от бота
@app.post("/career_query", response_model=QueryResponse)
async def handle_career_query(query: UserQuery):
    try:
        tg_id = int(query.tg_id)

        # === 1. Получаем данные пользователя из БД ===
        user_data = get_user_data_by_tg_id(tg_id)
        if not user_data:
            raise HTTPException(status_code=404, detail=f"Пользователь с tg_id={tg_id} не найден в БД")

        # === 2. Инициализируем сессию (если ещё нет) ===
        if tg_id not in sessions:
            sessions[tg_id] = initialize_user_session(tg_id, user_data)

        session = sessions[tg_id]

        # === 3. Готовим токен и заголовки ===
        load_dotenv()
        token = os.getenv("GIGACHAT_ACCESS_TOKEN")
        if not token:
            raise HTTPException(status_code=500, detail="GigaChat токен отсутствует")
        headers = {"Authorization": f"Bearer {token}"}

        # === 4. Отправляем запрос в GigaChat ===
        logger.info(f"Обрабатываю career_query для tg_id={tg_id}")

        result = process_career_query(tg_id, query.prompt, session, headers, user_data)

        # === 5. Возвращаем ответ ===
        return QueryResponse(
            tg_id=query.tg_id,
            response=result.get("response", ""),
            user_data=user_data
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Ошибка при обработке career_query: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обработки запроса: {str(e)}")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")