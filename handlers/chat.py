from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import MAX_MESSAGE_LENGTH
from database import (
    get_message, save_message, upsert_user,
    create_anon_chat, get_anon_chat,
)
from middlewares import contains_toxic

router = Router()


class ChatState(StatesGroup):
    writing_reply = State()


def chat_reply_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="💬 Yana javob yozish",
            callback_data=f"reply_chat:{chat_id}"
        )],
    ])


# ── Step 1: receiver taps "Anonim javob" on a message ─────────────────────────
@router.callback_query(F.data.startswith("reply:"))
async def cb_reply_start(call: CallbackQuery, state: FSMContext):
    await call.answer()
    msg_id = int(call.data.split(":")[1])
    original = await get_message(msg_id)

    if not original or original["receiver_id"] != call.from_user.id:
        await call.answer("❌ Xabar topilmadi", show_alert=True)
        return

    # create anon_chat entry: receiver → sender
    sender_id = original["sender_id"]
    if not sender_id:
        await call.message.answer("😔 Bu xabarni yuborgan foydalanuvchi anonim rejimda — javob yuborib bo'lmaydi.")
        return

    chat_id = await create_anon_chat(
        initiator_id=call.from_user.id,  # receiver is now replying
        target_id=sender_id,
        message_id=msg_id,
    )

    await state.set_state(ChatState.writing_reply)
    await state.update_data(chat_id=chat_id, target_id=sender_id)

    await call.message.answer(
        "💬 Anonim javobingizni yozing.\n"
        f"(max {MAX_MESSAGE_LENGTH} belgi — u kim ekaningizni <b>bilmaydi</b>)",
        parse_mode="HTML",
    )


# ── Step 1b: continue existing anon chat ──────────────────────────────────────
@router.callback_query(F.data.startswith("reply_chat:"))
async def cb_reply_chat(call: CallbackQuery, state: FSMContext):
    await call.answer()
    chat_id = int(call.data.split(":")[1])
    chat = await get_anon_chat(chat_id)

    if not chat:
        await call.answer("❌ Suhbat topilmadi", show_alert=True)
        return

    # figure out who the current user is in this chat
    user_id = call.from_user.id
    if user_id == chat["initiator_id"]:
        target_id = chat["target_id"]
    elif user_id == chat["target_id"]:
        target_id = chat["initiator_id"]
    else:
        await call.answer("❌ Ruxsat yo'q", show_alert=True)
        return

    await state.set_state(ChatState.writing_reply)
    await state.update_data(chat_id=chat_id, target_id=target_id)

    await call.message.answer(
        "💬 Javobingizni yozing:",
    )


# ── Step 2: receive the typed reply ───────────────────────────────────────────
@router.message(ChatState.writing_reply, F.text)
async def receive_reply(message: Message, state: FSMContext):
    text = message.text.strip()

    if len(text) > MAX_MESSAGE_LENGTH:
        await message.answer(f"❌ Juda uzun! Max {MAX_MESSAGE_LENGTH} belgi.")
        return

    if contains_toxic(text):
        await message.answer(
            "🚫 Xabarda haqoratli so'zlar bor. Iltimos qayta yozing."
        )
        return

    data = await state.get_data()
    chat_id = data.get("chat_id")
    target_id = data.get("target_id")

    await state.clear()

    if not target_id:
        await message.answer("❌ Xatolik. Qaytadan urinib ko'ring.")
        return

    # save to db
    msg_id = await save_message(
        sender_id=message.from_user.id,
        receiver_id=target_id,
        text=text,
        reply_chain_id=chat_id,
    )

    await message.answer(
        "✅ Anonim javobingiz yuborildi!\n\n"
        "U senga ham javob berishi mumkin. 😏",
        reply_markup=chat_reply_keyboard(chat_id),
    )

    # deliver to target
    try:
        await message.bot.send_message(
            target_id,
            "😏 U senga <b>anonim javob</b> yozdi:",
            parse_mode="HTML",
        )
        await message.bot.send_message(
            target_id,
            f"💬 <i>\u201c{text}\u201d</i>",
            reply_markup=chat_reply_keyboard(chat_id),
            parse_mode="HTML",
        )
    except Exception:
        pass
