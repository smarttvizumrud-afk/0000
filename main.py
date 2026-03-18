import os
import asyncio
import http.server
import socketserver
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

# --- НАСТРОЙКИ ---
# Вставь свой токен сюда между кавычками
TOKEN = "8682838491:AAG6BwrVEV8jaBi4Iw8Cua1Vebc2t_meOWw" 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройки для скачивания (с куками от капчи)
YDL_OPTIONS = {
    'format': 'best',
    'cookiefile': 'cookies.txt',
    'outtmpl': 'video.mp4',
    'noplaylist': True,
}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("👋 Бот запущен на Render! Кидай ссылку на YouTube.")

@dp.message()
async def download_video(message: types.Message):
    if "youtube.com" in message.text or "youtu.be" in message.text:
        msg = await message.answer("⏳ Начинаю скачивание...")
        try:
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                ydl.download([message.text])
            
            video = types.FSInputFile("video.mp4")
            await bot.send_video(message.chat.id, video)
            os.remove("video.mp4")
            await msg.delete()
        except Exception as e:
            await message.answer(f"❌ Ошибка: {str(e)}")
    else:
        await message.answer("Пришли рабочую ссылку на YouTube.")

# --- ОБМАНКА ДЛЯ RENDER ---
def run_server():
    # Render требует, чтобы какой-то порт был занят
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

async def main():
    # Запускаем сервер в отдельном потоке
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_server)
    
    # Запускаем бота
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
