from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from config import BOT_USERNAME
from database import upsert_user, get_unread_count

from utils import link_keyboard

router = Router()


@router.message(CommandStart(deep_link=False))
async def cmd_start(message: Message):
    user = message.from_user
    await upsert_user(user.id, user.username, user.full_name)

    link = f"https://t.me/{BOT_USERNAME}?start={user.id}"
    unread = await get_unread_count(user.id)
    unread_text = f"\n\n📬 Sizda <b>{unread} ta</b> o'qilmagan xabar bor!" if unread else ""

    await message.answer(
        f"Salom, <b>{user.first_name}</b>! 👋\n\n"
        f"Senga kimdir sir saqlab yozmoqchimi? 😏\n"
        f"Shaxsiy linkingni do'stlaringga yubor va <b>anonim xabarlar</b> ol.\n\n"
        f"🔗 Sening linking:\n<code>{link}</code>{unread_text}",
        reply_markup=link_keyboard(user.id),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "inbox")
async def cb_inbox(call: CallbackQuery):
    await call.answer()
    unread = await get_unread_count(call.from_user.id)
    if unread == 0:
        await call.message.answer(
            "📭 Hozircha xabar yo'q.\n\n"
            "Linkingni do'stlarga yubor va anonim xabarlarni kut! 😏",
            reply_markup=link_keyboard(call.from_user.id),
        )
    else:
        await call.message.answer(
            f"📬 Sizda <b>{unread} ta</b> o'qilmagan xabar bor!\n"
            f"/inbox — barcha xabarlarni ko'rish",
            parse_mode="HTML",
        )
