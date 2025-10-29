import aiohttp

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
