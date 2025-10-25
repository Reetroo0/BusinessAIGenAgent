import aiohttp

API_URL = "http://0.0.0.0:8000/digitalMaturity"
ASK_QUESTION_URL = "http://0.0.0.0:8000/askQuestion"

async def fetch_digital_maturity(data: dict) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, json=data) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                return {"result": f"Ошибка при запросе API: {resp.status}"}

async def ask_question(question: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(ASK_QUESTION_URL, json={"question": question}) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    return response_data.get("result", "Не удалось получить ответ от сервера.")
                else:
                    return f"Ошибка при запросе API: {resp.status}"
        except Exception as e:
            return f"Ошибка при выполнении запроса: {str(e)}"

async def send_result_to_user(message, answers: dict):
    try:
        response = await fetch_digital_maturity(answers)
        result_text = response.get("result", "Не удалось получить результат.")
        # Отправляем пользователю в Markdown
        await message.answer(result_text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"Ошибка: {str(e)}")