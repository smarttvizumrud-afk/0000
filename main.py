import os
import asyncio
import http.server
import socketserver
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import yt_dlp

# --- НАСТРОЙКИ ---
# Берем токен из настроек Render (Environment Variables)
# Если хочешь вставить вручную, замени os.getenv("BOT_TOKEN") на "ТВОЙ_ТОКЕН"
TOKEN = os.getenv("8682838491:AAG6BwrVEV8jaBi4Iw8Cua1Vebc2t_meOWw")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обновленные настройки: исправляют ошибку 'Requested format is not available'
YDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'cookiefile': 'cookies.txt',
    'outtmpl': 'video.mp4',
    'noplaylist': True,
    'merge_output_format': 'mp4',
}

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("👋 Бот обновлен! Теперь формат видео исправлен. Кидай ссылку!")

@dp.message()
async def download_video(message: types.Message):
    if "youtube.com" in message.text or "youtu.be" in message.text:
        msg = await message.answer("⏳ Начинаю скачивание видео, это может занять минуту...")
        try:
            # Скачиваем через yt-dlp
            with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
                ydl.download([message.text])
            
            # Отправляем файл
            video = types.FSInputFile("video.mp4")
            await bot.send_video(message.chat.id, video)
            
            # Удаляем файл с сервера после отправки
            if os.path.exists("video.mp4"):
                os.remove("video.mp4")
            await msg.delete()
            
        except Exception as e:
            error_text = str(e)
            if "Requested format is not available" in error_text:
                await message.answer("❌ YouTube не отдает это видео в mp4. Попробуй другую ссылку.")
            else:
                await message.answer(f"❌ Ошибка: {error_text}")
    else:
        await message.answer("Пришли рабочую ссылку на YouTube.")

# --- ОБМАНКА ДЛЯ RENDER (ЧТОБЫ НЕ ВЫКЛЮЧАЛСЯ) ---
def run_server():
    PORT = int(os.environ.get("PORT", 10000))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Сервер-обманка запущен на порту {PORT}")
        httpd.serve_forever()

async def main():
    # Запускаем сервер-заглушку в фоновом потоке
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_server)
    
    # Запускаем бота
    print("Бот Tubik67 запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
