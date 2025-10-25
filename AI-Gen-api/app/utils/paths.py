"""
Модуль для работы с путями к JSON файлам в проекте.
Централизует доступ к файлам данных.
"""

from pathlib import Path

# Базовые пути
ROOT_DIR = Path(__file__).parent.parent  # app/
JSONS_DIR = ROOT_DIR / "jsons"

# Пути к конкретным файлам
COURSES_DATA_PATH = JSONS_DIR / "courses_data.json"
VACANCIES_DATA_PATH = JSONS_DIR / "processed_vacancies.json"

# Убедимся, что директория существует
JSONS_DIR.mkdir(exist_ok=True)

def ensure_json_file(path: Path) -> None:
    """
    Проверяет существование JSON файла и создает пустой если отсутствует
    """
    if not path.exists():
        path.write_text("{}", encoding="utf-8")

# Инициализация файлов при импорте
ensure_json_file(COURSES_DATA_PATH)
ensure_json_file(VACANCIES_DATA_PATH)