import requests
import json
import time
from typing import Dict, List, Optional
import re


class HHDataCollector:
    """Класс для сбора данных с HH.ru API"""

    def __init__(self):
        self.base_url = "https://api.hh.ru/vacancies"
        # Словарь для маппинга ID регионов на их названия
        self.area_names = {
            1: "Москва",
            2: "Санкт-Петербург",
            87: "Тамбовская область",
            113: "Россия"
        }

    def fetch_vacancies(self,
                        queries: List[str] = None,
                        areas: List[int] = None,
                        per_page: int = 50,
                        pages_per_query: int = 2) -> List[Dict]:
        """
        Получает вакансии по нескольким запросам и регионам
        """
        if queries is None:
            queries = ["Python разработчик", "Data Scientist", "Frontend разработчик"]

        if areas is None:
            areas = [1, 2, 87, 113]  # Москва, СПб, Тамбовская область, Россия

        all_vacancies = []

        for query in queries:
            for area_id in areas:
                area_name = self.area_names.get(area_id, f"Регион {area_id}")
                print(f"Ищем: '{query}' в регионе {area_name} (ID: {area_id})")

                vacancies = self._fetch_vacancies_page(
                    query=query,
                    area=area_id,
                    per_page=per_page,
                    pages=pages_per_query
                )

                if vacancies:
                    # Добавляем информацию о регионе к каждой вакансии
                    for vacancy in vacancies:
                        vacancy['search_region_id'] = area_id
                        vacancy['search_region_name'] = area_name

                    all_vacancies.extend(vacancies)
                    print(f"Найдено: {len(vacancies)} вакансий")

                time.sleep(1)  # Пауза между запросами

        return all_vacancies

    def _fetch_vacancies_page(self, query: str, area: int, per_page: int, pages: int) -> List[Dict]:
        """Получает вакансии с пагинацией"""
        all_items = []

        for page in range(pages):
            params = {
                'text': query,
                'area': area,
                'per_page': per_page,
                'page': page
            }

            try:
                response = requests.get(self.base_url, params=params, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    all_items.extend(items)

                    # Проверяем, есть ли еще страницы
                    if page >= data.get('pages', 1) - 1:
                        break

                    time.sleep(0.5)

                else:
                    print(f"Ошибка HTTP {response.status_code}")
                    break

            except Exception as e:
                print(f"Ошибка: {e}")
                break

        return all_items

    def get_vacancy_details(self, vacancy_id: str) -> Optional[Dict]:
        """
        Получает детальную информацию о вакансии по ID
        включая ключевые навыки
        """
        url = f"{self.base_url}/{vacancy_id}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Ошибка при получении деталей вакансии {vacancy_id}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Ошибка соединения при получении вакансии {vacancy_id}: {e}")
            return None

    def process_vacancy(self, raw_vacancy: Dict) -> Dict:
        """Обрабатывает одну вакансию"""
        # Получаем детальную информацию о вакансии для извлечения ключевых навыков
        vacancy_id = raw_vacancy.get('id')
        detailed_info = self.get_vacancy_details(vacancy_id)

        # Обработка зарплаты
        salary = raw_vacancy.get('salary')
        salary_info = self._process_salary(salary)

        # Обработка навыков - используем детальную информацию если доступна
        if detailed_info and 'key_skills' in detailed_info:
            key_skills = [skill['name'] for skill in detailed_info.get('key_skills', [])]
        else:
            # Если детальная информация недоступна, используем базовую
            key_skills = [skill['name'] for skill in raw_vacancy.get('key_skills', [])]

        # Очистка описания
        description = ""
        if detailed_info:
            description = self._clean_description(detailed_info.get('description', ''))
        else:
            description = self._clean_description(raw_vacancy.get('description', ''))

        # Получаем информацию о локации вакансии
        location = self._get_location(raw_vacancy)

        return {
            "id": raw_vacancy.get("id"),
            "name": raw_vacancy.get("name"),
            "description": description[:1500],  # Ограничиваем длину
            "key_skills": key_skills,
            "company": raw_vacancy.get('employer', {}).get('name'),
            "salary": salary_info,
            "experience": raw_vacancy.get('experience', {}).get('name'),
            "employment": raw_vacancy.get('employment', {}).get('name'),
            "schedule": raw_vacancy.get('schedule', {}).get('name'),
            "url": raw_vacancy.get('alternate_url'),
            "published_at": raw_vacancy.get('published_at'),
            "source": "hh.ru",

            # Простой ключ с локацией (городом)
            "location": location
        }

    def _get_location(self, raw_vacancy: Dict) -> str:
        """Извлекает информацию о локации вакансии - возвращает только город"""
        area_data = raw_vacancy.get('area', {})
        area_name = area_data.get('name', 'Не указано')

        # Если в названии есть запятая, берем только город (первую часть)
        if area_name and ',' in area_name:
            city = area_name.split(',')[0].strip()
            return city

        # Если запятой нет, возвращаем полное название
        return area_name

    def _process_salary(self, salary: Optional[Dict]) -> Optional[str]:
        """Обрабатывает информацию о зарплате"""
        if not salary:
            return None

        salary_from = salary.get('from')
        salary_to = salary.get('to')
        currency = salary.get('currency', 'RUB')

        if salary_from and salary_to:
            return f"{salary_from:,} - {salary_to:,} {currency}".replace(',', ' ')
        elif salary_from:
            return f"от {salary_from:,} {currency}".replace(',', ' ')
        elif salary_to:
            return f"до {salary_to:,} {currency}".replace(',', ' ')
        else:
            return None

    def _clean_description(self, description: str) -> str:
        """Очищает описание от HTML-тегов"""
        if not description:
            return ""

        # Удаляем HTML-теги
        clean_text = re.sub('<[^<]+?>', '', description)
        # Заменяем HTML-сущности
        clean_text = clean_text.replace('&nbsp;', ' ').replace('&quot;', '"')
        # Убираем лишние пробелы
        clean_text = re.sub('\s+', ' ', clean_text).strip()

        return clean_text

    def save_to_json(self, data: List[Dict], filename: str = "vacancies.json"):
        """Сохраняет данные в JSON файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Данные сохранены в {filename}")

    def get_location_statistics(self, vacancies: List[Dict]) -> Dict:
        """Возвращает статистику по локациям"""
        location_stats = {}

        for vacancy in vacancies:
            location = vacancy.get('location', 'Неизвестно')
            if location not in location_stats:
                location_stats[location] = 0
            location_stats[location] += 1

        return dict(sorted(location_stats.items(), key=lambda x: x[1], reverse=True))

    def get_skills_statistics(self, vacancies: List[Dict]) -> Dict:
        """Возвращает статистику по навыкам"""
        skills_stats = {}

        for vacancy in vacancies:
            for skill in vacancy.get('key_skills', []):
                if skill not in skills_stats:
                    skills_stats[skill] = 0
                skills_stats[skill] += 1

        return dict(sorted(skills_stats.items(), key=lambda x: x[1], reverse=True))

    def run_collection(self):
        """Основной метод для запуска сбора данных"""
        print("Начинаем сбор вакансий с HH.ru...")

        # Получаем сырые данные
        raw_vacancies = self.fetch_vacancies()
        print(f"Всего собрано сырых вакансий: {len(raw_vacancies)}")

        # Обрабатываем данные с прогресс-баром
        processed_vacancies = []
        total_vacancies = len(raw_vacancies)

        print("\n🔄 Получаем детальную информацию о вакансиях...")
        for i, raw_vac in enumerate(raw_vacancies):
            processed = self.process_vacancy(raw_vac)
            processed_vacancies.append(processed)

            # Показываем прогресс каждые 10 вакансий
            if (i + 1) % 10 == 0 or (i + 1) == total_vacancies:
                print(f"Обработано: {i + 1}/{total_vacancies} вакансий")

            # Пауза между запросами чтобы не перегружать API
            time.sleep(0.2)

        print(f"✅ Обработано вакансий: {len(processed_vacancies)}")

        # Показываем статистику по локациям
        location_stats = self.get_location_statistics(processed_vacancies)
        print("\n📊 Статистика по городам (топ-15):")
        for location, count in list(location_stats.items())[:15]:
            print(f"  {location}: {count} вакансий")

        # Показываем статистику по навыкам
        skills_stats = self.get_skills_statistics(processed_vacancies)
        print("\n🛠️ Статистика по навыкам (топ-15):")
        for skill, count in list(skills_stats.items())[:15]:
            print(f"  {skill}: {count} упоминаний")

        # Показываем количество вакансий с навыками
        vacancies_with_skills = sum(1 for v in processed_vacancies if v.get('key_skills'))
        print(f"\n📈 Вакансий с указанными навыками: {vacancies_with_skills}/{len(processed_vacancies)}")

        # Сохраняем результат
        self.save_to_json(processed_vacancies, "processed_vacancies.json")

        return processed_vacancies


# Использование
if __name__ == "__main__":
    collector = HHDataCollector()
    vacancies = collector.run_collection()