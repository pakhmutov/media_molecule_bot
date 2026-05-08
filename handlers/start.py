from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎵 Музыка"), KeyboardButton(text="🎬 Видео")],
        [KeyboardButton(text="❓ Помощь")],
    ],
    resize_keyboard=True
)

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Отправь мне ссылку на музыку или видео.\n\n"
        "Поддерживаю: YouTube, TikTok, Instagram, VK и 1000+ сайтов.",
        reply_markup=kb
    )

@router.message(lambda m: m.text == "❓ Помощь")
async def cmd_help(message: Message):
    await message.answer(
        "Просто отправь ссылку — я определю формат сам.\n"
        "Или нажми кнопку 🎵 / 🎬 чтобы выбрать заранее."
    )