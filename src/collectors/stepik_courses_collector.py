import requests
import json
import time
from typing import Dict, List, Optional
import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class StepikCourseCollector:
    """Класс для сбора данных о IT-курсах с Stepik через комбинацию API и парсинга"""

    def __init__(self):
        self.base_url = "https://stepik.org/api"
        self.driver = None

        # IT-направления для поиска курсов
        self.it_categories = [
            "Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Rust",
            "Web Development", "Frontend", "Backend", "Fullstack",
            "Data Science", "Machine Learning", "Artificial Intelligence", "AI",
            "DevOps", "Cloud", "AWS", "Docker", "Kubernetes",
            "Mobile Development", "Android", "iOS", "React Native", "Flutter",
            "Cybersecurity", "Information Security", "Ethical Hacking",
            "Database", "SQL", "NoSQL", "PostgreSQL", "MongoDB",
            "Game Development", "Unity", "Unreal Engine",
            "UI/UX Design", "Graphic Design", "Figma",
            "Project Management", "Agile", "Scrum",
            "QA", "Testing", "Automation Testing",
            "Networking", "System Administration", "Linux"
        ]

    def _init_driver(self):
        """Инициализация Selenium WebDriver"""
        if not self.driver:
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # Фоновый режим
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

            self.driver = webdriver.Chrome(options=chrome_options)

    def _get_course_price_from_page(self, course_url: str) -> str:
        """Получает стоимость курса с HTML страницы"""
        try:
            self._init_driver()
            self.driver.get(course_url)

            # Ждем загрузки страницы
            wait = WebDriverWait(self.driver, 10)

            # Сначала проверяем, бесплатный ли курс
            if self._is_course_free():
                return "Бесплатно"

            # Если не бесплатный, ищем цену
            price = self._extract_course_price()
            if price:
                return price

            # Если цена не указана, считаем курс бесплатным
            return "Бесплатно"

        except Exception as e:
            print(f"      Ошибка при получении цены: {e}")
            return "Бесплатно"  # В случае ошибки тоже считаем бесплатным

    def _is_course_free(self) -> bool:
        """Проверяет, бесплатный ли курс"""
        free_indicators = [
            # По классу для бесплатных курсов
            "//span[contains(@class, 'format-price_free')]",
            "//*[contains(@class, 'free')]",
            # По тексту на русском
            "//*[contains(text(), 'Бесплатно')]",
            "//*[contains(text(), 'бесплатно')]",
            # По тексту на английском
            "//*[contains(text(), 'Free')]",
            "//*[contains(text(), 'free')]",
            # По data-атрибуту
            "//*[@data-default-price-free]"
        ]

        for indicator in free_indicators:
            try:
                elements = self.driver.find_elements(By.XPATH, indicator)
                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip().lower()
                        if any(word in text for word in ['бесплатно', 'free']):
                            return True
                        # Если нашли элемент с классом format-price_free, считаем бесплатным
                        if 'format-price_free' in element.get_attribute('class'):
                            return True
            except:
                continue

        return False

    def _extract_course_price(self) -> Optional[str]:
        """Извлекает цену платного курса"""

        # Метод 1: Из data-атрибутов в контейнере цены (ограничиваем область поиска)
        try:
            # Ищем конкретный контейнер цены и берем данные только из него
            price_container_selectors = [
                "//div[contains(@class, 'course-promo-enrollment_price-container')]",
                "//div[contains(@class, 'course-promo-enrollment__price-container')]",
                "//span[contains(@class, 'display-price_price')]",
                "//span[contains(@class, 'format-price')]"
            ]

            for container_selector in price_container_selectors:
                try:
                    container = self.driver.find_element(By.XPATH, container_selector)
                    # Ищем data-атрибуты только внутри этого контейнера
                    integer_elements = container.find_elements(By.XPATH, ".//span[@data-type='integer']")

                    if integer_elements:
                        price_parts = []
                        for elem in integer_elements:
                            # Сначала пробуем получить значение из data-value
                            data_value = elem.get_attribute('data-value')
                            if data_value and data_value.isdigit():
                                price_parts.append(data_value)
                            else:
                                # Если data-value нет, берем текст
                                text = elem.text.strip()
                                if text and any(c.isdigit() for c in text):
                                    # Убираем пробелы и нецифровые символы
                                    digits = ''.join(filter(str.isdigit, text))
                                    if digits:
                                        price_parts.append(digits)

                        if price_parts:
                            full_price = ''.join(price_parts)

                            # Определяем валюту
                            currency = "₽"  # По умолчанию рубли
                            currency_elements = container.find_elements(By.XPATH, ".//span[@data-type='currency']")
                            if currency_elements:
                                currency_data = currency_elements[0].get_attribute('data-value')
                                if currency_data == 'P':
                                    currency = "₽"

                            return f"{full_price} {currency}"

                except:
                    continue
        except Exception as e:
            print(f"      Метод data-атрибутов не сработал: {e}")

        # Метод 2: Поиск по тексту в контейнере цены
        try:
            price_containers = [
                "//div[contains(@class, 'course-promo-enrollment_price-container')]",
                "//div[contains(@class, 'course-promo-enrollment__price-container')]",
                "//span[contains(@class, 'display-price_price')]",
                "//span[contains(@class, 'format-price')]"
            ]

            for container_selector in price_containers:
                try:
                    container = self.driver.find_element(By.XPATH, container_selector)
                    price_text = container.text.strip()

                    # Пропускаем если текст содержит "Бесплатно"
                    if any(word in price_text.lower() for word in ['бесплатно', 'free']):
                        continue

                    # Ищем цену в тексте с помощью регулярных выражений
                    price_patterns = [
                        r'(\d[\d\s]*)\s*[PР₽]',
                        r'(\d+)\s*руб',
                        r'price:\s*(\d+)',
                        r'(\d[\d\s,]+)'
                    ]

                    for pattern in price_patterns:
                        match = re.search(pattern, price_text, re.IGNORECASE)
                        if match:
                            price = match.group(1)
                            # Очищаем цену от пробелов и запятых
                            price = re.sub(r'[\s,]', '', price)
                            if price.isdigit():
                                return f"{price} ₽"

                    # Если не нашли регулярками, извлекаем все цифры
                    digits = re.findall(r'\d+', price_text)
                    if digits:
                        # Берем только первую группу цифр (основную цену)
                        price = digits[0]
                        return f"{price} ₽"

                except:
                    continue

        except Exception as e:
            print(f"      Метод контейнеров не сработал: {e}")

        # Метод 3: Умный поиск по всей странице (только если предыдущие не сработали)
        try:
            # Ищем все элементы с ценами, но фильтруем их
            all_price_elements = self.driver.find_elements(By.XPATH, "//span[@data-type='integer']")

            if all_price_elements:
                # Собираем уникальные цены
                unique_prices = set()
                for elem in all_price_elements:
                    try:
                        # Проверяем, находится ли элемент в видимой области цены
                        parent_text = elem.find_element(By.XPATH, "./..").text
                        if any(word in parent_text.lower() for word in ['цена', 'price', 'стоимость', 'руб', '₽']):
                            data_value = elem.get_attribute('data-value')
                            if data_value and data_value.isdigit():
                                unique_prices.add(data_value)
                            else:
                                text = elem.text.strip()
                                if text and any(c.isdigit() for c in text):
                                    digits = ''.join(filter(str.isdigit, text))
                                    if digits:
                                        unique_prices.add(digits)
                    except:
                        continue

                # Если нашли только одну уникальную цену, возвращаем ее
                if len(unique_prices) == 1:
                    price = list(unique_prices)[0]
                    return f"{price} ₽"
                elif len(unique_prices) > 1:
                    # Если несколько цен, берем самую большую (обычно это полная цена)
                    price = max(unique_prices, key=len)
                    return f"{price} ₽"

        except Exception as e:
            print(f"      Метод поиска по странице не сработал: {e}")

        return None

    def _close_driver(self):
        """Закрывает WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def fetch_stepik_courses(self, query: str, limit: int = 50) -> List[Dict]:
        """Получает курсы с Stepik API"""
        print(f"🔍 Ищем курсы Stepik: '{query}'")

        courses = []
        page = 1

        while len(courses) < limit:
            url = f"{self.base_url}/courses"
            params = {
                'search': query,
                'page': page,
                'page_size': min(20, limit - len(courses))
            }

            try:
                response = requests.get(url, params=params, timeout=15)

                if response.status_code == 200:
                    data = response.json()
                    courses_list = data.get('courses', [])

                    if not courses_list:
                        break

                    for course in courses_list:
                        processed_course = self._process_stepik_course(course)
                        if processed_course:
                            courses.append(processed_course)

                    print(f"   Найдено курсов: {len(courses_list)}")

                    # Проверяем, есть ли следующая страница
                    if len(courses_list) < params['page_size']:
                        break

                    page += 1
                    time.sleep(1)  # Пауза между запросами

                elif response.status_code == 429:
                    print("   ⚠️ Превышен лимит запросов. Ждем 10 секунд...")
                    time.sleep(10)
                    continue
                else:
                    print(f"   Ошибка Stepik API: {response.status_code}")
                    break

            except requests.exceptions.Timeout:
                print("   ⏰ Таймаут запроса. Продолжаем...")
                continue
            except Exception as e:
                print(f"   Ошибка при запросе к Stepik: {e}")
                break

        return courses

    def _process_stepik_course(self, course: Dict) -> Optional[Dict]:
        """Обрабатывает курс с Stepik"""
        # Пропускаем непубличные курсы
        if not course.get('is_public', False):
            return None

        course_id = course.get('id')
        title = course.get('title', '')
        description = course.get('description', '')
        course_url = f"https://stepik.org/course/{course_id}"

        # Получаем дополнительную информацию о курсе
        course_details = self._get_course_details(course_id)

        # Получаем стоимость курса с HTML страницы
        print(f"      Получаем стоимость для курса {course_id}...")
        price = self._get_course_price_from_page(course_url)
        print(f"      Стоимость курса {course_id}: {price}")

        time.sleep(1)  # Пауза между запросами к страницам

        return {
            "id": f"stepik_{course_id}",
            "title": title,
            "description": self._clean_description(description),
            "url": course_url,
            "platform": "Stepik",
            "category": self._categorize_course(title + " " + description),
            "duration": course.get('hours', ''),
            "rating": course.get('rating', ''),
            "learners_count": course.get('learners_count', 0),
            "price": price,  # Используем полученную стоимость
            "language": course.get('language', 'ru'),
            "level": self._determine_level(title + " " + description),
            "skills": self._extract_skills(title + " " + description),
            "instructors": course_details.get('instructors', []),
            "sections_count": course_details.get('sections_count', 0),
            "units_count": course_details.get('units_count', 0),
            "cover_url": course.get('cover', ''),
            "is_certificate_issued": course.get('is_certificate_issued', False)
        }

    def _get_course_details(self, course_id: int) -> Dict:
        """Получает дополнительную информацию о курсе"""
        try:
            url = f"{self.base_url}/courses/{course_id}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                course = data.get('courses', [{}])[0]

                # Получаем информацию об инструкторах
                instructors = []
                owner_id = course.get('owner')
                if owner_id:
                    instructor_info = self._get_user_info(owner_id)
                    if instructor_info:
                        instructors.append(instructor_info)

                return {
                    'sections_count': course.get('sections', []),
                    'units_count': course.get('units', []),
                    'instructors': instructors,
                    'summary': course.get('summary', '')
                }

        except Exception as e:
            print(f"      Ошибка получения деталей курса {course_id}: {e}")

        return {}

    def _get_user_info(self, user_id: int) -> Optional[Dict]:
        """Получает информацию о пользователе (инструкторе)"""
        try:
            url = f"{self.base_url}/users/{user_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                user = data.get('users', [{}])[0]
                return {
                    'name': user.get('full_name', ''),
                    'avatar': user.get('avatar', ''),
                    'is_organization': user.get('is_organization', False)
                }

        except Exception:
            pass  # Игнорируем ошибки получения информации о пользователе

        return None

    def _categorize_course(self, text: str) -> str:
        """Определяет категорию курса на основе текста"""
        text_lower = text.lower()

        category_mapping = {
            'Python': ['python', 'django', 'flask', 'fastapi'],
            'JavaScript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'Java': ['java', 'spring'],
            'Web Development': ['web', 'fullstack', 'full-stack', 'html', 'css'],
            'Frontend': ['frontend', 'front-end'],
            'Backend': ['backend', 'back-end'],
            'Data Science': ['data science', 'data scientist', 'ml', 'machine learning'],
            'AI': ['ai', 'artificial intelligence', 'нейросеть'],
            'DevOps': ['devops', 'docker', 'kubernetes', 'aws', 'cloud'],
            'Mobile': ['mobile', 'android', 'ios', 'react native', 'flutter'],
            'Cybersecurity': ['cybersecurity', 'security', 'безопасность', 'hacking'],
            'Database': ['database', 'sql', 'postgresql', 'mysql', 'mongodb'],
            'Game Development': ['game', 'unity', 'unreal'],
            'Design': ['design', 'ui', 'ux', 'figma'],
            'Management': ['project management', 'agile', 'scrum'],
            'QA': ['qa', 'testing', 'test', 'quality assurance']
        }

        for category, keywords in category_mapping.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return 'Other IT'

    def _determine_level(self, text: str) -> str:
        """Определяет уровень сложности курса"""
        text_lower = text.lower()

        if any(word in text_lower for word in
               ['beginner', 'начальный', 'с нуля', 'для начинающих', 'basic', 'введение']):
            return 'Начальный'
        elif any(word in text_lower for word in ['intermediate', 'средний', 'продолжающий', 'middle']):
            return 'Средний'
        elif any(word in text_lower for word in ['advanced', 'продвинутый', 'senior', 'профессиональный']):
            return 'Продвинутый'
        else:
            return 'Не указан'

    def _extract_skills(self, text: str) -> List[str]:
        """Извлекает навыки из описания курса"""
        skills = []
        text_lower = text.lower()

        # Список IT-навыков для поиска
        it_skills = [
            'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'html', 'css', 'sass', 'less', 'typescript',
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring',
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'git',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy',
            'linux', 'bash', 'nginx', 'apache',
            'rest api', 'graphql', 'microservices', 'ci/cd',
            'agile', 'scrum', 'kanban', 'jira'
        ]

        for skill in it_skills:
            if skill in text_lower:
                skills.append(skill.title())

        return skills[:10]  # Ограничиваем количество навыков

    def _clean_description(self, description: str) -> str:
        """Очищает описание от HTML-тегов"""
        if not description:
            return ""

        # Удаляем HTML-теги
        clean_text = re.sub(r'<[^<]+?>', '', description)
        # Заменяем HTML-сущности
        clean_text = clean_text.replace('&nbsp;', ' ').replace('&quot;', '"')
        # Убираем лишние пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()

        return clean_text[:500]  # Ограничиваем длину

    def collect_all_courses(self, courses_per_category: int = 5) -> List[Dict]:
        """Собирает курсы по всем IT-категориям"""
        all_courses = []

        print("🚀 Начинаем сбор IT-курсов с Stepik...")
        print(f"📚 Категории: {', '.join(self.it_categories[:10])}...")

        for category in self.it_categories:
            print(f"\n🎯 Собираем курсы по категории: {category}")

            stepik_courses = self.fetch_stepik_courses(category, limit=courses_per_category)
            all_courses.extend(stepik_courses)

            time.sleep(2)  # Пауза между категориями

        # Удаляем дубликаты
        unique_courses = self._remove_duplicates(all_courses)
        print(f"\n✅ Собрано уникальных курсов Stepik: {len(unique_courses)}")

        # Закрываем драйвер после завершения сбора
        self._close_driver()

        return unique_courses

    def _remove_duplicates(self, courses: List[Dict]) -> List[Dict]:
        """Удаляет дубликаты курсов по ID"""
        seen_ids = set()
        unique_courses = []

        for course in courses:
            course_id = course.get('id')
            if course_id and course_id not in seen_ids:
                seen_ids.add(course_id)
                unique_courses.append(course)

        return unique_courses

    def save_to_json(self, data: List[Dict], filename: str = "stepik_courses.json"):
        """Сохраняет данные в JSON файл в каталог jsons/"""
        os.makedirs("jsons", exist_ok=True)  # Создаёт каталог jsons, если он не существует
        filepath = os.path.join("jsons", filename)  # Формирует путь jsons/filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"💾 Данные сохранены в {filepath}")

    def run_collection(self):
        """Основной метод для запуска сбора данных"""
        print("🎓 СБОР ДАННЫХ О IT-КУРСАХ С STEPIK")
        print("=" * 50)

        # Собираем курсы (уменьшаем количество для теста)
        courses = self.collect_all_courses(courses_per_category=3)

        if not courses:
            print("❌ Курсы не найдены")
            return []

        # Сохраняем результат
        self.save_to_json(courses, "courses_data.json")

        # Показываем примеры с ценами
        print("\n💰 Примеры курсов с ценами:")
        for course in courses[:5]:
            print(f"  {course['title'][:50]}... - {course['price']}")

        return courses


# Использование
if __name__ == "__main__":
    # Сбор данных о курсах
    collector = StepikCourseCollector()
    courses = collector.run_collection()