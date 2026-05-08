import asyncio
import os
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.downloader import download_audio, download_video, get_info

router = Router()

def is_url(text: str) -> bool:
    return bool(re.search(r'https?://[^\s]+', text or ""))

def format_duration(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"

def friendly_error(e: Exception) -> str:
    msg = str(e).lower()
    if 'drm' in msg:
        return "❌ Видео защищено DRM — скачать невозможно."
    if 'private' in msg or 'login' in msg or 'age' in msg:
        return "❌ Видео приватное или требует авторизации."
    if 'blocked' in msg or 'ip' in msg:
        return "❌ Платформа заблокировала доступ с нашего сервера."
    if 'not found' in msg or '404' in msg:
        return "❌ Видео не найдено или удалено."
    if 'timeout' in msg:
        return "❌ Сервер не ответил вовремя, попробуй ещё раз."
    if 'filesize' in msg or 'too large' in msg:
        return "❌ Файл слишком большой (лимит Telegram — 50 МБ)."
    if 'unsupported url' in msg:
        return "❌ Эта платформа не поддерживается."
    return "❌ Не удалось скачать. Попробуй другую ссылку."

@router.message(F.text.func(is_url))
async def handle_link(message: Message):
    match = re.search(r'https?://[^\s]+', message.text)
    url = match.group(0) if match else message.text
    msg = await message.answer("🔍 Получаю информацию...")

    try:
        info = await asyncio.to_thread(get_info, url)

        builder = InlineKeyboardBuilder()
        builder.button(text="🎵 MP3", callback_data=f"audio:{url}")
        builder.button(text="🎬 MP4", callback_data=f"video:{url}")
        builder.button(text="❌ Отмена", callback_data="cancel")
        builder.adjust(2, 1)

        duration = format_duration(info['duration']) if info['duration'] else "?"

        await msg.edit_text(
            f"🎵 <b>{info['title']}</b>\n"
            f"👤 {info['uploader']} · ⏱ {duration}\n\n"
            f"Выбери формат:",
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except Exception as e:
        await msg.edit_text(friendly_error(e))


@router.callback_query(F.data.startswith("audio:"))
async def download_mp3(callback: CallbackQuery):
    url = callback.data.split("audio:", 1)[1]
    await callback.message.edit_text("⏳ Скачиваю MP3...")

    try:
        filepath = await asyncio.to_thread(download_audio, url)
        await callback.message.answer_audio(FSInputFile(filepath))
        await callback.message.delete()
        os.remove(filepath)
    except Exception as e:
        await callback.message.edit_text(friendly_error(e))


@router.callback_query(F.data.startswith("video:"))
async def download_mp4(callback: CallbackQuery):
    url = callback.data.split("video:", 1)[1]
    await callback.message.edit_text("⏳ Скачиваю видео...")

    try:
        filepath = await asyncio.to_thread(download_video, url)
        await callback.message.answer_video(FSInputFile(filepath))
        await callback.message.delete()
        os.remove(filepath)
    except Exception as e:
        await callback.message.edit_text(friendly_error(e))


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery):
    await callback.message.delete()