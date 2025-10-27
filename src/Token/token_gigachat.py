import requests
import certifi

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

response = requests.request("POST", url, headers=headers, data=payload, verify=True)

# Получить только токен
access_token = response.json()['access_token']
print(access_token)