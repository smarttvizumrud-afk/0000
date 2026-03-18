import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.session.aiohttp import AiohttpSession
from yt_dlp import YoutubeDL

# Настройка логирования, чтобы видеть ошибки в Logs
logging.basicConfig(level=logging.INFO)

TOKEN = "8682838491:AAG6BwrVEV8jaBi4Iw8Cua1Vebc2t_meOWw"

# Используем сессию для более стабильного соединения
session = AiohttpSession()
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

progress_data = {}

def my_hook(d):
    chat_id = d.get('info_dict', {}).get('chat_id')
    if chat_id and d['status'] == 'downloading':
        p = d.get('_percent_str', '0%').strip()
        progress_data[chat_id] = f"⏳ Загрузка: {p}"

YDL_OPTIONS = {
    'format': 'best[ext=mp4][height<=720]/best[ext=mp4]',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'default_search': 'ytsearch1:',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("🚀 Бот запущен на сервере! Напиши название канала.")

@dp.message(F.text.lower().contains("где видео"))
async def status_check(message: types.Message):
    res = progress_data.get(message.chat.id, "🔍 Пока ничего не качаю.")
    await message.reply(res)

@dp.message()
async def handle_message(message: types.Message):
    if "где видео" in message.text.lower():
        return

    query = message.text
    chat_id = message.chat.id
    msg = await message.answer(f"🔎 Ищу: {query}...")

    try:
        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        loop = asyncio.get_event_loop()
        def run_dl():
            opts = YDL_OPTIONS.copy()
            opts['progress_hooks'] = [my_hook]
            with YoutubeDL(opts) as ydl:
                return ydl.extract_info(query, download=True, extra_info={'chat_id': chat_id})

        info = await loop.run_in_executor(None, run_dl)
        video_data = info['entries'][0] if 'entries' in info else info
        filename = ydl.prepare_filename(video_data)
        
        if os.path.exists(filename):
            filesize = os.path.getsize(filename) / (1024 * 1024)
            if filesize > 50:
                await msg.edit_text(f"⚠️ Видео слишком тяжелое ({filesize:.1f}МБ). Лимит ТГ — 50МБ.")
            else:
                video_file = types.FSInputFile(filename)
                await bot.send_video(chat_id, video=video_file, caption=f"✅ {video_data.get('title')}")
                await msg.delete()
            os.remove(filename)

    except Exception as e:
        await message.answer(f"❌ Ошибка YouTube: {str(e)[:100]}...")

async def main():
    # Запускаем бота с пропуском накопившихся сообщений
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")