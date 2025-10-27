import requests
import certifi
import urllib3

# Отключить предупреждения SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def install_russian_cert():
    # URL российского корневого сертификата
    url = "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt"

    try:
        # Скачать сертификат
        print("📥 Скачиваю сертификат...")
        response = requests.get(url, verify=False)
        russian_cert = response.text.strip()

        print("📄 Содержимое сертификата:")
        print("=" * 50)
        print(russian_cert[:200] + "..." if len(russian_cert) > 200 else russian_cert)
        print("=" * 50)

        # Получить путь к certifi
        certifi_path = certifi.where()
        print(f"📁 Путь к certifi: {certifi_path}")

        # Добавить сертификат
        with open(certifi_path, 'a', encoding='utf-8') as f:
            f.write('\n' + '# Russian Trusted Root CA\n')
            f.write(russian_cert + '\n')

        print("✅ Сертификат добавлен в хранилище!")

        # Проверить размер файла
        import os
        file_size = os.path.getsize(certifi_path)
        print(f"📊 Размер файла certifi: {file_size} байт")

        # Проверить содержимое
        with open(certifi_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'BEGIN CERTIFICATE' in russian_cert and 'END CERTIFICATE' in russian_cert:
                print("✅ Сертификат имеет правильный формат")
            else:
                print("⚠️  Проверьте формат сертификата")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def test_gigachat():
    print("\n🧪 Тестируем подключение к GigaChat...")

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': 'c5036fd3-68e5-4a0a-b357-2ca9f3976628',
        'Authorization': 'Basic MDE5OTYxODItM2M4Zi03MmM0LWI3MTItNzVlZDZjODBjMWZmOjhjMzRkZGQyLThmOGQtNDA0YS1hOTg1LWE1M2Q4ZDNiZmMwYw=='
    }

    try:
        response = requests.post(url, headers=headers, data=payload, verify=True)
        print("✅ Успех! SSL работает с verify=True")
        token = response.json()['access_token']
        print(f"🔑 Токен получен: {token[:50]}...")
    except Exception as e:
        print(f"❌ Ошибка с verify=True: {e}")
        print("🔄 Пробуем с verify=False...")
        try:
            response = requests.post(url, headers=headers, data=payload, verify=False)
            token = response.json()['access_token']
            print(f"🔑 Токен получен (без проверки SSL): {token}...")
        except Exception as e2:
            print(f"❌ Ошибка и с verify=False: {e2}")


if __name__ == "__main__":
    install_russian_cert()
    test_gigachat()