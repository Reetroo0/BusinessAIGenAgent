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
    'Authorization': 'Basic MDE5OTYyMzItY2VmOC03NjIxLTg4NmMtZWNmOWQ3MGU5OTEzOjQyNWE1ZjAwLWE5YWQtNGNiMC04NTRkLWQ4ZTY0M2I2ZTYwMA=='
}

response = requests.request("POST", url, headers=headers, data=payload, verify=True)

# Получить только токен
access_token = response.json()['access_token']
print(access_token)