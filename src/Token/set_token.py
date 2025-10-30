import requests
import certifi
from dotenv import load_dotenv, set_key
import os

def set_gigachat_access_token() -> str:
    """
    Получает токен от GigaChat API и сохраняет его в переменную окружения GIGACHAT_ACCESS_TOKEN в файле .env.
    Возвращает полученный токен.
    """
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': 'c5036fd3-68e5-4a0a-b357-2ca9f3976628',
        'Authorization': 'Basic MDE5OTYxODItM2M4Zi03MmM0LWI3MTItNzVlZDZjODBjMWZmOjhjMzRkZGQyLThmOGQtNDA0YS1hOTg1LWE1M2Q4ZDNiZmMwYw=='
    }

    try:
        response = requests.post(url, headers=headers, data=payload, verify=certifi.where())
        response.raise_for_status()  # Проверяем успешность запроса
        access_token = response.json()['access_token']
        
        # Сохраняем токен в .env
        env_file = '.env'
        set_key(env_file, 'GIGACHAT_ACCESS_TOKEN', access_token)
        
        print(f"Токен успешно сохранён в {env_file}: GIGACHAT_ACCESS_TOKEN={access_token}")
        return access_token
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"Ошибка при получении токена: {str(e)}")
    except KeyError:
        raise Exception("Ошибка: в ответе API отсутствует ключ 'access_token'")