import aiosqlite
from urllib.parse import quote
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from config import ADMIN_ID, BOT_USERNAME, DB_PATH
from database import get_unread_count, get_message, mark_read, upsert_user

router = Router()


def _share_kb(user_id: int) -> InlineKeyboardMarkup:
    bot_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    share_url = (
        "https://t.me/share/url"
        f"?url={quote(bot_link, safe='')}"
        f"&text={quote('Menga anonim yoz 😏', safe='')}"
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Story / do'stlarga yuborish", url=share_url)],
    ])


def _inbox_kb(user_id: int) -> InlineKeyboardMarkup:
    bot_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
    share_url = (
        "https://t.me/share/url"
        f"?url={quote(bot_link, safe='')}"
        f"&text={quote('Menga anonim yoz 😏', safe='')}"
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 Storyga yuborish", url=share_url)],
    ])


def _msg_kb(msg_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Anonim javob", callback_data=f"reply:{msg_id}"),
            InlineKeyboardButton(text="📤 Ulashish", callback_data=f"share:{msg_id}"),
        ],
        [InlineKeyboardButton(text="🚨 Shikoyat", callback_data=f"report:{msg_id}")],
    ])


@router.message(Command("inbox"))
async def cmd_inbox(message: Message):
    user = message.from_user
    await upsert_user(user.id, user.username, user.full_name)
    unread = await get_unread_count(user.id)
    if unread == 0:
        await message.answer(
            "📭 Hozircha o'qilmagan xabar yo'q.\n\n"
            "Linkingni ulash va anonim xabarlarni kut! 😏",
            reply_markup=_inbox_kb(user.id),
        )
        return
    await message.answer(
        f"📬 Sizda <b>{unread} ta</b> o'qilmagan xabar bor!\n\n"
        f"Ko'rish uchun /next yuboring.",
        parse_mode="HTML",
    )


@router.message(Command("next"))
async def cmd_next(message: Message):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM messages WHERE receiver_id=? AND is_read=0 ORDER BY created_at ASC LIMIT 1",
            (message.from_user.id,),
        ) as cur:
            row = await cur.fetchone()

    if not row:
        await message.answer(
            "📭 Barcha xabarlarni o'qidingiz!\n\nLinkingni ulashing va yangi xabarlarni kuting. 😏",
            reply_markup=_inbox_kb(message.from_user.id),
        )
        return

    msg = dict(row)
    await mark_read(msg["id"])
    remaining = await get_unread_count(message.from_user.id)
    remaining_text = f"\n\n📬 Yana <b>{remaining} ta</b> xabar bor → /next" if remaining else ""

    await message.answer(
        f"💌 <i>\u201c{msg['text']}\u201d</i>{remaining_text}",
        reply_markup=_msg_kb(msg["id"]),
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

    await call.message.answer(
        f"💌 Menga anonim xabar keldi:\n\n"
        f"<i>\u201c{msg['text']}\u201d</i>\n\n"
        f"Senga ham yozishsinmi? 👀",
        reply_markup=_share_kb(call.from_user.id),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("report:"))
async def cb_report(call: CallbackQuery):
    await call.answer("Shikoyat qabul qilindi ✅", show_alert=True)
    msg_id = int(call.data.split(":")[1])
    msg = await get_message(msg_id)
    if not msg:
        return
    if ADMIN_ID:
        try:
            sender_info = f"Sender: <code>{msg['sender_id']}</code>" if msg["sender_id"] else "Sender: anonymous"
            await call.bot.send_message(
                ADMIN_ID,
                f"🚨 <b>REPORT</b>\n\nMsg ID: <code>{msg_id}</code>\n{sender_info}\n"
                f"Receiver: <code>{msg['receiver_id']}</code>\n\n<i>\u201c{msg['text']}\u201d</i>",
                parse_mode="HTML",
            )
        except Exception:
            pass
    await call.message.answer(
        "🚨 Shikoyatingiz adminga yuborildi. Ko'rib chiqiladi."
    )