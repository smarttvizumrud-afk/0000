import os
import asyncio
import http.server
import socketserver
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

# --- НАСТРОЙКИ ---
# Вставил твой токен прямо сюда, чтобы Render его точно увидел
TOKEN = "8682838491:AAG6BwrVEV8jaBI4Iw8Cua1Vebc2t_meOWw"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройки для скачивания (исправлен формат и добавлены куки)
YDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'cookiefile': 'cookies.txt',
    'outtmpl': 'video.mp4',
    'noplaylist': True,
    'merge_output_format': 'mp4',
}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("👋 Бот Tubik67 запущен! Присылай ссылку на YouTube.")

@dp.message()
async def download_video(message: types.Message):
    if "youtube.com" in message.text or "youtu.be" in message.text:
        msg = await message.answer("⏳ Начинаю скачивание, подожди...")
        try:
            # Скачиваем видео
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                ydl.download([message.text])
            
            # Отправляем видео в Телеграм
            video = types.FSInputFile("video.mp4")
            await bot.send_video(message.chat.id, video)
            
            # Удаляем временный файл
            if os.path.exists("video.mp4"):
                os.remove("video.mp4")
            await msg.delete()
            
        except Exception as e:
            await message.answer(f"❌ Ошибка: {str(e)}")
    else:
        await message.answer("Пришли рабочую ссылку на YouTube.")

# --- МИНИ-СЕРВЕР ДЛЯ RENDER (ЧТОБЫ НЕ БЫЛО ОШИБКИ PORT TIMEOUT) ---
def run_server():
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Сервер запущен на порту {PORT}")
        httpd.serve_forever()

async def main():
    # Запускаем сервер в фоне
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_server)
    
    # Запускаем бота
    print("Бот Tubik67 в сети!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
