# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY scripts/ scripts/
COPY knowledge_base/ knowledge_base/

# Создаём папку для индекса
RUN mkdir -p data/faiss_index

# Собираем индекс при сборке образа
RUN python scripts/build_index.py

# Запуск бота
CMD ["python", "scripts/rag_bot.py"]