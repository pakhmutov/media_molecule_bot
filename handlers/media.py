import asyncio
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.downloader import download_audio, download_video, get_info

router = Router()

def is_url(text: str) -> bool:
    return text.startswith("http://") or text.startswith("https://")

def format_duration(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"

@router.message(F.text.func(is_url))
async def handle_link(message: Message):
    msg = await message.answer("🔍 Получаю информацию...")

    try:
        info = await asyncio.to_thread(get_info, message.text)

        builder = InlineKeyboardBuilder()
        builder.button(text="🎵 MP3", callback_data=f"audio:{message.text}")
        builder.button(text="🎬 MP4", callback_data=f"video:{message.text}")
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
    except Exception:
        await msg.edit_text("❌ Не удалось получить информацию. Проверь ссылку.")


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
        await callback.message.edit_text("❌ Ошибка при скачивании.")


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
        await callback.message.edit_text("❌ Ошибка при скачивании.")


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery):
    await callback.message.delete()