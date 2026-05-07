from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject

from config import BOT_USERNAME
from database import upsert_user, get_user, get_unread_count, save_message, count_pending_messages
from utils import link_keyboard, my_link_keyboard, make_share_text
from middlewares import contains_toxic

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


@router.message(CommandStart(deep_link=True))
async def cmd_start_deep(message: Message, command: CommandObject):
    sender = message.from_user
    await upsert_user(sender.id, sender.username, sender.full_name)

    raw = command.args or ""
    # args can be "USER_ID" or "reply_CHATID"
    if raw.startswith("reply_"):
        # handled in chat.py via state — redirect
        await message.answer(
            "💬 Anonim javob yozish uchun pastdagi tugmani bosing.",
        )
        return

    try:
        target_id = int(raw)
    except ValueError:
        await cmd_start.__wrapped__(message) if hasattr(cmd_start, "__wrapped__") else None
        return

    if target_id == sender.id:
        link = f"https://t.me/{BOT_USERNAME}?start={sender.id}"
        await message.answer(
            "😄 Bu sening o'z linking! Do'stlarga yubor:\n"
            f"<code>{link}</code>",
            reply_markup=my_link_keyboard(sender.id),
            parse_mode="HTML",
        )
        return

    target = await get_user(target_id)
    if not target:
        await message.answer("❌ Bu link endi ishlamaydi.")
        return

    pending = await count_pending_messages(target_id)
    from config import MAX_PENDING_MESSAGES
    if pending >= MAX_PENDING_MESSAGES:
        await message.answer("😅 Bu odamning xabar qutisi to'lib ketgan. Keyinroq urinib ko'ring.")
        return

    name = target["full_name"] or target["username"] or "bu odamga"

    # Store target in FSM via answer + state workaround: use callback_data
    from aiogram.fsm.context import FSMContext
    # We'll use a simple approach: store in message text handler state
    await message.answer(
        f"✍️ <b>{name}</b>ga anonim xabar yoz.\n"
        f"U kim ekaningni <b>bilmaydi</b>. 😏\n\n"
        f"Xabaringni yoz (max {500} belgi):",
        parse_mode="HTML",
    )

    # Store target via FSM
    from aiogram.fsm.context import FSMContext
    state: FSMContext = message.bot.get("fsm_storage")


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
