FROM python:3.11-slim

COPY . .

RUN apt-get update && apt-get install -y libpq-dev

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

WORKDIR /app

# Выполняем миграции перед запуском основного приложения python migrate.py && 
CMD ["sh", "-c", "python app.py"]