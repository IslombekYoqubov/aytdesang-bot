from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import ADMIN_ID, BOT_USERNAME
from database import (
    get_unread_count, get_message, mark_read,
    ban_user, save_message, upsert_user, create_anon_chat,
)
from utils import message_keyboard, link_keyboard, make_share_text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


@router.message(Command("inbox"))
async def cmd_inbox(message: Message):
    user = message.from_user
    await upsert_user(user.id, user.username, user.full_name)

    unread = await get_unread_count(user.id)
    if unread == 0:
        await message.answer(
            "📭 Hozircha o'qilmagan xabar yo'q.\n\n"
            "Linkingni ulash va anonim xabarlarni kut! 😏",
            reply_markup=link_keyboard(user.id),
        )
        return

    await message.answer(
        f"📬 Sizda <b>{unread} ta</b> o'qilmagan xabar bor!\n\n"
        f"Xabarlarni ko'rish uchun /next buyrug'ini yuboring.",
        parse_mode="HTML",
    )


@router.message(Command("next"))
async def cmd_next(message: Message):
    from database import db as db_module
    import aiosqlite
    from config import DB_PATH

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT * FROM messages
               WHERE receiver_id = ? AND is_read = 0
               ORDER BY created_at ASC LIMIT 1""",
            (message.from_user.id,),
        ) as cur:
            row = await cur.fetchone()

    if not row:
        await message.answer(
            "📭 Barcha xabarlarni o'qidingiz!\n\n"
            "Linkingni ulashing va yangi xabarlarni kuting. 😏",
            reply_markup=link_keyboard(message.from_user.id),
        )
        return

    msg = dict(row)
    await mark_read(msg["id"])

    remaining = await get_unread_count(message.from_user.id)
    remaining_text = f"\n\n📬 Yana <b>{remaining} ta</b> xabar bor → /next" if remaining else ""

    await message.answer(
        f"💌 <i>\u201c{msg['text']}\u201d</i>{remaining_text}",
        reply_markup=message_keyboard(msg["id"]),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("share:"))
async def cb_share(call: CallbackQuery):
    await call.answer()
    msg_id = int(call.data.split(":")[1])
    msg = await get_message(msg_id)

    if not msg or msg["receiver_id"] != call.from_user.id:
        await call.answer("❌ Xabar topilmadi", show_alert=True)
        return

    share_url = make_share_text(call.from_user.id)
    share_text = (
        f"💌 Menga anonim xabar keldi:\n\n"
        f"<i>\u201c{msg['text']}\u201d</i>\n\n"
        f"Senga ham yozishsinmi? 👀"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📤 Story / do'stlarga yuborish",
            url=f"https://t.me/share/url?url={share_url}&text=Menga+anonim+yoz"
        )]
    ])

    await call.message.answer(share_text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("report:"))
async def cb_report(call: CallbackQuery):
    await call.answer("Shikoyat qabul qilindi ✅", show_alert=True)
    msg_id = int(call.data.split(":")[1])
    msg = await get_message(msg_id)

    if not msg:
        return

    # notify admin
    if ADMIN_ID:
        try:
            sender_info = f"Sender ID: <code>{msg['sender_id']}</code>" if msg["sender_id"] else "Sender: anonymous"
            await call.bot.send_message(
                ADMIN_ID,
                f"🚨 <b>REPORT</b>\n\n"
                f"Message ID: <code>{msg_id}</code>\n"
                f"{sender_info}\n"
                f"Receiver ID: <code>{msg['receiver_id']}</code>\n\n"
                f"Text:\n<i>\u201c{msg['text']}\u201d</i>",
                parse_mode="HTML",
            )
        except Exception:
            pass

    await call.message.answer(
        "🚨 Shikoyatingiz adminga yuborildi. Ko'rib chiqiladi.\n"
        "Agar xabar qoidalarga zid bo'lsa, foydalanuvchi bloklanadi."
    )
