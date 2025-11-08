import aiohttp
from config import logger, connection_pool

CAREER_QUERY_URL = "http://0.0.0.0:8001/career_query"

async def send_career_query(tg_id: str, user_data: dict, prompt: str) -> dict:
    """
    Отправляет запрос к эндпоинту /career_query FastAPI-сервера.
    
    :param tg_id: ID пользователя Telegram
    :param user_data: словарь с данными пользователя (например: {"name": "Иван", "age": 25, "education": "Бакалавр"})
    :param prompt: текст запроса к нейросети
    :return: словарь с ответом от API
    """
    payload = {
        "tg_id": tg_id,
        "user_data": user_data,
        "prompt": prompt
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(CAREER_QUERY_URL, json=payload) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": f"Ошибка при запросе API: {resp.status}"}
        except Exception as e:
            return {"error": f"Ошибка при выполнении запроса: {str(e)}"}
        

def addUserData(user_data):
    try:
        conn = connection_pool.getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO user_data (tg_id, name, age, education, skills, experience, target_position)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (tg_id) DO UPDATE
                    SET name = EXCLUDED.name,
                        age = EXCLUDED.age,
                        education = EXCLUDED.education,
                        skills = EXCLUDED.skills,
                        experience = EXCLUDED.experience,
                        target_position = EXCLUDED.target_position;
                """, (
                    user_data["tg_id"],
                    user_data["name"],
                    user_data.get("age"),
                    user_data.get("education"),
                    user_data.get("skills", []),
                    user_data.get("experience"),
                    user_data.get("target_position")
                ))
                conn.commit()
                return True
        finally:
            connection_pool.putconn(conn)
    except Exception as e:
        logger.error(f"Ошибка добавления данных пользователя (addUserData): \n{e}")
        return False
