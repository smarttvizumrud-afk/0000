# Используем официальный Python
FROM python:3.10-slim

# Устанавливаем ffmpeg (он нужен для сборки видео)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Создаем рабочую папку
WORKDIR /app

# Копируем список библиотек
COPY requirements.txt .

# Устанавливаем библиотеки и сразу обновляем yt-dlp до последней версии
RUN pip install --no-cache-dir -r requirements.txt && pip install -U yt-dlp

# Копируем всё остальное (main.py и твой cookies.txt!)
COPY . .

# Команда для запуска
CMD ["python", "main.py"]
