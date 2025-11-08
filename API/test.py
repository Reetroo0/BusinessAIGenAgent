from main import process_career_query, initialize_user_session

# Инициализация сессии
session = initialize_user_session("user1", {
    "name": "Иван",
    "age": 20,
    "education": "студент"
})

# Обработка запроса
result = process_career_query("user1", "Я знаю Python и SQL, хочу работать в аналитике, подбери мне вакансии для работы, подбери мне конкретные предложения вакансий", session)
print(result["response"])