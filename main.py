import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

# Твой токен (Render сам подставит его из Environment Variables, если ты его там указал)
# Либо просто вставь его сюда в кавычки вместо os.getenv
TOKEN = os.getenv("BOT_TOKEN") 
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Настройки скачивания с куками
YDL_OPTIONS = {
    'format': 'best',
    'cookiefile': 'cookies.txt',  # Используем твой файл с куками
    'outtmpl': 'video.mp4',
    'noplaylist': True,
}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("👋 Привет, Ануар! Пришли мне ссылку на YouTube, и я скачаю видео без капчи.")

@dp.message()
async def download_video(message: types.Message):
    if "youtube.com" in message.text or "youtu.be" in message.text:
        msg = await message.answer("⏳ Начинаю скачивание, подожди...")
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
        await message.answer("Пришли мне рабочую ссылку на YouTube.")

# Мини-сервер для Render (чтобы не было ошибки Port Scan Timeout)
async def keep_alive():
    import http.server
    import socketserver
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

async def main():
    # Запускаем "пустой" сервер в фоне для Render
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, lambda: asyncio.run(keep_alive()))
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
